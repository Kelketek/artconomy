from datetime import date

from django.conf import settings
from django.contrib.auth import login, get_user_model, authenticate, logout
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.apis import dwolla_setup_link
from apps.lib.serializers import CommentSerializer
from apps.profiles.models import User, Character, ImageAsset
from apps.profiles.permissions import ObjectControls, UserControls, AssetViewPermission
from apps.profiles.serializers import CharacterSerializer, ImageAssetSerializer, SettingsSerializer, UserSerializer, \
    RegisterSerializer, ImageAssetManagementSerializer


class Register(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.save()
        login(self.request, serializer.instance)


class Dashboard(View):
    def get(self, request, username):
        target_user = get_object_or_404(User, username=username)
        return render(
            request, 'profiles/dashboard.html', {
                'dwolla_setup_link': dwolla_setup_link(),
                'target_user': target_user
            }
        )


class SettingsAPI(UpdateAPIView):
    serializer_class = SettingsSerializer
    permission_classes = [UserControls]

    def get_object(self):
        user = get_object_or_404(User, username__iexact=self.kwargs['username'])
        self.check_object_permissions(self.request, user)
        return user


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
        return char.assets.all()

    def perform_create(self, serializer):
        character = get_object_or_404(
            Character, user__username=self.kwargs['username'], name=self.kwargs['character']
        )
        self.check_object_permissions(self.request, character)
        asset = serializer.save(uploaded_by=self.request.user)
        asset.characters.add(character)
        return asset


class CharacterManager(RetrieveUpdateDestroyAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [ObjectControls]

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
    permission_classes = [ObjectControls]

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
        char = get_object_or_404(Character, user__username=self.kwargs['username'], name=self.kwargs['character'])
        self.check_object_permissions(request, char)
        if char.primary_asset == asset:
            char.primary_asset = None
        char.save()
        asset.characters.remove(char)
        if (asset.characters.all().count() == 0) or (self.request.user == asset.uploaded_by):
            self.perform_destroy(asset)
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


class UserInfo(APIView):
    def get(self, request):
        if request.user.is_authenticated():
            serializer = UserSerializer(request.user, request=request)
            data = serializer.data
        else:
            data = {}
        return Response(data=data, status=status.HTTP_200_OK)


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
            user = get_user_model().objects.get(id=user.id)
            user.last_action_date = date.today()
            user.save()
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
