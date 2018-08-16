from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import DateTimeField, Model, SlugField, CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver


class Comment(models.Model):
    deleted = models.BooleanField(default=False, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    text = models.CharField(max_length=8000)
    system = models.BooleanField(default=False, db_index=True)
    created_on = DateTimeField(auto_now_add=True)
    edited_on = DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('Comment', related_name='children', null=True, blank=True, on_delete=models.CASCADE)
    subscriptions = GenericRelation('lib.Subscription')

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.edited = True
        super().save(*args, **kwargs)

    def __str__(self):
        return "({}) Comment by {} on {}".format(self.id, self.user.username, self.created_on)

    class Meta:
        ordering = ('created_on',)


NEW_CHARACTER = 0
WATCHING = 1
CHAR_TRANSFER = 2
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
ASSET_SHARED = 23
CHAR_SHARED = 24
NEW_PM = 25
STREAMING = 26
RENEWAL_FAILURE = 27
SUBSCRIPTION_DEACTIVATED = 28
RENEWAL_FIXED = 29
NEW_JOURNAL = 30
ORDER_TOKEN_ISSUED = 31
TRANSFER_FAILED = 32

ORDER_NOTIFICATION_TYPES = (
    DISPUTE, SALE_UPDATE, ORDER_UPDATE, RENEWAL_FIXED, RENEWAL_FAILURE, SUBSCRIPTION_DEACTIVATED,
    CHAR_TRANSFER, REVISION_UPLOADED, ORDER_TOKEN_ISSUED, TRANSFER_FAILED
)


EVENT_TYPES = (
    (NEW_CHARACTER, 'New Character'),
    (WATCHING, 'New Watcher'),
    (CHAR_TRANSFER, 'Character Transfer Request'),
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
    (ORDER_TOKEN_ISSUED, 'Order Token Issued'),
    (TRANSFER_FAILED, 'Bank Transfer Failed')
)

EMAIL_SUBJECTS = {
    COMMISSIONS_OPEN: 'Commissions are open for {{ target.username }}!',
    ORDER_UPDATE: 'Order #{{ target.id}} has been updated!',
    REVISION_UPLOADED: 'New revision for order #{{ target.id }}!',
    SALE_UPDATE: '{% if target.status == 1 %}New Sale!{% else %}Sale #{{ target.id }} has been updated!{% endif %}'
                 ' #{{target.id}}',
    REFUND: 'A refund was issued for Order #{{ target.id }}',
    NEW_PM: 'You have a new private message from {{ target.sender.username }}!',
    COMMENT: 'New comment on {{ name }}',
    RENEWAL_FAILURE: 'Issue with your subscription',
    SUBSCRIPTION_DEACTIVATED: 'Your subscription has been deactivated.',
    RENEWAL_FIXED: 'Subscription renewed successfully',
    ORDER_TOKEN_ISSUED: 'A special order token has been issued to you!',
    TRANSFER_FAILED: 'Bank transfer failed.'
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
def auto_subscribe_thread(sender, instance, created=False, **_kwargs):
    if created and not instance.system:
        Subscription.objects.create(
            subscriber=instance.user,
            content_type=ContentType.objects.get_for_model(model=instance),
            object_id=instance.id,
            type=COMMENT,
        )
        if instance.parent:
            subscription, created = Subscription.objects.get_or_create(
                subscriber=instance.user,
                content_type=ContentType.objects.get_for_model(model=instance),
                object_id=instance.parent.id,
                type=COMMENT,
            )
            subscription.removed = False
            subscription.implicit = True
            subscription.save()
        from apps.lib.utils import notify
        primary_target = instance.parent or instance.content_object
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
        while target.parent:
            target = target.parent
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

# Additional signal for comment in utils, pre_save, since it would be recursive otherwise.
