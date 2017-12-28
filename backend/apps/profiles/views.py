import requests
from avatar.models import Avatar
from avatar.signals import avatar_updated
from django.conf import settings
from django.contrib.auth import login, get_user_model, authenticate, logout, update_session_auth_hash
from django.db.models import Q, Case, When, Value, IntegerField, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, \
    GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lib.models import Notification
from apps.lib.permissions import Any, All, IsSafeMethod
from apps.lib.serializers import CommentSerializer, NotificationSerializer, Base64ImageField, RelatedUserSerializer
from apps.profiles.models import User, Character, ImageAsset
from apps.profiles.permissions import ObjectControls, UserControls, AssetViewPermission, AssetControls, NonPrivate
from apps.profiles.serializers import CharacterSerializer, ImageAssetSerializer, SettingsSerializer, UserSerializer, \
    RegisterSerializer, ImageAssetManagementSerializer, CredentialsSerializer, AvatarSerializer
from shortcuts import make_url


class Register(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()
        login(self.request, instance)

    def get_serializer(self, instance=None, data=None, many=False, partial=False):
        return self.serializer_class(instance=instance, data=data, many=many, partial=partial, request=self.request)


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


class CharacterListAPI(ListCreateAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        qs = Character.objects.filter(user__username__iexact=self.kwargs['username'])
        if not (self.request.user.username.lower() == username or self.request.user.is_staff):
            qs = qs.exclude(private=True)
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
        return serializer.save(user=user)


class ImageAssetListAPI(ListCreateAPIView):
    serializer_class = ImageAssetSerializer
    permission_classes = [ObjectControls]

    def get_queryset(self):
        char = get_object_or_404(
            Character, user__username__iexact=self.kwargs['username'], name=self.kwargs['character']
        )
        return char.assets.filter(rating__lte=self.request.max_rating)

    def perform_create(self, serializer):
        character = get_object_or_404(
            Character, user__username=self.kwargs['username'], name=self.kwargs['character']
        )
        self.check_object_permissions(self.request, character)
        asset = serializer.save(uploaded_by=self.request.user)
        asset.characters.add(character)
        if character.primary_asset is None:
            character.primary_asset = asset
            character.save()
        return asset


class CharacterManager(RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [Any([All([IsSafeMethod, NonPrivate]), ObjectControls])]

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
        return get_object_or_404(
            ImageAsset, id=self.kwargs['asset_id'], characters__user__username=self.kwargs['username'],
            characters__name=self.kwargs['character']
        )

    def post(self, *args, **kwargs):
        asset = self.get_object()
        char = get_object_or_404(Character, user__username=self.kwargs['username'], name=self.kwargs['character'])
        self.check_object_permissions(self.request, char)
        char.primary_asset = asset
        char.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssetManager(RetrieveUpdateDestroyAPIView):
    serializer_class = ImageAssetManagementSerializer
    permission_classes = [Any([All([IsSafeMethod, NonPrivate]), AssetControls])]

    def get_object(self):
        asset = get_object_or_404(
            ImageAsset, id=self.kwargs['asset_id'],
        )
        if not (self.request.user.is_staff or asset.uploaded_by == self.request.user):
            if self.request.method != 'GET':
                raise PermissionDenied("You do not have permission to edit this asset.")
            if asset.private:
                raise PermissionDenied("You do not have permission to view this submission.")
        return asset

    def destroy(self, request, *args, **kwargs):
        asset = self.get_object()
        self.check_object_permissions(request, asset)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        image_file = Base64ImageField().to_internal_value(request.data['avatar'])
        avatar.avatar.save(image_file.name, image_file)
        avatar.save()
        avatar_updated.send(sender=Avatar, user=request.user, avatar=avatar)
        Avatar.objects.filter(user=request.user).exclude(id=avatar.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserInfo(APIView):
    def get_serializer(self, user):
        if self.request.user.is_staff:
            return UserSerializer
        if self.request.user == user:
            return UserSerializer
        else:
            return RelatedUserSerializer

    def get_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get(self, request, **kwargs):
        user = self.get_user()
        if user:
            serializer_class = self.get_serializer(user)
            serializer = serializer_class(instance=user, request=request)
            data = serializer.data
        else:
            data = {}
        return Response(data=data, status=status.HTTP_200_OK)


class CurrentUserInfo(UserInfo):
    def get_user(self):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            return

    def get_serializer(self, user):
        return UserSerializer


class CharacterSearch(ListAPIView):
    serializer_class = CharacterSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        try:
            commissions = int(self.request.GET.get('new_order', '0'))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['New Order must be an integer.']})
        exclude = Q(private=True)
        if commissions:
            exclude |= Q(open_requests=False)
        # If staffer, allow search on behalf of user.
        if self.request.user.is_staff:
            user = get_object_or_404(User, id=self.request.GET.get('user', self.request.user.id))
        else:
            user = self.request.user
        if self.request.user.is_authenticated():
            return Character.objects.filter(
                name__istartswith=query
            ).exclude(exclude & ~Q(user=user)).annotate(
                # Make target user characters negative so they're always first.
                mine=Case(
                    When(user_id=user.id, then=0-F('id')),
                    default=F('id'),
                    output_field=IntegerField(),
                )
            ).order_by('mine')
        return Character.objects.filter(name__istartswith=query).exclude(private=True).order_by('id')


class NotificationsList(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return PermissionDenied("You must be authenticated to view notifications.")
        return Notification.objects.filter(user=self.request.user).select_related('event').order_by('event__date')


def register_dwolla(request):
    """
    Gets the return code from a Dwolla registration and applies it to a user.
    """
    if not request.user.is_authenticated:
        return HttpResponse(
            status=status.HTTP_403_FORBIDDEN, content="Please log in and then re-attempt to link your account."
        )
    code = request.GET.get('code', '')
    if not code:
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Code not provided.")
    result = requests.post(
        'https://{}.dwolla.com/oauth/v2/token'.format('sandbox' if settings.SANDBOX_APIS else 'www'),
        json={
            'client_id': settings.DWOLLA_KEY,
            'client_secret': settings.DWOLLA_SECRET,
            'code': code,
            "grant_type": "authorization_code",
            "redirect_uri": make_url(reverse('profiles:register_dwolla')),
        }
    )
    result.raise_for_status()
    request.user.dwolla_url = result.json()['_links']['account']['href']
    request.user.save()
    return redirect('/profiles/{}/'.format(request.user.username))


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


@csrf_exempt
@api_view(['POST'])
def perform_login(request):
    """
    Handle post action
    """
    error_message = ''
    # Gather the username and password provided by the user.
    # This information is obtained from the login form.
    email = str(request.data.get('email', request.POST.get('email', ''))).lower()
    password = request.data.get('password', request.POST.get('email', ''))
    # Use Django's machinery to attempt to see if the username/password
    # combination is valid - a User object is returned if it is.
    user = authenticate(email=email, password=password)

    # If we have a User object, the details are correct.
    # If None (Python's way of representing the absence of a value), no user
    # with matching credentials was found.
    if user:
        # Is the account active? It could have been disabled.
        if user.is_active:
            # If the account is valid and active, we can log the user in.
            # We'll send the user to their account.
            login(request, user)
        else:
            # An inactive account was used - no logging in!
            logout(request)
            error_message = "Your account is disabled. Please contact support"
    else:
        error_message = "Either this account does not exist, or the password is incorrect."

    status_code = status.HTTP_401_UNAUTHORIZED if error_message else status.HTTP_200_OK
    return Response(
        status=status_code,
        data={
            'email': [],
            'password': [error_message],
        }
    )


@csrf_exempt
@api_view(['POST'])
def perform_logout(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)
