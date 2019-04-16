from django.db import transaction
from dwollav2 import ValidationError as DwollaValidationError
from rest_framework.exceptions import ValidationError

from apps.lib.utils import require_lock
from apps.sales.apis import dwolla
from ipware import get_client_ip

from apps.sales.models import BankAccount, TransactionRecord
from apps.sales.utils import account_balance


def make_dwolla_account(request, user, first_name, last_name):
    if user.artist_profile.dwolla_url:
        return user.artist_profile.dwolla_url

    request_body = {
        'firstName': first_name,
        'lastName': last_name,
        'email': user.email,
        'ipAddress': get_client_ip(request)[0]
    }

    with dwolla as api:
        user.artist_profile.dwolla_url = api.post('customers', request_body).headers['location']
        user.artist_profile.save()
    return user.artist_profile.dwolla_url


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
            response = api.post('{}/funding-sources'.format(user.artist_profile.dwolla_url), request_body)
        except DwollaValidationError as err:  # pragma: no cover
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
@require_lock(TransactionRecord, 'ACCESS EXCLUSIVE')
def initiate_withdraw(user, bank, amount, test_only=True):
    balance = account_balance(user, TransactionRecord.HOLDINGS)
    if amount.amount > balance:
        raise ValidationError({'amount': ['Amount cannot be greater than current balance of {}.'.format(balance)]})
    if test_only:
        return
    record = TransactionRecord(
        category=TransactionRecord.CASH_WITHDRAW,
        payee=user,
        payer=user,
        source=TransactionRecord.HOLDINGS,
        destination=TransactionRecord.BANK,
        status=TransactionRecord.PENDING,
        amount=amount,
        target=bank,
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
            record.remote_id = transfer.headers['location'].split('/transfers/')[-1].strip('/')
            record.save()
        except Exception as err:
            record.status = TransactionRecord.FAILURE
            record.remote_message = str(err)
            record.save()
            raise
        return record
