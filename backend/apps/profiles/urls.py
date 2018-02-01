"""artconomy URL Configuration
"""
from django.conf.urls import url, include

from apps.profiles.views import Register, CharacterListAPI, ImageAssetListAPI, \
    CharacterManager, AssetManager, MakePrimary, SettingsAPI, CurrentUserInfo, AssetComments, CredentialsAPI, \
    register_dwolla, \
    NotificationsList, SetAvatar, UserInfo, CharacterSearch, AssetFavorite, MarkNotificationsRead, AssetTagCharacter, \
    UserSearch, AssetTagArtist, TagSearch, AssetTag, AssetSearch, CharacterTag, UserBlacklist, RefColorList, \
    RefColorManager
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
    url(r'^v1/data/notifications/mark-read/$', MarkNotificationsRead.as_view(), name='mark_read'),
    url(r'^v1/data/user/(?P<username>[-\w]+)/', UserInfo.as_view(), name='user_info'),
    url(r'^v1/search/character/$', CharacterSearch.as_view(), name='character_search'),
    url(r'^v1/search/user/$', UserSearch.as_view(), name='character_search'),
    url(r'^v1/search/tag/$', TagSearch.as_view(), name='tag_search'),
    url(r'^v1/search/asset/$', AssetSearch.as_view(), name='asset_search'),
    url(r'^v1/account/(?P<username>[-\w]+)/settings/$', SettingsAPI.as_view(), name='settings_update'),
    url(r'^v1/account/(?P<username>[-\w]+)/credentials/$', CredentialsAPI.as_view(), name='credentials'),
    url(r'^v1/account/(?P<username>[-\w]+)/avatar/$', SetAvatar.as_view(), name='avatar'),
    url(r'^v1/account/(?P<username>[-\w]+)/blacklist/$', UserBlacklist.as_view(), name='user_blacklist'),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/$',
        AssetManager.as_view(), name='asset_manager'
    ),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/tag-characters/$',
        AssetTagCharacter.as_view(), name='asset_character_tag'
    ),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/tag-artists/$',
        AssetTagArtist.as_view(), name='asset_artist_tag'
    ),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/tag/$',
        AssetTag.as_view(), name='asset_tag'
    ),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/comments/$',
        AssetComments.as_view(),
        name='asset_comments'
    ),
    url(
        r'^v1/asset/(?P<asset_id>\d+)/favorite/$',
        AssetFavorite.as_view(),
        name='asset_favorite'
    ),
    url(
        r'^v1/account/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/assets/$',
        ImageAssetListAPI.as_view(), name='asset_upload'
    ),
    url(r'^v1/account/(?P<username>[-\w]+)/characters/$', CharacterListAPI.as_view(), name='character_list'),
    url(
        r'^v1/account/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/$',
        CharacterManager.as_view(),
        name='character'
    ),
    url(
        r'^v1/account/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/tag/$',
        CharacterTag.as_view(),
        name='character_tag'
    ),
    url(
        r'^v1/account/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/colors/$',
        RefColorList.as_view(),
        name='character_colors'
    ),
    url(
        r'^v1/account/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/colors/(?P<ref_color_id>\d+)/$',
        RefColorManager.as_view(),
        name='color_manager'
    ),
    url(
        r'^v1/account/(?P<username>[-\w]+)/characters/(?P<character>[-\w\s]+)/asset/primary/(?P<asset_id>\d+)/$',
        MakePrimary.as_view(), name='asset_primary'
    ),
    url(r"^mfa/", include("deux.urls", namespace="mfa")),
    url(r"^mfa/authtoken/", include("deux.authtoken.urls", namespace="mfa-authtoken:login")),
]
