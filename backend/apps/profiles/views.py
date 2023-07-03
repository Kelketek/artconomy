import logging
import uuid
from datetime import date
from functools import lru_cache
from textwrap import shorten
from typing import Dict

from apps.lib.abstract_models import GENERAL
from apps.lib.models import (
    ARTIST_TAG,
    CHAR_SHARED,
    CHAR_TAG,
    COMMENT,
    FAVORITE,
    ORDER_NOTIFICATION_TYPES,
    ORDER_UPDATE,
    REFERENCE_UPLOADED,
    RENEWAL_FAILURE,
    RENEWAL_FIXED,
    REVISION_APPROVED,
    REVISION_UPLOADED,
    SALE_UPDATE,
    SUBMISSION_ARTIST_TAG,
    SUBMISSION_CHAR_TAG,
    SUBMISSION_SHARED,
    SUBSCRIPTION_DEACTIVATED,
    Comment,
    EmailPreference,
    Notification,
    Subscription,
    Tag,
)
from apps.lib.permissions import (
    All,
    Any,
    BlockedCheckPermission,
    IsAnonymous,
    IsMethod,
    IsSafeMethod,
)
from apps.lib.serializers import (
    BulkNotificationSerializer,
    NotificationSerializer,
    RelatedUserSerializer,
    UserInfoSerializer,
)
from apps.lib.utils import (
    add_check,
    count_hit,
    demark,
    notify,
    preview_rating,
    recall_notification,
)
from apps.lib.views import BasePreview, PositionShift
from apps.profiles.models import (
    ArtistProfile,
    ArtistTag,
    Attribute,
    Character,
    Conversation,
    ConversationParticipant,
    Favorite,
    Journal,
    RefColor,
    Submission,
    User,
    trigger_reconnect,
)
from apps.profiles.permissions import (
    AccountAge,
    AccountCurrentPermission,
    ColorControls,
    ColorLimit,
    IsRegistered,
    IsSubject,
    IsUser,
    MessageReadPermission,
    ObjectControls,
    SharedWith,
    SubmissionControls,
    SubmissionTagPermission,
    SubmissionViewPermission,
    UserControls,
    ViewFavorites,
)
from apps.profiles.serializers import (
    ArtistProfileSerializer,
    ArtistTagSerializer,
    AttributeListSerializer,
    AttributeSerializer,
    CharacterManagementSerializer,
    CharacterSerializer,
    CharacterSharedSerializer,
    ConversationManagementSerializer,
    ConversationSerializer,
    CredentialsSerializer,
    DeleteUserSerializer,
    EmailPreferencesSerializer,
    EmailValidationSerializer,
    FavoriteSerializer,
    JournalSerializer,
    PasswordResetSerializer,
    PasswordValidationSerializer,
    RefColorSerializer,
    ReferralStatsSerializer,
    RegisterSerializer,
    SessionSettingsSerializer,
    SubmissionArtistTagSerializer,
    SubmissionCharacterTagSerializer,
    SubmissionManagementSerializer,
    SubmissionSerializer,
    SubmissionSharedSerializer,
    TelegramDeviceSerializer,
    TwoFactorTimerSerializer,
    UsernameValidationSerializer,
    UserSerializer,
)
from apps.profiles.tasks import drip_subscribe, mailchimp_subscribe
from apps.profiles.utils import (
    UserClearException,
    available_chars,
    available_submissions,
    char_ordering,
    clear_user,
    empty_user,
)
from apps.sales.models import Deliverable, Order, Reference, Revision
from apps.sales.serializers import SearchQuerySerializer
from apps.sales.tasks import withdraw_all
from apps.sales.utils import claim_order_by_token
from apps.tg_bot.models import TelegramDevice
from avatar.models import Avatar
from avatar.signals import avatar_updated
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Case, Count, F, IntegerField, Q, QuerySet, Subquery, When
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_otp import devices_for_user
from django_otp import login as otp_login
from django_otp import match_token, user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_bulk import BulkUpdateAPIView
from short_stuff import unslugify
from shortcuts import gen_textifier, make_url

logger = logging.getLogger(__name__)


def user_submissions(user: User, request, is_artist: bool):
    qs = available_submissions(
        request,
        request.user,
        show_all=True,
    )
    if is_artist:
        qs = qs.filter(artists=user, artisttag__hidden=False)
    else:
        qs = qs.filter(owner=user).exclude(artists=user)
    return qs


def character_submissions(char: Character, request, show_all=False):
    qs = available_submissions(request, request.user, show_all=show_all).filter(
        characters=char
    )
    return qs.order_by("-created_on")


class Register(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and self.request.user.guest:
            serializer.instance = self.request.user
        instance = serializer.save(guest=False, guest_email="")
        instance.set_password(instance.password)
        # Guests may have historical comments to be concerned with.
        instance.notification_set.all().update(read=True)
        # noinspection SpellCheckingInspection
        instance.offered_mailchimp = True
        add_to_newsletter = serializer.validated_data.get("mail")
        instance.rating = self.request.rating
        instance.sfw_mode = self.request.sfw_mode
        instance.birthday = self.request.birthday

        referrer = self.request.META.get("HTTP_X_REFERRED_BY", None)
        if referrer:
            instance.referred_by = User.objects.filter(username=referrer).first()
        # Specific fields here since other background operations may be happening in the
        # interim. Most relevant during dev since celery is always eager and doesn't
        # refresh the current object.
        instance.save(
            update_fields=[
                "offered_mailchimp",
                "rating",
                "sfw_mode",
                "birthday",
                "referred_by",
                "password",
            ]
        )
        instance.artist_profile = ArtistProfile()
        instance.artist_profile.save()
        if add_to_newsletter:
            mailchimp_subscribe.delay(instance.id)
            drip_subscribe.delay(instance.id)
        login(self.request, instance)
        order_claim = serializer.validated_data.get("order_claim", None)
        claim_order_by_token(order_claim, instance, force=True)

    def get_serializer(self, instance=None, data=None, many=False, partial=False):
        return self.serializer_class(
            instance=instance,
            data=data,
            many=many,
            partial=partial,
            context=self.get_serializer_context(),
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = UserSerializer(
            instance=serializer.instance, context=self.get_serializer_context()
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class ArtistProfileSettings(RetrieveUpdateAPIView):
    serializer_class = ArtistProfileSerializer
    permission_classes = [
        Any(
            All(UserControls, IsRegistered),
            IsSafeMethod,
        )
    ]

    @lru_cache()
    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"], guest=False)
        self.check_object_permissions(self.request, user)
        return user.artist_profile

    def patch(self, *args, **kwargs):
        return self.base_update("patch", *args, **kwargs)

    def base_update(self, method, *args, **kwargs):
        artist_profile = self.get_object()
        auto_withdraw = artist_profile.auto_withdraw
        self.check_object_permissions(self.request, artist_profile)
        response = getattr(super(), method)(*args, **kwargs)
        if not auto_withdraw and artist_profile.auto_withdraw:
            withdraw_all.apply_async((artist_profile.user_id,), countdown=10)
        return response

    def put(self, *args, **kwargs):
        return self.base_update("put", *args, **kwargs)

    def get(self, *args, **kwargs):
        profile = self.get_object()
        self.check_object_permissions(self.request, profile)
        count_hit(self.request, profile.user)
        return super().get(*args, **kwargs)


class CredentialsAPI(GenericAPIView):
    serializer_class = CredentialsSerializer
    permission_classes = [UserControls]

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user

    def post(self, request, **_kwargs):
        from apps.profiles.tasks import create_or_update_stripe_user

        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if request.user == serializer.instance:
            # make sure the user stays logged in
            update_session_auth_hash(request, instance)
        create_or_update_stripe_user.delay(instance.id, force=True)
        return Response(
            status=status.HTTP_200_OK,
            data=UserSerializer(
                instance=serializer.instance, context=self.get_serializer_context()
            ).data,
        )


class TOTPDeviceList(ListCreateAPIView):
    permission_classes = [IsUser]
    serializer_class = TwoFactorTimerSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user.totpdevice_set.all().order_by("-id")

    def perform_create(self, serializer):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return serializer.save(user=user, confirmed=False)


class TOTPDeviceManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsUser]
    serializer_class = TwoFactorTimerSerializer

    def get_object(self):
        device = get_object_or_404(
            TOTPDevice,
            user__username=self.kwargs["username"],
            id=self.kwargs["totp_id"],
        )
        self.check_object_permissions(self.request, device.user)
        return device


class Telegram2FA(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsUser]
    serializer_class = TelegramDeviceSerializer

    def get_object(self):
        return get_object_or_404(TelegramDevice, user__username=self.kwargs["username"])

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(request, user)
        return super().get(request, *args, **kwargs)

    # noinspection PyUnusedLocal,PyMethodOverriding
    def put(self, request, username):
        user = get_object_or_404(User, username=self.kwargs["username"])
        device = TelegramDevice.objects.get_or_create(user=user)
        return Response(
            status=status.HTTP_201_CREATED,
            data=self.get_serializer(instance=device).data,
        )

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(request, user)
        return super().delete(request, *args, **kwargs)

    # noinspection PyUnusedLocal
    def post(self, request, username):
        device = self.get_object()
        device.generate_challenge()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CharacterListAPI(ListCreateAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        if self.request.user.is_staff:
            requester = user
        else:
            requester = self.request.user
        self_search = requester == user
        qs = available_chars(
            requester, self_search=self_search, sfw=not self.request.rating
        ).filter(user=user)
        qs = qs.order_by("created_on")
        return qs

    def perform_create(self, serializer):
        user = get_object_or_404(User, username=self.kwargs["username"])
        if not (self.request.user.is_staff or self.request.user == user):
            raise PermissionDenied(
                "You do not have permission to create characters for that user."
            )
        if user.characters.all().count() >= settings.MAX_CHARACTER_COUNT:
            raise PermissionDenied(
                "You have reached your maximum number of characters. Please contact "
                "support if you believe your quota should be increased."
            )
        if user.characters.filter(name=serializer.validated_data["name"]):
            raise ValidationError(
                {"name": ["A character with this name already exists."]}
            )
        target = serializer.save(user=user)

        return target


class CharacterSubmissions(ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [Any(SharedWith, ObjectControls)]

    def get_queryset(self):
        char = get_object_or_404(
            Character,
            user__username=self.kwargs["username"],
            name=self.kwargs["character"],
        )
        self.check_object_permissions(self.request, char)
        return character_submissions(char, self.request)


class CharacterManager(RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterManagementSerializer
    permission_classes = [
        Any(
            All(IsSafeMethod, SharedWith),
            All(IsRegistered, SharedWith),
            All(IsRegistered, ObjectControls),
        )
    ]

    def get_object(self):
        character = get_object_or_404(
            Character,
            user__username=self.kwargs["username"],
            name=self.kwargs["character"],
        )
        self.check_object_permissions(self.request, character)
        return character


class CharacterById(RetrieveAPIView):
    serializer_class = CharacterManagementSerializer
    permission_classes = [
        Any(
            All(IsRegistered, SharedWith),
            ObjectControls,
        )
    ]

    def get_object(self):
        character = get_object_or_404(Character, id=self.kwargs["character_id"])
        self.check_object_permissions(self.request, character)
        return character


class SubmissionManager(RetrieveUpdateDestroyAPIView):
    serializer_class = SubmissionManagementSerializer
    permission_classes = [
        Any(
            All(
                Any(IsSafeMethod, All(IsMethod("PATCH"), IsRegistered)),
                SubmissionViewPermission,
            ),
            SubmissionControls,
        )
    ]
    cached_submission = None

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super(SubmissionManager, self).patch(request, *args, **kwargs)

    @lru_cache()
    def get_object(self):
        submission = get_object_or_404(
            Submission,
            id=self.kwargs["submission_id"],
        )
        hit_count = HitCount.objects.get_for_object(submission)
        HitCountMixin.hit_count(self.request, hit_count)
        return submission

    def get(self, request, *args, **kwargs):
        submission = self.get_object()
        self.check_object_permissions(request, submission)
        return super().get(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        submission = self.get_object()
        self.check_object_permissions(request, submission)
        submission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetAvatar(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [UserControls]

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        self.check_object_permissions(request, user)
        file_obj = request.data.get("files[]")
        file_obj.name = (
            file_obj.name.rsplit(".")[0][:50] + "." + file_obj.name.rsplit(".")[1][:4]
        )
        if not file_obj:
            raise ValidationError({"files[]": ["This field is required."]})
        avatar = Avatar(user=request.user, primary=True, avatar=file_obj)
        avatar.save()
        avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
        Avatar.objects.filter(user=request.user).exclude(id=avatar.id).delete()
        user.avatar_url = avatar.get_absolute_url()
        user.save(update_fields=["avatar_url"])
        return Response(
            data=UserSerializer(instance=user, context={"request": request}).data
        )


class UserInfo(APIView):
    # Serializers are the primary permission barrier here.
    permission_classes = [
        Any(
            IsSafeMethod,
            IsRegistered,
            All(IsAuthenticated, UserControls),
        )
    ]

    def get_serializer(self, user):
        if self.request.user.is_staff:
            return UserSerializer
        if self.request.user == user:
            return UserSerializer
        else:
            return UserInfoSerializer

    def get_object(self):
        if self.request.user.is_staff:
            extra = Q()
        else:
            extra = Q(is_active=True)
        user = get_object_or_404(User, extra, username=self.kwargs.get("username"))
        return user

    def get_serializer_context(self):
        return {"request": self.request}

    # noinspection PyUnusedLocal
    def get(self, request, **kwargs):
        user = self.get_object()
        if user:
            serializer_class = self.get_serializer(user)
            serializer = serializer_class(
                instance=user, context=self.get_serializer_context()
            )
            data = serializer.data
            if not request.user.is_registered:
                patch_data = empty_user(user=request.user, session=request.session)
                del patch_data["username"]
                data = {**data, **patch_data}
        else:
            data = empty_user(user=request.user, session=request.session)
        return Response(data=data, status=status.HTTP_200_OK)

    # noinspection PyUnusedLocal
    def patch(self, request, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        if user.is_authenticated and not user.is_registered:
            return CurrentUserInfo.patch(self, request, **kwargs)
        serializer_class = self.get_serializer(user)
        serializer = serializer_class(
            instance=user, data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserInfoByID(UserInfo):
    def get_object(self):
        return get_object_or_404(User, id=self.kwargs.get("user_id"), is_active=True)


class CurrentUserInfo(UserInfo):
    permission_classes = []

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, **kwargs)
        return Response(
            status=status.HTTP_200_OK,
            data=empty_user(session=request.session, user=request.user),
        )

    def patch(self, request, **kwargs):
        if request.user.is_registered:
            return super().patch(request, **kwargs)
        base_settings = empty_user(user=request.user, session=request.session)
        serializer = SessionSettingsSerializer(data={**base_settings, **request.data})
        serializer.is_valid(raise_exception=True)
        request.session.update(serializer.data)
        sfw_mode = serializer.data["sfw_mode"]
        request.max_rating = GENERAL if sfw_mode else serializer.data["rating"]
        request.birthday = serializer.data["birthday"] and date.fromisoformat(
            serializer.data["birthday"]
        )
        request.rating = serializer.data["rating"]
        request.sfw_mode = sfw_mode
        request.session.save()
        data = empty_user(session=request.session, user=request.user)
        if request.user.is_authenticated:
            base_data = UserSerializer(
                instance=request.user, context=self.get_serializer_context()
            ).data
            del data["username"]
            data = {**base_data, **data}
        return Response(status=status.HTTP_200_OK, data=data)

    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user
        else:
            return

    def get_serializer(self, user):
        return UserSerializer


class CharacterSearch(ListAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        tagging = self.request.GET.get("tagging", False)
        try:
            commissions = json.loads(
                self.request.query_params.get("new_order", "false")
            )
        except ValueError:
            raise ValidationError({"errors": ["New Order must be a boolean."]})

        # If staffer, allow search on behalf of user.
        if self.request.user.is_staff:
            user = get_object_or_404(
                User, id=self.request.GET.get("user", self.request.user.id)
            )
        else:
            user = self.request.user
        if self.request.user.is_authenticated:
            base_query = available_chars(
                user,
                query=query,
                commissions=commissions,
                tagging=tagging,
                sfw=not self.request.rating,
            )
            if tagging:
                return char_ordering(base_query, user, query=query)
            return base_query.order_by("-created_on")
        q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
        if self.request.rating:
            nsfw_filter = Q()
        else:
            nsfw_filter = Q(nsfw=False)
        return (
            Character.objects.filter(q)
            .filter(nsfw_filter)
            .exclude(private=True)
            .exclude(taggable=False)
            .distinct()
            .order_by(
                "-created_on",
            )
        )


class UserSearch(ListAPIView):
    serializer_class = RelatedUserSerializer

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        tagging = self.request.GET.get("tagging", False)
        if not query:
            return User.objects.none()
        qs = User.objects.filter(
            username__startswith=query, is_active=True, guest=False
        )
        if tagging and self.request.user.is_authenticated:
            qs = qs.filter(Q(taggable=True) | Q(id=self.request.user.id))
        elif tagging:
            qs = qs.filter(taggable=True)
        return qs.order_by("username")


class TagSearch(APIView):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return Response(status=status.HTTP_200_OK, data=[])
        return Response(
            status=status.HTTP_200_OK,
            data=Tag.objects.filter(name__istartswith=query)[:20].values_list(
                "name", flat=True
            ),
        )


class SubmissionSearch(ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        search_serializer = SearchQuerySerializer(data=self.request.GET)
        search_serializer.is_valid(raise_exception=True)
        qs = available_submissions(self.request, self.request.user)
        query = self.request.GET.get("q", "")
        query = query.split()
        for q in query:
            if q.startswith("!"):
                qs = qs.exclude(tags__name__iexact=q[1:])
            else:
                qs = qs.filter(tags__name__iexact=q)
        if (
            search_serializer.validated_data.get("watch_list", False)
            and self.request.user.is_authenticated
        ):
            qs = qs.filter(artists__in=self.request.user.watching.all())
        if search_serializer.validated_data.get("content_ratings", False):
            qs = qs.filter(
                rating__in=search_serializer.validated_data["content_ratings"]
            )
        if search_serializer.validated_data.get("commissions", False):
            qs = qs.filter(deliverable__isnull=False)
            qs = (
                qs.annotate(
                    artist_copy=Case(
                        When(artists=F("owner"), then=0),
                        default=1,
                        output_field=IntegerField(),
                    )
                )
                .order_by("file", "artist_copy")
                .distinct("file")
            )
            qs = Submission.objects.filter(id__in=Subquery(qs.values("pk")))
        return qs.order_by("-created_on").distinct()

    def get(self, *args, **kwargs):
        query = self.request.GET.get("q", "")
        query = query.split()
        if len(query) > 10:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "You cannot use more than 10 search terms at once."},
            )
        return super().get(*args, **kwargs)


class SubmissionArtistList(ListCreateAPIView):
    permission_classes = [
        SubmissionViewPermission,
        Any(
            IsSafeMethod,
            All(
                IsMethod("POST"),
                IsRegistered,
                SubmissionTagPermission,
                BlockedCheckPermission("owner"),
            ),
        ),
    ]
    serializer_class = SubmissionArtistTagSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs) -> Response:
        target = self.get_object()
        self.check_object_permissions(self.request, target)
        return super(SubmissionArtistList, self).create(request, *args, **kwargs)

    def perform_create(self, serializer) -> ArtistTag:
        submission = self.get_object()
        try:
            add_check(submission, "artists", serializer.validated_data["user_id"])
        except ValidationError as err:
            raise PermissionDenied("".join(err.detail))
        relation, _ = ArtistTag.objects.get_or_create(
            submission=self.get_object(),
            user_id=serializer.validated_data["user_id"],
        )
        if submission.owner != self.request.user:
            notify(
                ARTIST_TAG,
                relation.user,
                data={"user": self.request.user.id, "submission": submission.id},
                unique_data=True,
                mark_unread=True,
            )
        if self.request.user != submission.owner:
            notify(
                SUBMISSION_ARTIST_TAG,
                submission,
                data={"user": self.request.user.id, "artist": relation.user.id},
                unique_data=True,
                exclude=[self.request.user],
            )
        Subscription.objects.bulk_create(
            [
                Subscription(
                    subscriber=relation.user,
                    content_type=ContentType.objects.get_for_model(Submission),
                    object_id=submission.id,
                    type=sub_type,
                )
                for sub_type in [FAVORITE, COMMENT]
            ],
            ignore_conflicts=True,
        )
        serializer.instance = relation
        return relation

    def get_queryset(self) -> QuerySet:
        return ArtistTag.objects.filter(submission=self.get_object())

    @lru_cache()
    def get_object(self) -> Submission:
        return get_object_or_404(Submission, id=self.kwargs["submission_id"])


class SubmissionCharacterList(ListCreateAPIView):
    permission_classes = [
        SubmissionViewPermission,
        Any(
            IsSafeMethod,
            All(
                IsMethod("POST"),
                IsRegistered,
                SubmissionTagPermission,
                BlockedCheckPermission("owner"),
            ),
        ),
    ]
    pagination_class = None
    serializer_class = SubmissionCharacterTagSerializer

    def create(self, request, *args, **kwargs) -> Response:
        target = self.get_object()
        self.check_object_permissions(self.request, target)
        return super(SubmissionCharacterList, self).create(request, *args, **kwargs)

    def perform_create(self, serializer) -> Submission.characters.through:
        submission = self.get_object()
        try:
            add_check(
                submission, "characters", serializer.validated_data["character_id"]
            )
        except ValidationError as err:
            raise PermissionDenied("".join(err.detail))
        relation, _ = Submission.characters.through.objects.get_or_create(
            submission=self.get_object(),
            character_id=serializer.validated_data["character_id"],
        )
        if relation.character.user != self.request.user:
            notify(
                CHAR_TAG,
                relation.character,
                data={"user": self.request.user.id, "submission": submission.id},
                unique_data=True,
                mark_unread=True,
            )
        if self.request.user != submission.owner:
            notify(
                SUBMISSION_CHAR_TAG,
                submission,
                data={"user": self.request.user.id, "character": relation.character.id},
                unique_data=True,
                exclude=[self.request.user],
            )
        serializer.instance = relation
        return relation

    def get_queryset(self) -> QuerySet:
        return Submission.characters.through.objects.filter(
            submission=self.get_object()
        )

    @lru_cache()
    def get_object(self) -> Submission:
        submission = get_object_or_404(Submission, id=self.kwargs["submission_id"])
        self.check_object_permissions(self.request, submission)
        return submission


class SubmissionArtistManager(DestroyAPIView):
    permission_classes = [IsRegistered, SubmissionTagPermission]
    serializer_class = RelatedUserSerializer

    def get_object(self) -> ArtistTag:
        return get_object_or_404(
            ArtistTag,
            id=self.kwargs["tag_id"],
            submission__id=self.kwargs["submission_id"],
        )

    def perform_destroy(self, instance: ArtistTag):
        recall_notification(
            ARTIST_TAG, instance.user, data={"submission": instance.submission.id}
        )
        recall_notification(
            SUBMISSION_ARTIST_TAG,
            instance.submission,
            data={"user": self.request.user.id, "artist": instance.user.id},
        )
        if instance.user != instance.submission.owner:
            Subscription.objects.filter(
                subscriber=instance.user,
                content_type=ContentType.objects.get_for_model(Submission),
                object_id=instance.submission.id,
                type__in=[FAVORITE, COMMENT],
            ).delete()
        instance.delete()

    def delete(self, *args, **kwargs) -> Response:
        relationship = self.get_object()
        self.check_object_permissions(self.request, relationship.submission)
        return super().delete(*args, **kwargs)


class SubmissionCharacterManager(DestroyAPIView):
    permission_classes = [IsRegistered, SubmissionTagPermission]
    serializer_class = CharacterSerializer

    def get_object(self) -> ArtistTag:
        return get_object_or_404(
            Submission.characters.through,
            id=self.kwargs["tag_id"],
            submission__id=self.kwargs["submission_id"],
        )

    def perform_destroy(self, instance: ArtistTag):
        recall_notification(
            CHAR_TAG, instance.character, data={"submission": instance.submission.id}
        )
        recall_notification(
            SUBMISSION_CHAR_TAG,
            instance.submission,
            data={"user": self.request.user.id, "character": instance.character.id},
        )
        instance.delete()

    def delete(self, *args, **kwargs) -> Response:
        relationship = self.get_object()
        self.check_object_permissions(self.request, relationship.submission)
        return super().delete(*args, **kwargs)


class AttributeList(ListCreateAPIView):
    permission_classes = [
        Any(All(IsSafeMethod, SharedWith), All(IsRegistered, ObjectControls))
    ]
    serializer_class = AttributeListSerializer
    pagination_class = None

    def get_character(self):
        character = get_object_or_404(
            Character,
            name=self.kwargs["character"],
            user__username=self.kwargs["username"],
        )
        self.check_object_permissions(self.request, character)
        return character

    def get_queryset(self):
        character = self.get_character()
        self.check_object_permissions(self.request, character)
        return character.attributes.all()

    def perform_create(self, serializer):
        character = self.get_character()
        if character.attributes.all().count() >= settings.MAX_ATTRS:
            raise PermissionDenied(
                "You may not have more than {} attributes on one character.".format(
                    settings.MAX_ATTRS
                )
            )
        with transaction.atomic():
            existing = (
                character.attributes.filter(
                    key__iexact=serializer.validated_data["key"],
                )
                .select_for_update()
                .first()
            )
            if existing:
                serializer.instance = existing
        serializer.save(character=character)


class AttributeManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsRegistered, ObjectControls]
    serializer_class = AttributeSerializer

    @lru_cache()
    def get_object(self):
        attr = get_object_or_404(
            Attribute,
            character__name=self.kwargs["character"],
            character__user__username=self.kwargs["username"],
            id=self.kwargs["attribute_id"],
        )
        self.check_object_permissions(self.request, attr.character)
        return attr

    def destroy(self, *args, **kwargs):
        instance = self.get_object()
        if instance.sticky:
            raise PermissionDenied("You may not remove sticky attributes.")
        return super().destroy(*args, **kwargs)


class UserSerializerView:
    def get_serializer(self, user):
        if self.request.user.is_staff:
            return UserSerializer
        if self.request.user == user:
            return UserSerializer
        else:
            return UserInfoSerializer


ORDER_COMMENT_TYPES_STORE = None


def order_comment_types():
    global ORDER_COMMENT_TYPES_STORE
    if ORDER_COMMENT_TYPES_STORE is not None:
        return ORDER_COMMENT_TYPES_STORE
    ORDER_COMMENT_TYPES_STORE = (
        ContentType.objects.get_for_model(Order),
        ContentType.objects.get_for_model(Reference),
        ContentType.objects.get_for_model(Revision),
        ContentType.objects.get_for_model(Deliverable),
    )
    return ORDER_COMMENT_TYPES_STORE


class UnreadNotifications(APIView):
    permission_classes = [IsRegistered]

    # noinspection PyUnusedLocal
    def get(self, request):
        return Response(
            status=200,
            data={
                "count": Notification.objects.filter(user=self.request.user, read=False)
                .exclude(event__recalled=True)
                .count(),
                "community_count": Notification.objects.filter(
                    user=self.request.user, read=False
                )
                .exclude(event__recalled=True)
                .exclude(event__type__in=ORDER_NOTIFICATION_TYPES)
                .exclude(
                    event__type=COMMENT, event__content_type__in=order_comment_types()
                )
                .count(),
                "sales_count": Notification.objects.filter(
                    user=self.request.user,
                    read=False,
                )
                .exclude(event__recalled=True)
                .filter(
                    Q(event__type__in=ORDER_NOTIFICATION_TYPES)
                    | Q(
                        event__type=COMMENT,
                        event__content_type__in=order_comment_types(),
                    )
                )
                .count(),
            },
        )


class CommunityNotificationsList(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsRegistered]

    def get_queryset(self):
        qs = (
            Notification.objects.filter(user=self.request.user)
            .exclude(event__recalled=True)
            .exclude(event__type__in=ORDER_NOTIFICATION_TYPES)
            .exclude(
                event__type=COMMENT,
                event__content_type__in=order_comment_types(),
            )
        )
        if self.request.GET.get("unread"):
            qs = qs.filter(read=False)
        return qs.prefetch_related("event").order_by("-event__date")


class SalesNotificationsList(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsRegistered]

    def get_queryset(self):
        qs = (
            Notification.objects.filter(user=self.request.user)
            .exclude(event__recalled=True)
            .filter(
                Q(event__type__in=ORDER_NOTIFICATION_TYPES)
                | Q(event__type=COMMENT, event__content_type__in=order_comment_types())
            )
        )
        if self.request.GET.get("unread"):
            qs = qs.filter(read=False)
        return qs.select_related("event").order_by("-event__date")


class RefColorList(ListCreateAPIView):
    serializer_class = RefColorSerializer
    permission_classes = [
        Any(All(IsSafeMethod, SharedWith), All(ColorControls, ColorLimit))
    ]
    pagination_class = None

    def get_queryset(self):
        character = get_object_or_404(
            Character,
            name=self.kwargs["character"],
            user__username=self.kwargs["username"],
        )
        self.check_object_permissions(self.request, character)
        return RefColor.objects.filter(
            character__name=self.kwargs["character"],
            character__user__username=self.kwargs["username"],
        )

    def perform_create(self, serializer):
        character = get_object_or_404(
            Character,
            name=self.kwargs["character"],
            user__username=self.kwargs["username"],
        )
        self.check_object_permissions(self.request, character)
        return serializer.save(character=character)


class RefColorManager(RetrieveUpdateDestroyAPIView):
    serializer_class = RefColorSerializer
    permission_classes = [ColorControls]

    def get_object(self):
        obj = get_object_or_404(RefColor, id=self.kwargs["ref_color_id"])
        self.check_object_permissions(self.request, obj)
        return obj


class MarkNotificationsRead(BulkUpdateAPIView):
    permission_classes = [IsRegistered]
    serializer_class = BulkNotificationSerializer
    queryset = Notification.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)


class WatchListSubmissions(ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsRegistered]

    def get_queryset(self):
        return (
            available_submissions(self.request, self.request.user)
            .filter(
                artists__in=self.request.user.watching.all(),
                show_all=True,
            )
            .order_by("-created_on")
        )


class RecentCommissions(ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        qs = available_submissions(self.request, self.request.user).filter(
            deliverable__isnull=False
        )
        qs = (
            qs.annotate(
                artist_copy=Case(
                    When(artists=F("owner"), then=0),
                    default=1,
                    output_field=IntegerField(),
                )
            )
            .order_by("file", "artist_copy")
            .distinct("file")
        )
        qs = Submission.objects.filter(id__in=Subquery(qs.values("pk")))
        return qs.order_by("-created_on")


class RecentSubmissions(ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return (
            available_submissions(self.request, self.request.user)
            .filter(deliverable__isnull=True)
            .exclude(owner__username__in=settings.COMMUNITY_ACCOUNT_NAMES)
            .order_by("-created_on")
        )


class RecentArt(ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return available_submissions(self.request, self.request.user).order_by(
            "-created_on"
        )


class NewCharacters(ListAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        return (
            available_chars(self.request.user, sfw=not self.request.rating)
            .filter(primary_submission__isnull=False)
            .order_by("-created_on")
        )


def handle_login(request, user, token):
    # If we have a User object, the details are correct.
    # If None (Python's way of representing the absence of a value), no user
    # with matching credentials was found.
    if not user:
        return "Either this account does not exist, or the password is incorrect.", ""
        # Is the account active? It could have been disabled.

    if not user.is_active:
        # An inactive account was used - no logging in!
        logout(request)
        return "Your account is disabled. Please contact support", ""

    # Last check-- does the user have 2FA?
    device = None
    if not token:
        for dev in devices_for_user(user):
            try:
                dev.generate_challenge()
            except Exception as err:
                # Sending this to both fields since it otherwise might not be visible.
                return str(err), str(err)

    if user_has_device(user):
        device = match_token(user, token)
        if not device:
            return (
                "",
                "That Verification code is either invalid or expired. Please try "
                "again. If you've lost your 2FA device, please contact "
                "support@artconomy.com",
            )

    # If the account is valid and active, we can log the user in.
    # We'll send the user to their account.
    login(request, user)
    if device:
        otp_login(request, device)
    return "", ""


@csrf_exempt
@api_view(["POST"])
def perform_login(request):
    """
    Handle post action
    """
    # Gather the username and password provided by the user.
    # This information is obtained from the login form.
    email = (
        str(request.data.get("email", request.POST.get("email", ""))).lower().strip()
    )
    password = request.data.get("password", request.POST.get("password", "")).strip()
    token = (
        request.data.get("token", request.POST.get("token", ""))
        .strip()
        .replace(" ", "")
    )
    order_claim = request.data.get(
        "order_claim", request.POST.get("order_claim", "")
    ).strip()
    # Use Django's machinery to attempt to see if the username/password
    # combination is valid - a User object is returned if it is.
    user = authenticate(email=email, password=password)
    password_error, token_error = handle_login(request, user, token)

    status_code = (
        status.HTTP_401_UNAUTHORIZED
        if (password_error or token_error)
        else status.HTTP_200_OK
    )
    data = {
        "email": [],
        "password": [password_error] if password_error else [],
        "token": [token_error] if token_error else [],
    }
    if status_code == status.HTTP_200_OK:
        if order_claim:
            claim_order_by_token(unslugify(order_claim), user)
        data = UserSerializer(instance=user, context={"request": request}).data
    return Response(status=status_code, data=data)


class FavoritesList(ListAPIView):
    permission_classes = [ViewFavorites]
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return Favorite.objects.filter(
            user=user,
            submission_id__in=Subquery(
                available_submissions(self.request, user, show_all=True).values("id")
            ),
        )


class SubmissionList(ListCreateAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [UserControls, AccountCurrentPermission]

    def perform_create(self, serializer):
        self.check_object_permissions(self.request, self.request.subject)
        return serializer.save(owner=self.request.subject)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return (
            available_submissions(
                self.request,
                self.request.user,
            )
            .filter(owner=user)
            .order_by("-created_on")
        )


class FilteredSubmissionList(ListAPIView):
    """
    Shows all items which are uploaded by the user but in which they are not tagged as
    the artist. The creation function for this list is actually handled by GalleryList,
    since they are so similar.
    """

    serializer_class = SubmissionSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return user_submissions(
            user, self.request, self.kwargs.get("is_artist", False)
        ).order_by("-display_position")


class RawArtistSubmissionList(FilteredSubmissionList):
    permission_classes = [ObjectControls]


class CollectionManagementList(ListAPIView):
    """
    Shows all items which are uploaded by the user but in which they are not tagged as
    the artist. The creation function for this list is actually handled by GalleryList,
    since they are so similar.
    """

    serializer_class = SubmissionSerializer
    permission_classes = [ObjectControls]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user.owned_profiles_submission.exclude(artists=user)


class ArtRelationList(ListAPIView):
    """
    Gets all submissions for which the user is marked as an artist via the through
    table.
    """

    serializer_class = ArtistTagSerializer

    def get_queryset(self) -> QuerySet:
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        manage = self.kwargs.get("manage") and (
            self.request.user.is_staff or self.request.user == user
        )
        if manage:
            return ArtistTag.objects.filter(user=user)
        return ArtistTag.objects.filter(
            user=user,
            submission_id__in=Subquery(
                user_submissions(user, self.request, is_artist=True).values("pk")
            ),
        ).order_by("-display_position")


class ArtRelationManager(RetrieveUpdateDestroyAPIView):
    """
    View for modifying the relationship of an artist to their submission.
    """

    serializer_class = ArtistTagSerializer
    permission_classes = [ObjectControls]

    def get_object(self) -> Any:
        tag = get_object_or_404(
            ArtistTag, user__username=self.kwargs["username"], id=self.kwargs["tag_id"]
        )
        self.check_object_permissions(self.request, tag)
        return tag


class ArtRelationShift(PositionShift):
    serializer_class = ArtistTagSerializer
    permission_classes = [ObjectControls]

    def get_object(self) -> Any:
        return get_object_or_404(
            ArtistTag, user__username=self.kwargs["username"], id=self.kwargs["tag_id"]
        )


class CollectionShift(PositionShift):
    serializer_class = SubmissionSerializer
    permission_classes = [ObjectControls]

    def get_object(self) -> Any:
        return get_object_or_404(Submission, id=self.kwargs["submission_id"])


class SubmissionSharedList(ListCreateAPIView):
    permission_classes = [IsRegistered, ObjectControls]
    serializer_class = SubmissionSharedSerializer
    pagination_class = None

    def get_object(self) -> Submission:
        return get_object_or_404(Submission, id=self.kwargs["submission_id"])

    def get_queryset(self) -> QuerySet:
        return Submission.shared_with.through.objects.filter(
            submission=self.get_object()
        )

    def perform_create(self, serializer):
        relation, _ = Submission.shared_with.through.objects.get_or_create(
            submission=self.get_object(),
            user_id=serializer.validated_data["user_id"],
        )
        notify(
            SUBMISSION_SHARED,
            relation.user,
            data={"user": self.request.user.id, "submission": relation.submission.id},
            unique_data=True,
            mark_unread=True,
        )
        serializer.instance = relation
        return relation

    def create(self, *args, **kwargs) -> Response:
        submission = self.get_object()
        self.check_object_permissions(self.request, submission)
        return super().create(*args, **kwargs)

    def notify(self, user, target):
        if user != self.request.user:
            notify(
                SUBMISSION_SHARED,
                user,
                data={"user": self.request.user.id, "submission": target.id},
                unique_data=True,
                mark_unread=True,
            )


class SubmissionSharedManager(DestroyAPIView):
    permission_classes = [IsRegistered, ObjectControls]
    serializer_class = RelatedUserSerializer

    def get_object(self) -> Submission.shared_with.through:
        return get_object_or_404(
            Submission.shared_with.through,
            id=self.kwargs["share_id"],
            submission_id=self.kwargs["submission_id"],
        )

    def perform_destroy(self, instance: Character.shared_with.through):
        recall_notification(
            SUBMISSION_SHARED,
            instance.user,
            data={"submission": instance.submission.id},
        )
        instance.delete()

    def delete(self, *args, **kwargs) -> Response:
        relationship = self.get_object()
        self.check_object_permissions(self.request, relationship.submission)
        return super().delete(*args, **kwargs)


class CharacterSharedList(ListCreateAPIView):
    permission_classes = [IsRegistered, ObjectControls]
    serializer_class = CharacterSharedSerializer
    pagination_class = None

    def get_object(self) -> Character:
        return get_object_or_404(
            Character,
            user__username=self.kwargs["username"],
            name=self.kwargs["character"],
        )

    def get_queryset(self) -> QuerySet:
        return Character.shared_with.through.objects.filter(character=self.get_object())

    def perform_create(self, serializer):
        relation, _ = Character.shared_with.through.objects.get_or_create(
            character=self.get_object(),
            user_id=serializer.validated_data["user_id"],
        )
        notify(
            CHAR_SHARED,
            relation.user,
            data={"user": self.request.user.id, "character": relation.character.id},
            unique_data=True,
            mark_unread=True,
        )
        serializer.instance = relation
        return relation

    def create(self, *args, **kwargs) -> Response:
        character = self.get_object()
        self.check_object_permissions(self.request, character)
        return super().create(*args, **kwargs)

    def notify(self, user, target):
        if user != self.request.user:
            notify(
                CHAR_SHARED,
                user,
                data={"user": self.request.user.id, "character": target.id},
                unique_data=True,
                mark_unread=True,
            )


class CharacterSharedManager(DestroyAPIView):
    permission_classes = [IsRegistered, ObjectControls]
    serializer_class = RelatedUserSerializer

    def get_object(self) -> Character.shared_with.through:
        return get_object_or_404(
            Character.shared_with.through,
            id=self.kwargs["share_id"],
            character__name=self.kwargs["character"],
            character__user__username=self.kwargs["username"],
        )

    def perform_destroy(self, instance: Character.shared_with.through):
        recall_notification(
            CHAR_SHARED, instance.user, data={"character": instance.character.id}
        )
        instance.delete()

    def delete(self, *args, **kwargs) -> Response:
        relationship = self.get_object()
        self.check_object_permissions(self.request, relationship.character)
        return super().delete(*args, **kwargs)


class Watchers(ListAPIView):
    serializer_class = RelatedUserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return user.watched_by.all().order_by("username")


class Watching(ListAPIView):
    serializer_class = RelatedUserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return user.watching.all().order_by("username")


class Conversations(ListCreateAPIView):
    permission_classes = [
        IsSubject,
        Any(AccountAge(relativedelta(days=5)), IsSafeMethod),
    ]
    serializer_class = ConversationSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationSerializer
        else:
            return ConversationManagementSerializer

    def perform_create(self, serializer: ConversationSerializer):
        target_participants = set(serializer.validated_data["participants"])
        conversations = Conversation.objects.annotate(
            num_participants=Count("participants"),
        ).filter(num_participants=len(target_participants))
        for participant in target_participants:
            conversations = conversations.filter(participants__id=participant)
        conversation = conversations.first()
        if conversation:
            serializer.instance = conversation
            return
        serializer.save()

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return (
            user.conversations.all()
            .exclude(last_activity=None)
            .order_by("-last_activity")
        )


class ConversationManager(RetrieveUpdateDestroyAPIView):
    # Since conversations are
    permission_classes = [MessageReadPermission, IsSubject]
    serializer_class = ConversationManagementSerializer

    def get_object(self):
        message = get_object_or_404(
            Conversation,
            id=self.kwargs["message_id"],
            participants__username=self.request.subject.username,
        )
        self.check_object_permissions(self.request, message)
        # Leave this as request.user instead of request.subject, since we don't want a
        # superuser triggering read markers.
        return message

    def get(self, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(self.request, instance)
        return super(ConversationManager, self).get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(self.request, instance)
        return super(ConversationManager, self).delete(*args, **kwargs)

    def perform_update(self, serializer: BaseSerializer) -> None:
        self.check_object_permissions(self.request, serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        ConversationParticipant.objects.filter(
            conversation=instance, user=self.request.subject
        ).delete()
        count = instance.participants.all().count()
        if not count:
            instance.delete()
        elif count == 1:
            if not instance.comments.exclude(system=True).exists():
                instance.delete()
                return
        Comment(
            user=self.request.user,
            system=True,
            content_object=instance,
            text="left the conversation.",
        ).save()


class StartPasswordReset(APIView):
    permission_classes = [IsAnonymous]

    # noinspection PyMethodMayBeStatic
    def post(self, request):
        identifier = request.data.get("email")
        if not identifier:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"email": ["This field is required."]},
            )
        try:
            user = User.objects.exclude(guest=True).get(email__iexact=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.exclude(guest=True).get(username=identifier)
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        "email": [
                            "We could not find this username or email address in our "
                            "records. Please contact support."
                        ]
                    },
                )
        if user_has_device(user):
            raise PermissionDenied(
                "This account is protected by two factor authentication. Please email "
                "support@artconomy.com or hit the support button on the sidebar if you "
                "are having trouble logging in."
            )

        user.reset_token = uuid.uuid4()
        user.token_expiry = timezone.now() + relativedelta(days=1)
        user.save()
        subject = "Password reset request"
        to = [user.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        ctx = {
            "user": user,
        }
        message = get_template("profiles/email/password_reset.html").render(ctx)
        textifier = gen_textifier()
        msg = EmailMultiAlternatives(
            subject, textifier.handle(message), from_email=from_email, to=to
        )
        msg.attach_alternative(message, "text/html")
        msg.send()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenValidator(APIView):
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get(self, request, username, reset_token):
        get_object_or_404(
            User,
            username=username,
            reset_token=reset_token,
            token_expiry__gte=timezone.now(),
        )
        return Response(status=status.HTTP_200_OK, data={"success": True})


class PasswordReset(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def get_object(self):
        try:
            user = User.objects.get(
                username=self.kwargs["username"],
                reset_token=self.kwargs["reset_token"],
                token_expiry__gte=timezone.now(),
            )
        except User.DoesNotExist:
            raise ValidationError(
                {
                    "detail": "This user does not exist or the token has expired. "
                    "Please request a new reset link."
                }
            )
        return user

    def post(self, request, **_kwargs):
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Force login of user.
        login(self.request, serializer.instance)
        user.refresh_from_db()
        # Make sure there's no default value in case there's a bug here.
        user.reset_token = uuid.uuid4()
        user.token_expiry = timezone.now() - relativedelta(days=100)
        user.save()
        user.credit_cards.all().update(cvv_verified=False)
        data = UserSerializer(instance=user, context=self.get_serializer_context()).data
        return Response(status=status.HTTP_200_OK, data=data)


class Journals(ListCreateAPIView):
    serializer_class = JournalSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Journal.objects.filter(user=user).order_by("-created_on")

    def perform_create(self, serializer):
        user = get_object_or_404(User, username=self.kwargs["username"])
        if self.request.user != user:
            raise ValidationError(
                {
                    "errors": [
                        "You may not speak for someone else. Are you still logged in?"
                    ]
                }
            )
        journal = serializer.save(user=user)
        return journal


class JournalManager(RetrieveUpdateDestroyAPIView):
    serializer_class = JournalSerializer
    permission_classes = [
        Any(
            IsSafeMethod,
            All(IsMethod("PUT"), IsRegistered),
            All(IsRegistered, ObjectControls),
        )
    ]

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return get_object_or_404(Journal, user=user, id=self.kwargs["journal_id"])

    def put(self, request, *args, **kwargs):
        journal = self.get_object()
        data = {"subscribed": request.data.get("subscribed")}
        serializer = self.get_serializer(instance=journal, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@csrf_exempt
@api_view(["POST"])
def perform_logout(request):
    logout(request)
    request.session.pop("rating", None)
    return Response(
        status=status.HTTP_200_OK,
        data=empty_user(user=request.user, session=request.session),
    )


class CharacterPreview(BasePreview):
    permission_classes = [
        Any(All(IsSafeMethod, SharedWith), All(IsRegistered, ObjectControls))
    ]

    def context(self, username, character):
        char_context = {}
        character = get_object_or_404(
            Character, user__username=username, name=character
        )
        if not self.check_object_permissions(self.request, character):
            return char_context
        char_context[
            "title"
        ] = f"{demark(character.name)} - {character.user.username} on Artconomy.com"
        char_context["description"] = shorten(demark(character.description), 160)
        submissions = character_submissions(character, self.request)
        char_context["image_links"] = [character.preview_image(self.request)] + [
            submission.preview_link for submission in submissions[:24]
        ]
        return char_context


class ArtPreview(BasePreview):
    """
    Loads the meta tags for an artist's art.
    """

    is_artist = True

    def context(self, username):
        art_context = {}
        user = get_object_or_404(User, username=self.kwargs["username"])
        if self.is_artist:
            art_context["title"] = f"{user.username}'s art gallery"
        else:
            art_context["title"] = f"{user.username}'s collection"
        art_context["description"] = f"See the work of {demark(user.username)}"
        submissions = user_submissions(user, self.request, self.is_artist).order_by(
            "-display_position"
        )[:24]
        art_context["image_links"] = [make_url(user.avatar_url)] + [
            submission.preview_link for submission in submissions
        ]
        return art_context


class ProfilePreview(BasePreview):
    """
    Loads the meta tags for a user's profile.
    """

    def context(self, username):
        art_context = {}
        user = get_object_or_404(User, username=self.kwargs["username"])
        count_hit(self.request, user)
        is_artist = user.artist_mode
        art_context["title"] = f"{user.username} on Artconomy.com"
        art_context["description"] = shorten(demark(user.biography), 160)
        submissions = user_submissions(user, self.request, is_artist).order_by(
            "-display_position"
        )[:24]
        links = [make_url(user.avatar_url)] + [
            submission.preview_link for submission in submissions
        ]
        links = [link for link in links if link]
        art_context["image_links"] = links
        return art_context


class CollectionPreview(ArtPreview):
    is_artist = False


class SubmissionPreview(BasePreview):
    permission_classes = [SubmissionViewPermission]

    def context(self, submission_id):
        submission = get_object_or_404(Submission, id=submission_id)
        if not self.check_object_permissions(self.request, submission):
            return {}
        count_hit(self.request, submission)
        try:
            image = preview_rating(
                self.request, submission.rating, submission.preview_link
            )
        except Exception as err:
            logger.exception(err)
            image = None
        data = {
            "title": demark(submission.title),
            "description": demark(submission.caption),
        }
        if image:
            data["image_links"] = [image]
        return data


class ReferralStats(APIView):
    permission_classes = [UserControls]

    # noinspection PyUnusedLocal
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs.get("username"))
        self.check_object_permissions(self.request, user)
        return Response(
            status=status.HTTP_200_OK, data=ReferralStatsSerializer(user).data
        )


class MailingListPref(APIView):
    # noinspection PyMethodMayBeStatic
    def post(self, request):
        request.user.offered_mailchimp = True
        request.user.save()
        mailchimp_subscribe.delay(request.user.id)
        drip_subscribe.delay(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # noinspection PyMethodMayBeStatic
    def delete(self, request):
        request.user.offered_mailchimp = True
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidateUsername(GenericAPIView):
    serializer_class = UsernameValidationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidatePassword(GenericAPIView):
    serializer_class = PasswordValidationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidateEmail(GenericAPIView):
    serializer_class = EmailValidationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecommendedSubmissions(ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [SubmissionViewPermission]

    @lru_cache()
    def get_object(self):
        return get_object_or_404(Submission, id=self.kwargs["submission_id"])

    def get_queryset(self):
        submission = self.get_object()
        qs = available_submissions(self.request, self.request.user).exclude(
            id=submission.id
        )
        qs = qs.annotate(
            same_artist=Case(
                When(artists__id__in=submission.artists.all(), then=0 - F("id")),
                default=0,
                output_field=IntegerField(),
            ),
            same_collector=Case(
                When(owner_id=submission.owner.id, then=0),
                default=1,
                output_field=IntegerField(),
            ),
        ).order_by("same_artist", "same_collector", "?")
        return qs


class RecommendedCharacters(ListAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [
        Any(
            All(IsSafeMethod, SharedWith),
            ObjectControls,
        )
    ]

    @lru_cache()
    def get_object(self):
        character = get_object_or_404(
            Character,
            user__username=self.kwargs["username"],
            name=self.kwargs["character"],
        )
        self.check_object_permissions(self.request, character)
        return character

    def get_queryset(self):
        character = self.get_object()
        qs = (
            available_chars(self.request.user, sfw=not self.request.rating)
            .exclude(id=character.id)
            .exclude(primary_submission=None)
        )
        qs = qs.annotate(
            same_user=Case(
                When(user=character.user, then=0 - F("id")),
                default=0,
                output_field=IntegerField(),
            ),
        ).order_by("same_user", "?")
        return qs


class DestroyAccount(GenericAPIView):
    serializer_class = DeleteUserSerializer
    permission_classes = [UserControls]

    def get_object(self) -> User:
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user

    def get_serializer_context(self) -> Dict[str, Any]:
        context = super().get_serializer_context()
        context["user"] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            clear_user(serializer.context["user"])
        except UserClearException as err:
            raise ValidationError(str(err)) from err
        if serializer.context["user"] == request.user:
            logout(request)
            trigger_reconnect(request, include_current=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationSettings(RetrieveUpdateAPIView):
    serializer_class = EmailPreferencesSerializer
    permission_classes = [UserControls]

    @property
    def extra_deliverable_content_types(self):
        return [
            ContentType.objects.get_for_model(model) for model in [Revision, Reference]
        ]

    def get_object(self) -> User:
        user = get_object_or_404(User, username=self.kwargs["username"])
        self.check_object_permissions(self.request, user)
        return user

    @transaction.atomic()
    def perform_update(self, serializer):
        result = super().perform_update(serializer)
        revised_value = serializer.data.get("new_comment__deliverable")
        user = self.get_object()
        if revised_value is not None:
            EmailPreference.objects.filter(
                user=user,
                type=COMMENT,
                content_type__in=self.extra_deliverable_content_types,
            ).update(enabled=revised_value)
        revised_value = serializer.data.get("order_update")
        if revised_value is not None:
            EmailPreference.objects.filter(
                user=user,
                type__in=[
                    ORDER_UPDATE,
                    SALE_UPDATE,
                    REVISION_UPLOADED,
                    REFERENCE_UPLOADED,
                    REVISION_APPROVED,
                ],
            ).update(enabled=revised_value)
        revised_value = serializer.data.get("renewal_failure")
        if revised_value is not None:
            EmailPreference.objects.filter(
                user=user,
                type__in=[
                    RENEWAL_FAILURE,
                    RENEWAL_FIXED,
                    SUBSCRIPTION_DEACTIVATED,
                ],
            ).update(enabled=revised_value)
        return result

    def get_serializer_context(self) -> Dict[str, Any]:
        context = super().get_serializer_context()
        context["user"] = self.get_object()
        context["preferences"] = (
            EmailPreference.objects.filter(user=context["user"])
            .exclude(
                type=COMMENT,
                content_type__in=self.extra_deliverable_content_types,
            )
            .exclude(
                type__in=[
                    SALE_UPDATE,
                    RENEWAL_FIXED,
                    SUBSCRIPTION_DEACTIVATED,
                    REVISION_UPLOADED,
                    REFERENCE_UPLOADED,
                    REVISION_APPROVED,
                ]
            )
            .order_by("id")
        )
        return context

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response(serializer.data)


class CommunitySubmissions(ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return (
            available_submissions(
                self.request,
                self.request.user,
            )
            .filter(owner__username__in=settings.COMMUNITY_ACCOUNT_NAMES)
            .order_by("-created_on")
        )
