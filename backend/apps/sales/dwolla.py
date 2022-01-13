from apps.sales.apis import dwolla

from apps.sales.models import TransactionRecord

TRANSACTION_STATUS_MAP = {
    'pending': TransactionRecord.PENDING,
    'processed': TransactionRecord.SUCCESS,
    'failed': TransactionRecord.FAILURE,
    'cancelled': TransactionRecord.FAILURE,
}


VALIDATION_FIELD_MAP = {
    '/routingNumber': 'routing_number',
    '/accountNumber': 'account_number'
}


def destroy_bank_account(account):
    with dwolla as api:
        api.post(account.url, {'removed': True})
    account.deleted = True
    account.save()
