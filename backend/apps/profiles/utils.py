from django.db.models import Case, When, F, IntegerField, Q

from apps.profiles.models import Character, ImageAsset


def char_ordering(qs, requester, query=''):
    return qs.annotate(
        # Make target user characters negative so they're always first.
        mine=Case(
            When(user_id=requester.id, then=0-F('id')),
            default=F('id'),
            output_field=IntegerField(),
        ),
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
    ).order_by('matches', 'mine', 'tag_matches')


def available_chars(requester, query='', commissions=False, ordering=True):
    exclude = Q(private=True)
    if commissions:
        exclude |= Q(open_requests=False)
    q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
    qs = Character.objects.filter(q).exclude(exclude & ~Q(user=requester))
    qs = qs.exclude(tags__in=requester.blacklist.all())
    if ordering:
        qs = char_ordering(qs, requester, query=query)
    return qs.distinct()


def available_assets(request, requester):
    exclude = Q(private=True)
    if request.user.is_authenticated():
        exclude &= ~Q(uploaded_by=requester)
    return ImageAsset.objects.exclude(exclude).exclude(rating__gt=request.max_rating).exclude(tags__in=request.blacklist)
