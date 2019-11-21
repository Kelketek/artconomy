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
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField, \
    URLField, SET_NULL, ManyToManyField, CASCADE, DecimalField, DateField, PROTECT
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.datetime_safe import datetime, date
from django.utils.encoding import force_bytes
from rest_framework.authtoken.models import Token

from apps.lib.abstract_models import GENERAL, RATINGS, ImageModel
from apps.lib.models import Comment, Subscription, FAVORITE, SYSTEM_ANNOUNCEMENT, DISPUTE, REFUND, Event, \
    SUBMISSION_CHAR_TAG, CHAR_TAG, COMMENT, Tag, ASSET_SHARED, CHAR_SHARED, \
    NEW_CHARACTER, RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED, RENEWAL_FIXED, NEW_JOURNAL, ORDER_TOKEN_ISSUED, \
    TRANSFER_FAILED, SUBMISSION_ARTIST_TAG, REFERRAL_LANDSCAPE_CREDIT, REFERRAL_PORTRAIT_CREDIT
from apps.lib.utils import (
    clear_events, tag_list_cleaner, notify, recall_notification, preview_rating,
    send_transaction_email
)
from apps.profiles.permissions import AssetViewPermission, AssetCommentPermission, MessageReadPermission, \
    JournalCommentPermission
from shortcuts import make_url


def banned_named_validator(value):
    if value.lower() in settings.BANNED_USERNAMES:
        raise ValidationError('This name is not permitted', code='invalid')


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
    user.save()


class User(AbstractEmailUser):
    """
    User model for Artconomy.
    """
    HAS_US_ACCOUNT = 1
    NO_US_ACCOUNT = 2
    BANK_STATUS_CHOICES = (
        (None, "Unset"),
        (HAS_US_ACCOUNT, "Has US Bank account"),
        (NO_US_ACCOUNT, "No US Bank account")
    )
    username = CharField(
        max_length=30, unique=True, db_index=True, validators=[UnicodeUsernameValidator(), banned_named_validator]
    )
    primary_character = ForeignKey('Character', blank=True, null=True, related_name='+', on_delete=SET_NULL)
    primary_card = ForeignKey('sales.CreditCardToken', null=True, blank=True, related_name='+', on_delete=SET_NULL)
    dwolla_url = URLField(blank=True, default='')
    favorites = ManyToManyField('ImageAsset', blank=True, related_name='favorited_by')
    commissions_closed = BooleanField(
        default=False, db_index=True,
        help_text="When enabled, no one may commission you."
    )
    commissions_disabled = BooleanField(
        default=False, db_index=True,
        help_text="Internal check for commissions that prevents taking on more work when max load is exceeded."
    )
    bank_account_status = IntegerField(null=True, choices=BANK_STATUS_CHOICES, db_index=True, default=None, blank=True)
    favorites_hidden = BooleanField(default=False)
    taggable = BooleanField(default=True, db_index=True)
    artist_tagging_disabled = BooleanField(default=False, db_index=True)
    escrow_disabled = BooleanField(default=False, db_index=True)
    # Whether the suer has made a shield purchase.
    bought_shield_on = DateTimeField(null=True, default=None, blank=True, db_index=True)
    sold_shield_on = DateTimeField(null=True, default=None, blank=True, db_index=True)
    watching = ManyToManyField('User', symmetrical=False, related_name='watched_by', blank=True)
    landscape_enabled = BooleanField(default=False, db_index=True)
    landscape_paid_through = DateField(null=True, default=None, blank=True, db_index=True)
    portrait_enabled = BooleanField(default=False, db_index=True)
    portrait_paid_through = DateField(null=True, default=None, blank=True, db_index=True)
    auto_withdraw = BooleanField(default=True)
    registration_code = ForeignKey('sales.Promo', null=True, blank=True, on_delete=SET_NULL)
    # Whether the user's been offered the mailing list
    offered_mailchimp = BooleanField(default=False)
    referred_by = ForeignKey('User', related_name='referrals', blank=True, on_delete=PROTECT, null=True)
    tg_key = CharField(db_index=True, default=tg_key_gen, max_length=30)
    tg_chat_id = CharField(db_index=True, default='', max_length=30)
    avatar_url = URLField(blank=True)
    max_load = IntegerField(
        validators=[MinValueValidator(1)], default=10,
        help_text="How much work you're willing to take on at once (for artists)"
    )
    rating = IntegerField(
        choices=RATINGS, db_index=True, default=GENERAL,
        help_text="Shows the maximum rating to display. By setting this to anything other than general, you certify "
                  "that you are of legal age to view adult content in your country."
    )
    stars = DecimalField(default=None, null=True, blank=True, max_digits=3, decimal_places=2, db_index=True)
    sfw_mode = BooleanField(
        default=False,
        help_text="Enable this to only display clean art. "
                  "Useful if temporarily browsing from a location where adult content is not appropriate."
    )
    blacklist = ManyToManyField('lib.Tag', blank=True)
    blacklist__max = 500
    biography = CharField(max_length=5000, blank=True, default='')
    blocking = ManyToManyField('User', symmetrical=False, related_name='blocked_by', blank=True)
    notifications = ManyToManyField('lib.Event', through='lib.Notification')
    commission_info = CharField(max_length=5000, blank=True, default='')
    has_products = BooleanField(default=False, db_index=True)
    # Random default value to make extra sure it will never be invoked by mistake.
    reset_token = CharField(max_length=36, blank=True, default=uuid.uuid4)
    # Auto now add to avoid problems when filtering where 'null' is considered less than something else.
    token_expiry = DateTimeField(auto_now_add=True)
    load = IntegerField(default=0)

    @property
    def landscape(self):
        return self.landscape_paid_through and self.landscape_paid_through >= date.today()

    @property
    def portrait(self):
        return (
            self.landscape
            or (self.portrait_paid_through and self.portrait_paid_through >= date.today())
        )

    @property
    def percentage_fee(self):
        if self.landscape:
            return settings.PREMIUM_PERCENTAGE_FEE
        else:
            return settings.STANDARD_PERCENTAGE_FEE

    @property
    def static_fee(self):
        if self.landscape:
            return settings.PREMIUM_STATIC_FEE
        else:
            return settings.STANDARD_STATIC_FEE

    def save(self, *args, **kwargs):
        self.email = self.email and self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def notification_serialize(self, context):
        from .serializers import RelatedUserSerializer
        return RelatedUserSerializer(instance=self, context=context).data


@receiver(pre_save, sender=User)
def reg_code_action(sender, instance, created=False, **_kwargs):
    if instance.id is None and instance.registration_code:
        instance.landscape_paid_through = timezone.now() + relativedelta(months=1)
        send_transaction_email('Welcome to Landscape.', 'registration_code.html', instance, {})


@receiver(post_save, sender=User)
def auto_subscribe(sender, instance, created=False, **_kwargs):
    if created:
        Subscription.objects.create(
            subscriber=instance,
            content_type=None,
            object_id=None,
            type=SYSTEM_ANNOUNCEMENT
        )
        Token.objects.create(user_id=instance.id)
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=ASSET_SHARED
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=CHAR_SHARED
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=RENEWAL_FAILURE,
            email=True,
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=SUBSCRIPTION_DEACTIVATED,
            email=True,
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=RENEWAL_FIXED,
            email=True,
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=ORDER_TOKEN_ISSUED,
            email=True,
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=TRANSFER_FAILED,
            email=True,
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=REFERRAL_LANDSCAPE_CREDIT,
            email=True,
        )
        Subscription.objects.create(
            subscriber=instance,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=REFERRAL_PORTRAIT_CREDIT,
            email=True,
        )
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

    # These are synced right now, mostly for legacy purposes, but we expect them to be separate again
    # once we implement banks for other countries.
    if instance.bank_account_status == User.HAS_US_ACCOUNT:
        instance.escrow_disabled = False
    elif instance.bank_account_status == User.NO_US_ACCOUNT:
        instance.escrow_disabled = True


class ImageAsset(ImageModel):
    """
    Uploaded submission
    """
    title = CharField(blank=True, default='', max_length=100)
    caption = CharField(blank=True, default='', max_length=2000)
    private = BooleanField(default=False, help_text="Only show this to people I have explicitly shared it to.")
    characters = ManyToManyField('Character', related_name='assets', blank=True)
    characters__max = 50
    tags = ManyToManyField('lib.Tag', related_name='assets', blank=True)
    tags__max = 200
    comments = GenericRelation(
        Comment, related_query_name='order', content_type_field='content_type', object_id_field='object_id'
    )
    comments_disabled = BooleanField(default=False)
    artists = ManyToManyField('User', related_name='art', blank=True)
    artists__max = 10
    order = ForeignKey('sales.Order', null=True, blank=True, on_delete=SET_NULL, related_name='outputs')
    subscriptions = GenericRelation('lib.Subscription')
    shared_with = ManyToManyField('User', related_name='shared_assets', blank=True)
    shared_with__max = 150  # Dunbar limit

    comment_permissions = [AssetViewPermission, AssetCommentPermission]

    def notification_serialize(self, context):
        from .serializers import ImageAssetNotificationSerializer
        return ImageAssetNotificationSerializer(instance=self).data

    def notification_name(self, context):
        return self.title

    def notification_link(self, context):
        return {'name': 'Submission', 'params': {'assetID': self.id}}

    def favorite_count(self):
        return self.favorited_by.all().count()


@receiver(post_save, sender=ImageAsset)
def auto_subscribe_image(sender, instance, created=False, **_kwargs):
    if created:
        Subscription.objects.create(
            subscriber=instance.owner,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=FAVORITE
        )
        Subscription.objects.create(
            subscriber=instance.owner,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=SUBMISSION_CHAR_TAG
        )
        Subscription.objects.create(
            subscriber=instance.owner,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=SUBMISSION_ARTIST_TAG
        )
        Subscription.objects.create(
            subscriber=instance.owner,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=COMMENT,
        )


@receiver(post_delete, sender=ImageAsset)
def auto_remove_image_subscriptions(sender, instance, **kwargs):
    Subscription.objects.filter(
        subscriber=instance.owner,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=FAVORITE
    ).delete()
    Subscription.objects.filter(
        subscriber=instance.owner,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=SUBMISSION_CHAR_TAG
    ).delete()
    Subscription.objects.filter(
        subscriber=instance.owner,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=COMMENT
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=FAVORITE,
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=SUBMISSION_CHAR_TAG,
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=COMMENT,
    ).delete()
    Event.objects.filter(
        data__asset=instance.id
    ).delete()


remove_asset_events = receiver(pre_delete, sender=ImageAsset)(clear_events)


class Character(Model):
    """
    For storing information about Characters for commissioning
    """
    name = CharField(
        max_length=150, validators=[
            RegexValidator(r'^[^/\\?%&+#]+$', message='Names may not contain /, \\, ?, #, or &.')
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
    primary_asset = ForeignKey('ImageAsset', null=True, on_delete=SET_NULL)
    taggable = BooleanField(default=True, db_index=True)
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='characters', on_delete=CASCADE)
    created_on = DateTimeField(auto_now_add=True)
    tags = ManyToManyField('lib.Tag', related_name='characters', blank=True)
    shared_with = ManyToManyField('User', related_name='shared_characters', blank=True)
    tags__max = 100
    colors__max = 10
    shared_with__max = 150  # Dunbar limit

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'user'),)

    def preview_image(self, request):
        if not self.primary_asset:
            return make_url('/static/images/default-avatar.png')
        return preview_rating(
            request, self.primary_asset.rating, self.primary_asset.preview_link,
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
        if old.value:
            tag_name = tag_list_cleaner([old.value])[0]
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


@receiver(post_save, sender=Character)
def auto_subscribe_character(sender, instance, created=False, **_kwargs):
    if created:
        Subscription.objects.create(
            subscriber=instance.user,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=CHAR_TAG
        )


@receiver(post_delete, sender=Character)
def auto_remove_character(sender, instance, **kwargs):
    Subscription.objects.filter(
        subscriber=instance.user,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=CHAR_TAG
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=CHAR_TAG,
        recalled=True
    )
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        data__character=instance.id,
        type=SUBMISSION_CHAR_TAG,
        recalled=True
    )
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        data__character=instance.id,
        type=NEW_CHARACTER,
        recalled=True
    )


@receiver(post_save, sender=Character)
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


@receiver(post_save, sender=Character)
def auto_notify_watchers(sender, instance, created=False, **kwargs):
    if not created:
        return
    if instance.private:
        return
    notify(NEW_CHARACTER, instance.user, {'character': instance.id}, unique_data=True)


remove_order_events = receiver(pre_delete, sender=Character)(clear_events)


class RefColor(Model):
    """
    Stores a reference color for a character.
    """
    color = CharField(max_length=7, validators=[RegexValidator(r'^#[0-9a-f]{6}$')])
    note = CharField(max_length=100)
    character = ForeignKey(Character, related_name='colors', on_delete=CASCADE)


class MessageRecipientRelationship(Model):
    """
    Leaf table for tracking read status of messages.
    """
    user = ForeignKey(User, related_name='message_record', on_delete=CASCADE)
    message = ForeignKey('Message', related_name='message_record', on_delete=CASCADE)
    read = BooleanField(default=False, db_index=True)


class Message(Model):
    """
    Model for private messages.
    """
    sender = ForeignKey(User, on_delete=CASCADE, related_name='sent_messages')
    sender_left = BooleanField(default=False, db_index=True)
    recipients = ManyToManyField(
        User, related_name='received_messages', through=MessageRecipientRelationship, blank=True
    )
    subject = CharField(max_length=150)
    body = CharField(max_length=5000)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    last_activity = DateTimeField(auto_now_add=True, db_index=True)
    sender_read = BooleanField(default=True)
    edited_on = DateTimeField(auto_now=True)
    edited = BooleanField(default=False)
    recipients__max = 20
    comments = GenericRelation(
        Comment, related_query_name='message', content_type_field='content_type', object_id_field='object_id'
    )
    comment_permissions = [MessageReadPermission]

    def new_comment(self, comment):
        self.last_activity = datetime.now()
        if comment.user != self.sender:
            self.sender_read = False
            self.save()
        MessageRecipientRelationship.objects.filter(message=self).exclude(user=comment.user).update(read=False)

    def notification_name(self, context):
        return "message with subject: {}".format(self.subject)

    def notification_link(self, context):
        return {'name': 'Message', 'params': {'messageID': self.id, 'username': context['request'].user.username}}

    def notification_serialize(self, context):
        from .serializers import MessageManagementSerializer
        return MessageManagementSerializer(instance=self, context=context).data

    def notification_display(self, context):
        return {'file': {'notification': self.sender.avatar_url}}


class Journal(Model):
    """
    Model for private messages.
    """
    user = ForeignKey(User, on_delete=CASCADE, related_name='journals')
    subject = CharField(max_length=150)
    body = CharField(max_length=5000)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    edited_on = DateTimeField(auto_now=True)
    comments_disabled = BooleanField(default=False)
    comments = GenericRelation(
        Comment, related_query_name='message', content_type_field='content_type', object_id_field='object_id'
    )
    subscriptions = GenericRelation('lib.Subscription')
    comment_permissions = [JournalCommentPermission]

    def notification_serialize(self, context):
        from .serializers import JournalSerializer
        return JournalSerializer(instance=self, context=context).data

    def notification_display(self, context):
        return {'file': {'notification': self.user.avatar_url}}

    def notification_name(self, context):
        return "journal with subject: {}".format(self.subject)

    def notification_link(self, context):
        return {'name': 'Journal', 'params': {'journalID': self.id, 'username': self.user.username}}


@receiver(post_save, sender=Journal)
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


@receiver(post_delete, sender=Journal)
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