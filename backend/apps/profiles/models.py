"""
Models dealing primarily with user preferences and personalization.
"""
from django.conf import settings
from custom_user.models import AbstractEmailUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, DateTimeField, \
    URLField, SET_NULL, ManyToManyField, CASCADE
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from apps.lib.abstract_models import GENERAL, RATINGS, ImageModel
from apps.lib.models import Comment, Subscription, FAVORITE, SYSTEM_ANNOUNCEMENT, DISPUTE, REFUND, Event, \
    SUBMISSION_CHAR_TAG, CHAR_TAG, SUBMISSION_TAG, COMMENT, Tag, CHAR_TRANSFER
from apps.lib.utils import clear_events, tag_list_cleaner
from apps.profiles.permissions import AssetViewPermission, AssetCommentPermission


def banned_named_validator(value):
    if value.lower() in settings.BANNED_USERNAMES:
        raise ValidationError('This name is not permitted', code='invalid')


class User(AbstractEmailUser):
    """
    User model for Artconomy.
    """
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
    favorites_hidden = BooleanField(default=False)
    taggable = BooleanField(default=True, db_index=True)
    artist_tagging_disabled = BooleanField(default=False, db_index=True)
    use_load_tracker = BooleanField(
        default=True,
        help_text="Whether to use load tracking to automatically open or close commissions."
    )
    max_load = IntegerField(
        validators=[MinValueValidator(1)], default=10,
        help_text="How much work you're willing to take on at once (for artists)"
    )
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
    blacklist = ManyToManyField('lib.Tag', blank=True)
    blacklist__max = 500
    biography = CharField(max_length=5000, blank=True, default='')
    notifications = ManyToManyField('lib.Event', through='lib.Notification')
    load = IntegerField(default=0)

    @property
    def fee(self):
        return .1

    def save(self, *args, **kwargs):
        self.email = self.email and self.email.lower()
        super().save(*args, **kwargs)

    def notification_serialize(self, context):
        from .serializers import RelatedUserSerializer
        return RelatedUserSerializer(instance=self).data


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
    if instance.is_staff:
        Subscription.objects.get_or_create(
            subscriber=instance,
            content_type=None,
            object_id=None,
            type=DISPUTE
        )
    if instance.is_superuser:
        Subscription.objects.get_or_create(
            subscriber=instance,
            content_type=None,
            object_id=None,
            type=REFUND
        )


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
            type=SUBMISSION_TAG
        )
        Subscription.objects.create(
            subscriber=instance.owner,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=COMMENT,
        )


@receiver(post_delete, sender=ImageAsset)
def auto_remove(sender, instance, **kwargs):
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


remove_asset_events = receiver(pre_delete, sender=ImageAsset)(clear_events)


class Character(Model):
    """
    For storing information about Characters for commissioning
    """
    name = CharField(max_length=150)
    description = CharField(max_length=5000, blank=True, default='')
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
    transfer = ForeignKey('sales.CharacterTransfer', on_delete=SET_NULL, null=True, blank=True, related_name='+')
    tags = ManyToManyField('lib.Tag', related_name='characters', blank=True)
    tags__max = 100
    colors__max = 10

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'user'),)

    def notification_serialize(self, context):
        from .serializers import CharacterSerializer
        return CharacterSerializer(instance=self).data


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
                self.character.tags.remove(*tags)
                tag = tags[0]
                tag.self_clean()
        if self.value:
            tag_name = tag_list_cleaner([self.value])[0]
            tag, _ = Tag.objects.get_or_create(name=tag_name)
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


@receiver(pre_delete, sender=Character)
def auto_recall_character(sender, instance, **kwargs):
    from apps.sales.models import CharacterTransfer
    for transfer in CharacterTransfer.objects.filter(character=instance):
        Event.objects.filter(
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=CHAR_TRANSFER,
            recalled=True
        )
        if transfer.status == CharacterTransfer.NEW:
            transfer.status = CharacterTransfer.CANCELLED
            transfer.save()


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


@receiver(post_save, sender=Character)
def auto_add_attrs(sender, instance, created=False, **_kwargs):
    if created:
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


remove_order_events = receiver(pre_delete, sender=Character)(clear_events)


class RefColor(Model):
    """
    Stores a reference color for a character.
    """
    color = CharField(max_length=7, validators=[RegexValidator(r'^#[0-9a-f]{6}$')])
    note = CharField(max_length=100)
    character = ForeignKey(Character, related_name='colors', on_delete=CASCADE)
