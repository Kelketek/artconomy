"""artconomy URL Configuration
"""
from django.conf.urls import url

from apps.profiles.views import Register, CharacterListAPI, ImageAssetListAPI, \
    CharacterManager, AssetManager, MakePrimary, SettingsAPI, CurrentUserInfo, AssetComments, CredentialsAPI, \
    register_dwolla, \
    NotificationsList, SetAvatar, UserInfo
from apps.profiles.views import check_username, check_email, perform_login, perform_logout

urlpatterns = [
    url('^v1/register_dwolla/', register_dwolla, name='register_dwolla'),
    url(r'^v1/form-validators/username/', check_username, name='username_validator'),
    url(r'^v1/form-validators/email/', check_email, name='email_validator'),
    url(r'^v1/login/', perform_login, name='login'),
    url(r'^v1/logout/', perform_logout, name='logout'),
    url(r'^v1/register/$', Register.as_view(), name='register'),
    url(r'^v1/data/requester/$', CurrentUserInfo.as_view(), name='current_user_info'),
    url(r'^v1/data/notifications/$', NotificationsList.as_view(), name='notifications'),
    url(r'^v1/data/user/(?P<username>[-\w]+)/', UserInfo.as_view(), name='user_info'),
    url(r'^v1/(?P<username>[-\w]+)/settings/$', SettingsAPI.as_view(), name='settings_update'),
    url(r'^v1/(?P<username>[-\w]+)/credentials/$', CredentialsAPI.as_view(), name='credentials'),
    url(r'^v1/(?P<username>[-\w]+)/avatar/$', SetAvatar.as_view(), name='avatar'),
    url(
        r'^v1/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/asset/primary/(?P<asset_id>\d+)/$',
        MakePrimary.as_view(), name='asset_primary'
    ),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/$',
        AssetManager.as_view(), name='asset_manager'
    ),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/comments/$',
        AssetComments.as_view(),
        name='asset_comments'
    ),
    url(
        r'^v1/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/assets/$',
        ImageAssetListAPI.as_view(), name='asset_upload'
    ),
    url(r'^v1/(?P<username>[-\w]+)/characters/$', CharacterListAPI.as_view(), name='character_list'),
    url(r'^v1/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/$', CharacterManager.as_view(), name='character'),
]
