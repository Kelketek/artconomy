from itertools import chain

import reversion
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import DateTimeField, Model, SlugField, CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.signals import saved_file
from uuid import uuid4

from apps.lib.abstract_models import ALLOWED_EXTENSIONS
from apps.lib.permissions import CommentViewPermission
from apps.lib.tasks import generate_thumbnails, check_asset_associations
from shortcuts import disable_on_load


class Comment(models.Model):
    deleted = models.BooleanField(default=False, db_index=True)
    thread_deleted = models.BooleanField(default=False, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    text = models.CharField(max_length=8000)
    system = models.BooleanField(default=False, db_index=True)
    created_on = DateTimeField(auto_now_add=True)
    edited_on = DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True, db_index=True, related_name='+',
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    top_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=False, db_index=True, related_name='+',
    )
    top_object_id = models.PositiveIntegerField(null=True, blank=False, db_index=True)
    top = GenericForeignKey('top_content_type', 'top_object_id')
    # This field to be removed once data is verified to be working right in production.
    parent = models.ForeignKey('Comment', related_name='children', null=True, blank=True, on_delete=models.CASCADE)
    subscriptions = GenericRelation('lib.Subscription')
    comments = GenericRelation(
        'self', related_query_name='message', content_type_field='content_type', object_id_field='object_id'
    )

    comment_permissions = [CommentViewPermission]

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.edited = True
        if self.deleted:
            self.edited = False
        if getattr(self.top, 'preserve_comments', False):
            with reversion.create_revision():
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return "({}) Comment by {} on {}".format(self.id, self.user.username, self.created_on)

    def notification_serialize(self, context):
        from apps.lib.serializers import CommentSerializer
        return CommentSerializer(self, context=context).data

    class Meta:
        ordering = ('created_on',)

reversion.register(Comment)


NEW_CHARACTER = 0
WATCHING = 1
# Character tagged on submission, sent on character listener
CHAR_TAG = 3
COMMENT = 4
NEW_PRODUCT = 6
COMMISSIONS_OPEN = 7
NEW_CHAR_SUBMISSION = 8
SUBMISSION_TAG = 10
NEW_AUCTION = 11
ANNOUNCEMENT = 12
SYSTEM_ANNOUNCEMENT = 13
FAVORITE = 14
DISPUTE = 15
REFUND = 16
# Character tagged on submission, sent on submission listener
SUBMISSION_CHAR_TAG = 17
ORDER_UPDATE = 18
SALE_UPDATE = 19
ARTIST_TAG = 20
SUBMISSION_ARTIST_TAG = 21
REVISION_UPLOADED = 22
SUBMISSION_SHARED = 23
CHAR_SHARED = 24
STREAMING = 26
RENEWAL_FAILURE = 27
SUBSCRIPTION_DEACTIVATED = 28
RENEWAL_FIXED = 29
NEW_JOURNAL = 30
# ORDER_TOKEN_ISSUED = 31   -- Reserved for removed status.
TRANSFER_FAILED = 32
REFERRAL_PORTRAIT_CREDIT = 33
REFERRAL_LANDSCAPE_CREDIT = 34

ORDER_NOTIFICATION_TYPES = (
    DISPUTE, SALE_UPDATE, ORDER_UPDATE, RENEWAL_FIXED, RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED,
    REVISION_UPLOADED, TRANSFER_FAILED, REFUND,
)

EVENT_TYPES = (
    (NEW_CHARACTER, 'New Character'),
    (WATCHING, 'New Watcher'),
    (CHAR_TAG, 'Character Tagged'),
    (COMMENT, 'New Comment'),
    (COMMISSIONS_OPEN, 'Commission Slots Available'),
    (NEW_PRODUCT, 'New Product'),
    (NEW_AUCTION, 'New Auction'),
    (ORDER_UPDATE, 'Order Update'),
    (REVISION_UPLOADED, 'Revision Uploaded'),
    (SALE_UPDATE, 'Sale Update'),
    (DISPUTE, 'Dispute Filed'),
    (REFUND, 'Refund Processed'),
    (NEW_CHAR_SUBMISSION, 'New Submission of Character'),
    (FAVORITE, 'New Favorite'),
    (SUBMISSION_TAG, 'Submission Tagged'),
    (SUBMISSION_CHAR_TAG, 'Submission tagged with Character'),
    (ARTIST_TAG, 'Tagged as the artist of a submission'),
    (SUBMISSION_ARTIST_TAG, 'Tagged the artist of a submission'),
    (ANNOUNCEMENT, 'Announcement'),
    (SYSTEM_ANNOUNCEMENT, 'System-wide announcement'),
    (RENEWAL_FAILURE, 'Renewal Failure'),
    (SUBSCRIPTION_DEACTIVATED, 'Subscription Deactivated'),
    (NEW_JOURNAL, 'New Journal Posted'),
    (TRANSFER_FAILED, 'Bank Transfer Failed')
)

EMAIL_SUBJECTS = {
    COMMISSIONS_OPEN: 'Commissions are open for {{ target.username }}!',
    ORDER_UPDATE: 'Order #{{ target.id}} has been updated!',
    REVISION_UPLOADED: 'New revision for order #{{ target.id }}!',
    SALE_UPDATE: '{% if target.status == 1 %}New Sale!{% else %}Sale #{{ target.id }} has been updated!{% endif %}'
                 ' #{{target.id}}',
    REFUND: 'A refund was issued for Order #{{ target.id }}',
    COMMENT: '{% if data.subject %}{{ data.subject }}{% else %}New comment on {{ data.name }}{% endif %}',
    RENEWAL_FAILURE: 'Issue with your subscription',
    SUBSCRIPTION_DEACTIVATED: 'Your subscription has been deactivated.',
    RENEWAL_FIXED: 'Subscription renewed successfully',
    TRANSFER_FAILED: 'Bank transfer failed.',
    REFERRAL_PORTRAIT_CREDIT: "One of your referrals just made a purchase!",
    REFERRAL_LANDSCAPE_CREDIT: "One of your referrals just made a sale!"
}


class Event(models.Model):
    type = models.IntegerField(db_index=True, choices=EVENT_TYPES)
    data = JSONField(default=dict)
    date = models.DateTimeField(auto_now_add=True)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    recalled = models.BooleanField(default=False, db_index=True)


class Subscription(models.Model):
    type = models.IntegerField(db_index=True, choices=EVENT_TYPES)
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    target = GenericForeignKey('content_type', 'object_id')
    implicit = models.BooleanField(default=True, db_index=True)
    email = models.BooleanField(default=False, db_index=True)
    telegram = models.BooleanField(default=False, db_index=True)
    removed = models.BooleanField(default=False, db_index=True)
    until = models.DateField(null=True, db_index=True)

    class Meta:
        unique_together = ('type', 'subscriber', 'object_id', 'content_type')


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    event = models.ForeignKey(Event, on_delete=CASCADE, related_name='notifications')
    read = models.BooleanField(default=False, db_index=True)


class Tag(Model):
    name = SlugField(db_index=True, unique=True, primary_key=True)

    def self_clean(self):
        from apps.lib.utils import translate_related_names
        fields = self._meta.get_fields()
        names = [field.related_name for field in fields if getattr(field, 'related_name', None)]
        names = translate_related_names(names)
        if not any([getattr(self, name).all().exists() for name in names]):
            self.delete()

    def notification_serialize(self, context):
        return self.name


def _comment_transform(old_data, new_data):
    return {
        'comments': old_data['comments'] + new_data['comments'],
        'subcomments': old_data['subcomments'] + new_data['subcomments']
    }


@receiver(post_save, sender=Comment)
@disable_on_load
def auto_subscribe_thread(sender, instance, created=False, **_kwargs):
    if created and not instance.system:
        Subscription.objects.create(
            subscriber=instance.user,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=COMMENT,
        )
        target = instance.content_object
        if not isinstance(target, Comment):
            target = None
        if target:
            subscription, created = Subscription.objects.get_or_create(
                subscriber=instance.user,
                content_type_id=instance.content_type_id,
                object_id=instance.object_id,
                type=COMMENT,
            )
            subscription.removed = False
            subscription.implicit = True
            subscription.save()
        from apps.lib.utils import notify
        primary_target = instance.content_object
        # Notify who is subscribed to the parent comment or the top level if there isn't one.
        notify(
            COMMENT, primary_target, data={
                'comments': [instance.id],
                'subcomments': []
            },
            unique=True, mark_unread=True,
            transform=_comment_transform,
            exclude=[instance.user],
            force_create=True,
        )
        # Notify whoever is subscribed to top level, if that's not what we already notified.
        target = instance
        while isinstance(target, Comment) and target.content_object:
            target = target.content_object
        if target != primary_target:
            notify(
                COMMENT, target, data={
                    # Subcomment, so not marking a direct comment.
                    'comments': [],
                    'subcomments': [instance.id]
                },
                unique=True, mark_unread=True,
                transform=_comment_transform,
                exclude=[instance.user],
                force_create=True,
            )
        if hasattr(target, 'new_comment'):
            target.new_comment(instance)


@receiver(saved_file)
@disable_on_load
def generate_thumbnails_async(sender, fieldfile, **kwargs):
    generate_thumbnails(
        model=sender, pk=fieldfile.instance.pk,
        field=fieldfile.field.name)


# Additional signal for comment in utils, pre_save, since it would be recursive otherwise.


class Asset(Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file = ThumbnailerImageField(
        upload_to='art/%Y/%m/%d/', validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)]
    )
    created_on = DateTimeField(default=timezone.now)
    edited_on = DateTimeField(auto_now=True)

    def can_reference(self, user):
        if not user.is_authenticated:
            # Why are we even letting the user submit in this case?
            return False
        if user == self.uploaded_by:
            return True
        # noinspection PyTypeChecker
        for item in get_all_foreign_references(self):
            if getattr(item, 'can_reference_asset', lambda x: False)(user):
                return True
        return False


    def delete(self, using=None, keep_parents=False, cleanup=False):
        if not cleanup:
            raise AssertionError('Never attempt to delete an asset directly. Use the purge_asset task.')
        super().delete(using=using, keep_parents=keep_parents)


@receiver(post_save, sender=Asset)
@disable_on_load
def cleanup_old_asset(sender, instance, created=False, **kwargs):
    if not created:
        return
    # Assets will expire after an hour of non-reference.
    check_asset_associations.apply_async(countdown=60 * 60, args=[str(instance.id)])


def related_iterable_from_field(instance, field, check_existence=False):
    try:
        related_name = field.related_name
    except AttributeError:
        related_name = None
        field = field.related
    auto = False
    if related_name is None:
        related_name = field.name
        auto = True
    if related_name == '+':
        return []
    if field.one_to_one:
        if check_existence:
            if getattr(instance, related_name + '_id'):
                return [True]
            return []
        # This may be wrong but I'm not using it anywhere yet.
        obj = getattr(instance, related_name)
        if obj:
            return [obj]
        return []
    if auto:
        related_name += '_set'
    if field.one_to_many or field.many_to_many:
        if check_existence:
            if getattr(instance, related_name).exists():
                return [True]
            return []
        return getattr(instance, related_name).all()
    raise RuntimeError(f'Unknown related field type, {field}')


def get_all_foreign_references(instance, check_existence=False):
    check_fields = [field for field in instance._meta.get_fields() if (any(
        (field.one_to_many, field.many_to_many, field.one_to_one))
    )]
    yield from chain.from_iterable(
        (related_iterable_from_field(instance, field, check_existence=check_existence) for field in check_fields),
    )