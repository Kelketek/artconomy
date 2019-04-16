"""artconomy URL Configuration
"""
from django.urls import path

from apps.profiles import views

app_name = "profiles"

urlpatterns = [
    path('v1/recent-submissions/', views.RecentSubmissions.as_view(), name='recent_submissions'),
    path('v1/recent-commissions/', views.RecentCommissions.as_view(), name='recent_commissions'),
    path('v1/recent-art/', views.RecentArt.as_view(), name='recent_art'),
    path('v1/watch-list-submissions/', views.WatchListSubmissions.as_view(), name='watch_list_submissions'),
    path('v1/new-characters/', views.NewCharacters.as_view(), name='new_characters'),
    path('v1/form-validators/username/', views.ValidateUsername.as_view(), name='username_validator'),
    path('v1/form-validators/email/', views.ValidateEmail.as_view(), name='email_validator'),
    path('v1/form-validators/password/', views.ValidatePassword.as_view(), name='email_validator'),
    path('v1/mailing-list-pref/', views.MailingListPref.as_view(), name='referral_stats'),
    path('v1/login/', views.perform_login, name='login'),
    path('v1/logout/', views.perform_logout, name='logout'),
    path('v1/register/', views.Register.as_view(), name='register'),
    path(
        'v1/forgot-password/token-check/<username>/<reset_token>/', views.TokenValidator.as_view(),
        name='reset_token_check'
    ),
    path(
        'v1/forgot-password/perform-reset/<username>/<reset_token>/', views.PasswordReset.as_view(),
        name='perform_reset'
    ),
    path('v1/forgot-password/', views.StartPasswordReset.as_view(), name='password_reset_start'),
    path('v1/data/requester/', views.CurrentUserInfo.as_view(), name='current_user_info'),
    path('v1/data/notifications/unread/', views.UnreadNotifications.as_view(), name='unread_notifications'),
    path('v1/data/notifications/mark-read/', views.MarkNotificationsRead.as_view(), name='mark_read'),
    path('v1/data/notifications/community/', views.CommunityNotificationsList.as_view(),
         name='community_notifications'),
    path('v1/data/notifications/sales/', views.SalesNotificationsList.as_view(), name='sales_notifications'),
    path('v1/data/user/id/<int:user_id>/', views.UserInfoByID.as_view(), name='user_info'),
    path('v1/search/character/', views.CharacterSearch.as_view(), name='character_search'),
    path('v1/search/character/indexed/', views.CharacterSearch.as_view(), name='indexed_character_search'),
    path('v1/search/user/', views.UserSearch.as_view(), name='character_search'),
    path('v1/search/tag/', views.TagSearch.as_view(), name='tag_search'),
    path('v1/search/submission/', views.SubmissionSearch.as_view(), name='submission_search'),
    path(
        'v1/account/<username>/artist-profile/', views.ArtistProfileSettings.as_view(),
        name='artist_profile_update',
    ),
    path('v1/account/<username>/auth/credentials/', views.CredentialsAPI.as_view(), name='credentials'),
    path(
        'v1/account/<username>/auth/two-factor/totp/<int:totp_id>/',
        views.TOTPDeviceManager.as_view(), name='totp_manager'
    ),
    path('v1/account/<username>/auth/two-factor/totp/', views.TOTPDeviceList.as_view(), name='totp_list'),
    path('v1/account/<username>/auth/two-factor/tg/', views.Telegram2FA.as_view(), name='telegram_2fa'),
    path('v1/account/<username>/referral_stats/', views.ReferralStats.as_view(), name='referral_stats'),
    path('v1/account/<username>/watching/', views.Watching.as_view(), name='watching'),
    path('v1/account/<username>/watchers/', views.Watchers.as_view(), name='watchers'),
    path('v1/account/<username>/avatar/', views.SetAvatar.as_view(), name='avatar'),
    path('v1/account/<username>/favorites/', views.FavoritesList.as_view(), name='favorites_list'),
    path('v1/account/<username>/journals/', views.Journals.as_view(), name='journal_list'),
    path('v1/account/<username>/journals/<int:journal_id>/', views.JournalManager.as_view(), name='journal'),
    path(
        'v1/account/<username>/submissions/', views.SubmissionList.as_view(), name='art_list',
    ),
    path(
        'v1/account/<username>/submissions/art/', views.FilteredSubmissionList.as_view(), kwargs={'is_artist': True},
        name='art_list',
    ),
    path(
        'v1/account/<username>/submissions/collection/', views.FilteredSubmissionList.as_view(),
        kwargs={'is_artist': False}, name='collection_list',
    ),
    path('v1/account/<username>/conversations/', views.Conversations.as_view(), name='conversations'),
    path(
        'v1/account/<username>/conversations/<int:message_id>/', views.ConversationManager.as_view(),
        name='conversation_manager',
    ),
    path('v1/account/<username>/', views.UserInfo.as_view(), name='user_info'),
    path(
        r'v1/submission/<int:submission_id>/characters/',
        views.SubmissionCharacterList.as_view(), name='submission_character_list'
    ),
    path(
        r'v1/submission/<int:submission_id>/characters/<int:tag_id>/',
        views.SubmissionCharacterManager.as_view(), name='submission_character_manager'
    ),
    path(
        r'v1/submission/<int:submission_id>/artists/',
        views.SubmissionArtistList.as_view(), name='submission_artist_list'
    ),
    path(
        r'v1/submission/<int:submission_id>/artists/<int:tag_id>/',
        views.SubmissionArtistManager.as_view(), name='submission_artist_manager'
    ),
    path(
        r'v1/submission/<int:submission_id>/share/',
        views.SubmissionSharedList.as_view(), name='submission_share'
    ),
    path(
        r'v1/submission/<int:submission_id>/share/<int:share_id>/',
        views.SubmissionSharedManager.as_view(), name='submission_share_manager'
    ),
    path(
        r'v1/submission/<int:submission_id>/recommended/',
        views.RecommendedSubmissions.as_view(), name='submission_recommendations'
    ),
    path(
        'v1/submission/<int:submission_id>/',
        views.SubmissionManager.as_view(), name='submission_manager'
    ),
    path(
        'v1/account/<username>/characters/<character>/submissions/',
        views.CharacterSubmissions.as_view(), name='submission_upload'
    ),
    path(
        'v1/account/<username>/characters/<character>/share/',
        views.CharacterSharedList.as_view(),
        name='character_share'
    ),
    path(
        'v1/account/<username>/characters/<character>/share/<int:share_id>/',
        views.CharacterSharedManager.as_view(),
        name='character_share_manager'
    ),
    path(
        'v1/account/<username>/characters/<character>/colors/',
        views.RefColorList.as_view(),
        name='character_colors'
    ),
    path(
        'v1/account/<username>/characters/<character>/colors/<int:ref_color_id>/',
        views.RefColorManager.as_view(),
        name='color_manager'
    ),
    path(
        'v1/account/<username>/characters/<character>/attributes/<int:attribute_id>/',
        views.AttributeManager.as_view(), name='attribute_manager'
    ),
    path(
        'v1/account/<username>/characters/<character>/attributes/',
        views.AttributeList.as_view(), name='attribute_list'
    ),
    path(
        'v1/account/<username>/characters/<character>/',
        views.CharacterManager.as_view(),
        name='character'
    ),
    path(r'v1/account/<username>/characters/', views.CharacterListAPI.as_view(), name='character_list'),
]
