from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.db.models import Case, When, F, IntegerField, Q
from django.utils import timezone
from short_stuff import gen_guid, slugify

from apps.lib.models import REFERRAL_LANDSCAPE_CREDIT, REFERRAL_PORTRAIT_CREDIT, Comment
from apps.lib.utils import notify, destroy_comment
from apps.profiles.models import Character, Submission, User, Conversation, ConversationParticipant
from apps.sales.dwolla import destroy_bank_account
from apps.sales.models import Order, TransactionRecord
from apps.sales.utils import account_balance, PENDING, cancel_order


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
    return qs.distinct()


def available_artists(requester):
    qs = User.objects.filter(Q(id=requester.id) | Q(taggable=True))
    if not requester.is_staff and requester.is_authenticated:
        qs = qs.exclude(blocking=requester)
    return qs


def available_submissions(request, requester):
    exclude = Q(private=True)
    if not request.user.is_staff and request.user.is_authenticated:
        exclude |= Q(owner__blocking=requester)
        exclude |= Q(owner__blocked_by=requester)
        exclude |= Q(artists__blocking=requester)
        exclude |= Q(artists__blocked_by=requester)
    if request.user.is_authenticated:
        exclude &= ~(Q(owner=requester) | Q(shared_with=requester))
    return Submission.objects.exclude(exclude).exclude(
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


def empty_user(request):
    return {'blacklist': [], 'rating': request.rating, 'sfw_mode': request.sfw_mode, 'username': '_'}


def create_guest_user(email: str) -> User:
    # Start with a username unlikely to cause collision
    username = f'__{slugify(gen_guid())}'
    user = User.objects.create(
        guest=True, email=f'{username}@localhost', guest_email=email, username=username
    )
    # Create username in a pattern we can quickly recognize elsewhere in the code even if the user is not yet loaded.
    user.username = f'__{user.id}'
    user.email = f'__{user.id}@localhost'
    user.save()
    return user


def clear_user(user: User):
    # Clears out as much user data as is practical. Uses normal iterators, despite being slow, to ensure all cleanup
    # hooks are run.
    holdup_statuses = [Order.DISPUTED, Order.IN_PROGRESS, Order.QUEUED, Order.REVIEW]
    if user.sales.filter(status__in=holdup_statuses).exists():
        raise RuntimeError('User has outstanding sales to finish. Cannot remove!')
    if user.buys.filter(status__in=holdup_statuses).exists():
        raise RuntimeError('User has outstanding orders which are unfinished. Cannot remove!')
    for sale in user.sales.filter(status__in=[Order.NEW, Order.PAYMENT_PENDING]):
        cancel_order(sale, user)
    for order in user.buys.filter(status__in=[Order.NEW, Order.PAYMENT_PENDING]):
        cancel_order(order, user)
    stoppers = [
        account_balance(user, TransactionRecord.HOLDINGS),
        account_balance(user, TransactionRecord.HOLDINGS, PENDING)
    ]
    if any(stoppers):
        raise RuntimeError('User has uncleared transactions! Cannot remove!')

    notes = user.notes
    if notes:
        notes += f'\n\nUsername: {user.username}, Email: {user.email}, removed on {timezone.now()}'
    user.username = f'__deleted{user.id}'
    user.set_password(str(uuid4()))
    user.is_active = False
    user.landscape_enabled = False
    user.portrait_enabled = False
    user.subscription_set.all().delete()
    user.save()
    for favorite in user.favorites.all():
        user.favorites.remove(favorite)
    for watcher in user.watched_by.all():
        user.watched_by.remove(watcher)
    for watcher in user.watching.all():
        user.watching.remove(watcher)
    for submission in user.owned_profiles_submission.all():
        submission.delete()
    for character in user.characters.all():
        character.delete()
    for conversation in user.conversations.all():
        leave_conversation(user, conversation)
    for comment in user.comment_set.all():
        destroy_comment(comment)
    for product in user.products.all():
        product.delete()
    for bank in user.banks.all():
        destroy_bank_account(bank)
    for card in user.credit_cards.all():
        card.mark_deleted()
    # These can just be straight up cleared.
    user.notifications.all().delete()


def leave_conversation(user: User, conversation: Conversation):
    participant = ConversationParticipant.objects.filter(conversation=conversation, user=user).first()
    if participant:
        participant.delete()
    count = conversation.participants.all().count()
    if not count:
        conversation.delete()
    elif count == 1:
        if not conversation.comments.exclude(system=True).exists():
            conversation.delete()
            return
    if participant:
        Comment(user=user, system=True, content_object=conversation, text='left the conversation.').save()
