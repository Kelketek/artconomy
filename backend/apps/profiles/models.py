"""
Models dealing primarily with user preferences and personalization.
"""
from django.conf import settings
from custom_user.models import AbstractEmailUser
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.core.validators import MinValueValidator
from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, ManyToManyField, DateTimeField, \
    URLField, SlugField, SET_NULL
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.lib.abstract_models import GENERAL, RATINGS, ImageModel
from apps.lib.models import Comment, Subscription, FAVORITE, SYSTEM_ANNOUNCEMENT, DISPUTE
from apps.profiles.permissions import AssetViewPermission, AssetCommentPermission


class User(AbstractEmailUser):
    """
    User model for Artconomy.
    """
    username = CharField(max_length=30, unique=True, db_index=True)
    primary_character = ForeignKey('Character', blank=True, null=True, related_name='+')
    primary_card = ForeignKey('sales.CreditCardToken', null=True, blank=True, related_name='+')
    dwolla_url = URLField(blank=True, default='')
    favorites = ManyToManyField('ImageAsset', blank=True, related_name='favorited_by')
    commissions_closed = BooleanField(
        default=True, db_index=True,
        help_text="When enabled, no one may commission you."
    )
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
    notifications = ManyToManyField('lib.Event', through='lib.Notification')

    @property
    def fee(self):
        return .1

    def save(self, *args, **kwargs):
        self.email = self.email and self.email.lower()
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def auto_subscribe(sender, instance, created=False, **_kwargs):
    if created:
        Subscription.objects.create(
            subscriber=instance,
            content_type=None,
            object_id=None,
            type=SYSTEM_ANNOUNCEMENT
        )
    if instance.is_staff:
        Subscription.objects.get_or_create(
            subscriber=instance,
            content_type=None,
            object_id=None,
            type=DISPUTE
        )


class ImageAsset(ImageModel):
    """
    Uploaded image for either commission deliveries or
    """
    title = CharField(blank=True, default='', max_length=100)
    caption = CharField(blank=True, default='', max_length=2000)
    private = BooleanField(default=False, help_text="Only show this to people I have explicitly shared it to.")
    characters = ManyToManyField('Character', related_name='assets')
    tags = ManyToManyField('Tag', related_name='assets')
    comments = GenericRelation(
        Comment, related_query_name='order', content_type_field='content_type', object_id_field='object_id'
    )
    comments_disabled = BooleanField(default=False)
    artist = ForeignKey('User', related_name='art', null=True, blank=True)
    order = ForeignKey('sales.Order', null=True, blank=True, on_delete=SET_NULL, related_name='outputs')

    comment_permissions = [AssetViewPermission, AssetCommentPermission]

    def favorite_count(self):
        return self.favorited_by.all().count()


@receiver(post_save, sender=ImageAsset)
def auto_subscribe_image(sender, instance, created=False, **_kwargs):
    if created:
        Subscription.objects.create(
            subscriber=instance.uploaded_by,
            content_type=ContentType.objects.get_for_model(model=sender),
            object_id=instance.id,
            type=FAVORITE
        )


@receiver(post_delete, sender=ImageAsset)
def auto_remove(sender, instance, **kwargs):
    Subscription.objects.filter(
        subscriber=instance.uploaded_by,
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=FAVORITE
    ).delete()


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
        default=True, help_text="Allow others to request commissions with my character, such as for gifts."
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
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='characters')
    created_on = DateTimeField(auto_now_add=True)
    species = CharField(max_length=150, blank=True, default='')
    gender = CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'user'),)


class RefColor(Model):
    """
    Stores a reference color for a character.
    """
    name = CharField(max_length=50)
    color = CharField(max_length=6)
    note = CharField(max_length=100)
    character = ForeignKey(Character)


class Category(Model):
    name = CharField(max_length=50)
    rating = IntegerField(choices=RATINGS)
    description = CharField(max_length=250, default='')


class Tag(Model):
    name = SlugField(db_index=True)
    category = ForeignKey(Category, null=True, blank=True)
    description = CharField(max_length=250, default='')
