from uuid import uuid4

from avatar.models import Avatar
from avatar.templatetags.avatar_tags import avatar_url
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Case, When, F, IntegerField, Q
from django.utils import timezone
from short_stuff import gen_shortcode

from apps.lib.models import REFERRAL_LANDSCAPE_CREDIT, Comment
from apps.lib.utils import notify, destroy_comment
from apps.profiles.middleware import derive_session_settings
from apps.profiles.models import Character, Submission, User, Conversation, ConversationParticipant
from apps.sales.dwolla import destroy_bank_account
from apps.sales.models import TransactionRecord, DISPUTED, IN_PROGRESS, QUEUED, REVIEW, PAYMENT_PENDING, NEW, \
    Deliverable, WAITING, StripeAccount, CreditCardToken, ServicePlan
from apps.sales.utils import account_balance, PENDING, cancel_deliverable


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
    q = q.exclude(user__is_active=False)
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
    qs = User.objects.filter(Q(id=requester.id) | Q(taggable=True), is_active=True)
    if not requester.is_staff and requester.is_authenticated:
        qs = qs.exclude(blocking=requester)
    return qs


def available_submissions(request, requester):
    exclude = Q(private=True)
    exclude |= Q(owner__is_active=False)
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


def available_users(user):
    if user.is_staff or not user.is_authenticated:
        return User.objects.exclude(is_active=False)
    return User.objects.exclude(id__in=user.blocked_by.all().values('id')).exclude(is_active=False)


def extend_landscape(user, months):
    today = timezone.now().date()
    if user.service_plan_paid_through and user.service_plan_paid_through > today:
        start_point = user.landscape_paid_through
    else:
        start_point = today
    user.service_plan_paid_through = start_point + relativedelta(months=months)
    user.service_plan = ServicePlan.objects.get(name='Landscape')
    user.save()


def credit_referral(deliverable):
    seller_credit = False
    if not deliverable.order.seller.sold_shield_on:
        seller_credit = True
        deliverable.order.seller.sold_shield_on = timezone.now()
        deliverable.order.seller.save()
    if deliverable.order.buyer and not deliverable.order.buyer.bought_shield_on:
        deliverable.order.buyer.bought_shield_on = timezone.now()
        deliverable.order.buyer.save()
    if seller_credit and deliverable.order.seller.referred_by:
        extend_landscape(deliverable.order.seller, months=1)
        notify(REFERRAL_LANDSCAPE_CREDIT, deliverable.order.seller.referred_by, unique=False)


def empty_user(*, session, user):
    session_settings = derive_session_settings(user=user, session=session)
    return {
        'blacklist': [],
        'rating': session_settings['rating'],
        'sfw_mode': session_settings['sfw_mode'],
        'username': '_',
        'birthday': session_settings['birthday'] and session_settings['birthday'].isoformat(),
    }


def create_guest_user(email: str) -> User:
    # Start with a username unlikely to cause collision
    username = f'__{gen_shortcode()}'
    user = User.objects.create(
        guest=True, email=f'{username}@localhost', guest_email=email, username=username
    )
    # Create username in a pattern we can quickly recognize elsewhere in the code even if the user is not yet loaded.
    user.username = f'__{user.id}'
    user.email = f'__{user.id}@localhost'
    user.save()
    return user


class UserClearException(Exception):
    """
    Exception raised in the case a user can't be deleted.
    """


def clear_user(user: User):
    # Clears out as much user data as is practical. Uses normal iterators, despite being slow, to ensure all cleanup
    # hooks are run.
    assert user
    holdup_statuses = [DISPUTED, IN_PROGRESS, QUEUED, REVIEW]
    clearable_statuses = [NEW, PAYMENT_PENDING, WAITING]
    if user.sales.filter(deliverables__status__in=holdup_statuses).exists():
        raise UserClearException(f'{user.username} has outstanding sales to complete or refund. Cannot remove!')
    if user.buys.filter(deliverables__status__in=holdup_statuses).exists():
        raise UserClearException(f'{user.username} has outstanding orders which are unfinished. Cannot remove!')
    if user.is_staff or user.is_superuser:
        raise UserClearException(
            f'{user.username} is an administrative account. It cannot be removed until it is deprivileged.',
        )
    stoppers = [
        account_balance(user, TransactionRecord.HOLDINGS),
        account_balance(user, TransactionRecord.HOLDINGS, PENDING)
    ]
    if any(stoppers):
        raise UserClearException(f'{user.username} has pending transactions! Cannot remove!')
    for sale in Deliverable.objects.filter(status__in=clearable_statuses, order__seller=user):
        cancel_deliverable(sale, user)
    for order in Deliverable.objects.filter(status__in=clearable_statuses, order__buyer=user):
        cancel_deliverable(order, user)

    notes = user.notes
    if notes:
        notes += f'\n\nUsername: {user.username}, Email: {user.email}, removed on {timezone.now()}'
    for account in StripeAccount.objects.filter(user=user):
        try:
            account.delete()
        except Exception as err:
            raise UserClearException(f'Error removing stripe account for {user.username}: {err}') from err
    for bank in user.banks.exclude(deleted=True):
        try:
            destroy_bank_account(bank)
        except Exception as err:
            raise UserClearException(f'Error removing bank account information: {err}') from err
    for card in user.credit_cards.all():
        try:
            card.mark_deleted()
        except Exception as err:
            raise UserClearException(f'Error removing card information: {err}') from err
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
    # These can just be straight up cleared.
    user.notifications.all().delete()
    user.username = f'__deleted{user.id}'
    user.set_password(str(uuid4()))
    user.email = f'{uuid4()}@local'
    user.is_active = False
    user.landscape_enabled = False
    user.subscription_set.all().delete()
    for avatar in Avatar.objects.filter(user=user):
        avatar.avatar.delete()
        avatar.delete()
    user.avatar_url = avatar_url(user)
    user.save()


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


def get_anonymous_user() -> User:
    """
    Grabs the anonymous user from the database and returns it. The anonymous user is created via the
    create_anonymous_user command.
    """
    return User.objects.get(username=settings.ANONYMOUS_USER_USERNAME)
