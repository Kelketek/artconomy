"""artconomy URL Configuration
"""
from apps.profiles import views
from django.urls import path, register_converter
from short_stuff.django.converters import ShortCodeConverter

app_name = "profiles"

register_converter(ShortCodeConverter, "short_code")

urlpatterns = [
    path(
        "recent-submissions/",
        views.RecentSubmissions.as_view(),
        name="recent_submissions",
    ),
    path(
        "community-submissions/",
        views.CommunitySubmissions.as_view(),
        name="community_submissions",
    ),
    path(
        "recent-commissions/",
        views.RecentCommissions.as_view(),
        name="recent_commissions",
    ),
    path("recent-art/", views.RecentArt.as_view(), name="recent_art"),
    path(
        "watch-list-submissions/",
        views.WatchListSubmissions.as_view(),
        name="watch_list_submissions",
    ),
    path("new-characters/", views.NewCharacters.as_view(), name="new_characters"),
    path(
        "form-validators/username/",
        views.ValidateUsername.as_view(),
        name="username_validator",
    ),
    path(
        "form-validators/email/",
        views.ValidateEmail.as_view(),
        name="email_validator",
    ),
    path(
        "form-validators/password/",
        views.ValidatePassword.as_view(),
        name="email_validator",
    ),
    path(
        "mailing-list-pref/",
        views.MailingListPref.as_view(),
        name="mailing_list_pref",
    ),
    path("login/", views.perform_login, name="login"),
    path("logout/", views.perform_logout, name="logout"),
    path("register/", views.Register.as_view(), name="register"),
    path(
        "forgot-password/token-check/<username>/<reset_token>/",
        views.TokenValidator.as_view(),
        name="reset_token_check",
    ),
    path(
        "forgot-password/perform-reset/<username>/<reset_token>/",
        views.PasswordReset.as_view(),
        name="perform_reset",
    ),
    path(
        "forgot-password/",
        views.StartPasswordReset.as_view(),
        name="password_reset_start",
    ),
    path("data/requester/", views.CurrentUserInfo.as_view(), name="current_user_info"),
    path(
        "data/notifications/unread/",
        views.UnreadNotifications.as_view(),
        name="unread_notifications",
    ),
    path(
        "data/notifications/mark-read/",
        views.MarkNotificationsRead.as_view(),
        name="mark_read",
    ),
    path(
        "data/notifications/community/",
        views.CommunityNotificationsList.as_view(),
        name="community_notifications",
    ),
    path(
        "data/notifications/sales/",
        views.SalesNotificationsList.as_view(),
        name="sales_notifications",
    ),
    path("data/user/id/<int:user_id>/", views.UserInfoByID.as_view(), name="user_info"),
    path(
        "data/character/id/<int:character_id>/",
        views.CharacterById().as_view(),
        name="character_info_by_id",
    ),
    path("search/character/", views.CharacterSearch.as_view(), name="character_search"),
    path(
        "search/character/indexed/",
        views.CharacterSearch.as_view(),
        name="indexed_character_search",
    ),
    path("search/user/", views.UserSearch.as_view(), name="character_search"),
    path("search/tag/", views.TagSearch.as_view(), name="tag_search"),
    path(
        "search/submission/",
        views.SubmissionSearch.as_view(),
        name="submission_search",
    ),
    path(
        "account/<username>/notification-settings/",
        views.NotificationSettings.as_view(),
        name="profile",
    ),
    path(
        "account/<username>/artist-profile/",
        views.ArtistProfileSettings.as_view(),
        name="artist_profile_update",
    ),
    path(
        "account/<username>/auth/credentials/",
        views.CredentialsAPI.as_view(),
        name="credentials",
    ),
    path(
        "account/<username>/auth/delete-account/",
        views.DestroyAccount.as_view(),
        name="destroy_account",
    ),
    path(
        "account/<username>/auth/two-factor/totp/<int:totp_id>/",
        views.TOTPDeviceManager.as_view(),
        name="totp_manager",
    ),
    path(
        "account/<username>/auth/two-factor/totp/",
        views.TOTPDeviceList.as_view(),
        name="totp_list",
    ),
    path(
        "account/<username>/auth/two-factor/tg/",
        views.Telegram2FA.as_view(),
        name="telegram_2fa",
    ),
    path(
        "account/<username>/referral_stats/",
        views.ReferralStats.as_view(),
        name="referral_stats",
    ),
    path("account/<username>/watching/", views.Watching.as_view(), name="watching"),
    path("account/<username>/watchers/", views.Watchers.as_view(), name="watchers"),
    path("account/<username>/avatar/", views.SetAvatar.as_view(), name="avatar"),
    path(
        "account/<username>/favorites/",
        views.FavoritesList.as_view(),
        name="favorites_list",
    ),
    path("account/<username>/journals/", views.Journals.as_view(), name="journal_list"),
    path(
        "account/<username>/journals/<int:journal_id>/",
        views.JournalManager.as_view(),
        name="journal",
    ),
    path(
        "account/<username>/submissions/",
        views.SubmissionList.as_view(),
        name="art_list",
    ),
    path(
        "account/<username>/submissions/sample-options/",
        views.RawArtistSubmissionList.as_view(),
        kwargs={"is_artist": True},
        name="art_list",
    ),
    path(
        "account/<username>/submissions/art/",
        views.ArtRelationList.as_view(),
        kwargs={"is_artist": True},
        name="art_list",
    ),
    path(
        "account/<username>/submissions/art/management/",
        views.ArtRelationList.as_view(),
        kwargs={"manage": True},
        name="art_relation_list",
    ),
    path(
        "account/<username>/submissions/art/management/<short_code:tag_id>/",
        views.ArtRelationManager.as_view(),
        name="art_relation_manager",
    ),
    path(
        "account/<username>/submissions/art/management/<short_code:tag_id>/up/",
        views.ArtRelationShift.as_view(),
        kwargs={"delta": 1},
        name="art_relation_shift_up",
    ),
    path(
        "account/<username>/submissions/art/management/<short_code:tag_id>/down/",
        views.ArtRelationShift.as_view(),
        kwargs={"delta": -1},
        name="art_relation_shift_down",
    ),
    path(
        "account/<username>/submissions/collection/",
        views.FilteredSubmissionList.as_view(),
        kwargs={"is_artist": False},
        name="collection_list",
    ),
    path(
        "account/<username>/submissions/collection/management/",
        views.FilteredSubmissionList.as_view(),
        kwargs={"is_artist": False},
        name="collection_list",
    ),
    path(
        "account/<username>/submissions/collection/management/<int:submission_id>/",
        views.SubmissionManager.as_view(),
    ),
    path(
        "account/<username>/submissions/collection/management/<int:submission_id>/up/",
        views.CollectionShift.as_view(),
        kwargs={"delta": 1},
        name="collection_shift_up",
    ),
    path(
        "account/<username>/submissions/collection/management/<int:submission_id>/down/",
        views.CollectionShift.as_view(),
        kwargs={"delta": -1},
        name="collection_shift_down",
    ),
    path(
        "account/<username>/conversations/",
        views.Conversations.as_view(),
        name="conversations",
    ),
    path(
        "account/<username>/conversations/<int:message_id>/",
        views.ConversationManager.as_view(),
        name="conversation_manager",
    ),
    path("account/<username>/", views.UserInfo.as_view(), name="user_info"),
    path(
        r"submission/<int:submission_id>/characters/",
        views.SubmissionCharacterList.as_view(),
        name="submission_character_list",
    ),
    path(
        r"submission/<int:submission_id>/characters/<short_code:tag_id>/",
        views.SubmissionCharacterManager.as_view(),
        name="submission_character_manager",
    ),
    path(
        r"submission/<int:submission_id>/artists/",
        views.SubmissionArtistList.as_view(),
        name="submission_artist_list",
    ),
    path(
        r"submission/<int:submission_id>/artists/<short_code:tag_id>/",
        views.SubmissionArtistManager.as_view(),
        name="submission_artist_manager",
    ),
    path(
        r"submission/<int:submission_id>/share/",
        views.SubmissionSharedList.as_view(),
        name="submission_share",
    ),
    path(
        r"submission/<int:submission_id>/share/<int:share_id>/",
        views.SubmissionSharedManager.as_view(),
        name="submission_share_manager",
    ),
    path(
        r"submission/<int:submission_id>/recommended/",
        views.RecommendedSubmissions.as_view(),
        name="submission_recommendations",
    ),
    path(
        "submission/<int:submission_id>/",
        views.SubmissionManager.as_view(),
        name="submission_manager",
    ),
    path(
        "account/<username>/characters/<character>/recommended/",
        views.RecommendedCharacters.as_view(),
        name="character_recommendations",
    ),
    path(
        "account/<username>/characters/<character>/submissions/",
        views.CharacterSubmissions.as_view(),
        name="submission_upload",
    ),
    path(
        "account/<username>/characters/<character>/share/",
        views.CharacterSharedList.as_view(),
        name="character_share",
    ),
    path(
        "account/<username>/characters/<character>/share/<int:share_id>/",
        views.CharacterSharedManager.as_view(),
        name="character_share_manager",
    ),
    path(
        "account/<username>/characters/<character>/colors/",
        views.RefColorList.as_view(),
        name="character_colors",
    ),
    path(
        "account/<username>/characters/<character>/colors/<int:ref_color_id>/",
        views.RefColorManager.as_view(),
        name="color_manager",
    ),
    path(
        "account/<username>/characters/<character>/attributes/<int:attribute_id>/",
        views.AttributeManager.as_view(),
        name="attribute_manager",
    ),
    path(
        "account/<username>/characters/<character>/attributes/",
        views.AttributeList.as_view(),
        name="attribute_list",
    ),
    path(
        "account/<username>/characters/<character>/",
        views.CharacterManager.as_view(),
        name="character",
    ),
    path(
        r"account/<username>/characters/",
        views.CharacterListAPI.as_view(),
        name="character_list",
    ),
]
