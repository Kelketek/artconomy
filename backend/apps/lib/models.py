from hashlib import sha256
from uuid import uuid4

import reversion
from apps.lib.abstract_models import ALLOWED_EXTENSIONS
from apps.lib.constants import (
    EVENT_TYPES,
    COMMENT,
    ORDER_NOTIFICATION_TYPES,
    FLAG_REASONS,
)
from apps.lib.permissions import CommentViewPermission, Or, StaffPower
from apps.lib.tasks import check_asset_associations, generate_thumbnails
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import (
    CASCADE,
    SET_NULL,
    DateTimeField,
    ForeignKey,
    JSONField,
    Model,
    SlugField,
    UUIDField,
)
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.signals import saved_file
from short_stuff import unslugify

from apps.profiles.permissions import ObjectControls
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
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name="+",
    )
    content_object = GenericForeignKey("content_type", "object_id")
    top_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        db_index=True,
        related_name="+",
    )
    # The content of this data is user specified. DO NOT TRUST IT.
    extra_data = JSONField(default=dict, blank=True)
    top_object_id = models.PositiveIntegerField(null=True, blank=False, db_index=True)
    top = GenericForeignKey("top_content_type", "top_object_id")
    # This field to be removed once data is verified to be working right in production.
    parent = models.ForeignKey(
        "Comment",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    subscriptions = GenericRelation("lib.Subscription")
    comments = GenericRelation(
        "self",
        related_query_name="message",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    comment_permissions = [CommentViewPermission]
    watch_permissions = {CommentViewPermission}

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.edited = True
        if self.deleted:
            self.edited = False
        if getattr(self.top, "preserve_comments", False):
            with reversion.create_revision():
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return "({}) Comment by {} on {}".format(
            self.id, self.user.username, self.created_on
        )

    def notification_serialize(self, context):
        from apps.lib.serializers import CommentSerializer

        return CommentSerializer(self, context=context).data

    class Meta:
        ordering = ("created_on",)


reversion.register(Comment)


class Event(models.Model):
    type = models.IntegerField(db_index=True, choices=EVENT_TYPES)
    data = JSONField(default=dict)
    date = models.DateTimeField(auto_now_add=True)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    target = GenericForeignKey("content_type", "object_id")
    recalled = models.BooleanField(default=False, db_index=True)


class Subscription(models.Model):
    type = models.IntegerField(db_index=True, choices=EVENT_TYPES)
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True, db_index=True
    )
    target = GenericForeignKey("content_type", "object_id")
    implicit = models.BooleanField(default=True, db_index=True)
    # Deprecated field-- we now use the EmailPreference model.
    email = models.BooleanField(default=False, db_index=True)
    telegram = models.BooleanField(default=False, db_index=True)
    removed = models.BooleanField(default=False, db_index=True)
    until = models.DateField(null=True, db_index=True)

    class Meta:
        unique_together = ("type", "subscriber", "object_id", "content_type")


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    event = models.ForeignKey(Event, on_delete=CASCADE, related_name="notifications")
    read = models.BooleanField(default=False, db_index=True)
    watch_permissions = {
        "NotificationSerializer": [Or(StaffPower("view_as"), ObjectControls)]
    }

    def announce_channels(self):
        if self.event.type in ORDER_NOTIFICATION_TYPES:
            return [f"profiles.User.pk.{self.user.id}.sales_notifications"]
        else:
            return [f"profiles.User.pk.{self.user.id}.community_notifications"]


@receiver(post_delete, sender=Notification)
def recalc_totals(sender, instance, **kwargs):
    if not instance.read:
        from apps.lib.consumers import send_updated

        send_updated(instance.user, serializers=["UnreadNotificationsSerializer"])


class EmailPreference(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="email_preferences"
    )
    type = models.IntegerField(db_index=True, choices=EVENT_TYPES)
    enabled = models.BooleanField(default=True, db_index=True)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        unique_together = ("user", "type", "content_type")


class Tag(Model):
    name = SlugField(db_index=True, unique=True, primary_key=True)

    def self_clean(self):
        from apps.lib.utils import translate_related_names

        fields = self._meta.get_fields()
        names = [
            field.related_name
            for field in fields
            if getattr(field, "related_name", None)
        ]
        names = translate_related_names(names)
        if not any([getattr(self, name).all().exists() for name in names]):
            self.delete()

    def notification_serialize(self, context):
        return self.name


class GenericReference(Model):
    object_id = UUIDField(db_index=True)
    content_type = ForeignKey(ContentType, on_delete=SET_NULL, null=True, blank=False)
    target = GenericForeignKey("content_type", "object_id")

    def notification_serialize(self, context):
        from apps.lib.serializers import get_link

        return {
            "model": self.target and self.target.__class__.__name__,
            "id": self.target and self.target.pk,
            "link": get_link(self.target, context=context),
        }

    def __str__(self):
        return f"::ref#{self.id}:: {self.target}"

    class Meta:
        unique_together = (("object_id", "content_type"),)


def ref_for_instance(instance: Model) -> GenericReference:
    if isinstance(instance, GenericReference):
        return instance
    pk = instance.pk
    if isinstance(pk, str):
        pk = unslugify(pk)
    result, _created = GenericReference.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(instance),
        object_id=pk,
    )
    return result


def _comment_transform(old_data, new_data):
    return {
        "comments": old_data["comments"] + new_data["comments"],
        "subcomments": old_data["subcomments"] + new_data["subcomments"],
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
        from apps.lib.utils import mark_modified, mark_read, notify

        primary_target = instance.content_object
        # Notify who is subscribed to the parent comment or the top level if there isn't
        # one.
        notify(
            COMMENT,
            primary_target,
            data={"comments": [instance.id], "subcomments": []},
            unique=True,
            mark_unread=True,
            transform=_comment_transform,
            exclude=[instance.user],
            force_create=True,
        )
        mark_modified(
            obj=instance.top,
            **getattr(instance.top, "modified_kwargs", lambda x: {})(
                instance.extra_data
            ),
        )
        mark_read(obj=instance.top, user=instance.user)
        # Notify whoever is subscribed to top level, if that's not what we already
        # notified.
        target = instance
        while isinstance(target, Comment) and target.content_object:
            target = target.content_object
        if target != primary_target:
            notify(
                COMMENT,
                target,
                data={
                    # Subcomment, so not marking a direct comment.
                    "comments": [],
                    "subcomments": [instance.id],
                },
                unique=True,
                mark_unread=True,
                transform=_comment_transform,
                exclude=[instance.user],
                force_create=True,
            )
        if hasattr(target, "new_comment"):
            target.new_comment(instance)


@receiver(saved_file)
@disable_on_load
def generate_thumbnails_async(sender, fieldfile, **kwargs):
    generate_thumbnails(
        model=sender, pk=fieldfile.instance.pk, field=fieldfile.field.name
    )


# Additional signal for comment in utils, pre_save, since it would be recursive
# otherwise.


class Asset(Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_assets",
    )
    file = ThumbnailerImageField(
        upload_to="art/%Y/%m/%d/",
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
    )
    hash = models.BinaryField(max_length=32, default=b"", db_index=True)
    redacted_on = models.DateTimeField(null=True, db_index=True, blank=True)
    redacted_by = models.ForeignKey(
        "profiles.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assets_redacted",
    )
    redacted_reason = models.IntegerField(
        choices=FLAG_REASONS, null=True, blank=True, db_index=True
    )
    created_on = DateTimeField(default=timezone.now)
    edited_on = DateTimeField(auto_now=True)

    def can_reference(self, request):
        from apps.lib.utils import get_all_foreign_references, request_key

        socket_key = request_key(request)
        if cache.get(f"upload_grant_{socket_key}-to-{self.id}"):
            return True
        user = request.user
        if not user.is_authenticated:
            # Why are we even letting the user submit in this case?
            return False
        if user == self.uploaded_by:
            return True
        # noinspection PyTypeChecker
        for item in get_all_foreign_references(self):
            if getattr(item, "can_reference_asset", lambda x: False)(user):
                return True
        return False

    def redact(self, *, reason, by):
        """
        Delete the associated file and blacklist it from being uploaded ever again.
        """
        self.file.delete()
        self.redacted_by = by
        self.redacted_reason = reason
        self.redacted_on = timezone.now()
        self.save()

    def delete(self, using=None, keep_parents=False, cleanup=False):
        if not cleanup:
            raise AssertionError(
                "Never attempt to delete an asset directly. Use the purge_asset task."
            )
        super().delete(using=using, keep_parents=keep_parents)


class ReadMarker(Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey("profiles.User", on_delete=CASCADE)
    last_read_on = models.DateTimeField(default=None, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.UUIDField(db_index=True)
    target = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("content_type", "object_id", "user")


class ModifiedMarker(Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    modified_on = models.DateTimeField(db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.UUIDField(db_index=True)
    target = GenericForeignKey("content_type", "object_id")
    # Efficiency shortcuts for deeply nested items.
    order = models.ForeignKey("sales.Order", on_delete=CASCADE, null=True)
    deliverable = models.ForeignKey("sales.Deliverable", on_delete=CASCADE, null=True)

    class Meta:
        unique_together = ("content_type", "object_id")


@receiver(post_save, sender=Asset)
@disable_on_load
def cleanup_old_asset(sender, instance, created=False, **kwargs):
    if not created:
        return
    # Assets will expire after an hour of non-reference.
    check_asset_associations.apply_async(countdown=60 * 60, args=[str(instance.id)])


class Note(Model):
    created_on = DateTimeField(default=timezone.now, db_index=True)
    text = models.TextField()
    hash = models.BinaryField(max_length=32, default=b"", db_index=True, unique=True)

    def save(
        self,
        **kwargs,
    ):
        if not self.hash:
            self.hash = sha256(self.text.encode("utf-8")).digest()
        super().save(
            **kwargs,
        )


def note_for_text(text):
    return Note.objects.get_or_create(
        hash=sha256(text.encode("utf-8")).digest(), defaults={"text": text}
    )[0]
