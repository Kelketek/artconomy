"""
Models dealing primarily with user preferences and personalization.
"""

import hashlib
import uuid
from urllib.parse import urlencode, urljoin
from django.contrib.auth import models as auth_models
from django.contrib.auth import user_logged_in, user_logged_out
from apps.lib.abstract_models import (
    GENERAL,
    RATINGS,
    HitsMixin,
    ImageModel,
    get_next_increment,
    thumbnail_hook,
)
from apps.lib.models import (
    Comment,
    EmailPreference,
    Event,
    Notification,
    Subscription,
    Tag,
)
from apps.lib.constants import (
    NEW_CHARACTER,
    WATCHING,
    CHAR_TAG,
    COMMENT,
    COMMISSIONS_OPEN,
    SYSTEM_ANNOUNCEMENT,
    FAVORITE,
    DISPUTE,
    REFUND,
    SUBMISSION_CHAR_TAG,
    ORDER_UPDATE,
    SALE_UPDATE,
    SUBMISSION_ARTIST_TAG,
    REVISION_UPLOADED,
    SUBMISSION_SHARED,
    CHAR_SHARED,
    RENEWAL_FAILURE,
    SUBSCRIPTION_DEACTIVATED,
    RENEWAL_FIXED,
    NEW_JOURNAL,
    TRANSFER_FAILED,
    REFERRAL_LANDSCAPE_CREDIT,
    REFERENCE_UPLOADED,
    WAITLIST_UPDATED,
    AUTO_CLOSED,
    REVISION_APPROVED,
    FLAG_REASONS,
    SUBMISSION_KILLED,
    PRODUCT_KILLED,
)
from apps.lib.permissions import Or, StaffPower
from apps.lib.utils import (
    clear_events,
    clear_events_subscriptions_and_comments,
    exclude_request,
    notify,
    preview_rating,
    recall_notification,
    remove_watch_subscriptions,
    send_transaction_email,
    tag_list_cleaner,
    watch_subscriptions,
    websocket_send,
    post_commit_defer,
)
from apps.profiles.constants import POWER_LIST
from apps.profiles.permissions import (
    IsRegistered,
    JournalCommentPermission,
    MessageReadPermission,
    SubmissionCommentPermission,
    SubmissionViewPermission,
    staff_power,
    ObjectControls,
    IsSuperuser,
    SocialsVisible,
)
from apps.sales.constants import PROCESSOR_CHOICES
from avatar.models import Avatar
from custom_user.models import AbstractEmailUser
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator, URLValidator
from django.db import ProgrammingError, models
from django.db.models import (
    CASCADE,
    PROTECT,
    SET_NULL,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    FloatField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    Model,
    OneToOneField,
    TextField,
    URLField,
)
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.encoding import force_bytes
from short_stuff import gen_shortcode
from short_stuff.django.models import ShortCodeField
from shortcuts import disable_on_load, make_url


def banned_named_validator(value):
    if value.lower() in settings.BANNED_USERNAMES:
        raise ValidationError("This name is not permitted", code="invalid")


def banned_prefix_validator(value):
    value = value.strip().lower()
    if value.startswith("__"):
        raise ValidationError("A username may not start with __")
    if value.startswith("guest"):
        raise ValidationError('A username may not start with the word "guest".')
    if value.startswith("@"):
        raise ValidationError("A username may not start with the symbol @.")


def tg_key_gen():
    return str(uuid.uuid4())[:30]


def set_avatar_url(user):
    avatar = user.avatar_set.order_by("-primary", "-date_uploaded").first()
    if avatar:
        avatar = Avatar.objects.get(id=avatar.id)
        user.avatar_url = avatar.avatar_url(80)
    else:
        params = {"s": "80"}
        path = "%s.jpg?%s" % (
            hashlib.md5(force_bytes(getattr(user, "email"))).hexdigest(),
            urlencode(params),
        )
        user.avatar_url = urljoin("https://www.gravatar.com/avatar/", path)
    user.save(update_fields=["avatar_url"])


def default_plan():
    from apps.sales.models import ServicePlan

    try:
        return ServicePlan.objects.filter(
            name=settings.DEFAULT_SERVICE_PLAN_NAME
        ).first()
    except ProgrammingError:
        # During initialization, as Django is checking for common issues, it
        # instantiates a copy of the User model to verify that certain attributes are
        # defined correctly. Of course, instantiating before migrations have been run
        # means that the tables for ServicePlan have not yet been created, so we have to
        # catch the resulting exception in order to move forward.
        return None


UNSET = 0
IN_SUPPORTED_COUNTRY = 1
NO_SUPPORTED_COUNTRY = 2
BANK_STATUS_CHOICES = (
    (UNSET, "Unset"),
    (IN_SUPPORTED_COUNTRY, "In supported country"),
    (NO_SUPPORTED_COUNTRY, "No supported country"),
)


class User(AbstractEmailUser, HitsMixin):
    """
    User model for Artconomy.
    """

    class Meta:
        ordering = ("-date_joined",)

    username = CharField(
        max_length=40,
        unique=True,
        db_index=True,
        validators=[
            UnicodeUsernameValidator(),
            banned_named_validator,
            banned_prefix_validator,
        ],
        db_collation="case_insensitive",
    )
    primary_character = ForeignKey(
        "Character", blank=True, null=True, related_name="+", on_delete=SET_NULL
    )
    primary_card = ForeignKey(
        "sales.CreditCardToken",
        null=True,
        blank=True,
        related_name="+",
        on_delete=SET_NULL,
    )
    favorites = ManyToManyField(
        "profiles.Submission",
        blank=True,
        related_name="favorites",
        through="profiles.Favorite",
    )
    favorites_hidden = BooleanField(default=False)
    taggable = BooleanField(default=True, db_index=True)
    # Used for states that require hard ID-based verification for access to adult
    # content. Ignored otherwise. See the THEOCRACIES setting.
    verified_adult = BooleanField(default=False, db_index=True)
    authorize_token = CharField(max_length=50, default="", db_index=True)
    stripe_token = CharField(max_length=50, default="", db_index=True)
    # Whether the user has made a shield purchase.
    bought_shield_on = DateTimeField(null=True, default=None, blank=True, db_index=True)
    sold_shield_on = DateTimeField(null=True, default=None, blank=True, db_index=True)
    watching = ManyToManyField(
        "User", symmetrical=False, related_name="watched_by", blank=True
    )
    # Used for the users where we have received bounce notifications for their email
    # address. Prevents us from sending email to them.
    email_nulled = BooleanField(
        default=False,
        db_index=True,
        help_text="Drop all emails that would otherwise be sent to this user. Will "
        "reset to off if the email address is updated by the user.",
    )
    next_service_plan = ForeignKey(
        "sales.ServicePlan",
        related_name="future_users",
        null=True,
        blank=True,
        on_delete=SET_NULL,
    )
    service_plan = ForeignKey(
        "sales.ServicePlan",
        related_name="current_users",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        default=default_plan,
    )
    service_plan_paid_through = DateField(null=True, default=None, blank=True)
    registration_code = ForeignKey(
        "sales.Promo", null=True, blank=True, on_delete=SET_NULL
    )
    birthday = DateField(null=True, default=None, db_index=True)
    guest = BooleanField(default=False, db_index=True)
    referred_by = ForeignKey(
        "User", related_name="referrals", blank=True, on_delete=PROTECT, null=True
    )
    tg_key = CharField(db_index=True, default=tg_key_gen, max_length=30)
    tg_chat_id = CharField(db_index=True, default="", max_length=30)
    discord_id = CharField(db_index=True, default="", max_length=30, blank=True)
    guest_email = EmailField(db_index=True, default="", blank=True)
    avatar_url = URLField(blank=True)
    rating = IntegerField(
        choices=RATINGS,
        db_index=True,
        default=GENERAL,
        help_text="Shows the maximum rating to display. By setting this to anything "
        "other than general, you certify that you are of legal age to view "
        "adult content in your country.",
    )
    sfw_mode = BooleanField(
        default=False,
        help_text="Enable this to only display clean art. Useful if temporarily "
        "browsing from a location where adult content is not appropriate.",
    )
    artist_mode = BooleanField(
        default=False,
        db_index=True,
        blank=True,
        help_text="Enable Artist functionality",
    )
    delinquent = BooleanField(
        default=False,
        db_index=True,
        help_text="Enabled when a user's account is in arrears beyond the grace "
        "period.",
    )
    featured = BooleanField(
        default=False,
        db_index=True,
        help_text="Enabling features all of a user's products and puts them in the "
        "featured users listing. This is mostly managed by a scheduled task, "
        "but it can be manually triggered here, too.",
    )
    blacklist = ManyToManyField(
        "lib.Tag", blank=True, related_name="blacklisting_users"
    )
    blacklist__max = 500
    nsfw_blacklist = ManyToManyField("lib.Tag", related_name="nsfw_blacklisting_users")
    nsfw_blacklist__max = 500
    biography = CharField(max_length=5000, blank=True, default="")
    blocking = ManyToManyField(
        "User", symmetrical=False, related_name="blocked_by", blank=True
    )
    stars = DecimalField(
        default=None,
        null=True,
        blank=True,
        max_digits=3,
        decimal_places=2,
        db_index=True,
    )
    processor_override = CharField(
        choices=PROCESSOR_CHOICES, blank=True, default="", max_length=24
    )
    # Used for Stripe payment to upgrade account.
    current_intent = CharField(max_length=30, db_index=True, default="", blank=True)
    rating_count = IntegerField(default=0, blank=True)
    notifications = ManyToManyField("lib.Event", through="lib.Notification")
    # Random default value to make extra sure it will never be invoked by mistake.
    reset_token = CharField(max_length=36, blank=True, default=uuid.uuid4)
    # Currently only used to make sure sellers can't change the email on an order which
    # a buyer has logged into via email link.
    verified_email = BooleanField(default=False, db_index=True)
    # Auto now add to avoid problems when filtering where 'null' is considered less than
    # something else.
    token_expiry = DateTimeField(auto_now_add=True)
    notes = TextField(default="", blank=True)
    hit_counter = GenericRelation(
        "hitcount.HitCount",
        object_id_field="object_pk",
        related_query_name="hit_counter",
    )
    drip_id = models.CharField(max_length=32, db_index=True, default="")
    watch_permissions = {
        "UserSerializer": [Or(ObjectControls, StaffPower("administrate_users"))],
        "UserInfoSerializer": [],
        "UnreadNotificationsSerializer": [
            IsRegistered,
            Or(ObjectControls, StaffPower("view_as")),
        ],
        None: [Or(ObjectControls, StaffPower("administrate_users"))],
    }

    @property
    def landscape(self) -> bool:
        return bool(
            self.service_plan
            and self.service_plan.name == "Landscape"
            and self.service_plan_paid_through
            and self.service_plan_paid_through >= timezone.now().date()
        )

    @property
    def landscape_paid_through(self):
        if not (self.service_plan and self.service_plan.name == "Landscape"):
            return None
        return self.service_plan_paid_through

    @property
    def landscape_enabled(self):
        return bool(
            self.next_service_plan and self.next_service_plan.name == "Landscape"
        )

    @landscape_enabled.setter
    def landscape_enabled(self, value: bool):
        from apps.sales.models import ServicePlan

        if value:
            self.next_service_plan = ServicePlan.objects.get(name="Landscape")
        else:
            self.next_service_plan = ServicePlan.objects.get(
                name=settings.DEFAULT_SERVICE_PLAN_NAME, hidden=False
            )

    @property
    def is_registered(self):
        return not self.guest

    def save(self, *args, **kwargs):
        self.email = self.email and self.email.lower()
        self.next_service_plan = self.next_service_plan or self.service_plan
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    @property
    def escrow_available(self):
        try:
            return self.artist_profile.bank_account_status == IN_SUPPORTED_COUNTRY
        except ArtistProfile.DoesNotExist:
            return False

    def notification_serialize(self, context):
        from .serializers import RelatedUserSerializer

        data = RelatedUserSerializer(instance=self, context=context).data
        # Shim this file data in here so that it behaves like any other displayable
        # 'asset' on the notifications list.
        extra = {
            "rating": GENERAL,
            "preview": None,
            "file": {"full": data["avatar_url"], "notification": data["avatar_url"]},
            "__type__": "data:image",
        }
        data.update(extra)
        return data

    def watches(self):
        return self.watched_by.all().count()


class ArtconomyAnonymousUser(AnonymousUser):
    @property
    def is_registered(self):
        return False


# Replace Django's internal AnonymousUser model with our own that has the is_registered
# flag, needed to distinguish guests from normal users.
auth_models.AnonymousUser = ArtconomyAnonymousUser


def trigger_reconnect(request, include_current=False):
    """
    Forces listeners on an IP to reconnect, as long as they aren't the current listener.
    """
    socket_key = request.COOKIES.get("ArtconomySocketKey")
    if not socket_key:
        return
    exclude = exclude_request(request)
    if include_current:
        exclude = None
    websocket_send(
        group=f"client.socket_key.{socket_key}",
        command="reset",
        exclude=exclude,
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
    from apps.sales.models import ServicePlan

    if instance.service_plan is None and instance.id is None:
        if instance.registration_code:
            instance.service_plan = ServicePlan.objects.get(name="Landscape")
            instance.service_plan_paid_through = timezone.now().date() + relativedelta(
                months=1
            )
            send_transaction_email(
                "Welcome to Landscape.", "registration_code.html", instance, {}
            )
        else:
            instance.service_plan = ServicePlan.objects.get(
                name=settings.DEFAULT_SERVICE_PLAN_NAME
            )
            instance.service_plan_paid_through = timezone.now().date()


def create_user_subscriptions(instance):
    user_type = ContentType.objects.get_for_model(model=instance)
    Subscription.objects.bulk_create(
        [
            Subscription(
                subscriber=instance,
                content_type=None,
                object_id=None,
                type=SYSTEM_ANNOUNCEMENT,
            )
        ]
        + [
            Subscription(
                subscriber=instance,
                content_type=user_type,
                object_id=instance.id,
                type=sub_type,
                email=email,
            )
            for sub_type, email in [
                (SUBMISSION_SHARED, False),
                (CHAR_SHARED, False),
                (RENEWAL_FAILURE, True),
                (SUBSCRIPTION_DEACTIVATED, True),
                (RENEWAL_FIXED, True),
                (TRANSFER_FAILED, True),
                (REFERRAL_LANDSCAPE_CREDIT, True),
                (WAITLIST_UPDATED, True),
                (AUTO_CLOSED, True),
            ]
        ],
        ignore_conflicts=True,
    )


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
@disable_on_load
def auto_subscribe(sender, instance, created=False, **_kwargs):
    if created:
        if not instance.guest:
            create_user_subscriptions(instance)
        create_email_preferences(instance)
        set_avatar_url(instance)
    if instance.is_staff:
        StaffPowers.objects.get_or_create(user=instance)
    if instance.is_superuser:
        subscription, _ = Subscription.objects.get_or_create(
            subscriber=instance, content_type=None, object_id=None, type=REFUND
        )
        subscription.email = True
        subscription.save()

    try:
        artist_profile = instance.artist_profile
    except ArtistProfile.DoesNotExist:
        return
    artist_profile.save()


@receiver(post_save, sender=User)
@disable_on_load
@post_commit_defer
def mail_tag_tasks(sender, instance, **_kwargs):
    from apps.profiles.tasks import drip_tag

    drip_tag.delay(instance.id)


@receiver(post_save, sender=User)
@disable_on_load
@post_commit_defer
def stripe_setup(sender, instance, created=False, **kwargs):
    from apps.profiles.tasks import create_or_update_stripe_user

    if not created:
        return
    if not settings.STRIPE_KEY:
        return
    create_or_update_stripe_user.apply_async((instance.id,))


class ArtistProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name="artist_profile")
    load = IntegerField(default=0)
    max_load = IntegerField(
        validators=[MinValueValidator(1)],
        default=10,
        help_text="How much work you're willing to take on at once (for artists)",
    )
    bank_account_status = IntegerField(
        choices=BANK_STATUS_CHOICES, db_index=True, default=UNSET, blank=True
    )
    commissions_closed = BooleanField(
        default=False,
        db_index=True,
        help_text="When enabled, no one may commission you.",
    )
    commissions_disabled = BooleanField(
        default=False,
        db_index=True,
        help_text="Internal check for commissions that prevents taking on more work "
        "when max load is exceeded.",
    )
    public_queue = BooleanField(
        default=True,
        help_text="Allow people to see your queue.",
    )
    has_products = BooleanField(default=False, db_index=True)
    escrow_enabled = BooleanField(default=True, db_index=True)
    artist_of_color = BooleanField(default=False, db_index=True)
    lgbt = BooleanField(default=False, db_index=True)
    auto_withdraw = BooleanField(default=True)
    dwolla_url = URLField(blank=True, default="")
    commission_info = CharField(max_length=14000, blank=True, default="")
    watch_permissions = {
        "ArtistProfileSerializer": [],
        "SalesStatsSerializer": [
            Or(StaffPower("view_financials"), StaffPower("view_as"), ObjectControls)
        ],
    }

    def __str__(self):
        return f"Artist profile for {self.user and self.user.username}"


class SocialSettings(Model):
    """
    Settings for social media.
    """

    watch_permissions = {
        "SocialSettingsSerializer": [
            Or(ObjectControls, StaffPower("view_social_data"), SocialsVisible)
        ],
    }
    user = OneToOneField(User, on_delete=CASCADE, related_name="social_settings")
    allow_promotion = BooleanField(
        default=False,
        db_index=True,
        help_text="Whether we may promote you and your content in particular on social "
        "media. We will link/ping your account on the relevant service when we do this.",
    )
    allow_site_promotion = BooleanField(
        default=False,
        db_index=True,
        help_text="Whether we may use assets you upload to promote the site in a general "
        "sense-- such as using screenshots with your content",
    )
    nsfw_promotion = BooleanField(
        default=False,
        db_index=True,
        help_text="Whether we may promote your NSFW content on social media which "
        "allows such content, if applicable.",
    )
    quick_description = CharField(
        max_length=150,
        help_text="A quick description of your art/style/offerings, for use by our social media specialist when promoting you.",
        default="",
        blank=True,
    )
    promotion_notes = TextField(
        max_length=500,
        help_text="Any notes/requests/conditions on using your content in promotions.",
        blank=True,
    )
    display_socials = BooleanField(
        default=True,
        db_index=True,
        help_text="Whether to display your socials on your profile.",
    )

    class Meta:
        ordering = ("-id",)


class SocialLink(Model):
    watch_permissions = {
        "SocialLinkSerializer": [
            Or(ObjectControls, StaffPower("view_social_data"), SocialsVisible)
        ]
    }
    user = ForeignKey(User, on_delete=CASCADE, related_name="social_links")
    site_name = CharField(
        max_length=25,
        db_index=True,
        blank=False,
        help_text="The name of the site your account is on.",
    )
    identifier = CharField(
        max_length=100, default="", blank=True, help_text="Username on this site."
    )
    url = URLField(
        help_text="URL of account on site.",
        validators=[URLValidator(schemes=("https",))],
    )
    comment = CharField(
        max_length=30,
        help_text="Short comment, such as 'Cat Photo Account'.",
        default="",
        blank=True,
    )

    class Meta:
        ordering = ("id",)


@receiver(pre_save, sender=ArtistProfile)
def sync_escrow_status(sender, instance, **kwargs):
    from apps.sales.models import StripeAccount

    if instance.bank_account_status == IN_SUPPORTED_COUNTRY:
        instance.escrow_enabled = True
    elif instance.bank_account_status == NO_SUPPORTED_COUNTRY:
        instance.escrow_enabled = StripeAccount.objects.filter(
            user=instance.user, active=True
        ).exists()


@receiver(post_save, sender=ArtistProfile)
def auto_withdraw(sender, instance, created=False, **kwargs):
    from apps.sales.tasks import withdraw_all

    withdraw_all.delay(instance.user.id)


def get_next_submission_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(Submission, "display_position")


class Submission(ImageModel, HitsMixin):
    """
    Uploaded submission
    """

    title = CharField(blank=True, default="", max_length=100)
    caption = CharField(blank=True, default="", max_length=2000)
    private = BooleanField(
        default=False,
        help_text="Only show this to people I have explicitly shared it to.",
    )
    characters = ManyToManyField(
        "Character", related_name="submissions", blank=True, through="CharacterTag"
    )
    characters__max = 50
    tags = ManyToManyField("lib.Tag", related_name="submissions", blank=True)
    tags__max = 200
    comments = GenericRelation(
        Comment,
        related_query_name="order",
        content_type_field="content_type",
        object_id_field="object_id",
    )
    comments_disabled = BooleanField(default=False)
    artists = ManyToManyField(
        "User", related_name="art", blank=True, through="ArtistTag"
    )
    artists__max = 10
    removed_on = DateTimeField(null=True, db_index=True, blank=True)
    removed_reason = IntegerField(
        choices=FLAG_REASONS, db_index=True, null=True, blank=True
    )
    removed_by = ForeignKey(
        "profiles.User",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="submission_removals",
    )
    deliverable = ForeignKey(
        "sales.Deliverable",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="outputs",
    )
    revision = ForeignKey(
        "sales.Revision",
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="submissions",
    )
    subscriptions = GenericRelation("lib.Subscription")
    # Can't be used as a direct access to the hit counter, no matter what the docs say.
    # Useful for querying and sorting by hitcount, though.
    hit_counter = GenericRelation(
        "hitcount.HitCount",
        object_id_field="object_pk",
        related_query_name="hit_counter",
    )
    shared_with = ManyToManyField("User", related_name="shared_submissions", blank=True)
    shared_with__max = 150  # Dunbar limit
    display_position = FloatField(
        db_index=True, default=get_next_submission_position, unique=True
    )

    comment_view_permissions = [SubmissionViewPermission]
    watch_permissions = {"SubmissionSerializer": [SubmissionViewPermission]}
    comment_permissions = [
        IsRegistered,
        SubmissionViewPermission,
        SubmissionCommentPermission,
    ]

    def __str__(self):
        return f"{repr(self.title)} owned by {self.owner and self.owner.username}"

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
        return {"name": "Submission", "params": {"submissionId": self.id}}

    def favorite_count(self):
        return self.favorites.all().count()


@receiver(post_save, sender=Submission)
@disable_on_load
def auto_subscribe_image(sender, instance, created=False, **_kwargs):
    if created:
        image_type = ContentType.objects.get_for_model(model=sender)
        Subscription.objects.bulk_create(
            [
                Subscription(
                    subscriber=instance.owner,
                    content_type=image_type,
                    object_id=instance.id,
                    type=sub_type,
                )
                for sub_type in [
                    FAVORITE,
                    SUBMISSION_CHAR_TAG,
                    SUBMISSION_ARTIST_TAG,
                    COMMENT,
                    SUBMISSION_KILLED,
                ]
            ],
            ignore_conflicts=True,
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
            FAVORITE,
            SUBMISSION_CHAR_TAG,
            SUBMISSION_ARTIST_TAG,
            COMMENT,
            SUBMISSION_KILLED,
        ],
    ).delete()
    Event.objects.filter(data__submission=instance.id).delete()


remove_submission_events = receiver(pre_delete, sender=Submission)(clear_events)
submission_thumbnailer = receiver(post_save, sender=Submission)(thumbnail_hook)


class Favorite(Model):
    """
    Custom through model for favorites.
    """

    user = ForeignKey("User", on_delete=CASCADE, related_name="+")
    submission = ForeignKey("Submission", on_delete=CASCADE, related_name="+")
    created_on = DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        unique_together = ("user", "submission")
        ordering = ("-created_on",)


def get_next_artist_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(ArtistTag, "display_position")


class ArtistTag(Model):
    id = ShortCodeField(default=gen_shortcode, db_index=True, primary_key=True)
    user = ForeignKey("User", on_delete=CASCADE)
    submission = ForeignKey("Submission", on_delete=CASCADE)
    display_position = FloatField(
        db_index=True, default=get_next_artist_position, unique=True
    )
    hidden = BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ("-display_position", "id")


@receiver(post_save, sender=ArtistTag)
def subscribe_for_favorites(sender, instance, created=False, *args, **kwargs):
    if not created:
        return
    image_type = ContentType.objects.get_for_model(model=instance.submission)
    Subscription.objects.get_or_create(
        subscriber=instance.user,
        content_type=image_type,
        object_id=instance.submission.id,
        type=FAVORITE,
    )


@receiver(post_delete, sender=ArtistTag)
def unsubscribe_for_favorites(sender, instance, *args, **kwargs):
    image_type = ContentType.objects.get_for_model(model=instance.submission)
    if instance.user == instance.submission.owner:
        return
    Subscription.objects.filter(
        subscriber=instance.user,
        content_type=image_type,
        object_id=instance.submission.id,
        type=FAVORITE,
    ).delete()


def get_next_character_position():
    """
    Must be defined in root for migrations.
    """
    return get_next_increment(CharacterTag, "display_position")


class Character(Model, HitsMixin):
    """
    For storing information about Characters for commissioning
    """

    name = CharField(
        max_length=150,
        validators=[
            RegexValidator(
                r"^[^/\\?%&+#@]+$",
                message="Names may not contain /, \\, ?, #, @, or &.",
            ),
            RegexValidator(r"^[^.]", message="Names may not start with a period."),
            RegexValidator(r"[^.]$", message="Names may not end with a period."),
        ],
    )
    description = CharField(max_length=20000, blank=True, default="")
    private = BooleanField(
        default=False,
        help_text="Only show this character to people I have explicitly shared it to.",
    )
    open_requests = BooleanField(
        default=False,
        help_text="Allow others to request commissions with my character, such as for "
        "gifts.",
    )
    open_requests_restrictions = CharField(
        max_length=2000,
        help_text="Write any particular conditions or requests to be considered when "
        "someone else is commissioning a piece with this character. "
        "For example, 'This character should only be drawn in Safe for "
        "Work Pieces.'",
        blank=True,
        default="",
    )
    primary_submission = ForeignKey(
        "profiles.Submission", null=True, on_delete=SET_NULL, blank=True
    )
    user = ForeignKey("User", related_name="characters", on_delete=CASCADE)
    created_on = DateTimeField(auto_now_add=True)
    tags = ManyToManyField("lib.Tag", related_name="characters", blank=True)
    nsfw = BooleanField(
        db_index=True,
        default=False,
        help_text="Used to indicate that this character should not be shown when in "
        "SFW mode, and its tags should be "
        "excluded based on a user's NSFW blocked tags.",
    )
    shared_with = ManyToManyField("User", related_name="shared_characters", blank=True)
    hit_counter = GenericRelation(
        "hitcount.HitCount",
        object_id_field="object_pk",
        related_query_name="hit_counter",
    )
    tags__max = 100
    colors__max = 24
    shared_with__max = 150  # Dunbar limit

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("name", "user"),)
        ordering = ("-created_on",)

    def preview_image(self, request):
        if not self.primary_submission:
            return make_url("/static/images/default-avatar.png")
        return preview_rating(
            request,
            self.primary_submission.rating,
            self.primary_submission.preview_link,
            sub_link="/static/images/default-avatar.png",
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
            recall_notification(
                NEW_CHARACTER, self.user, {"character": pk}, unique_data=True
            )
        return result

    def delete(self, *args, **kwargs):
        return self.wrap_operation(super().delete, always=True, *args, **kwargs)

    def save(self, *args, **kwargs):
        return self.wrap_operation(super().save, *args, **kwargs)


Character_shared_with = Character.shared_with.through


class CharacterTag(Model):
    id = ShortCodeField(default=gen_shortcode, db_index=True, primary_key=True)
    character = ForeignKey("Character", on_delete=CASCADE)
    submission = ForeignKey("Submission", on_delete=CASCADE)
    display_position = FloatField(
        db_index=True, default=get_next_character_position, unique=True
    )
    hidden = BooleanField(default=False, db_index=True)
    reference = BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ("-display_position", "id")


@receiver(post_save, sender=CharacterTag)
@disable_on_load
def set_primary_if_first(sender, instance, created=False, **kwargs):
    if not created:
        return
    if not instance.character.primary_submission:
        instance.character.primary_submission = instance.submission
        instance.character.save()


@receiver(post_delete, sender=CharacterTag)
@disable_on_load
def remove_if_primary(sender, instance, **kwargs):
    if instance.submission == instance.character.primary_submission:
        instance.character.primary_submission = None
        instance.character.save()


class Attribute(Model):
    key = CharField(max_length=50, db_index=True)
    value = CharField(max_length=100, default="")
    sticky = BooleanField(db_index=True, default=False)
    character = ForeignKey(Character, on_delete=CASCADE, related_name="attributes")

    class Meta:
        unique_together = (("key", "character"),)
        ordering = ["id"]

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
            type=CHAR_TAG,
        )


@receiver(post_delete, sender=Character)
@disable_on_load
def auto_remove_character(sender, instance, **kwargs):
    character_type = ContentType.objects.get_for_model(model=sender)
    Subscription.objects.filter(
        subscriber=instance.user,
        content_type=character_type,
        object_id=instance.id,
        type=CHAR_TAG,
    ).delete()
    Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type__in=[CHAR_TAG, NEW_CHARACTER],
    ).delete()
    Event.objects.filter(type=SUBMISSION_CHAR_TAG, data__character=instance.id).delete()


# noinspection PyUnusedLocal
@receiver(post_save, sender=Character)
@disable_on_load
def auto_add_attrs(sender, instance, created=False, **_kwargs):
    if not created:
        return
    Attribute.objects.create(key="sex", value="", sticky=True, character=instance)
    Attribute.objects.create(key="species", value="", sticky=True, character=instance)


# noinspection PyUnusedLocal
@receiver(post_save, sender=Character)
@disable_on_load
def auto_notify_watchers(sender, instance, created=False, **kwargs):
    if not created:
        return
    if instance.private:
        return
    notify(NEW_CHARACTER, instance.user, {"character": instance.id}, unique_data=True)


remove_order_events = receiver(pre_delete, sender=Character)(
    disable_on_load(clear_events)
)


class RefColor(Model):
    """
    Stores a reference color for a character.
    """

    color = CharField(max_length=7, validators=[RegexValidator(r"^#[0-9a-fA-F]{6}$")])
    note = CharField(max_length=100)
    character = ForeignKey(Character, related_name="colors", on_delete=CASCADE)


class ConversationParticipant(Model):
    """
    Leaf table for tracking read status of messages.
    """

    user = ForeignKey(User, related_name="message_record", on_delete=CASCADE)
    conversation = ForeignKey(
        "profiles.Conversation", related_name="message_record", on_delete=CASCADE
    )
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
        User, related_name="conversations", through=ConversationParticipant, blank=True
    )
    created_on = DateTimeField(default=timezone.now, db_index=True)
    participants__max = 20
    comments = GenericRelation(
        Comment,
        related_query_name="message",
        content_type_field="content_type",
        object_id_field="object_id",
    )
    last_activity = DateTimeField(default=None, null=True, db_index=True)
    comment_permissions = [IsRegistered, MessageReadPermission]

    def new_comment(self, comment):
        ConversationParticipant.objects.filter(conversation=self).exclude(
            user=comment.user
        ).update(read=False)
        self.last_activity = comment.created_on
        self.save()

    def comment_deleted(self, comment):
        last_comment = (
            self.comments.filter(deleted=False).order_by("-created_on").first()
        )
        if not last_comment:
            self.last_activity = None
        else:
            self.last_activity = last_comment.created_on
        self.save()

    # noinspection PyUnusedLocal
    def notification_name(self, context):
        participants = (
            self.participants.exclude(
                username=context["request"].user.username,
            )
            .order_by("username")
            .distinct("username")
            .values_list("username", flat=True)
        )

        count, participants = participants.count(), participants[:3]
        if count > 3:
            additional = count - 3
            names = (
                f"{participants[0]}, {participants[1]}, {participants[2]} and "
                f"{additional} others"
            )
        elif count == 3:
            names = f"{participants[0]}, {participants[1]}, and {participants[2]}"
        elif count == 2:
            names = f"{participants[0]} and {participants[1]}"
        elif count == 1:
            names = f"{participants[0]}"
        else:
            names = "(None)"
        return f"conversation with {names}"

    def notification_link(self, context):
        return {
            "name": "Conversation",
            "params": {
                "conversationId": self.id,
                "username": context["request"].user.username,
            },
        }

    def notification_serialize(self, context):
        from .serializers import ConversationManagementSerializer

        return ConversationManagementSerializer(instance=self, context=context).data


@receiver(post_delete, sender=Conversation)
@disable_on_load
def auto_remove_order(sender, instance, **_kwargs):
    clear_events_subscriptions_and_comments(instance)


class Journal(Model):
    """
    Model for private messages.
    """

    class Meta:
        ordering = ("-created_on",)

    user = ForeignKey(User, on_delete=CASCADE, related_name="journals")
    subject = CharField(max_length=150)
    body = CharField(max_length=5000)
    edited = models.BooleanField(default=False)
    created_on = DateTimeField(auto_now_add=True, db_index=True)
    edited_on = DateTimeField(auto_now=True)
    comments_disabled = BooleanField(default=False)
    comments = GenericRelation(
        Comment,
        related_query_name="message",
        content_type_field="content_type",
        object_id_field="object_id",
    )
    subscriptions = GenericRelation("lib.Subscription")
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
        return {"file": {"notification": self.user.avatar_url}}

    # noinspection PyUnusedLocal
    def notification_name(self, context):
        return "journal with subject: {}".format(self.subject)

    # noinspection PyUnusedLocal
    def notification_link(self, context):
        return {
            "name": "Journal",
            "params": {"journalId": self.id, "username": self.user.username},
        }


# noinspection PyUnusedLocal
@receiver(post_save, sender=Journal)
@disable_on_load
def auto_subscribe_journal(sender, instance, created=False, **kwargs):
    if not created:
        return
    notify(NEW_JOURNAL, instance.user, data={"journal": instance.id})
    Subscription.objects.create(
        type=COMMENT,
        subscriber=instance.user,
        object_id=instance.id,
        content_type=ContentType.objects.get_for_model(Journal),
    )


# noinspection PyUnusedLocal
@receiver(post_delete, sender=Journal)
@disable_on_load
def auto_unsubscribe_journal(sender, instance, **kwargs):
    recall_notification(
        NEW_JOURNAL,
        target=instance.user,
        data={"journal": instance.id},
        unique_data=True,
    )
    Subscription.objects.filter(
        type=COMMENT,
        object_id=instance.id,
        content_type=ContentType.objects.get_for_model(Journal),
    ).delete()
    # Need to trigger the cleanup handlers.
    for event in Event.objects.filter(
        content_type=ContentType.objects.get_for_model(model=sender),
        object_id=instance.id,
        type=COMMENT,
    ):
        event.delete()
    for event in Event.objects.filter(
        type=NEW_JOURNAL,
        data__journal=instance.id,
    ):
        event.delete()


class StaffPowers(models.Model):
    watch_permissions = {
        "StaffPowersSerializer": [ObjectControls, IsSuperuser],
    }
    user = OneToOneField(User, on_delete=CASCADE, related_name="staff_powers")
    # Enables the ability to handle disputes, create and perform actions on invoices.
    handle_disputes = BooleanField(default=False)
    # Allows someone to view the social media promotion settings of particular users.
    view_social_data = BooleanField(default=False)
    # Allows the user to view and download financial data
    view_financials = BooleanField(default=False)
    # Allows a user to edit other user's submissions
    moderate_content = BooleanField(default=False)
    # Allows a user to delete comments
    moderate_discussion = BooleanField(default=False)
    # Grants access to the virtual table control panel and associated features.
    table_seller = BooleanField(default=False)
    # Allows a staffer to view things from the other user's perspective.
    view_as = BooleanField(default=False)
    # Allows a staffer to do things like reset passwwords, change usernames,
    # disable accounts, and update emails.
    administrate_users = BooleanField(default=False)


for power in POWER_LIST:
    assert hasattr(StaffPowers, power)


@receiver(post_save, sender=StaffPowers)
def power_subscriptions(sender, instance, **kwargs):
    user = instance.user
    if user.is_superuser or (user.is_staff and instance.handle_disputes):
        Subscription.objects.get_or_create(
            subscriber=user, content_type=None, object_id=None, type=DISPUTE
        )

    else:
        Subscription.objects.filter(
            subscriber=user,
            content_type=None,
            object_id=None,
            type=DISPUTE,
        ).delete()
    if user.is_superuser or (user.is_staff and instance.view_financials):
        Subscription.objects.get_or_create(
            defaults={"email": True},
            subscriber=user,
            content_type=None,
            object_id=None,
            type=REFUND,
        )
    else:
        Subscription.objects.filter(
            subscriber=user,
            content_type=None,
            object_id=None,
            type=REFUND,
        ).delete()


@disable_on_load
def subscribe_watching(sender, instance, **kwargs):
    action = kwargs.get("action", "")
    for pk in kwargs.get("pk_set", set()):
        user = User.objects.get(pk=pk)
        if action == "post_add":
            watch_subscriptions(instance, user)
            notify(WATCHING, user, {"user_id": instance.id}, unique_data=True)
        elif action == "post_remove":
            remove_watch_subscriptions(instance, user)
            recall_notification(
                WATCHING, user, {"user_id": instance.id}, unique_data=True
            )


@disable_on_load
def favorite_notification(sender, instance, **kwargs):
    action = kwargs.get("action", "")
    pk_set = kwargs.get("pk_set", None)
    if not pk_set:
        return
    for pk in kwargs.get("pk_set", set()):
        submission = Submission.objects.get(pk=pk)
        if action == "post_add":
            if instance.favorites_hidden:
                continue
            notify(
                FAVORITE,
                submission,
                {"user_id": instance.id},
                unique_data=True,
                exclude=[instance],
            )
        elif action == "post_remove":
            recall_notification(
                FAVORITE, submission, {"user_id": instance.id}, unique_data=True
            )


models.signals.m2m_changed.connect(subscribe_watching, User.watching.through)
models.signals.m2m_changed.connect(favorite_notification, User.favorites.through)


def create_email_preferences(user: User):
    """
    Creates email preferences for a user.
    """
    from apps.sales.models import Deliverable, Reference, Revision, Product
    from apps.profiles.models import Submission

    user_content_type = ContentType.objects.get_for_model(User)
    conversation_content_type = ContentType.objects.get_for_model(Conversation)
    deliverable_content_type = ContentType.objects.get_for_model(Deliverable)
    revision_content_type = ContentType.objects.get_for_model(Revision)
    reference_content_type = ContentType.objects.get_for_model(Reference)
    product_content_type = ContentType.objects.get_for_model(Product)
    submission_content_type = ContentType.objects.get_for_model(Submission)
    preferences = [
        EmailPreference(
            user=user,
            content_type=deliverable_content_type,
            type=ORDER_UPDATE,
            enabled=True,
        ),
        EmailPreference(
            user=user,
            content_type=deliverable_content_type,
            type=COMMENT,
            enabled=True,
        ),
        EmailPreference(
            user=user,
            content_type=revision_content_type,
            type=COMMENT,
            enabled=True,
        ),
        EmailPreference(
            user=user,
            content_type=reference_content_type,
            type=COMMENT,
            enabled=True,
        ),
        EmailPreference(
            user=user,
            content_type=deliverable_content_type,
            type=REVISION_UPLOADED,
            enabled=True,
        ),
        EmailPreference(
            user=user,
            content_type=deliverable_content_type,
            type=REFERENCE_UPLOADED,
            enabled=True,
        ),
        EmailPreference(
            user=user,
            content_type=submission_content_type,
            type=SUBMISSION_KILLED,
            enabled=True,
        ),
        EmailPreference(
            user=user,
            content_type=product_content_type,
            type=PRODUCT_KILLED,
            enabled=True,
        ),
    ]
    if not user.guest:
        preferences.extend(
            [
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=COMMISSIONS_OPEN,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=WAITLIST_UPDATED,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=deliverable_content_type,
                    type=SALE_UPDATE,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=conversation_content_type,
                    type=COMMENT,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=RENEWAL_FIXED,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=RENEWAL_FAILURE,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=SUBSCRIPTION_DEACTIVATED,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=TRANSFER_FAILED,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=REFERRAL_LANDSCAPE_CREDIT,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=user_content_type,
                    type=AUTO_CLOSED,
                    enabled=True,
                ),
                EmailPreference(
                    user=user,
                    content_type=revision_content_type,
                    type=REVISION_APPROVED,
                    enabled=True,
                ),
            ]
        )
    if staff_power(user, "handle_disputes"):
        preferences.extend(
            [
                EmailPreference(
                    user=user,
                    content_type=deliverable_content_type,
                    type=REFUND,
                    enabled=True,
                ),
            ]
        )
    EmailPreference.objects.bulk_create(preferences, ignore_conflicts=True)
