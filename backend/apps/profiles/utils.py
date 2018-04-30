from django.db.models import Case, When, F, IntegerField, Q

from apps.profiles.models import Character, ImageAsset, User


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


def available_chars(requester, query='', commissions=False, tagging=False, self_search=False):
    exclude = Q(private=True)
    if commissions:
        exclude |= Q(open_requests=False)
    if query:
        q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
    else:
        q = Q()
    q = Character.objects.filter(q)
    if requester.is_authenticated:
        qs = q.exclude(exclude & ~(Q(user=requester) | Q(shared_with=requester)))
        if not self_search:
            # Never make our blacklist exclude our own characters, lest we lose track of them.
            qs = qs.exclude(tags__in=requester.blacklist.all())
    else:
        qs = q.exclude(exclude)
    if tagging:
        qs = qs.exclude(Q(taggable=False) & ~Q(user=requester))
        qs.exclude(transfer__isnull=False)
    return qs.distinct()


def available_artists(requester):
    return User.objects.filter(Q(id=requester.id) | Q(artist_tagging_disabled=False))


def available_assets(request, requester):
    exclude = Q(private=True)
    if request.user.is_authenticated:
        exclude &= ~(Q(owner=requester) | Q(shared_with=requester))
    return ImageAsset.objects.exclude(exclude).exclude(
        rating__gt=request.max_rating
    ).exclude(tags__in=request.blacklist)
