"""artconomy URL Configuration
"""
from django.urls import path

from apps.profiles.views import Register, CharacterListAPI, CharacterAssets, \
    CharacterManager, AssetManager, MakePrimary, SettingsAPI, CurrentUserInfo, AssetComments, CredentialsAPI, \
    CommunityNotificationsList, SetAvatar, UserInfo, CharacterSearch, AssetFavorite, MarkNotificationsRead, \
    AssetTagCharacter, \
    UserSearch, AssetTagArtist, TagSearch, AssetTag, AssetSearch, CharacterTag, UserBlacklist, RefColorList, \
    RefColorManager, RecentSubmissions, RecentCommissions, NewCharacters, FavoritesList, GalleryList, SubmissionList, \
    AttributeManager, AttributeList, SessionSettings, AssetShare, CharacterShare, WatchUser, Watching, Watchers, \
    MessagesTo, MessagesFrom, MessageManager, MessageComments, LeaveConversation, BlockUser, StartPasswordReset, \
    TokenValidator, PasswordReset, Journals, JournalManager, JournalComments, SalesNotificationsList, \
    UnreadNotifications, WatchListSubmissions
from apps.profiles.views import check_username, check_email, perform_login, perform_logout

app_name = "profiles"


urlpatterns = [
    path('v1/session/settings/', SessionSettings.as_view(), name='session_settings'),
    path('v1/recent-submissions/', RecentSubmissions.as_view(), name='recent_submissions'),
    path('v1/recent-commissions/', RecentCommissions.as_view(), name='recent_commissions'),
    path('v1/watch-list-submissions/', WatchListSubmissions.as_view(), name='watch_list_submissions'),
    path('v1/new-characters/', NewCharacters.as_view(), name='new_characters'),
    path('v1/form-validators/username/', check_username, name='username_validator'),
    path('v1/form-validators/email/', check_email, name='email_validator'),
    path('v1/login/', perform_login, name='login'),
    path('v1/logout/', perform_logout, name='logout'),
    path('v1/register/', Register.as_view(), name='register'),
    path(
        'v1/forgot-password/token-check/<username>/<reset_token>/', TokenValidator.as_view(), name='reset_token_check'
    ),
    path(
        'v1/forgot-password/perform-reset/<username>/<reset_token>/', PasswordReset.as_view(), name='perform_reset'
    ),
    path('v1/forgot-password/', StartPasswordReset.as_view(), name='password_reset_start'),
    path('v1/data/requester/', CurrentUserInfo.as_view(), name='current_user_info'),
    path('v1/data/notifications/unread/', UnreadNotifications.as_view(), name='unread_notifications'),
    path('v1/data/notifications/mark-read/', MarkNotificationsRead.as_view(), name='mark_read'),
    path('v1/data/notifications/community/', CommunityNotificationsList.as_view(), name='community_notifications'),
    path('v1/data/notifications/sales/', SalesNotificationsList.as_view(), name='sales_notifications'),
    path('v1/data/user/<username>/', UserInfo.as_view(), name='user_info'),
    path('v1/search/character/', CharacterSearch.as_view(), name='character_search'),
    path('v1/search/user/', UserSearch.as_view(), name='character_search'),
    path('v1/search/tag/', TagSearch.as_view(), name='tag_search'),
    path('v1/search/asset/', AssetSearch.as_view(), name='asset_search'),
    path('v1/account/<username>/settings/', SettingsAPI.as_view(), name='settings_update'),
    path('v1/account/<username>/watching/', Watching.as_view(), name='watching'),
    path('v1/account/<username>/watchers/', Watchers.as_view(), name='watchers'),
    path('v1/account/<username>/credentials/', CredentialsAPI.as_view(), name='credentials'),
    path('v1/account/<username>/avatar/', SetAvatar.as_view(), name='avatar'),
    path('v1/account/<username>/blacklist/', UserBlacklist.as_view(), name='user_blacklist'),
    path('v1/account/<username>/favorites/', FavoritesList.as_view(), name='favorites_list'),
    path('v1/account/<username>/gallery/', GalleryList.as_view(), name='gallery_list'),
    path('v1/account/<username>/journals/', Journals.as_view(), name='journal_list'),
    path('v1/account/<username>/journals/<int:journal_id>/', JournalManager.as_view(), name='journal'),
    path(
        'v1/account/<username>/journals/<int:journal_id>/comments/', JournalComments.as_view(), name='journal_comments'
    ),
    path('v1/account/<username>/submissions/', SubmissionList.as_view(), name='submission_list'),
    path('v1/account/<username>/messages/inbox/', MessagesTo.as_view(), name='messages_to'),
    path('v1/account/<username>/messages/sent/', MessagesFrom.as_view(), name='messages_from'),
    path('v1/messages/<int:message_id>/', MessageManager.as_view(), name='message_manager'),
    path('v1/messages/<int:message_id>/leave/', LeaveConversation.as_view(), name='leave_conversation'),
    path('v1/messages/<int:message_id>/comments/', MessageComments.as_view(), name='message_comments'),
    path(
        r'v1/asset/<int:asset_id>/tag-characters/',
        AssetTagCharacter.as_view(), name='asset_character_tag'
    ),
    path(
        r'v1/asset/<int:asset_id>/tag-artists/',
        AssetTagArtist.as_view(), name='asset_artist_tag'
    ),
    path(
        r'v1/asset/<int:asset_id>/share/',
        AssetShare.as_view(), name='asset_share'
    ),
    path(
        'v1/asset/<int:asset_id>/tag/',
        AssetTag.as_view(), name='asset_tag'
    ),
    path(
        'v1/asset/<int:asset_id>/comments/',
        AssetComments.as_view(),
        name='asset_comments'
    ),
    path(
        'v1/asset/<int:asset_id>/favorite/',
        AssetFavorite.as_view(),
        name='asset_favorite'
    ),
    path(
        'v1/asset/<int:asset_id>/',
        AssetManager.as_view(), name='asset_manager'
    ),
    path(
        'v1/account/<username>/characters/<character>/assets/',
        CharacterAssets.as_view(), name='asset_upload'
    ),
    path(
        'v1/account/<username>/characters/<character>/tag/',
        CharacterTag.as_view(),
        name='character_tag'
    ),
    path(
        'v1/account/<username>/characters/<character>/share/',
        CharacterShare.as_view(),
        name='character_share'
    ),
    path(
        'v1/account/<username>/characters/<character>/colors/',
        RefColorList.as_view(),
        name='character_colors'
    ),
    path(
        'v1/account/<username>/characters/<character>/colors/<int:ref_color_id>/',
        RefColorManager.as_view(),
        name='color_manager'
    ),
    path(
        'v1/account/<username>/characters/<character>/asset/primary/<int:asset_id>/',
        MakePrimary.as_view(), name='asset_primary'
    ),
    path(
        'v1/account/<username>/characters/<character>/attributes/<int:attribute_id>/',
        AttributeManager.as_view(), name='attribute_manager'
    ),
    path(
        'v1/account/<username>/characters/<character>/attributes/',
        AttributeList.as_view(), name='attribute_list'
    ),
    path(
        'v1/account/<username>/characters/<character>/',
        CharacterManager.as_view(),
        name='character'
    ),
    path(r'v1/account/<username>/characters/', CharacterListAPI.as_view(), name='character_list'),
    path(r'v1/account/<username>/watch/', WatchUser.as_view(), name='watch_user'),
    path(r'v1/account/<username>/block/', BlockUser.as_view(), name='block_user')
]
