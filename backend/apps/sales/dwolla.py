from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from dwollav2 import ValidationError as DwollaValidationError
from rest_framework.exceptions import ValidationError

from apps.lib.models import ref_for_instance
from apps.lib.utils import require_lock
from apps.sales.apis import dwolla
from ipware import get_client_ip

from apps.sales.models import BankAccount, TransactionRecord, COMPLETED, Deliverable
from apps.sales.utils import account_balance

TRANSACTION_STATUS_MAP = {
    'pending': TransactionRecord.PENDING,
    'processed': TransactionRecord.SUCCESS,
    'failed': TransactionRecord.FAILURE,
    'cancelled': TransactionRecord.FAILURE,
}


def make_dwolla_account(request, user, first_name, last_name):
    if user.artist_profile.dwolla_url:
        return user.artist_profile.dwolla_url

    request_body = {
        'firstName': first_name,
        'lastName': last_name,
        'email': user.email,
        'type': 'receive-only',
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


@require_lock(TransactionRecord, 'ACCESS EXCLUSIVE')
def initiate_withdraw(user, bank, amount, test_only=True):
    balance = account_balance(user, TransactionRecord.HOLDINGS)
    if amount.amount > balance:
        raise ValidationError({'amount': ['Amount cannot be greater than current balance of {}.'.format(balance)]})
    if test_only:
        return None, Deliverable.objects.none()
    main_record = TransactionRecord(
        category=TransactionRecord.CASH_WITHDRAW,
        payee=user,
        payer=user,
        source=TransactionRecord.HOLDINGS,
        destination=TransactionRecord.BANK,
        status=TransactionRecord.PENDING,
        amount=amount,
    )
    main_record.save()
    main_record.targets.add(ref_for_instance(bank))
    deliverables = Deliverable.objects.select_for_update().filter(
        payout_sent=False, order__seller=user, status=COMPLETED, escrow_disabled=False,
    )
    main_record.targets.add(*(ref_for_instance(deliverable) for deliverable in deliverables))
    return main_record, deliverables


def perform_transfer(record, deliverables, note='Disbursement'):
    from .tasks import get_transaction_fees
    bank = record.targets.filter(content_type=ContentType.objects.get_for_model(BankAccount)).get().target
    transfer_request = {
        '_links': {
            'source': {
                'href': dwolla.funding_url
            },
            'destination': {
                'href': bank.url
            }
        },
        'amount': {
            'currency': str(record.amount.currency),
            'value': str(record.amount.amount),
        },
        'metadata': {
            'customerId': str(bank.user.id),
            'notes': note
        }
    }
    with dwolla as api:
        try:
            transfer = api.post('transfers', transfer_request)
            record.remote_id = transfer.headers['location'].split('/transfers/')[-1].strip('/')
            record.remote_message = ''
            record.save()
            deliverables.update(payout_sent=True)
            get_transaction_fees.delay(str(record.id))
        except Exception as err:
            record.status = TransactionRecord.FAILURE
            record.remote_message = str(err)
            record.save()
            raise
        return record
