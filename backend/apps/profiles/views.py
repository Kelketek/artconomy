import logging
import uuid

from avatar.models import Avatar
from avatar.signals import avatar_updated
from avatar.templatetags.avatar_tags import avatar_url
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import login, get_user_model, authenticate, logout, update_session_auth_hash
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.db.models import Q
from django.db.transaction import atomic
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django_otp import user_has_device, match_token, login as otp_login, devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, \
    GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_bulk import BulkUpdateAPIView

from apps.lib.models import (
    Notification, FAVORITE, CHAR_TAG, SUBMISSION_CHAR_TAG, SUBMISSION_ARTIST_TAG, ARTIST_TAG,
    SUBMISSION_TAG, Tag, ASSET_SHARED, CHAR_SHARED, WATCHING, Comment, NEW_PM, Subscription,
    COMMENT, ORDER_NOTIFICATION_TYPES
)
from apps.lib.permissions import Any, All, IsSafeMethod, IsMethod, IsAnonymous, IsAuthenticatedObj
from apps.lib.serializers import CommentSerializer, NotificationSerializer, RelatedUserSerializer, \
    BulkNotificationSerializer, UserInfoSerializer
from apps.lib.utils import (
    recall_notification, notify, safe_add, add_tags, remove_watch_subscriptions,
    watch_subscriptions, add_check, demark, preview_rating
)
from apps.lib.views import BaseTagView, BaseUserTagView, BasePreview
from apps.profiles.models import User, Character, ImageAsset, RefColor, Attribute, Message, \
    MessageRecipientRelationship, Journal
from apps.profiles.permissions import ObjectControls, UserControls, AssetViewPermission, AssetControls, \
    ColorControls, ColorLimit, ViewFavorites, SharedWith, MessageReadPermission, MessageControls, IsUser, \
    JournalCommentPermission
from apps.profiles.serializers import (
    CharacterSerializer, ImageAssetSerializer, SettingsSerializer, UserSerializer,
    RegisterSerializer, ImageAssetManagementSerializer, CredentialsSerializer, AvatarSerializer, RefColorSerializer,
    AttributeSerializer, SessionSettingsSerializer, MessageManagementSerializer, MessageSerializer,
    PasswordResetSerializer, JournalSerializer, TwoFactorTimerSerializer, TelegramDeviceSerializer,
    ReferralStatsSerializer
)
from apps.profiles.tasks import mailchimp_subscribe
from apps.profiles.utils import available_chars, char_ordering, available_assets, available_artists, available_users
from apps.sales.models import Order
from apps.sales.utils import claim_order_by_token
from apps.tg_bot.models import TelegramDevice


logger = logging.getLogger(__name__)


class Register(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.offered_mailchimp = True
        add_to_newsletter = serializer.validated_data.get('mail')
        instance.rating = self.request.max_rating
        referrer = self.request.META.get('HTTP_X_REFERRED_BY', None)
        if referrer:
            instance.referred_by = User.objects.filter(username__iexact=referrer).first()
        instance.save()
        if add_to_newsletter:
            mailchimp_subscribe.delay(instance.id)
        login(self.request, instance)
        order_claim = serializer.validated_data.get('order_claim', None)
        claim_order_by_token(order_claim, instance)

    def get_serializer(self, instance=None, data=None, many=False, partial=False):
        return self.serializer_class(
            instance=instance, data=data, many=many, partial=partial, context=self.get_serializer_context()
        )


class SettingsAPI(UpdateAPIView):
    serializer_class = SettingsSerializer
    permission_classes = [UserControls]

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user


class CredentialsAPI(GenericAPIView):
    serializer_class = CredentialsSerializer
    permission_classes = [UserControls]

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user

    def post(self, request, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(data=request.data, instance=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.user == serializer.instance:
            # make sure the user stays logged in
            update_session_auth_hash(request, serializer.instance)

        return Response(status=status.HTTP_200_OK, data=serializer.data)


class TOTPDeviceList(ListCreateAPIView):
    permission_classes = [IsUser]
    serializer_class = TwoFactorTimerSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user.totpdevice_set.all().order_by('-id')

    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return serializer.save(user=user, confirmed=False)


class TOTPDeviceManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsUser]
    serializer_class = TwoFactorTimerSerializer

    def get_object(self):
        device = get_object_or_404(
            TOTPDevice, user__username__iexact=self.kwargs['username'], id=self.kwargs['totp_id']
        )
        self.check_object_permissions(self.request, device.user)
        return device


class Telegram2FA(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsUser]
    serializer_class = TelegramDeviceSerializer

    http_method_names = View.http_method_names + ['create']

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        if self.request.method == 'CREATE':
            devices = TelegramDevice.objects.filter(user=user)
            if devices.exists():
                return devices.first()
            return None
        return get_object_or_404(TelegramDevice, user=user)

    def create(self, request, username):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        device = self.get_object()
        if not device:
            device = TelegramDevice(user=user, confirmed=False)
            device.save()
        return Response(status=status.HTTP_201_CREATED, data=self.get_serializer(instance=device).data)

    def post(self, request, username):
        device = self.get_object()
        device.generate_challenge()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CharacterListAPI(ListCreateAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username__iexact=username)
        if self.request.user.is_staff:
            requester = user
        else:
            requester = self.request.user
        self_search = requester == user
        qs = available_chars(requester, self_search=self_search).filter(user=user)
        qs = qs.order_by('created_on')
        return qs

    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        if not (self.request.user.is_staff or self.request.user == user):
            raise PermissionDenied("You do not have permission to create characters for that user.")
        if user.characters.all().count() >= settings.MAX_CHARACTER_COUNT:
            raise PermissionDenied(
                "You have reached your maximum number of characters. Please contact support "
                "if you believe your quota should be increased."
            )
        if user.characters.filter(name=serializer.validated_data['name']):
            raise ValidationError({'name': ['A character with this name already exists.']})
        target = serializer.save(user=user)
        # ignore the tagging result. In the case it fails, someone's doing something pretty screwwy anyway, and it's
        # not essential for creating the character.
        add_tags(self.request, target, field_name='tags')

        return target


class CharacterAssets(ListCreateAPIView):
    serializer_class = ImageAssetSerializer
    permission_classes = [ObjectControls]

    def get_queryset(self):
        char = get_object_or_404(
            Character, user__username__iexact=self.kwargs['username'], name=self.kwargs['character']
        )
        qs = char.assets.filter(rating__lte=self.request.max_rating).exclude(tags__in=self.request.blacklist)
        return qs.order_by('-created_on')

    def perform_create(self, serializer):
        character = get_object_or_404(
            Character, user__username=self.kwargs['username'], name=self.kwargs['character']
        )
        self.check_object_permissions(self.request, character)
        asset = serializer.save(owner=self.request.user)
        safe_add(asset, 'characters', character)
        if character.primary_asset is None:
            character.primary_asset = asset
            character.save()
        if serializer.validated_data.get('is_artist'):
            asset.artists.add(self.request.user)
        # ignore the tagging result. In the case it fails, someone's doing something pretty screwwy anyway, and it's
        # not essential for creating the character.
        add_tags(self.request, asset, field_name='tags')
        return asset


class CharacterManager(RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [Any(All(IsSafeMethod, SharedWith), ObjectControls)]

    def get_object(self):
        character = get_object_or_404(Character, user__username=self.kwargs['username'], name=self.kwargs['character'])
        self.check_object_permissions(self.request, character)
        return character

    def destroy(self, request, *args, **kwargs):
        char = self.get_object()
        for asset in char.assets.all():
            if asset.characters.all().count == 1:
                asset.delete()
        return super().destroy(request, *args, **kwargs)


class MakePrimary(APIView):
    serializer_class = ImageAssetSerializer
    permission_classes = [ObjectControls]

    def get_object(self):
        asset = get_object_or_404(
            ImageAsset, id=self.kwargs['asset_id']
        )
        get_object_or_404(
            Character, assets=asset.id, name=self.kwargs['character'], user__username=self.kwargs['username']
        )
        if asset.private:
            self.check_object_permissions(self.request, asset)
        return asset

    def post(self, *args, **kwargs):
        asset = self.get_object()
        char = get_object_or_404(Character, user__username=self.kwargs['username'], name=self.kwargs['character'])
        self.check_object_permissions(self.request, char)
        char.primary_asset = asset
        char.save()
        return Response(
            status=status.HTTP_200_OK,
            data=ImageAssetManagementSerializer(
                instance=asset, context={'request': self.request}
            ).data
        )


class AssetManager(RetrieveUpdateDestroyAPIView):
    serializer_class = ImageAssetManagementSerializer
    permission_classes = [
        Any(All(Any(IsSafeMethod, All(IsMethod('PUT'), IsAuthenticatedObj)), AssetViewPermission), AssetControls)
    ]

    def get_object(self):
        asset = get_object_or_404(
            ImageAsset, id=self.kwargs['asset_id'],
        )
        self.check_object_permissions(self.request, asset)
        return asset

    def destroy(self, request, *args, **kwargs):
        asset = self.get_object()
        self.check_object_permissions(request, asset)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        asset = self.get_object()
        data = {'subscribed': request.data.get('subscribed')}
        serializer = self.get_serializer(instance=asset, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class AssetComments(ListCreateAPIView):
    permission_classes = [AssetViewPermission]
    serializer_class = CommentSerializer

    def get_queryset(self):
        asset = get_object_or_404(ImageAsset, id=self.kwargs['asset_id'])
        self.check_object_permissions(self.request, asset)
        return asset.comments.all()

    def perform_create(self, serializer):
        asset = get_object_or_404(ImageAsset, id=self.kwargs['asset_id'])
        self.check_object_permissions(self.request, asset)
        serializer.save(user=self.request.user, content_object=asset)

    class Meta:
        pass


class SetAvatar(GenericAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [UserControls]

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        avatar = Avatar(user=request.user, primary=True)
        image_file = serializer.validated_data.get('avatar')
        avatar.avatar.save(image_file.name, image_file)
        avatar.save()
        avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
        Avatar.objects.filter(user=request.user).exclude(id=avatar.id).delete()
        user.avatar_url = avatar_url(user)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


def empty_user(request):
    return {'blacklist': [], 'rating': request.max_rating}


class UserInfo(APIView):
    permission_classes = [Any(IsSafeMethod, ObjectControls)]

    def get_serializer(self, user):
        if self.request.user.is_staff:
            return UserSerializer
        if self.request.user == user:
            return UserSerializer
        else:
            return UserInfoSerializer

    def get_user(self):
        return get_object_or_404(User, username__iexact=self.kwargs.get('username'))

    def get_serializer_context(self):
        return {'request': self.request}

    def get(self, request, **kwargs):
        user = self.get_user()
        if user:
            serializer_class = self.get_serializer(user)
            serializer = serializer_class(instance=user, context=self.get_serializer_context())
            data = serializer.data
        else:
            data = {'blacklist': [], 'rating': request.max_rating}
        return Response(data=data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        user = self.get_user()
        self.check_object_permissions(request, user)
        serializer_class = self.get_serializer(user)
        serializer = serializer_class(instance=user, data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserInfoByID(UserInfo):
    def get_user(self):
        get_object_or_404(User, id=self.kwargs.get('user_id'))


class SessionSettings(APIView):
    permission_classes = [IsAnonymous]

    def get(self, request):
        self.check_permissions(request)
        return Response(status=status.HTTP_200_OK, data={'rating': request.max_rating})

    def patch(self, request):
        self.check_permissions(request)
        serializer = SessionSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.session.update(serializer.data)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CurrentUserInfo(UserInfo):
    def get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        else:
            return

    def get_serializer(self, user):
        return UserSerializer


class CharacterSearch(ListAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        tagging = self.request.GET.get('tagging', False)
        if not query:
            return Character.objects.none()
        try:
            commissions = json.loads(self.request.query_params.get('new_order', 'false'))
        except ValueError:
            raise ValidationError({'errors': ['New Order must be a boolean.']})

        # If staffer, allow search on behalf of user.
        if self.request.user.is_staff:
            user = get_object_or_404(User, id=self.request.GET.get('user', self.request.user.id))
        else:
            user = self.request.user
        if self.request.user.is_authenticated:
            return char_ordering(
                available_chars(user, query=query, commissions=commissions, tagging=tagging), user, query=query
            )
        q = Q(name__istartswith=query) | Q(tags__name__iexact=query)
        return Character.objects.filter(q).exclude(private=True).exclude(taggable=False).distinct().order_by('id')


class CharacterSearchIndexed(ListAPIView):
    """
    Indexed search for the more general case of searching blind, like in the top search bar.
    """
    serializer_class = CharacterSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        return SearchQuerySet.models(Character).filter(content=AutoQuery(query))


class UserSearch(ListAPIView):
    serializer_class = RelatedUserSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        tagging = self.request.GET.get('tagging', False)
        if not query:
            return User.objects.none()
        qs = User.objects.filter(username__istartswith=query)
        if tagging and self.request.user.is_authenticated:
            qs = qs.filter(Q(taggable=True) | Q(id=self.request.user.id))
        elif tagging:
            qs = qs.filter(taggable=True)
        return qs


class TagSearch(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response(status=status.HTTP_200_OK, data=[])
        return Response(
            status=status.HTTP_200_OK,
            data=Tag.objects.filter(name__istartswith=query)[:20].values_list('name', flat=True)
        )


class AssetSearch(ListAPIView):
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        qs = available_assets(self.request, self.request.user)
        query = self.request.GET.getlist('q', [])
        if not query:
            return qs.none()
        for q in query:
            if q.startswith('!'):
                qs = qs.exclude(tags__name__iexact=q[1:])
            else:
                qs = qs.filter(tags__name__iexact=q)
        return qs.distinct()

    def get(self, *args, **kwargs):
        query = self.request.GET.getlist('q', [])
        if len(query) > 10:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={'error': 'You cannot use more than 10 search terms at once.'}
            )
        return super().get(*args, **kwargs)


class AssetTagCharacter(APIView):
    permission_classes = [IsAuthenticated, AssetViewPermission]

    def delete(self, request, asset_id):
        asset = get_object_or_404(ImageAsset, id=asset_id)
        self.check_object_permissions(request, asset)
        # Check has to be different here.
        # Might find a way to better simplify this sort of permission checking if
        # we end up doing it a lot.
        if 'characters' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'characters': ['This field is required.']})
        id_list = request.data.get('characters', [])
        qs = Character.objects.filter(id__in=id_list, transfer__isnull=True)
        if (asset.owner == request.user) or request.user.is_staff:
            asset.characters.remove(*qs)
            return Response(
                status=status.HTTP_200_OK,
                data=ImageAssetManagementSerializer(
                    instance=asset,
                    context={'request': self.request}
                ).data
            )
        else:
            qs = qs.filter(user=request.user)
        if not qs.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'characters': [
                    'No characters specified. Those IDs do not exist, or you do not have permission '
                    'to remove any of them.'
                ]}
            )
        asset.characters.remove(*qs)
        return Response(
            status=status.HTTP_200_OK, data=ImageAssetManagementSerializer(
                instance=asset, context={'request': self.request}
            ).data
        )

    def post(self, request, asset_id):
        asset = get_object_or_404(ImageAsset, id=asset_id)
        self.check_object_permissions(request, asset)
        if 'characters' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'characters': ['This field is required.']})
        id_list = request.data.getlist('characters')
        qs = available_chars(request.user, commissions=False, tagging=True).filter(id__in=id_list)
        qs = qs.exclude(id__in=asset.characters.all().values_list('id', flat=True))

        for character in qs:
            if character.user != request.user:
                notify(
                    CHAR_TAG, character, data={'user': request.user.id, 'asset': asset.id},
                    unique=True, mark_unread=True
                )
            if asset.owner != request.user:
                notify(SUBMISSION_CHAR_TAG, asset, data={'user': request.user.id, 'character': character.id})
        if qs.exists():
            safe_add(asset, 'characters', *qs)
        return Response(
            status=status.HTTP_200_OK,
            data=ImageAssetManagementSerializer(
                instance=asset, context={'request': self.request}
            ).data,
        )


class AssetTagArtist(BaseUserTagView):
    field_name = 'artists'
    permission_classes = [IsAuthenticated, AssetViewPermission]
    serializer_class = ImageAssetManagementSerializer

    def get_target(self):
        return ImageAsset.objects.get(id=self.kwargs['asset_id'])

    def free_delete_check(self, target):
        return (target.owner == self.request.user) or self.request.user.is_staff

    def notify(self, user, target):
        if user != self.request.user:
            notify(
                ARTIST_TAG, user, data={'user': self.request.user.id, 'asset': target.id},
                unique=True, mark_unread=True
            )
        if user != target.owner:
            notify(
                SUBMISSION_ARTIST_TAG, target, data={'user': self.request.user.id, 'artist': user.id},
                exclude=[self.request.user]
            )

    def recall(self, target, qs):
        for user in qs:
            recall_notification(
                ARTIST_TAG, user, data={'asset': target.id}
            )
            recall_notification(
                SUBMISSION_ARTIST_TAG, target,
            )


class AssetTag(BaseTagView):
    permission_classes = [IsAuthenticated, AssetViewPermission]

    def get_object(self):
        return get_object_or_404(ImageAsset, id=self.kwargs['asset_id'])

    def post_delete(self, asset, qs):
        return Response(
            status=status.HTTP_200_OK,
            data=ImageAssetManagementSerializer(
                instance=asset, context=self.get_serializer_context()
            ).data
        )

    def post_post(self, asset, tag_list):
        def transform(old_data, new_data):
            return {
                'users': list(set(old_data['users'] + new_data['users'])),
                'tags': list(set(old_data['tags'] + new_data['tags']))
            }

        if asset.owner != self.request.user:
            notify(
                SUBMISSION_TAG, asset, data={
                    'users': [self.request.user.id],
                    'tags': tag_list
                },
                unique=True, mark_unread=True,
                transform=transform
            )
        return Response(
            status=status.HTTP_200_OK, data=ImageAssetManagementSerializer(
                instance=asset, context=self.get_serializer_context()
            ).data
        )


class CharacterTag(BaseTagView):
    permission_classes = [ObjectControls]

    def get_object(self):
        return get_object_or_404(
            Character, user__username__iexact=self.kwargs['username'], name=self.kwargs['character']
        )

    def post_delete(self, character, _tags):
        return Response(
            status=status.HTTP_200_OK,
            data=CharacterSerializer(instance=character, context=self.get_serializer_context()).data
        )

    def post_post(self, character, _qs):
        return Response(
            status=status.HTTP_200_OK, data=CharacterSerializer(
                instance=character, context=self.get_serializer_context()
            ).data
        )


class AttributeList(ListCreateAPIView):
    permission_classes = [Any(All(IsSafeMethod, SharedWith), ObjectControls)]
    serializer_class = AttributeSerializer

    def get_character(self):
        character = get_object_or_404(Character, name=self.kwargs['character'], user__username=self.kwargs['username'])
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
                "You may not have more than {} attributes on one character.".format(settings.MAX_ATTRS)
            )
        if character.attributes.filter(key__iexact=serializer.validated_data['key']).exists():
            raise ValidationError({'key': ['There is already an attribute with this name.']})
        serializer.save(character=character)


class AttributeManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [ObjectControls]
    serializer_class = AttributeSerializer

    def get_object(self):
        attr = get_object_or_404(
            Attribute, character__name=self.kwargs['character'], character__user__username=self.kwargs['username'],
            id=self.kwargs['attribute_id']
        )
        self.check_object_permissions(self.request, attr.character)
        return attr

    def mod_values(self):
        instance = self.get_object()
        if instance.sticky:
            self.request.data.pop('key', None)

    def patch(self, *args, **kwargs):
        self.mod_values()
        return super().patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        self.mod_values()
        return super().put(*args, **kwargs)

    def destroy(self, *args, **kwargs):
        instance = self.get_object()
        if instance.sticky:
            raise PermissionDenied("You may not remove sticky attributes.")
        return super().destroy(*args, **kwargs)


class UserBlacklist(BaseTagView):
    field_name = 'blacklist'
    permission_classes = [ObjectControls]

    def get_object(self):
        return User.objects.get(username__iexact=self.kwargs['username'])

    def post_delete(self, user, result):
        return Response(
            status=status.HTTP_200_OK,
            data=UserSerializer(instance=user, context=self.get_serializer_context()).data
        )

    def post_post(self, user, result):
        return Response(
            status=status.HTTP_200_OK,
            data=UserSerializer(instance=user, context=self.get_serializer_context()).data
        )


class AssetFavorite(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageAssetManagementSerializer

    def get_object(self):
        asset = get_object_or_404(ImageAsset, id=self.kwargs['asset_id'])
        private = asset.private and not asset.shared_with.filter(id=self.request.user.id)
        if private and not asset.owner == self.request.user:
            raise PermissionDenied('This submission is private.')
        return asset

    def post(self, request, **_kwargs):
        asset = self.get_object()
        self.check_object_permissions(request, asset)
        if self.request.user.favorites.filter(id=asset.id).exists():
            self.request.user.favorites.remove(asset)
            recall_notification(FAVORITE, asset, {'user_id': self.request.user.id}, unique_data=True)
        else:
            self.request.user.favorites.add(asset)
            notify(FAVORITE, asset, {'user_id': self.request.user.id}, unique_data=True)
        serializer = self.get_serializer()
        serializer.instance = asset
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class UserSerializerView:
    def get_serializer(self, user):
        if self.request.user.is_staff:
            return UserSerializer
        if self.request.user == user:
            return UserSerializer
        else:
            return UserInfoSerializer


class WatchUser(UserSerializerView, GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def post(self, request, **_kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        if self.request.user.watching.filter(id=user.id).exists():
            self.request.user.watching.remove(user)
            remove_watch_subscriptions(self.request.user, user)
            recall_notification(WATCHING, user, {'user_id': self.request.user.id}, unique_data=True)
        else:
            self.request.user.watching.add(user)
            watch_subscriptions(self.request.user, user)
            notify(WATCHING, user, {'user_id': self.request.user.id}, unique_data=True)
        serializer = self.get_serializer(user)(instance=user, context=self.get_serializer_context())
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class BlockUser(UserSerializerView, GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        user = get_object_or_404(User, username__iexact=username)
        if request.user.blocking.filter(id=user.id):
            request.user.blocking.remove(user)
        else:
            request.user.blocking.add(user)
        serializer = self.get_serializer(user)(instance=user, context=self.get_serializer_context())
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class UnreadNotifications(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            status=200,
            data={
                'count': Notification.objects.filter(
                    user=self.request.user, read=False
                ).exclude(event__recalled=True).count(),
                'community_count': Notification.objects.filter(
                    user=self.request.user, read=False
                ).exclude(
                    event__recalled=True
                ).exclude(
                    event__type__in=ORDER_NOTIFICATION_TYPES
                ).exclude(
                    event__type=COMMENT, event__content_type=ContentType.objects.get_for_model(Order)
                ).count(),
                'sales_count': Notification.objects.filter(
                    user=self.request.user, read=False,
                ).exclude(event__recalled=True).filter(
                    Q(event__type__in=ORDER_NOTIFICATION_TYPES) |
                    Q(event__type=COMMENT, event__content_type=ContentType.objects.get_for_model(Order))
                ).count()
            }
        )


class CommunityNotificationsList(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).exclude(event__recalled=True).exclude(
            event__type__in=ORDER_NOTIFICATION_TYPES
        ).exclude(
            event__type=COMMENT, event__content_type=ContentType.objects.get_for_model(Order)
        )
        if self.request.GET.get('unread'):
            qs = qs.filter(read=False)
        return qs.prefetch_related('event').order_by('-event__date')


class SalesNotificationsList(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).exclude(event__recalled=True).filter(
            Q(event__type__in=ORDER_NOTIFICATION_TYPES) |
            Q(event__type=COMMENT, event__content_type=ContentType.objects.get_for_model(Order))
        )
        if self.request.GET.get('unread'):
            qs = qs.filter(read=False)
        return qs.select_related('event').order_by('-event__date')


class RefColorList(ListCreateAPIView):
    serializer_class = RefColorSerializer
    permission_classes = [Any(All(IsSafeMethod, SharedWith), All(ColorControls, ColorLimit))]

    def get_queryset(self):
        character = get_object_or_404(Character, name=self.kwargs['character'], user__username=self.kwargs['username'])
        self.check_object_permissions(self.request, character)
        return RefColor.objects.filter(
            character__name=self.kwargs['character'], character__user__username=self.kwargs['username']
        )

    def perform_create(self, serializer):
        character = get_object_or_404(
            Character, name=self.kwargs['character'], user__username=self.kwargs['username']
        )
        self.check_object_permissions(self.request, character)
        return serializer.save(character=character)


class RefColorManager(RetrieveUpdateDestroyAPIView):
    serializer_class = RefColorSerializer
    permission_classes = [ColorControls]

    def get_object(self):
        obj = get_object_or_404(RefColor, id=self.kwargs['ref_color_id'])
        self.check_object_permissions(self.request, obj)
        return obj


class MarkNotificationsRead(BulkUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BulkNotificationSerializer
    queryset = Notification.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)


class WatchListSubmissions(ListAPIView):
    serializer_class = ImageAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return available_assets(self.request, self.request.user).filter(
            artists__in=self.request.user.watching.all()
        ).order_by('-created_on')


class RecentCommissions(ListAPIView):
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        return available_assets(self.request, self.request.user).filter(order__isnull=False).order_by('-created_on')


class RecentSubmissions(ListAPIView):
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        return available_assets(self.request, self.request.user).filter(order__isnull=True).order_by('-created_on')


class RecentArt(ListAPIView):
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        return available_assets(self.request, self.request.user).order_by('-created_on')


class NewCharacters(ListAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        return available_chars(self.request.user).filter(primary_asset__isnull=False).order_by('-created_on')


@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username')
    if not username:
        return Response({'error': 'No username provided.'}, status=status.HTTP_400_BAD_REQUEST)
    cls = get_user_model()
    try:
        cls.objects.get(username__iexact=username)
    except cls.DoesNotExist:
        return Response({'available': True})
    return Response({'available': False})


@api_view(['GET'])
def check_email(request):
    email = request.GET.get('email')
    if not email:
        return Response({'success': False, 'error': 'No email provided.'}, status=status.HTTP_400_BAD_REQUEST)
    cls = get_user_model()
    try:
        cls.objects.get(email__iexact=email)
    except cls.DoesNotExist:
        return Response({'available': True})
    return Response({'available': False})


def handle_login(request, user, token):
    # If we have a User object, the details are correct.
    # If None (Python's way of representing the absence of a value), no user
    # with matching credentials was found.
    if not user:
        return "Either this account does not exist, or the password is incorrect.", ''
        # Is the account active? It could have been disabled.

    if not user.is_active:
        # An inactive account was used - no logging in!
        logout(request)
        return "Your account is disabled. Please contact support", ''

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
            return '', "That Verification code is either invalid or expired. Please try again. If you've lost your" \
                   " 2FA device, please contact support@artconomy.com"

    # If the account is valid and active, we can log the user in.
    # We'll send the user to their account.
    login(request, user)
    if device:
        otp_login(request, device)
    return '', ''


@csrf_exempt
@api_view(['POST'])
def perform_login(request):
    """
    Handle post action
    """
    # Gather the username and password provided by the user.
    # This information is obtained from the login form.
    email = str(request.data.get('email', request.POST.get('email', ''))).lower().strip()
    password = request.data.get('password', request.POST.get('password', '')).strip()
    token = request.data.get('token', request.POST.get('token', '')).strip()
    order_claim = request.data.get('order_claim', request.POST.get('order_claim', '')).strip()
    # Use Django's machinery to attempt to see if the username/password
    # combination is valid - a User object is returned if it is.
    user = authenticate(email=email, password=password)
    password_error, token_error = handle_login(request, user, token)

    status_code = status.HTTP_401_UNAUTHORIZED if (password_error or token_error) else status.HTTP_200_OK
    data = {
        'email': [],
        'password': [password_error] if password_error else [],
        'token': [token_error] if token_error else [],
    }
    if status_code == status.HTTP_200_OK:
        if order_claim:
            claim_order_by_token(order_claim, user)
        data['csrftoken'] = get_token(request)
    return Response(
        status=status_code,
        data=data
    )


class FavoritesList(ListAPIView):
    permission_classes = [ViewFavorites]
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return available_assets(self.request, user).filter(favorited_by=user)


class GalleryList(ListCreateAPIView):
    serializer_class = ImageAssetSerializer
    permission_classes = [Any(IsSafeMethod, ObjectControls)]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return available_assets(self.request, user).filter(artists=user)

    @atomic
    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        char_pks = [char.pk for char in serializer.validated_data.get('characters', []) or []]
        artist_pks = [artist.pk for artist in serializer.validated_data.get('artists', []) or []]
        is_artist = serializer.validated_data.get('is_artist')
        instance = serializer.save(owner=user)
        if is_artist:
            instance.artists.add(user)
        add_tags(self.request, instance)
        instance.artists.add(*available_artists(user).filter(pk__in=artist_pks))
        characters = available_chars(user, tagging=True).filter(pk__in=char_pks)
        for character in characters:
            instance.characters.add(character)
            if character.user == user and not character.primary_asset:
                character.primary_asset = instance
                character.save()
        return instance


class SubmissionList(ListAPIView):
    """
    Shows all items which are uploaded by the user but in which they are not tagged as the artist.
    The creation function for this list is actually handled by GalleryList, since they are so similar.
    """
    serializer_class = ImageAssetSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return available_assets(
            self.request, user
        ).filter(owner=user).exclude(artists=user)


class AssetShare(BaseUserTagView):
    field_name = 'shared_with'
    permission_classes = [IsAuthenticated, ObjectControls]
    serializer_class = ImageAssetManagementSerializer

    def get_target(self):
        return ImageAsset.objects.get(id=self.kwargs['asset_id'])

    def free_delete_check(self, target):
        return (target.owner == self.request.user) or self.request.user.is_staff

    def recall(self, target, qs):
        for user in qs:
            recall_notification(
                ASSET_SHARED, user, data={'asset': target.id}
            )

    def notify(self, user, target):
        if user != self.request.user:
            notify(
                ASSET_SHARED, user, data={'user': self.request.user.id, 'asset': target.id},
                unique_data=True, mark_unread=True
            )


class CharacterShare(BaseUserTagView):
    field_name = 'shared_with'
    permission_classes = [IsAuthenticated, ObjectControls]
    serializer_class = CharacterSerializer

    def get_target(self):
        return Character.objects.get(user__username__iexact=self.kwargs['username'], name=self.kwargs['character'])

    def free_delete_check(self, target):
        return (target.user == self.request.user) or self.request.user.is_staff

    def recall(self, target, qs):
        for user in qs:
            recall_notification(
                CHAR_SHARED, user, data={'character': target.id}
            )

    def notify(self, user, target):
        if user != self.request.user:
            notify(
                CHAR_SHARED, user, data={'user': self.request.user.id, 'character': target.id},
                unique_data=True, mark_unread=True
            )


class Watchers(ListAPIView):
    serializer_class = RelatedUserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        return user.watched_by.all().order_by('username')


class Watching(ListAPIView):
    serializer_class = RelatedUserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        return user.watching.all().order_by('username')


class MessagesFrom(ListCreateAPIView):
    permission_classes = [IsUser]
    serializer_class = MessageSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageSerializer
        else:
            return MessageManagementSerializer

    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        message = serializer.save(sender=user)
        recipient_pks = [artist.pk for artist in serializer.validated_data.get('recipients', []) or []]
        users = available_users(self.request).filter(id__in=recipient_pks)
        if not users:
            message.delete()
            raise ValidationError({'recipients': ["No valid recipients provided."]})
        try:
            add_check(message, 'recipients', users)
        except ValidationError:
            raise ValidationError({'recipients': ["Too many recipients."]})
        MessageRecipientRelationship.objects.bulk_create(
            MessageRecipientRelationship(message=message, user=user) for user in users
        )
        for user in users:
            Subscription.objects.create(
                subscriber=user,
                content_type=ContentType.objects.get_for_model(model=message),
                object_id=message.id,
                type=COMMENT,
                email=True,
            )
            Subscription.objects.create(
                subscriber=user,
                content_type=ContentType.objects.get_for_model(model=message),
                object_id=message.id,
                type=NEW_PM,
                email=True,
            )
        Subscription.objects.get_or_create(
            subscriber=message.sender,
            content_type=ContentType.objects.get_for_model(model=message),
            object_id=message.id,
            email=True,
            type=COMMENT,
        )
        notify(NEW_PM, target=message)
        return message

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user.sent_messages.filter(sender_left=False).order_by('-last_activity')


class MessagesTo(ListAPIView):
    permission_classes = [IsUser]
    serializer_class = MessageManagementSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user.received_messages.all().order_by('-last_activity')


class MessageManager(RetrieveUpdateDestroyAPIView):
    permission_classes = [Any(All(Any(IsSafeMethod, IsMethod('PUT')), MessageReadPermission), MessageControls)]
    serializer_class = MessageManagementSerializer

    def get_object(self):
        message = get_object_or_404(Message, id=self.kwargs['message_id'])
        self.check_object_permissions(self.request, message)
        if self.request.user == message.sender:
            message.sender_read = True
            message.save()
        else:
            MessageRecipientRelationship.objects.filter(user=self.request.user, message=message).update(read=True)
        return message

    def perform_update(self, serializer: BaseSerializer) -> None:
        serializer.save(edited=True)


class MessageComments(ListCreateAPIView):
    permission_classes = [MessageReadPermission]
    serializer_class = CommentSerializer

    def get_queryset(self):
        message = get_object_or_404(Message, id=self.kwargs['message_id'])
        self.check_object_permissions(self.request, message)
        return message.comments.all()

    def perform_create(self, serializer):
        message = get_object_or_404(Message, id=self.kwargs['message_id'])
        self.check_object_permissions(self.request, message)
        serializer.save(user=self.request.user, content_object=message)

    class Meta:
        pass


class LeaveConversation(APIView):
    permission_classes = [MessageReadPermission]

    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id)
        self.check_object_permissions(self.request, message)
        if message.sender == request.user:
            message.sender_left = True
            message.save()
        MessageRecipientRelationship.objects.filter(user=request.user, message=message).delete()
        Subscription.objects.filter(
            subscriber=request.user, content_type=ContentType.objects.get_for_model(message),
            object_id=message.id
        ).delete()
        if (not message.recipients.all().exists()) and message.sender_left:
            recall_notification(NEW_PM, message)
            recall_notification(COMMENT, message)
            message.delete()
        else:
            Comment(user=self.request.user, system=True, content_object=message, text='left the conversation.').save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StartPasswordReset(APIView):
    permission_classes = [IsAnonymous]

    def post(self, request):
        identifier = request.data.get('email')
        if not identifier:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'email': ['This field is required.']})
        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username__iexact=identifier)
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'email': [
                            'We could not find this username or email address in our records. Please contact support.'
                        ]
                    }
                )
        if user_has_device(user):
            token = request.data.get('token')
            if not token:
                error = {
                    'token': ['This account is protected by Two-factor authentication. Please enter the 2FA code.']
                }
                for dev in devices_for_user(user):
                    try:
                        dev.generate_challenge()
                    except Exception as err:
                        # Sending this to email field since it might otherwise not be visible.
                        error['email'] = str(err)
                        error['token'] = str(err)
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data=error
                )
            if not match_token(user, token):
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={
                        'token': [
                            "That 2FA code is either invalid or expired."
                        ]
                    }
                )

        user.reset_token = uuid.uuid4()
        user.token_expiry = timezone.now() + relativedelta(days=1)
        user.save()
        subject = "Password reset request"
        to = [user.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        ctx = {
            'user': user,
        }
        message = get_template('profiles/email/password_reset.html').render(ctx)
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenValidator(APIView):
    def get(self, request, username, reset_token):
        get_object_or_404(User, username__iexact=username, reset_token=reset_token, token_expiry__gte=timezone.now())
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordReset(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def get_object(self):
        try:
            user = User.objects.get(
                username__iexact=self.kwargs['username'], reset_token=self.kwargs['reset_token'],
                token_expiry__gte=timezone.now()
            )
        except User.DoesNotExist:
            raise ValidationError(
                {'detail': ['This user does not exist or the token has expired. Please request a new reset link.']}
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
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class Journals(ListCreateAPIView):
    serializer_class = JournalSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        return Journal.objects.filter(user=user).order_by('-created_on')

    def perform_create(self, serializer):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        if self.request.user != user:
            raise ValidationError({'errors': ['You may not speak for someone else. Are you still logged in?']})
        journal = serializer.save(user=user)
        return journal


class JournalManager(RetrieveUpdateDestroyAPIView):
    serializer_class = JournalSerializer
    permission_classes = [Any(IsSafeMethod, All(IsMethod('PUT'), IsAuthenticated), ObjectControls)]

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        return get_object_or_404(Journal, user=user, id=self.kwargs['journal_id'])

    def put(self, request, *args, **kwargs):
        journal = self.get_object()
        data = {'subscribed': request.data.get('subscribed')}
        serializer = self.get_serializer(instance=journal, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class JournalComments(ListCreateAPIView):
    permission_classes = [JournalCommentPermission]
    serializer_class = CommentSerializer

    def get_queryset(self):
        journal = get_object_or_404(Journal, id=self.kwargs['journal_id'], user__username=self.kwargs['username'])
        self.check_object_permissions(self.request, journal)
        return journal.comments.all()

    def perform_create(self, serializer):
        journal = get_object_or_404(Journal, id=self.kwargs['journal_id'], user__username=self.kwargs['username'])
        self.check_object_permissions(self.request, journal)
        serializer.save(user=self.request.user, content_object=journal)

    class Meta:
        pass


@csrf_exempt
@api_view(['POST'])
def perform_logout(request):
    logout(request)
    request.session.pop('rating', None)
    return Response(status=status.HTTP_200_OK, data=empty_user(request))


class CharacterPreview(BasePreview):
    permission_classes = [Any(All(IsSafeMethod, SharedWith), ObjectControls)]

    def context(self, username, character):
        char_context = {}
        character = get_object_or_404(Character, user__username=username, name=character)
        if not self.check_object_permissions(self.request, character):
            return char_context
        char_context['title'] = demark(character.name)
        char_context['description'] = demark(character.description)
        char_context['image_link'] = character.preview_image(self.request)
        return char_context


class SubmissionPreview(BasePreview):
    permission_classes = [AssetViewPermission]

    def context(self, submission_id):
        submission = get_object_or_404(ImageAsset, id=submission_id)
        if not self.check_object_permissions(self.request, submission):
            return {}

        image = preview_rating(self.request, submission.rating, submission.preview_link)
        return {
            'title': demark(submission.title),
            'description': demark(submission.caption),
            'image_link': image
        }


class ReferralStats(APIView):
    permission_classes = [UserControls]

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username__iexact=kwargs.get('username'))
        self.check_object_permissions(self.request, user)
        return Response(status=status.HTTP_200_OK, data=ReferralStatsSerializer(user).data)


class MailingListPref(APIView):
    def post(self, request):
        request.user.offered_mailchimp = True
        request.user.save()
        mailchimp_subscribe.delay(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request):
        request.user.offered_mailchimp = True
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
