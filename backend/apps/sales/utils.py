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
            str(user.escrow_holdings.filter(
                status=PaymentRecord.SUCCESS).exclude(
                type__in=[
                    PaymentRecord.DISBURSEMENT_SENT,
                    PaymentRecord.DISBURSEMENT_RETURNED,
                ]
            ).aggregate(Sum('amount'))['amount__sum']))
    except InvalidOperation:
        credit = Decimal('0.00')

    return credit - debit


def available_balance(user):
    try:
        debit = Decimal(
            str(user.debits.filter(
                status=PaymentRecord.SUCCESS,
                source=PaymentRecord.ACCOUNT,
                # In the case of disbursement failed, we use success by default since it's a record from Dwolla, not
                # us.
                type__in=[PaymentRecord.DISBURSEMENT_SENT, PaymentRecord.TRANSFER, PaymentRecord.DISBURSEMENT_RETURNED],
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


def product_ordering(qs, query=''):
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
        # How can we make it distinct on id while making matches and tag_matches priority ordering?
    ).order_by('id', 'matches', 'tag_matches').distinct('id')


def available_products(requester, query=''):
    exclude = Q(hidden=True)
    q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
    if requester.is_authenticated:
        qs = Product.objects.filter(q).exclude(exclude & ~Q(user=requester))
        qs = qs.exclude(Q(task_weight__gt=F('user__max_load')-F('user__load')) & ~Q(user=requester))
        qs = qs.filter(Q(max_parallel=0) | Q(parallel__lt=F('max_parallel')) | Q(user=requester))
    else:
        qs = Product.objects.filter(q).exclude(exclude)
        qs = qs.exclude(Q(task_weight__gt=F('user__max_load')-F('user__load')))
        qs = qs.filter(Q(max_parallel=0) | Q(parallel__lt=F('max_parallel')))
    return product_ordering(qs, query)


RESPONSE_TRANSLATORS = {
    '54': 'This transaction cannot be refunded. It may not yet have posted. '
          'Please try again tomorrow, and contact support if it still fails.',
    'E00027': "The zip or address we have on file for your card is either incorrect or has changed. Please remove the "
          "card and add it again with updated information.",
    'E00040': "Something is wrong in our records with the card you've added. Please remove the card and re-add it."
}
