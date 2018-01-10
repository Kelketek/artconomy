from decimal import Decimal, InvalidOperation

from django.db.models import Sum

from apps.sales.models import PaymentRecord


def escrow_balance(user):
    try:
        debit = Decimal(
            str(user.credits.filter(
                status=PaymentRecord.SUCCESS,
                source=PaymentRecord.ESCROW
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    try:
        credit = Decimal(
            str(user.escrow_holdings.filter(status=PaymentRecord.SUCCESS).aggregate(Sum('amount'))['amount__sum']))
    except InvalidOperation:
        credit = Decimal('0.00')

    return credit - debit


def available_balance(user):
    try:
        debit = Decimal(
            str(user.debits.filter(
                status=PaymentRecord.SUCCESS,
                source=PaymentRecord.ACCOUNT,
                type=PaymentRecord.DISBURSEMENT,
            ).aggregate(Sum('amount'))['amount__sum'])
        )
    except InvalidOperation:
        debit = Decimal('0.00')
    try:
        credit = Decimal(
            str(user.credits.filter(status=PaymentRecord.SUCCESS).aggregate(Sum('amount'))['amount__sum']))
    except InvalidOperation:
        credit = Decimal('0.00')

    return credit - debit