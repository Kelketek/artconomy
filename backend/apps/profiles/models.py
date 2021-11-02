"""
Models dealing primarily with user preferences and personalization.
"""
import hashlib
import uuid
from urllib.parse import urlencode, urljoin

from avatar.models import Avatar
from dateutil.relativedelta import relativedelta
from django.conf import settings
from custom_user.models import AbstractEmailUser
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import (
    Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField,
    URLField, SET_NULL, ManyToManyField, CASCADE, DecimalField, DateField, PROTECT,
    OneToOneField,
    EmailField, TextField)
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.datetime_safe import date
from django.utils.encoding import force_bytes

from apps.lib.abstract_models import GENERAL, RATINGS, ImageModel, thumbnail_hook, HitsMixin
from apps.lib.models import (
    Comment, Subscription, FAVORITE, SYSTEM_ANNOUNCEMENT, DISPUTE, REFUND, Event,
    SUBMISSION_CHAR_TAG, CHAR_TAG, COMMENT, Tag, SUBMISSION_SHARED, CHAR_SHARED,
    NEW_CHARACTER, RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED, RENEWAL_FIXED, NEW_JOURNAL,
    TRANSFER_FAILED, SUBMISSION_ARTIST_TAG, REFERRAL_LANDSCAPE_CREDIT, REFERRAL_PORTRAIT_CREDIT,
    WATCHING,
    Notification, WAITLIST_UPDATED)
from apps.lib.utils import (
    clear_events, tag_list_cleaner, notify, recall_notification, preview_rating,
    send_transaction_email,
    watch_subscriptions,
    remove_watch_subscriptions, websocket_send, exclude_request
)
from apps.profiles.permissions import (
    SubmissionViewPermission, SubmissionCommentPermission, MessageReadPermission,
    JournalCommentPermission,
    IsRegistered, UserControls)
from apps.sales.apis import PROCESSOR_CHOICES, STRIPE, AUTHORIZE
from shortcuts import make_url, disable_on_load


def banned_named_validator(value):
    if value.lower() in settings.BANNED_USERNAMES:
        raise ValidationError('This name is not permitted', code='invalid')


def banned_prefix_validator(value):
    value = value.strip().lower()
    if value.startswith('__'):
        raise ValidationError('A username may not start with __')
    if value.startswith('guest'):
        raise ValidationError('A username may not start with the word "guest".')


def tg_key_gen():
    return str(uuid.uuid4())[:30]


def set_avatar_url(user):
    avatar = user.avatar_set.order_by("-primary", "-date_uploaded").first()
    if avatar:
        avatar = Avatar.objects.get(id=avatar.id)
        user.avatar_url = avatar.avatar_url(80)
    else:
        params = {'s': '80'}
        path = "%s.jpg?%s" % (hashlib.md5(force_bytes(getattr(user,
                                                              'email'))).hexdigest(), urlencode(params))
        user.avatar_url = urljoin('https://www.gravatar.com/avatar/', path)
    user.save(update_fields=['avatar_url'])


UNSET = 0
IN_SUPPORTED_COUNTRY = 1
NO_SUPPORTED_COUNTRY = 2
BANK_STATUS_CHOICES = (
    (UNSET, "Unset"),
    (IN_SUPPORTED_COUNTRY, "In supported country"),
    (NO_SUPPORTED_COUNTRY, "No supported country")
)

NORMAL = 0
VERIFIED = 1

TRUST_LEVELS = (
    (NORMAL, 'Normal'),
    (VERIFIED, 'Verified'),
)


class User(AbstractEmailUser, HitsMixin):
    """
    User model for Artconomy.
    """
    username = CharField(
        max_length=40, unique=True, db_index=True, validators=[
            UnicodeUsernameValidator(), banned_named_validator, banned_prefix_validator,
        ]
    )
    primary_character = ForeignKey('Character', blank=True, null=True, related_name='+', on_delete=SET_NULL)
    primary_card = ForeignKey('sales.CreditCardToken', null=True, blank=True, related_name='+', on_delete=SET_NULL)
    favorites = ManyToManyField('profiles.Submission', blank=True, related_name='favorites')
    favorites_hidden = BooleanField(default=False)
    taggable = BooleanField(default=True, db_index=True)
    authorize_token = CharField(max_length=50, default='', db_index=True)
    stripe_token = CharField(max_length=50, default='', db_index=True)
    # Whether the user has made a shield purchase.
    bought_shield_on = DateTimeField(null=True, default=None, blank=True, db_index=True)
    sold_shield_on = DateTimeField(null=True, default=None, blank=True, db_index=True)
    watching = ManyToManyField('User', symmetrical=False, related_name='watched_by', blank=True)
    landscape_enabled = BooleanField(default=False, db_index=True)
    landscape_paid_through = DateField(null=True, default=None, blank=True, db_index=True)
    portrait_enabled = BooleanField(default=False, db_index=True)
    portrait_paid_through = DateField(null=True, default=None, blank=True, db_index=True)
    registration_code = ForeignKey('sales.Promo', null=True, blank=True, on_delete=SET_NULL)
    # Whether the user's been offered the mailing list
    offered_mailchimp = BooleanField(default=False)
    birthday = DateField(null=True, default=None, db_index=True)
    guest = BooleanField(default=False, db_index=True)
    referred_by = ForeignKey('User', related_name='referrals', blank=True, on_delete=PROTECT, null=True)
    tg_key = CharField(db_index=True, default=tg_key_gen, max_length=30)
    tg_chat_id = CharField(db_index=True, default='', max_length=30)
    guest_email = EmailField(db_index=True, default='', blank=True)
    avatar_url = URLField(blank=True)
    trust_level = IntegerField(choices=TRUST_LEVELS, default=NORMAL, db_index=True)
    rating = IntegerField(
        choices=RATINGS, db_index=True, default=GENERAL,
        help_text="Shows the maximum rating to display. By setting this to anything other than general, you certify "
                  "that you are of legal age to view adult content in your country."
    )
    sfw_mode = BooleanField(
        default=False,
        help_text="Enable this to only display clean art. "
                  "Useful if temporarily browsing from a location where adult content is not appropriate."
    )
    artist_mode = BooleanField(
        default=False,
        db_index=True,
        blank=True,
        help_text="Enable Artist functionality"
    )
    blacklist = ManyToManyField('lib.Tag', blank=True)
    blacklist__max = 500
    biography = CharField(max_length=5000, blank=True, default='')
    blocking = ManyToManyField('User', symmetrical=False, related_name='blocked_by', blank=True)
    stars = DecimalField(default=None, null=True, blank=True, max_digits=3, decimal_places=2, db_index=True)
    processor_override = CharField(choices=PROCESSOR_CHOICES, blank=True, default='', max_length=24)
    # Used for Stripe payment to upgrade account.
    current_intent = CharField(max_length=30, db_index=True, default='', blank=True)
    rating_count = IntegerField(default=0, blank=True)
    notifications = ManyToManyField('lib.Event', through='lib.Notification')
    # Random default value to make extra sure it will never be invoked by mistake.
    reset_token = CharField(max_length=36, blank=True, default=uuid.uuid4)
    # Auto now add to avoid problems when filtering where 'null' is considered less than something else.
    token_expiry = DateTimeField(auto_now_add=True)
    notes = TextField(default='')
    hit_counter = GenericRelation(
        'hitcount.HitCount', object_id_field='object_pk',
        related_query_name='hit_counter')
    mailchimp_id = models.CharField(max_length=32, db_index=True, default='')
    watch_permissions = {'UserSerializer': [UserControls], 'UserInfoSerializer': [], None: [UserControls]}

    @property
    def landscape(self) -> bool:
        return bool(self.landscape_paid_through and self.landscape_paid_through >= date.today())

    @property
    def portrait(self) -> bool:
        return bool(
            self.landscape
            or (self.portrait_paid_through and self.portrait_paid_through >= date.today())
        )

    @property
    def is_registered(self):
        return not self.guest

    def save(self, *args, **kwargs):
        self.email = self.email and self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def notification_serialize(self, context):
        from .serializers import RelatedUserSerializer
        return RelatedUserSerializer(instance=self, context=context).data

    def watches(self):
        return self.watched_by.all().count()


class ArtconomyAnonymousUser(AnonymousUser):
    @property
    def is_registered(self):
        return False


# Replace Django's internal AnonymousUser model with our own that has the is_registered flag, needed to distinguish
# guests from normal users.
from django.contrib.auth import models as auth_models, user_logged_in, user_logged_out

auth_models.AnonymousUser = ArtconomyAnonymousUser


def trigger_reconnect(request, include_current=False):
    """
    Forces listeners on an IP to reconnect, as long as they aren't the current listener.
    """
    socket_key = request.COOKIES.get('ArtconomySocketKey')
    if not socket_key:
        return
    exclude = exclude_request(request)
    if include_current:
        exclude = None
    websocket_send(
        group=f'client.socket_key.{socket_key}', command='reset', exclude=exclude,
    )


def signal_trigger_reconnect(sender, user, request, **kwargs):
    """
    Trigger reconnect, but for Django signals.
    """
    # Middleware should set this, but doesn't always during tests.
    trigger_reconnect(request)


user_logged_in.connect(signal_trigger_reconnect)
user_logged_out.connect(signal_trigger_reconnect)


# noinspection PyUnusedLocal
@receiver(pre_save, sender=User)
@disable_on_load
def reg_code_action(sender, instance, **_kwargs):
    if instance.id is None and instance.registration_code:
        instance.landscape_paid_through = timezone.now().date() + relativedelta(months=1)
        send_transaction_email('Welcome to Landscape.', 'registration_code.html', instance, {})


def create_user_subscriptions(instance):
    user_type = ContentType.objects.get_for_model(model=instance)
    Subscription.objects.bulk_create(
        [Subscription(subscriber=instance, content_type=None, object_id=None, type=SYSTEM_ANNOUNCEMENT)] +
        [Subscription(
            subscriber=instance,
            content_type=user_type,
            object_id=instance.id,
            type=sub_type,
            email=email,
        ) for sub_type, email in [
            (SUBMISSION_SHARED, False), (CHAR_SHARED, False), (RENEWAL_FAILURE, True),
            (SUBSCRIPTION_DEACTIVATED, True), (RENEWAL_FIXED, True),
            (TRANSFER_FAILED, True), (REFERRAL_LANDSCAPE_CREDIT, True),
            (REFERRAL_PORTRAIT_CREDIT, True),
            (WAITLIST_UPDATED, True),
        ]],
        ignore_conflicts=True,
    )


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
@disable_on_load
def auto_subscribe(sender, instance, created=False, **_kwargs):
    from apps.profiles.tasks import mailchimp_tag
    if created:
        if not instance.guest:
            create_user_subscriptions(instance)
        set_avatar_url(instance)
    if instance.is_staff:
        Subscription.objects.get_or_create(
            subscriber=instance,
            content_type=None,
            object_id=None,
            type=DISPUTE
        )
    if instance.is_superuser:
        subscription, _ = Subscription.objects.get_or_create(
            subscriber=instance,
            content_type=None,
            object_id=None,
            type=REFUND
        )
        subscription.email = True
        subscription.save()

    try:
        artist_profile = instance.artist_profile
    except ArtistProfile.DoesNotExist:
        return
    artist_profile.save()
    mailchimp_tag.delay(instance.id)


@receiver(post_save, sender=User)
@disable_on_load
def stripe_setup(sender, instance, created=False, **kwargs):
    from apps.profiles.tasks import create_or_update_stripe_user
    if not created:
        return
    if not settings.STRIPE_KEY:
        return
    create_or_update_stripe_user.delay(instance.id)


class ArtistProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='artist_profile')
    load = IntegerField(default=0)
    max_load = IntegerField(
        validators=[MinValueValidator(1)], default=10,
        help_text="How much work you're willing to take on at once (for artists)"
    )
    bank_account_status = IntegerField(choices=BANK_STATUS_CHOICES, db_index=True, default=UNSET, blank=True)
    commissions_closed = BooleanField(
        default=False, db_index=True,
        help_text="When enabled, no one may commission you."
    )
    commissions_disabled = BooleanField(
        default=False, db_index=True,
        help_text="Internal check for commissions that prevents taking on more work when max load is exceeded."
    )
    max_rating = IntegerField(
        choices=RATINGS, db_index=True, default=GENERAL,
        help_text="The maximum content rating you are willing to create."
    )
    public_queue = BooleanField(
        default=True,
        help_text='Allow people to see your queue.',
    )
    has_products = BooleanField(default=False, db_index=True)
    escrow_disabled = BooleanField(default=False, db_index=True)
    artist_of_color = BooleanField(default=False, db_index=True)
    lgbt = BooleanField(default=False, db_index=True)
    auto_withdraw = BooleanField(default=True)
    dwolla_url = URLField(blank=True, default='')
    commission_info = CharField(max_length=5000, blank=True, default='')
    watch_permissions = {'ArtistProfileSerializer': []}

    def __str__(self):
        return f'Artist profile for {self.user and self.user.username}'


@receiver(pre_save, sender=ArtistProfile)
def sync_escrow_status(sender, instance, **kwargs):
    from apps.sales.models import StripeAccount
    if instance.bank_account_status == IN_SUPPORTED_COUNTRY:
        instance.escrow_disabled = False
    elif instance.bank_account_status == NO_SUPPORTED_COUNTRY:
        if not StripeAccount.objects.filter(user=instance.user, active=True):
            instance.escrow_disabled = True
        else:
            instance.escrow_disabled = False


class Submission(ImageModel, HitsMixin):
    """
    Uploaded submission
    """
    title = CharField(blank=True, default='', max_length=100)
    caption = CharField(blank=True, default='', max_length=2000)
    private = BooleanField(default=False, help_text="Only show this to people I have explicitly shared it to.")
    characters = ManyToManyField('Character', related_name='submissions', blank=True)
    characters__max = 50
    tags = ManyToManyField('lib.Tag', related_name='submissions', blank=True)
    tags__max = 200
    comments = GenericRelation(
        Comment, related_query_name='order', content_type_field='content_type', object_id_field='object_id'
    )
    comments_disabled = BooleanField(default=False)
    artists = ManyToManyField('User', related_name='art', blank=True)
    artists__max = 10
    deliverable = ForeignKey('sales.Deliverable', null=True, blank=True, on_delete=SET_NULL, related_name='outputs')
    subscriptions = GenericRelation('lib.Subscription')
    # Can't be used as a direct access to the hit counter, no matter what the docs say.
    # Useful for querying and sorting by hitcount, though.
    hit_counter = GenericRelation(
        'hitcount.HitCount', object_id_field='object_pk',
        related_query_name='hit_counter')
    shared_with = ManyToManyField('User', related_name='shared_submissions', blank=True)
    shared_with__max = 150  # Dunbar limit

    comment_view_permissions = [SubmissionViewPermission]
    watch_permissions = {'SubmissionSerializer': [SubmissionViewPermission]}
    comment_permissions = [IsRegistered, SubmissionViewPermission, SubmissionCommentPermission]

    def __str__(self):
        return f'{repr(self.title)} owned by {self.owner and self.owner.username}'

    def can_reference_asset(self, user):
        return user == self.owner

    # noinspection PyUnusedLocal
    def notification_serialize(self, context):
        from .serializers import SubmissionNotificationSerializer
        return SubmissionNotificationSerializer(instance=self).data

    # noinspection PyUnusedLocal
    def notification_name(self, context):
        return self.title

    # noinspection PyUnusedLocal
    def notification_link(self, context):
        return {'name': 'Submission', 'params': {'submissionId': self.id}}

    def favorite_count(self):
        return self.favorites.all().count()


@receiver(post_save, sender=Submission)
@disable_on_load
def auto_subscribe_image(sender, instance, created=False, **_kwargs):
    if created:
        image_type = ContentType.objects.get_for_model(model=sender)
        Subscription.objects.bulk_create(
            [Subscription(
                subscriber=instance.owner,
                content_type=image_type,
                object_id=instance.id,
                type=sub_type,
            ) for sub_type in [FAVORITE, SUBMISSION_CHAR_TAG, SUBMISSION_ARTIST_TAG, COMMENT]],
            ignore_conflicts=True
        )


# noinspection PyUnusedLocal
@receiver(post_delete, sender=Submission)
@disable_on_load
def auto_remove_image_subscriptions(sender, instance, **kwargs):
    Subscription.objects.filter(
        subscriber=instance.owner,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type__in=[
            FAVORITE, SUBMISSION_CHAR_TAG, SUBMISSION_ARTIST_TAG, COMMENT,
        ]
    ).delete()
    Event.objects.filter(
        data__submission=instance.id
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=COMMENT,
    ).delete()


remove_submission_events = receiver(pre_delete, sender=Submission)(clear_events)
submission_thumbnailer = receiver(post_save, sender=Submission)(thumbnail_hook)


class Character(Model, HitsMixin):
    """
    For storing information about Characters for commissioning
    """
    name = CharField(
        max_length=150, validators=[
            RegexValidator(r'^[^/\\?%&+#]+$', message='Names may not contain /, \\, ?, #, or &.'),
            RegexValidator(r'^[^.]', message='Names may not start with a period.'),
            RegexValidator(r'[^.]$', message='Names may not end with a period.'),
        ]
    )
    description = CharField(max_length=20000, blank=True, default='')
    private = BooleanField(
        default=False, help_text="Only show this character to people I have explicitly shared it to."
    )
    open_requests = BooleanField(
        default=False, help_text="Allow others to request commissions with my character, such as for gifts."
    )
    open_requests_restrictions = CharField(
        max_length=2000,
        help_text="Write any particular conditions or requests to be considered when someone else is "
                  "commissioning a piece with this character. "
                  "For example, 'This character should only be drawn in Safe for Work Pieces.'",
        blank=True,
        default=''
    )
    primary_submission = ForeignKey('profiles.Submission', null=True, on_delete=SET_NULL, blank=True)
    taggable = BooleanField(default=True, db_index=True)
    user = ForeignKey('User', related_name='characters', on_delete=CASCADE)
    created_on = DateTimeField(auto_now_add=True)
    tags = ManyToManyField('lib.Tag', related_name='characters', blank=True)
    shared_with = ManyToManyField('User', related_name='shared_characters', blank=True)
    hit_counter = GenericRelation(
        'hitcount.HitCount', object_id_field='object_pk',
        related_query_name='hit_counter')
    tags__max = 100
    colors__max = 10
    shared_with__max = 150  # Dunbar limit

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'user'),)

    def preview_image(self, request):
        if not self.primary_submission:
            return make_url('/static/images/default-avatar.png')
        return preview_rating(
            request, self.primary_submission.rating, self.primary_submission.preview_link,
            sub_link='/static/images/default-avatar.png'
        )

    def notification_serialize(self, context):
        from .serializers import CharacterSerializer
        return CharacterSerializer(instance=self, context=context).data

    def wrap_operation(self, function, always=False, *args, **kwargs):
        do_recall = False
        pk = self.pk
        if self.pk and not always:
            old = Character.objects.get(pk=self.pk)
            if self.private and not old.private:
                do_recall = True
        result = function(*args, **kwargs)
        if do_recall or always:
            recall_notification(NEW_CHARACTER, self.user, {'character': pk}, unique_data=True)
        return result

    def delete(self, *args, **kwargs):
        return self.wrap_operation(super().delete, always=True, *args, **kwargs)

    def save(self, *args, **kwargs):
        return self.wrap_operation(super().save, *args, **kwargs)


Character_shared_with = Character.shared_with.through


class Attribute(Model):
    key = CharField(max_length=50, db_index=True)
    value = CharField(max_length=100, default='')
    sticky = BooleanField(db_index=True, default=False)
    character = ForeignKey(Character, on_delete=CASCADE, related_name='attributes')

    class Meta:
        unique_together = (('key', 'character'),)
        ordering = ['id']

    def update_tag(self):
        old = Attribute.objects.get(id=self.id)
        if old.value == self.value:
            return
        if old.value and (tags := tag_list_cleaner([old.value])):
            tag_name = tags[0]
            tags = self.character.tags.filter(name=tag_name)
            if tags.exists():
                tag = tags[0]
                self.character.tags.remove(*tags)
                tag.self_clean()
        if self.value:
            tag_name = tag_list_cleaner([self.value])
            if tag_name:
                tag_name = tag_name[0]
            else:
                return
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            if not self.character.tags.filter(name=tag.name).exists():
                self.character.tags.add(tag)

    def save(self, *args, **kwargs):
        self.key = self.key.lower()
        if self.id and self.sticky:
            self.update_tag()
        super().save(*args, **kwargs)


# noinspection PyUnusedLocal
@receiver(post_save, sender=Character)
@disable_on_load
def auto_subscribe_character(sender, instance, created=False, **kwargs):
    if created:
        Subscription.objects.create(
            subscriber=instance.user,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=CHAR_TAG
        )


@receiver(post_delete, sender=Character)
@disable_on_load
def auto_remove_character(sender, instance, **kwargs):
    character_type = ContentType.objects.get_for_model(model=sender)
    Subscription.objects.filter(
        subscriber=instance.user,
        content_type=character_type,
        object_id=instance.id,
        type=CHAR_TAG
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type__in=[CHAR_TAG, NEW_CHARACTER],
    ).delete()
    Event.objects.filter(
        type=SUBMISSION_CHAR_TAG,
        data__character=instance.id
    ).delete()


# noinspection PyUnusedLocal
@receiver(post_save, sender=Character)
@disable_on_load
def auto_add_attrs(sender, instance, created=False, **_kwargs):
    if not created:
        return
    Attribute.objects.create(
        key='sex',
        value='',
        sticky=True,
        character=instance
    )
    Attribute.objects.create(
        key='species',
        value='',
        sticky=True,
        character=instance
    )


# noinspection PyUnusedLocal
@receiver(post_save, sender=Character)
@disable_on_load
def auto_notify_watchers(sender, instance, created=False, **kwargs):
    if not created:
        return
    if instance.private:
        return
    notify(NEW_CHARACTER, instance.user, {'character': instance.id}, unique_data=True)


remove_order_events = receiver(pre_delete, sender=Character)(disable_on_load(clear_events))


class RefColor(Model):
    """
    Stores a reference color for a character.
    """
    color = CharField(max_length=7, validators=[RegexValidator(r'^#[0-9a-fA-F]{6}$')])
    note = CharField(max_length=100)
    character = ForeignKey(Character, related_name='colors', on_delete=CASCADE)


class ConversationParticipant(Model):
    """
    Leaf table for tracking read status of messages.
    """
    user = ForeignKey(User, related_name='message_record', on_delete=CASCADE)
    conversation = ForeignKey('profiles.Conversation', related_name='message_record', on_delete=CASCADE)
    read = BooleanField(default=False, db_index=True)


@receiver(post_save, sender=ConversationParticipant)
@disable_on_load
def subscribe_conversation_comments(sender, instance, created=False, **kwargs):
    if not created:
        return
    Subscription.objects.create(
        subscriber=instance.user,
        content_type=ContentType.objects.get_for_model(model=instance.conversation),
        object_id=instance.conversation.id,
        type=COMMENT,
        email=True,
    )


@receiver(pre_delete, sender=ConversationParticipant)
@disable_on_load
def unsubscribe_conversation_comments(sender, instance, **kwargs):
    Subscription.objects.filter(
        subscriber=instance.user,
        content_type=ContentType.objects.get_for_model(model=instance.conversation),
        object_id=instance.conversation.id,
        type=COMMENT,
    ).delete()
    Notification.objects.filter(
        event__content_type=ContentType.objects.get_for_model(model=sender),
        event__object_id=instance.id,
        event__type=COMMENT,
        user=instance.user,
    ).delete()


class Conversation(Model):
    """
    Model for private messages.
    """
    participants = ManyToManyField(
        User, related_name='conversations', through=ConversationParticipant, blank=True
    )
    created_on = DateTimeField(default=timezone.now, db_index=True)
    participants__max = 20
    comments = GenericRelation(
        Comment, related_query_name='message', content_type_field='content_type', object_id_field='object_id'
    )
    last_activity = DateTimeField(default=None, null=True, db_index=True)
    comment_permissions = [IsRegistered, MessageReadPermission]

    def new_comment(self, comment):
        ConversationParticipant.objects.filter(conversation=self).exclude(user=comment.user).update(read=False)
        self.last_activity = comment.created_on
        self.save()

    def comment_deleted(self, comment):
        last_comment = self.comments.filter(deleted=False).order_by('-created_on').first()
        if not last_comment:
            self.last_activity = None
        else:
            self.last_activity = last_comment.created_on
        self.save()

    # noinspection PyUnusedLocal
    def notification_name(self, context):
        participants = self.participants.exclude(
            username=context['request'].user.username,
        ).order_by('username').distinct('username').values_list('username', flat=True)

        count, participants = participants.count(), participants[:3]
        if count > 3:
            additional = count() - 3
            names = f'{participants[0]}, {participants[1]}, {participants[2]} and {additional} others'
        elif count == 3:
            names = f'{participants[0]}, {participants[1]}, and {participants[2]}'
        elif count == 2:
            names = f'{participants[0]} and {participants[1]}'
        elif count == 1:
            names = f'{participants[0]}'
        else:
            names = '(None)'
        return f'conversation with {names}'

    def notification_link(self, context):
        return {
            'name': 'Conversation', 'params': {
                'conversationId': self.id, 'username': context['request'].user.username,
            }
        }

    def notification_serialize(self, context):
        from .serializers import ConversationManagementSerializer
        return ConversationManagementSerializer(instance=self, context=context).data


class Journal(Model):
    """
    Model for private messages.
    """
    user = ForeignKey(User, on_delete=CASCADE, related_name='journals')
    subject = CharField(max_length=150)
    body = CharField(max_length=5000)
    edited = models.BooleanField(default=False)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    edited_on = DateTimeField(auto_now=True)
    comments_disabled = BooleanField(default=False)
    comments = GenericRelation(
        Comment, related_query_name='message', content_type_field='content_type', object_id_field='object_id'
    )
    subscriptions = GenericRelation('lib.Subscription')
    comment_permissions = [IsRegistered, JournalCommentPermission]
    comment_view_permissions = []

    def save(self, **kwargs):
        if self.id:
            old = Journal.objects.get(id=self.id)
            if old.body != self.body:
                self.edited = True
            if old.subject != self.subject:
                self.edited = True
        super().save(**kwargs)

    def notification_serialize(self, context):
        from .serializers import JournalSerializer
        return JournalSerializer(instance=self, context=context).data

    # noinspection PyUnusedLocal
    def notification_display(self, context):
        return {'file': {'notification': self.user.avatar_url}}

    # noinspection PyUnusedLocal
    def notification_name(self, context):
        return "journal with subject: {}".format(self.subject)

    # noinspection PyUnusedLocal
    def notification_link(self, context):
        return {'name': 'Journal', 'params': {'journalId': self.id, 'username': self.user.username}}


# noinspection PyUnusedLocal
@receiver(post_save, sender=Journal)
@disable_on_load
def auto_subscribe_journal(sender, instance, created=False, **kwargs):
    if not created:
        return
    notify(NEW_JOURNAL, instance.user, data={'journal': instance.id})
    Subscription.objects.create(
        type=COMMENT,
        subscriber=instance.user,
        object_id=instance.id,
        content_type=ContentType.objects.get_for_model(Journal)
    )


# noinspection PyUnusedLocal
@receiver(post_delete, sender=Journal)
@disable_on_load
def auto_unsubscribe_journal(sender, instance, **kwargs):
    recall_notification(NEW_JOURNAL, instance.user, data={'journal': instance.id})
    Subscription.objects.filter(
        type=COMMENT,
        object_id=instance.id,
        content_type=ContentType.objects.get_for_model(Journal)
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=COMMENT,
    ).delete()


@disable_on_load
def subscribe_watching(sender, instance, **kwargs):
    action = kwargs.get('action', '')
    for pk in kwargs.get('pk_set', set()):
        user = User.objects.get(pk=pk)
        if action == 'post_add':
            watch_subscriptions(instance, user)
            notify(WATCHING, user, {'user_id': instance.id}, unique_data=True)
        elif action == 'post_remove':
            remove_watch_subscriptions(instance, user)
            recall_notification(WATCHING, user, {'user_id': instance.id}, unique_data=True)


@disable_on_load
def favorite_notification(sender, instance, **kwargs):
    action = kwargs.get('action', '')
    pk_set = kwargs.get('pk_set', None)
    if not pk_set:
        return
    for pk in kwargs.get('pk_set', set()):
        submission = Submission.objects.get(pk=pk)
        if action == 'post_add':
            if instance.favorites_hidden:
                continue
            notify(FAVORITE, submission, {'user_id': instance.id}, unique_data=True)
        elif action == 'post_remove':
            recall_notification(FAVORITE, submission, {'user_id': instance.id}, unique_data=True)

models.signals.m2m_changed.connect(subscribe_watching, User.watching.through)
models.signals.m2m_changed.connect(favorite_notification, User.favorites.through)
