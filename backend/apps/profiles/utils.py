from dateutil.relativedelta import relativedelta
from django.db.models import Case, When, F, IntegerField, Q
from django.utils import timezone

from apps.lib.models import REFERRAL_LANDSCAPE_CREDIT, REFERRAL_PORTRAIT_CREDIT
from apps.lib.utils import notify
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
    if (not requester.is_staff) and requester.is_authenticated:
        exclude |= Q(user__blocking=requester)
    if commissions:
        exclude |= Q(open_requests=False)
    if query:
        q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
    else:
        q = Q()
    q = Character.objects.filter(q)
    if requester.is_authenticated:
        if commissions:
            exclude_exception = Q(shared_with=requester) & Q(open_requests=True)
        else:
            exclude_exception = Q(shared_with=requester)
        qs = q.exclude(exclude & ~(Q(user=requester) | exclude_exception))
        if not self_search:
            # Never make our blacklist exclude our own characters, lest we lose track of them.
            qs = qs.exclude(tags__in=requester.blacklist.all())
    else:
        qs = q.exclude(exclude)
    if tagging:
        qs = qs.exclude(Q(taggable=False) & ~Q(user=requester))
        qs = qs.exclude(transfer__isnull=False)
    return qs.distinct()


def available_artists(requester):
    qs = User.objects.filter(Q(id=requester.id) | Q(artist_tagging_disabled=False))
    if not requester.is_staff and requester.is_authenticated:
        qs = qs.exclude(blocking=requester)
    return qs


def available_assets(request, requester):
    exclude = Q(private=True)
    if not request.user.is_staff and request.user.is_authenticated:
        exclude |= Q(owner__blocking=requester)
        exclude |= Q(owner__blocked_by=requester)
        exclude |= Q(artists__blocking=requester)
        exclude |= Q(artists__blocked_by=requester)
    if request.user.is_authenticated:
        exclude &= ~(Q(owner=requester) | Q(shared_with=requester))
    return ImageAsset.objects.exclude(exclude).exclude(
        rating__gt=request.max_rating
    ).exclude(tags__in=request.blacklist)


def available_users(request):
    if request.user.is_staff or not request.user.is_authenticated:
        return User.objects.all()
    return User.objects.exclude(id__in=request.user.blocked_by.all().values('id'))


def extend_landscape(user, months):
    today = timezone.now().date()
    if user.landscape_paid_through and user.landscape_paid_through > today:
        start_point = user.landscape_paid_through
    else:
        start_point = today
    user.landscape_paid_through = start_point + relativedelta(months=months)
    if not (user.portrait_paid_through and user.portrait_paid_through > user.landscape_paid_through):
        user.portrait_paid_through = user.landscape_paid_through
    user.save()


def extend_portrait(user, months):
    today = timezone.now().date()
    if user.portrait_paid_through and user.portrait_paid_through > today:
        start_point = user.portrait_paid_through
    else:
        start_point = today
    user.portrait_paid_through = start_point + relativedelta(months=months)
    user.save()


def credit_referral(order):
    seller_credit = False
    buyer_credit = False
    if not order.seller.sold_shield_on:
        seller_credit = True
        order.seller.sold_shield_on = timezone.now()
        order.seller.save()
    if not order.buyer.bought_shield_on:
        buyer_credit = True
        order.buyer.bought_shield_on = timezone.now()
        order.buyer.save()
    if seller_credit and order.seller.referred_by:
        extend_landscape(order.seller, months=1)
        notify(REFERRAL_LANDSCAPE_CREDIT, order.seller.referred_by, unique=False)
    if buyer_credit and order.buyer.referred_by:
        extend_portrait(order.seller, months=1)
        notify(REFERRAL_PORTRAIT_CREDIT, order.buyer.referred_by, unique=False)
