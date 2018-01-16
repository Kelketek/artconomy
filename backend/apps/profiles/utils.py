from django.db.models import Case, When, F, IntegerField, Q

from apps.profiles.models import Character


def char_ordering(qs, requester):
    return qs.annotate(
        # Make target user characters negative so they're always first.
        mine=Case(
            When(user_id=requester.id, then=0-F('id')),
            default=F('id'),
            output_field=IntegerField(),
        )
    ).order_by('mine')


def available_chars(requester, query='', commissions=False, ordering=True):
    exclude = Q(private=True)
    if commissions:
        exclude |= Q(open_requests=False)
    qs = Character.objects.filter(
        name__istartswith=query
    ).exclude(exclude & ~Q(user=requester))

    if ordering:
        qs = char_ordering(qs, requester)
    return qs
