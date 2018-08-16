from django.db import transaction
from dwollav2 import ValidationError as DwollaValidationError
from rest_framework.exceptions import ValidationError

from apps.lib.models import TRANSFER_FAILED
from apps.lib.utils import require_lock, notify
from apps.sales.apis import dwolla
from ipware import get_client_ip

from apps.sales.models import BankAccount, PaymentRecord
from apps.sales.utils import available_balance


def make_dwolla_account(request, user, first_name, last_name):
    if user.dwolla_url:
        return user.dwolla_url

    request_body = {
        'firstName': first_name,
        'lastName': last_name,
        'email': user.email,
        'ipAddress': get_client_ip(request)[0]
    }

    with dwolla as api:
        user.dwolla_url = api.post('customers', request_body).headers['location']
        user.save()
    return user.dwolla_url


VALIDATION_FIELD_MAP = {
    '/routingNumber': 'routing_number',
    '/accountNumber': 'account_number'
}


def add_bank_account(user, account_number, routing_number, account_type):
    type_label = 'checking' if account_type == BankAccount.CHECKING else 'savings'
    request_body = {
        'routingNumber': routing_number,
        'accountNumber': account_number,
        'bankAccountType': type_label,
        'name': '{} - {} {}'.format(
            '{} (ID: {})'.format(user.username, user.id), type_label.title(), account_number[-4:]
        )
    }
    with dwolla as api:
        try:
            response = api.post('{}/funding-sources'.format(user.dwolla_url), request_body)
        except DwollaValidationError as err:
            errors = {}
            for err in err.body['_embedded']['errors']:
                field = VALIDATION_FIELD_MAP.get(err['path'])
                if field in errors:
                    errors[field].append(err['message'])
                else:
                    errors[field] = [err['message']]
            raise ValidationError(errors)

    account = BankAccount(user=user, last_four=account_number[-4:], type=account_type, url=response.headers['location'])
    account.save()

    return account


def destroy_bank_account(account):
    with dwolla as api:
        api.post(account.url, {'removed': True})
    account.deleted = True
    account.save()


@transaction.atomic
@require_lock(PaymentRecord, 'ACCESS EXCLUSIVE')
def initiate_withdraw(user, bank, amount, test_only=True):
    balance = available_balance(user)
    if amount.amount > balance:
        raise ValidationError({'amount': ['Amount cannot be greater than current balance of {}.'.format(balance)]})
    if test_only:
        return
    record = PaymentRecord(
        type=PaymentRecord.DISBURSEMENT_SENT,
        payee=None,
        payer=user,
        # We will flip this if there's any issue. For now, we need to make sure there is not a chance for someone
        # to withdraw within the next millisecond.
        # If there's a bug in the code between here and then, these funds will be inaccessible and it will be
        # a customer service issue.
        status=PaymentRecord.SUCCESS,
        amount=amount,
        source=PaymentRecord.ACCOUNT,
        txn_id='N/A',
        target=bank,
        finalized=False
    )
    record.save()
    return record


def perform_transfer(record, note='Disbursement'):
    transfer_request = {
        '_links': {
            'source': {
                'href': dwolla.funding_url
            },
            'destination': {
                'href': record.target.url
            }
        },
        'amount': {
            'currency': str(record.amount.currency),
            'value': str(record.amount.amount),
        },
        'metadata': {
            'customerId': str(record.target.user.id),
            'notes': note
        }
    }
    with dwolla as api:
        try:
            transfer = api.post('transfers', transfer_request)
            record.txn_id = transfer.headers['location'].split('/transfers/')[-1].strip('/')
            record.save()
        except Exception:
            record.status = PaymentRecord.FAILURE
            record.finalized = True
            record.save()
            raise
        return record


@require_lock(PaymentRecord, 'ACCESS EXCLUSIVE')
@transaction.atomic
def refund_transfer(record):
    if PaymentRecord.objects.filter(txn_id=record.txn_id, type=PaymentRecord.DISBURSEMENT_RETURNED).count():
        return
    PaymentRecord(
        status=PaymentRecord.SUCCESS,
        type=PaymentRecord.DISBURSEMENT_RETURNED,
        amount=record.amount,
        payer=None,
        payee=record.payer,
        source=PaymentRecord.ACH,
        txn_id=record.txn_id
    ).save()
    notify(
        TRANSFER_FAILED,
        record.payer,
        data={
            'error': 'The bank rejected the transfer. Please try again, update your account information, '
                     'or contact support.'
        }
    )
