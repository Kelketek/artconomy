from apps.sales.apis import dwolla
from ipware import get_client_ip
from uuid import uuid4


def make_dwolla_account(request, user):
    request_body = {
        'firstName': user.first_name,
        'lastName': user.last_name,
        'email': user.email,
        'ipAddress': get_client_ip(request)
    }

    if user.dwolla_url:
        return user.dwolla_url

    with dwolla as api:
        user.dwolla_url = api.post('customers', request_body).headers['location']
        user.save()
    return user.dwolla_url


def add_bank_account(user, account_number, routing_number, account_type):
    from apps.sales.models import BankAccount
    type_label = 'checking' if account_type == BankAccount.CHECKING else 'savings'
    request_body = {
        'routingNumber': routing_number,
        'accountNumber': account_number,
        'bankAccountType': type_label,
        'name': '{} - {} {}'.format(user.get_full_name(), type_label.title(), account_number[:4])
    }
    with dwolla as api:
        response = api.post('{}/funding-sources'.format(user.dwolla_url), request_body)

    account = BankAccount(user=user, last_four=account_number[:4], type=account_type, url=response.headers['location'])
    account.save()

    return account


def perform_transfer(target_account, amount, note='Disbursement'):
    from apps.sales.models import PaymentRecord
    uuid = uuid4()
    record = PaymentRecord(
        payee=None,
        payer=target_account,
        status=PaymentRecord.FAILURE,
        amount=amount,
        source=PaymentRecord.ACCOUNT,
        txn_id=uuid,
    )
    record.save()
    transfer_request = {
        '_links': {
            'source': {
                'href': dwolla.funding_url
            },
            'destination': {
                'href': target_account
            }
        },
        'amount': {
            'currency': amount.currency,
            'value': str(amount.amount),
        },
        'metadata': {
            'customerId': str(target_account.user.id),
            'notes': note
        }
    }

    with dwolla as api:
        transfer = api.post('transfers', transfer_request)
        print(transfer)
        record.success = True
        record.save()
        return record
