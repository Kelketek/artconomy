from decimal import Decimal, InvalidOperation

from django.db.models import Sum, Q, IntegerField, Case, When, F

from apps.sales.models import PaymentRecord, Product


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


def translate_authnet_error(err):
    response = str(err)
    if hasattr(err, 'full_response'):
        # API is inconsistent in how it returns error info.
        if 'response_reason_text' in err.full_response:
            response = err.full_response['response_reason_text']
        if 'response_text' in err.full_response:
            response = err.full_response['response_text']
        if 'response_reason_code' in err.full_response:
            response = RESPONSE_TRANSLATORS.get(err.full_response['response_reason_code'], response)
        if 'response_code' in err.full_response:
            response = RESPONSE_TRANSLATORS.get(err.full_response['response_code'], response)
    return response


def product_ordering(qs, requester, query=''):
    return qs.annotate(
        matches=Case(
            When(name__iexact=query, then=0),
            default=1,
            output_field=IntegerField()
        ),
        tag_matches=Case(
            When(tags__name__iexact=query, then=0),
            default=1,
            output_field=IntegerField()
        )
    ).order_by('matches', 'tag_matches')


def available_products(requester, query='', ordering=True):
    exclude = Q(hidden=True)
    q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
    qs = Product.objects.filter(q).exclude(exclude & ~Q(user=requester))

    if ordering:
        qs = product_ordering(qs, requester, query=query)
    return qs


RESPONSE_TRANSLATORS = {
    '54': 'This transaction cannot be refunded. It may not yet have posted. '
          'Please try again tomorrow, and contact support if it still fails.',
    'E00027': "The zip or address we have on file for your card is either incorrect or has changed. Please remove the "
          "card and add it again with updated information.",
    'E00040': "Something is wrong in our records with the card you've added. Please remove the card and re-add it."
}
