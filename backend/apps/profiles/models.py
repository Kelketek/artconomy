"""
Models dealing primarily with user preferences and personalization.
"""
from django.conf import settings
from custom_user.models import AbstractEmailUser
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db.models import Model, CharField, ForeignKey, IntegerField, BooleanField, ManyToManyField, DateTimeField, \
    URLField, SlugField

from apps.lib.abstract_models import GENERAL, RATINGS, ImageModel
from apps.lib.models import Comment


class User(AbstractEmailUser):
    """
    User model for Artconomy.
    """
    username = CharField(max_length=30, unique=True, db_index=True)
    primary_character = ForeignKey('Character', blank=True, null=True, related_name='+')
    primary_card = ForeignKey('sales.CreditCardToken', null=True, blank=True, related_name='+')
    dwolla_url = URLField(blank=True, default='')
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

    def save(self, *args, **kwargs):
        self.email = self.email and self.email.lower()
        super().save(*args, **kwargs)


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
    primary_asset = ForeignKey('ImageAsset', null=True)
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
