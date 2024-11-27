import os
from decimal import Decimal
from typing import List, Union

from moneyed import Money

from apps.lib.abstract_models import THUMBNAIL_IMAGE_EXTENSIONS
from apps.lib.consumers import register_serializer
from apps.lib.models import (
    Asset,
    Comment,
    Event,
    Notification,
    Subscription,
    Tag,
)
from apps.lib.constants import (
    NEW_CHARACTER,
    CHAR_TAG,
    COMMENT,
    NEW_PRODUCT,
    COMMISSIONS_OPEN,
    FAVORITE,
    DISPUTE,
    SUBMISSION_CHAR_TAG,
    ORDER_UPDATE,
    SALE_UPDATE,
    SUBMISSION_ARTIST_TAG,
    REVISION_UPLOADED,
    SUBMISSION_SHARED,
    CHAR_SHARED,
    STREAMING,
    NEW_JOURNAL,
    REFERENCE_UPLOADED,
    WAITLIST_UPDATED,
    TIP_RECEIVED,
    REVISION_APPROVED,
)
from apps.lib.utils import add_check, set_tags, tag_list_cleaner
from apps.profiles.models import (
    Character,
    Conversation,
    Journal,
    Submission,
    User,
)
from apps.sales.constants import WAITING
from apps.sales.models import Deliverable, Product, Revision
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, empty, BooleanField
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin

from shortcuts import make_url


# noinspection PyUnresolvedReferences
class RelatedAtomicMixin:
    @atomic
    def update(self, instance, validated_data):
        data = {**validated_data}
        for field_name, value in validated_data.items():
            field = self.fields.get(field_name)
            if not getattr(field, "save_related", False):
                continue
            data.pop(field_name)
            field.mod_instance(instance, value)
        if not data:
            # Don't run an update directly if there are no more fields to update.
            # We may add a way to force saving anyway if it ends up needed,
            # but this prevents us from updating edit timestamps for things like
            # subscribing to comments.
            return instance
        return super().update(instance, data)

    @atomic
    def create(self, validated_data):
        data = {**validated_data}
        post_handle = {}
        for field_name, value in validated_data.items():
            field = self.fields.get(field_name)
            if not getattr(field, "save_related", False):
                continue
            post_handle[field_name] = value
            data.pop(field_name)
        instance = super(RelatedAtomicMixin, self).create(data)
        for field_name, value in post_handle.items():
            field = self.fields[field_name]
            field.mod_instance(instance, value)
        return instance


class RelatedUserSerializer(serializers.ModelSerializer):
    stars = serializers.FloatField()
    service_plan = serializers.SerializerMethodField()
    international = serializers.SerializerMethodField()

    def get_international(self, obj):
        from apps.sales.models import StripeAccount

        return StripeAccount.objects.filter(
            user=obj, country=settings.SOURCE_COUNTRY
        ).exists()

    def get_service_plan(self, obj):
        return obj.service_plan.name

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "avatar_url",
            "stars",
            "is_staff",
            "is_superuser",
            "guest",
            "artist_mode",
            "taggable",
            "landscape",
            "rating_count",
            "service_plan",
            "international",
            "verified_email",
        )
        read_only_fields = fields


def notification_serialize(obj, context):
    if obj is None:
        return None
    if hasattr(obj, "notification_serialize"):
        return obj.notification_serialize(context)
    return {obj.__class__.__name__: obj.id}


def notification_display(obj, context):
    """
    For determining which icon is used in the notification area.
    """
    if hasattr(obj, "notification_display"):
        return obj.notification_display(context)
    return notification_serialize(obj, context)


def get_link(obj, context):
    if obj is None:
        return None
    if hasattr(obj, "notification_link"):
        return obj.notification_link(context)
    return None


def get_display_name(obj, context):
    if obj is None:
        return "<removed>"
    if hasattr(obj, "notification_name"):
        return obj.notification_name(context) or "Untitled"
    return "Unknown"


# noinspection PyAbstractClass
class EventTargetRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `content_object` generic relationship.

    Invokes the notification_serialize function on the target.
    """

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        return notification_serialize(value, self.context)


# Custom image field - handles base 64 encoded images
class RelatedAssetField(serializers.UUIDField):
    default_error_messages = dict(
        **serializers.UUIDField.default_error_messages,
        **{
            "non_existent": "We can't find that upload. It may have expired,"
            " or you may not have permission to reference it.",
            "null": "This field may not be blank.",
        },
    )

    def __init__(self, *args, **kwargs):
        self.thumbnail_namespace = kwargs.pop("thumbnail_namespace", "")
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if data == "":
            if self.allow_null:
                return None
            else:
                self.fail("null")
        data = super(RelatedAssetField, self).to_internal_value(data)
        if not data:
            return data
        asset = Asset.objects.filter(id=data).first()
        if not asset:
            self.fail("non_existent")
        if not asset.can_reference(self.context["request"]):
            self.fail("non_existent")
        return asset

    def get_value(self, dictionary):
        result = super(RelatedAssetField, self).get_value(dictionary)
        return result

    def to_representation(self, value):
        if not value:
            return None
        value = value.file
        extension = os.path.splitext(value.name)[1][1:].lower()
        if extension not in THUMBNAIL_IMAGE_EXTENSIONS:
            if extension != "svg":
                extension = f"data:{extension}"
            else:
                extension = "data:image"
            return {
                "__type__": extension,
                "full": make_url("{}{}".format(settings.MEDIA_URL, value.name)),
            }
        values = {}
        # Construct URLs manually and avoid hitting the disk/network.
        for key, val in settings.THUMBNAIL_ALIASES[self.thumbnail_namespace].items():
            thumb_extension = value.name.split(".")[-1]
            if extension.lower() == "webp":
                extension = "png"
            values[key] = make_url(
                "{}{}.{}x{}_q{}{}.{}".format(
                    settings.MEDIA_URL,
                    value.name,
                    val["size"][0],
                    val["size"][1],
                    85,
                    "_crop-{}".format(val.get("crop")) if val.get("crop") else "",
                    thumb_extension.lower(),
                )
            )
        values["full"] = make_url(settings.MEDIA_URL + value.name)
        values["__type__"] = "data:image"
        return values

    def mod_instance(self, instance, value):
        pass


# noinspection PyAbstractClass
class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class SubscribedField(serializers.Field):
    save_related = True

    def __init__(
        self,
        *args,
        related_name="subscriptions",
        extra_args=None,
        subscription_type=COMMENT,
        **kwargs,
    ):
        self.extra_args = extra_args or {}
        self.related_name = related_name
        self.subscription_type = subscription_type
        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        if not self.context["request"].user.is_authenticated:
            return False
        return (
            getattr(instance, self.related_name)
            .filter(
                subscriber=self.context["request"].user,
                object_id=instance.id,
                content_type=ContentType.objects.get_for_model(instance),
                type=self.subscription_type,
                removed=False,
                **self.extra_args,
            )
            .exists()
        )

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if data is None:
            return
        return bool(data)

    def mod_instance(self, instance, value):
        subscription, created = Subscription.objects.get_or_create(
            subscriber=self.context["request"].user,
            type=self.subscription_type,
            object_id=instance.id,
            content_type=ContentType.objects.get_for_model(instance),
        )
        if value:
            subscription.removed = False
            subscription.save()
            return instance
        elif created:
            subscription.delete()
        subscription.removed = True
        subscription.save()


class CommentMixin:
    def get_user(self, obj):
        if obj.deleted:
            return None
        return RelatedUserSerializer(context=self.context, instance=obj.user).data

    def get_comments(self, obj):
        if self.context.get("history"):
            return []
        return CommentSerializer(
            many=True,
            instance=reversed(obj.comments.all().order_by("-created_on")[:5]),
            context=self.context,
        ).data

    def get_comment_count(self, obj):
        return obj.comments.all().count()


class CommentSerializer(RelatedAtomicMixin, CommentMixin, serializers.ModelSerializer):
    user = SerializerMethodField()
    comments = SerializerMethodField()
    comment_count = SerializerMethodField()
    subscribed = SubscribedField(required=False)
    # Used in the broadcast to commissioners view, otherwise removed.
    include_active = BooleanField(required=True)
    include_waitlist = BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.context.get("broadcast_mode"):
            del self.fields["include_active"]
            del self.fields["include_waitlist"]

    def create(self, validated_data):
        validated_data.pop("include_active", None)
        validated_data.pop("include_waitlist", None)
        return super().create(validated_data)

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "created_on",
            "edited_on",
            "user",
            "comments",
            "comment_count",
            "edited",
            "deleted",
            "subscribed",
            "system",
            "extra_data",
            "include_active",
            "include_waitlist",
        )
        read_only_fields = (
            "id",
            "created_on",
            "edited_on",
            "user",
            "comments",
            "edited",
            "deleted",
            "system",
        )
        extra_kwargs = {"extra_data": {"write_only": True, "required": False}}


class CommentSubscriptionSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    user = RelatedUserSerializer(read_only=True)
    children = RecursiveField(many=True, read_only=True)
    subscribed = SubscribedField(required=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "created_on",
            "edited_on",
            "user",
            "children",
            "edited",
            "deleted",
            "subscribed",
            "system",
        )
        read_only_fields = (
            "id",
            "text",
            "created_on",
            "edited_on",
            "user",
            "children",
            "edited",
            "deleted",
            "system",
        )


def get_user(user_id):
    try:
        return RelatedUserSerializer(instance=User.objects.get(id=user_id)).data
    except User.DoesNotExist:
        return None


def char_tag(obj, context):
    value = obj.data
    from apps.profiles.serializers import CharacterSerializer, SubmissionSerializer

    try:
        submission = Submission.objects.get(id=value["submission"])
        submission_serialized = SubmissionSerializer(
            instance=submission, context=context
        ).data
        display = submission_serialized
    except Character.DoesNotExist:
        display = None
        submission_serialized = None
    user = get_user(value["user"])
    return {
        "character": CharacterSerializer(instance=obj.target, context=context).data,
        "user": user,
        "submission": submission_serialized,
        "display": display,
    }


def submission_char_tag(obj, context):
    value = obj.data
    from apps.profiles.serializers import CharacterSerializer, SubmissionSerializer

    try:
        character = Character.objects.get(id=value["character"])
        character_serialized = CharacterSerializer(
            instance=character, context=context
        ).data
        display = notification_display(character, context)["primary_submission"]
    except Character.DoesNotExist:
        display = None
        character_serialized = None
    user = get_user(value["user"])
    return {
        "character": character_serialized,
        "user": user,
        "submission": SubmissionSerializer(instance=obj.target, context=context).data,
        "display": display,
    }


def revision_uploaded(obj, context):
    value = obj.data
    from apps.sales.serializers import RevisionSerializer

    try:
        revision = Revision.objects.get(id=value["revision"])
        if revision.deliverable.revisions_hidden:
            raise Revision.DoesNotExist
        revision = RevisionSerializer(instance=revision, context=context).data
    except Revision.DoesNotExist:
        revision = None
    return {
        "revision": revision,
        "display": revision or notification_display(obj.target, context=context),
    }


def revision_approved(obj, context):
    from apps.sales.serializers import DeliverableSerializer, RevisionSerializer

    return {
        "deliverable": DeliverableSerializer(
            instance=obj.target.deliverable, context=context
        ).data,
        "display": RevisionSerializer(instance=obj.target, context=context).data,
    }


def reference_uploaded(obj, context):
    value = obj.data
    from apps.sales.models import Reference
    from apps.sales.serializers import ReferenceSerializer

    try:
        reference = Reference.objects.get(id=value["reference"])
        reference = ReferenceSerializer(instance=reference, context=context).data
    except Revision.DoesNotExist:
        reference = None
    if context["request"].user == obj.target.order.buyer:
        buyer = True
    else:
        buyer = False
    return {
        "reference": reference,
        "display": reference or notification_display(obj.target, context=context),
        "buyer": buyer,
    }


def order_update(obj, context):
    return {"display": notification_display(obj.target, context=context)}


def comment_made(obj, context):
    comment = (
        Comment.objects.filter(id__in=obj.data["comments"]).order_by("-id").first()
    )
    is_thread = isinstance(comment.content_object, Comment)
    subject = ""
    display = notification_display(comment.top, context)
    if isinstance(comment.top, Conversation):
        subject = f"New message from {comment.user.username}"
        display = notification_display(comment.user, context)
    commenters = (
        Comment.objects.filter(id__in=obj.data["comments"] + obj.data["subcomments"])
        .exclude(user=context["request"].user)
        .order_by("user__username")
        .distinct("user__username")
    )

    if commenters.count() > 3:
        additional = commenters.count() - 3
    else:
        additional = 0
    context = dict(**context)
    # This data not to be trusted, as it is user provided.
    context["extra_data"] = comment.extra_data
    context["view_name"] = "DeliverableOverview"
    link = get_link(comment.top, context)
    if link:
        if "query" in link:
            link["query"]["commentId"] = comment.id
        else:
            link["query"] = {"commentId": comment.id}
    return {
        "top": notification_serialize(comment.top, context),
        "commenters": list(commenters[:3].values_list("user__username", flat=True)),
        "additional": additional,
        "is_thread": is_thread,
        "subject": subject,
        "most_recent_comment": notification_serialize(comment, context),
        "display": display,
        "link": link,
        "name": get_display_name(comment.top, context),
    }


def submission_shared(obj, context):
    try:
        submission = Submission.objects.get(id=obj.data["submission"])
    except Submission.DoesNotExist:
        submission = None

    try:
        user = User.objects.get(id=obj.data["user"])
    except User.DoesNotExist:
        user = None

    serialized = notification_display(submission, context)

    return {
        "submission": serialized,
        "display": serialized,
        "user": notification_display(user, context),
    }


def char_shared(obj, context):
    try:
        character = Character.objects.get(id=obj.data["character"])
    except Character.DoesNotExist:
        character = None

    try:
        user = User.objects.get(id=obj.data["user"])
    except User.DoesNotExist:
        user = None

    return {
        "character": notification_display(character, context),
        "display": notification_display(character.primary_submission, context),
        "user": notification_display(user, context),
    }


def new_char(obj, context):
    try:
        character = Character.objects.get(id=obj.data["character"])
    except Character.DoesNotExist:
        character = None

    return {
        "character": notification_display(character, context),
        "display": notification_display(character.primary_submission, context),
    }


def new_product(obj, context):
    from apps.sales.serializers import ProductSerializer

    try:
        product = Product.objects.get(id=obj.data["product"])
    except Product.DoesNotExist:
        product = None

    serialized = ProductSerializer(instance=product, context=context).data

    return {
        "product": serialized,
        "display": notification_display(product, context),
    }


def streaming(obj, context):
    # Maybe some day we'll update all the entries in the DB for this, but for now,
    # 'order' actually points to Deliverable.
    deliverable = Deliverable.objects.get(id=obj.data["order"])
    user_data = notification_display(deliverable.order.seller, context)
    # Don't want to use full order here, would have too much info sent.
    return {
        "stream_link": deliverable.stream_link,
        "seller": user_data,
        "display": user_data,
    }


def waitlist_updated(obj, context):
    return {
        "display": notification_display(obj.target, context),
        "count": obj.target.sales.filter(deliverables__status=WAITING)
        .distinct()
        .count(),
    }


def new_journal(obj, context):
    journal = Journal.objects.get(id=obj.data["journal"])
    return {
        "display": notification_display(journal.user, context),
        "journal": notification_serialize(journal, context),
    }


def favorite(obj, context):
    user = User.objects.get(id=obj.data["user_id"])
    return {
        "display": notification_display(obj.target, context),
        "user": notification_serialize(user, context),
    }


def submission_artist_tag(obj, context):
    submission = Submission.objects.get(id=obj.target.id)
    return {
        "user": notification_display(User.objects.get(id=obj.data["user"]), context),
        "artist": notification_display(
            User.objects.get(id=obj.data["artist"]), context
        ),
        "display": notification_display(submission, context),
    }


def commissions_open(obj, context):
    return {
        "display": notification_display(obj.target, context),
    }


NOTIFICATION_TYPE_MAP = {
    CHAR_TAG: char_tag,
    ORDER_UPDATE: order_update,
    SALE_UPDATE: order_update,
    SUBMISSION_CHAR_TAG: submission_char_tag,
    REVISION_UPLOADED: revision_uploaded,
    REFERENCE_UPLOADED: reference_uploaded,
    COMMENT: comment_made,
    SUBMISSION_SHARED: submission_shared,
    CHAR_SHARED: char_shared,
    NEW_CHARACTER: new_char,
    NEW_PRODUCT: new_product,
    STREAMING: streaming,
    NEW_JOURNAL: new_journal,
    FAVORITE: favorite,
    DISPUTE: order_update,
    SUBMISSION_ARTIST_TAG: submission_artist_tag,
    WAITLIST_UPDATED: waitlist_updated,
    TIP_RECEIVED: order_update,
    REVISION_APPROVED: revision_approved,
    COMMISSIONS_OPEN: commissions_open,
}


class EventSerializer(serializers.ModelSerializer):
    target = EventTargetRelatedField(read_only=True)
    data = SerializerMethodField(read_only=True)
    recalled = BooleanField()

    def get_data(self, obj):
        return NOTIFICATION_TYPE_MAP.get(obj.type, lambda x, _: x.data)(
            obj, self.context
        )

    class Meta:
        model = Event
        fields = ("id", "type", "data", "date", "target", "recalled")
        read_only_fields = fields


@register_serializer
class NotificationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("event", "read", "id")
        read_only_fields = ("event", "id")


class BulkNotificationSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ("event", "read", "id")
        read_only_fields = ("event", "id")
        list_serializer_class = BulkListSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


# noinspection PyAbstractClass
class TagListField(serializers.ListSerializer):
    save_related = True

    def __init__(self, *args, **kwargs):
        kwargs["child"] = serializers.SlugField()
        self.min = kwargs.pop("min", 5)
        self.hints = kwargs.pop(
            "hints",
            (
                "sex/gender (required, if character)",
                "species (ditto)",
                "kinks/fetishes (ditto)",
                "genre",
                "subject matter",
                "focus of the piece",
                "location",
                "pose/position",
                "art style",
                "clothing/accessories",
                "relationships depicted",
            ),
        )
        super().__init__(*args, **kwargs)

    def get_value(self, dictionary):
        if hasattr(dictionary, "getlist"):
            result = dictionary.getlist(self.field_name, empty)
        else:
            result = dictionary.get(self.field_name, empty)
        return result

    def to_representation(self, value):
        if hasattr(value, "all"):
            return list(value.all().values_list("name", flat=True))
        return [getattr(val, "name", str(val)) for val in value]

    def to_internal_value(self, value):
        return [getattr(val, "name", str(val)) for val in value]

    def run_validation(self, data=empty):
        super().run_validation(data=data)
        if data is empty:
            return empty
        data = tag_list_cleaner(data)
        if len(data) < self.min:
            message = (
                f"You must specify at least {self.min} tags. Think about the "
                f"following: " + ", ".join(self.hints)
            )
            raise ValidationError(message)
        add_check(self.parent.instance, self.field_name, replace=True)
        return data

    def mod_instance(self, instance, value):
        set_tags(instance, self.field_name, value)


class UserRelationField(serializers.Field):
    save_related = True

    def get_initial(self):
        return self.to_representation(None)

    def to_representation(self, _instance):
        request = self.context.get("request", None)
        if not request:
            return None
        if not request.user.is_authenticated:
            return None
        if not (self.parent.instance and self.parent.instance.id):
            return None
        return (
            getattr(request.user, self.field_name)
            .filter(id=self.parent.instance.id)
            .exists()
        )

    def to_internal_value(self, data):
        return bool(data)

    def mod_instance(self, instance, value):
        request = self.context.get("request", None)
        if value:
            getattr(request.user, self.field_name).add(instance)
        else:
            getattr(request.user, self.field_name).remove(instance)


# noinspection PyUnresolvedReferences
class RelatedSetMixin:
    def get_value(self, dictionary):
        # We want to be able to take either a set of integers or a set of dictionaries
        # that contain an id field.
        value = super().get_value(dictionary)
        if value is empty:
            return empty
        if not isinstance(value, list):
            # Let it fail elsewhere.
            return value
        result = []
        for item in value:
            if isinstance(item, int):
                result.append(item)
            if isinstance(item, dict):
                # If there's no ID field, it'll fail elsewhere.
                result.append(item.get("id", item))
        return result

    def get_initial(self):
        if hasattr(self, "initial_data"):
            return self.initial_data
        if not self.parent.instance:
            return []
        return getattr(self.parent.instance, self.field_name).values_list(
            "id", flat=True
        )

    def to_internal_value(self, data):
        return data

    def mod_instance(self, instance, value):
        if self.model:
            base_kwargs = {self.back_name: instance}
            for user_id in value:
                self.model.objects.create(user_id=user_id, **base_kwargs)
            to_remove = self.model.objects.filter(**base_kwargs).exclude(
                user_id__in=value
            )
            for instance in to_remove:
                instance.delete()
        else:
            getattr(instance, self.field_name).set(value)


# noinspection PyAbstractClass
class UserListField(RelatedSetMixin, serializers.ListSerializer):
    save_related = True

    def __init__(
        self,
        *args,
        block_check=True,
        tag_check=False,
        back_name=None,
        model=None,
        add_self=False,
        **kwargs,
    ):
        kwargs["child"] = serializers.IntegerField()
        self.block_check = block_check
        self.tag_check = tag_check
        self.back_name = back_name
        self.model = model
        self.add_self = add_self
        if back_name is None and model is not None:
            raise TypeError(
                "You must specify a 'back_name' for the through table the model the "
                "users will be tied to.",
            )
        super().__init__(*args, **kwargs)

    def get_initial(self):
        if hasattr(self, "initial_data"):
            return self.initial_data
        if not self.parent.instance:
            return []
        return getattr(self.parent.instance, self.field_name).values_list(
            "id", flat=True
        )

    def to_representation(self, user_manager):
        return RelatedUserSerializer(many=True, instance=user_manager.all()).data

    def run_validation(self, data: Union[empty, List[int]] = empty):
        from apps.profiles.utils import available_users

        super().run_validation(data=data)
        if data is empty:
            return empty
        if self.add_self:
            data.append(self.context.get("request").user.id)
        data = list(set(data))
        if self.block_check:
            qs = available_users(self.context.get("request").user).filter(id__in=data)
        else:
            qs = User.objects.filter(id__in=data)
        if self.tag_check:
            qs = qs.filter(Q(taggable=True) | Q(id=self.context.get("request").user.id))

        data = qs.values_list("id", flat=True)
        if not len(data) >= (self.min_length or 0):
            error = f"Minimum number of users is {self.min_length}"
            if self.add_self:
                error += ", including yourself."
            else:
                error += "."
            raise ValidationError(error)
        add_check(self.parent.instance, self.field_name, *data, replace=True)
        return data


class CharacterListField(RelatedSetMixin, serializers.ListSerializer):
    def __init__(
        self,
        *args,
        tag_check=False,
        back_name=None,
        model=None,
        add_self=False,
        **kwargs,
    ):
        kwargs["child"] = serializers.IntegerField()
        self.tag_check = tag_check
        self.back_name = back_name
        self.model = model
        self.add_self = add_self
        if back_name is None and model is not None:
            raise TypeError(
                "You must specify a 'back_name' for the through table to the model the "
                "users will be tied to.",
            )
        super().__init__(*args, **kwargs)

    def to_representation(self, character_manager):
        from apps.profiles.serializers import CharacterSerializer

        return CharacterSerializer(
            many=True, instance=character_manager.all(), context=self.context
        ).data

    def run_validation(self, data: Union[empty, List[int]] = empty):
        from apps.profiles.utils import available_chars

        super().run_validation(data=data)
        if data is empty:
            return empty
        data = list(set(data))
        qs = available_chars(
            self.context.get("request").user,
            tagging=self.tag_check,
        ).filter(id__in=data)
        data = qs.values_list("id", flat=True)
        add_check(self.parent.instance, self.field_name, *data, replace=True)
        return data


@register_serializer
class UserInfoSerializer(RelatedAtomicMixin, serializers.ModelSerializer):
    watching = UserRelationField(required=False)
    blocking = UserRelationField(required=False)
    stars = serializers.FloatField(required=False, read_only=True)
    service_plan = serializers.SerializerMethodField()
    international = serializers.SerializerMethodField()

    def get_international(self, obj):
        from apps.sales.models import StripeAccount

        return StripeAccount.objects.filter(
            user=obj, country=settings.SOURCE_COUNTRY
        ).exists()

    def get_service_plan(self, obj):
        return obj.service_plan.name

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "avatar_url",
            "biography",
            "favorites_hidden",
            "watching",
            "blocking",
            "stars",
            "is_staff",
            "is_superuser",
            "guest",
            "artist_mode",
            "hits",
            "watches",
            "rating_count",
            "service_plan",
            "international",
        )
        read_only_fields = [
            field for field in fields if field not in ["watching", "blocking"]
        ]


class IdWritable:
    def to_internal_value(self, data):
        if not data:
            return None
        if isinstance(data, dict):
            return super().to_internal_value(data)
        if not self.parent:
            return data
        return self.Meta.model.objects.filter(id=data).first()


class MoneyToString(serializers.FloatField):
    """
    String values are unable to be misinterpreted by approximations and can be turned
    into fixed point values on the other end.

    TODO: Make this properly currency aware.
    """

    def to_representation(self, value):
        if isinstance(value, Money):
            value = value.amount
        return str(Decimal(value).quantize(Decimal("0.00")))

    def to_internal_value(self, data):
        return Money(data, settings.DEFAULT_CURRENCY)


class CookieConsent(serializers.Serializer):
    first_party_analytics = serializers.BooleanField()
    third_party_analytics = serializers.BooleanField()


class EmailPreferenceField(serializers.BooleanField):
    save_related = True

    def __init__(
        self,
        *args,
        instance,
        **kwargs,
    ):
        self.instance = instance
        super().__init__(*args, **kwargs)

    def get_attribute(self, instance):
        return self.instance.enabled

    def to_representation(self, value):
        return value

    def mod_instance(self, instance, value):
        self.instance.enabled = value
        self.instance.save()


class AssetSerializer(serializers.ModelSerializer):
    uploaded_by = RelatedUserSerializer()

    class Meta:
        model = Asset
        fields = ("id", "hash", "created_on", "uploaded_by", "file")
        read_only_fields = fields
