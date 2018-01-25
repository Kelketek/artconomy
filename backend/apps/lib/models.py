from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import DateTimeField, Model, SlugField


class Comment(models.Model):
    deleted = models.BooleanField(default=False, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.CharField(max_length=8000)
    created_on = DateTimeField(auto_now_add=True)
    edited_on = DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('Comment', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.edited = True
        super().save(*args, **kwargs)

    def __str__(self):
        return "({}) Comment by {} on {}".format(self.id, self.user.username, self.created_on)

    class Meta:
        ordering = ('created_on',)


NEW_CHARACTER = 0
FOLLOWING = 1
CHAR_TRANSFER = 2
# Character tagged on submission, sent on character listener
CHAR_TAG = 3
COMMENT = 4
CHAR_CREATION = 5
NEW_PRODUCT = 6
COMMISSIONS_OPEN = 7
NEW_CHAR_SUBMISSION = 8
NEW_PORTFOLIO_ITEM = 9
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


EVENT_TYPES = (
    (NEW_CHARACTER, 'New Submission'),
    (FOLLOWING, 'New Follower'),
    (CHAR_TRANSFER, 'Character Transfer Request'),
    (CHAR_TAG, 'Character Tagged'),
    (COMMENT, 'New Comment'),
    (CHAR_CREATION, 'New Character'),
    (COMMISSIONS_OPEN, 'Commission Slots Available'),
    (NEW_PRODUCT, 'New Product'),
    (NEW_AUCTION, 'New Auction'),
    (ORDER_UPDATE, 'Order Update'),
    (SALE_UPDATE, 'Sale Update'),
    (DISPUTE, 'Dispute Filed'),
    (REFUND, 'Refund Processed'),
    (NEW_CHAR_SUBMISSION, 'New Submission of Character'),
    (NEW_PORTFOLIO_ITEM, 'New Portfolio Item'),
    (FAVORITE, 'New Favorite'),
    (SUBMISSION_TAG, 'Submission Tagged'),
    (SUBMISSION_CHAR_TAG, 'Submission tagged with Character'),
    (ARTIST_TAG, 'Tagged as the artist of a submission'),
    (SUBMISSION_ARTIST_TAG, 'Tagged the artist of a submission'),
    (ANNOUNCEMENT, 'Announcement'),
    (SYSTEM_ANNOUNCEMENT, 'System-wide announcement'),
)


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
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    target = GenericForeignKey('content_type', 'object_id')
    implicit = models.BooleanField(default=True, db_index=True)
    removed = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('type', 'subscriber', 'object_id', 'content_type')


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    event = models.ForeignKey(Event)
    read = models.BooleanField(default=False, db_index=True)


class Tag(Model):
    name = SlugField(db_index=True, unique=True, primary_key=True)
