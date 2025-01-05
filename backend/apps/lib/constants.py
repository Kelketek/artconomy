"""
Constants for the lib app.
"""

NEW_CHARACTER = 0
WATCHING = 1
# Character tagged on submission, sent on character listener
CHAR_TAG = 3
COMMENT = 4
NEW_PRODUCT = 6
COMMISSIONS_OPEN = 7
# Character tagged on submission, sent on submission listener
NEW_CHAR_SUBMISSION = 8
SUBMISSION_TAG = 10
NEW_AUCTION = 11
ANNOUNCEMENT = 12
SYSTEM_ANNOUNCEMENT = 13
FAVORITE = 14
DISPUTE = 15
REFUND = 16
SUBMISSION_CHAR_TAG = 17
ORDER_UPDATE = 18
SALE_UPDATE = 19
ARTIST_TAG = 20
SUBMISSION_ARTIST_TAG = 21
REVISION_UPLOADED = 22
SUBMISSION_SHARED = 23
CHAR_SHARED = 24
STREAMING = 26
RENEWAL_FAILURE = 27
SUBSCRIPTION_DEACTIVATED = 28
RENEWAL_FIXED = 29
NEW_JOURNAL = 30
# ORDER_TOKEN_ISSUED = 31  -- Reserved for removed status.
TRANSFER_FAILED = 32
# REFERRAL_PORTRAIT_CREDIT = 33  -- Reserved for removed status
REFERRAL_LANDSCAPE_CREDIT = 34
REFERENCE_UPLOADED = 35
WAITLIST_UPDATED = 36
TIP_RECEIVED = 37
AUTO_CLOSED = 38
REVISION_APPROVED = 39
SUBMISSION_KILLED = 40
PRODUCT_KILLED = 41
EVENT_TYPES = (
    (NEW_CHARACTER, "New Character"),
    (WATCHING, "New Watcher"),
    (CHAR_TAG, "Character Tagged"),
    (COMMENT, "New Comment"),
    (COMMISSIONS_OPEN, "Commission Slots Available"),
    (NEW_PRODUCT, "New Product"),
    (NEW_AUCTION, "New Auction"),
    (ORDER_UPDATE, "Order Update"),
    (REVISION_UPLOADED, "Revision Uploaded"),
    (REFERENCE_UPLOADED, "Reference Uploaded"),
    (SALE_UPDATE, "Sale Update"),
    (DISPUTE, "Dispute Filed"),
    (REFUND, "Refund Processed"),
    (STREAMING, "Artist is streaming"),
    (NEW_CHAR_SUBMISSION, "New Submission of Character"),
    (SUBMISSION_SHARED, "Submission shared"),
    (CHAR_SHARED, "Character Shared"),
    (FAVORITE, "New Favorite"),
    (SUBMISSION_TAG, "Submission Tagged"),
    (SUBMISSION_CHAR_TAG, "Submission tagged with Character"),
    (ARTIST_TAG, "Tagged as the artist of a submission"),
    (SUBMISSION_ARTIST_TAG, "Tagged the artist of a submission"),
    (ANNOUNCEMENT, "Announcement"),
    (SYSTEM_ANNOUNCEMENT, "System-wide announcement"),
    (RENEWAL_FAILURE, "Renewal Failure"),
    (RENEWAL_FIXED, "Renewal Fixed"),
    (REFERRAL_LANDSCAPE_CREDIT, "Referral Landscape Credit"),
    (SUBSCRIPTION_DEACTIVATED, "Subscription Deactivated"),
    (NEW_JOURNAL, "New Journal Posted"),
    (TRANSFER_FAILED, "Bank Transfer Failed"),
    (WAITLIST_UPDATED, "Wait list updated"),
    (TIP_RECEIVED, "Tip Received"),
    (AUTO_CLOSED, "Commissions automatically closed"),
    (REVISION_APPROVED, "WIP Approved"),
    (SUBMISSION_KILLED, "Submission Killed"),
    (PRODUCT_KILLED, "Product Killed"),
)
ORDER_NOTIFICATION_TYPES = (
    DISPUTE,
    SALE_UPDATE,
    ORDER_UPDATE,
    RENEWAL_FIXED,
    RENEWAL_FAILURE,
    SUBSCRIPTION_DEACTIVATED,
    REVISION_UPLOADED,
    TRANSFER_FAILED,
    REFUND,
    REFERENCE_UPLOADED,
    WAITLIST_UPDATED,
    TIP_RECEIVED,
    AUTO_CLOSED,
    REVISION_APPROVED,
    PRODUCT_KILLED,
)
EMAIL_SUBJECTS = {
    COMMISSIONS_OPEN: "Commissions are open for {{ target.username }}!",
    ORDER_UPDATE: "Order #{{ target.order.id}} [{{target.name}}] has been updated!",
    REVISION_UPLOADED: "New revision for order #{{ target.order.id }} "
    "[{{target.name}}]!",
    REFERENCE_UPLOADED: "New reference for order #{{ target.order.id }} "
    "[{{target.name}}]!",
    SALE_UPDATE: "{% if target.status == 1 %}New Sale!{% elif target.status == 11 %}"
    "Your sale was cancelled.{% else %}Sale #{{ target.order.id }} "
    "[{{target.name}}] has been updated!{% endif %} #{{target.id}}",
    REFUND: "A refund was issued for Order #{{ target.order.id }} [{{target.name}}]",
    COMMENT: "{% if data.subject %}{{ data.subject }}{% else %}New comment on "
    "{{ data.name }}{% endif %}",
    RENEWAL_FAILURE: "Issue with your subscription",
    SUBSCRIPTION_DEACTIVATED: "Your subscription has been deactivated.",
    RENEWAL_FIXED: "Subscription renewed successfully",
    TRANSFER_FAILED: "Bank transfer failed.",
    REFERRAL_LANDSCAPE_CREDIT: "One of your referrals just made a sale!",
    WAITLIST_UPDATED: "A new order has been added to your waitlist!",
    AUTO_CLOSED: "Your commissions have been automatically closed.",
    REVISION_APPROVED: "Your WIP/Revision for Sale "
    "#{{ raw_target.deliverable.order.id }} "
    "[{{raw_target.deliverable.name}}] has been approved!",
    SUBMISSION_KILLED: "Your submission was removed.",
    PRODUCT_KILLED: "Your product was removed.",
}
IMPROPERLY_TAGGED = 0
IMPROPERLY_RATED = 1
SPAM_OR_NOT_ART = 2
COPYRIGHT_CLAIMED = 3
EXPLICIT_PHOTOGRAPHS = 4
ILLEGAL_CONTENT = 5

FLAG_REASONS = (
    (IMPROPERLY_TAGGED, "Improperly tagged"),
    (IMPROPERLY_RATED, "Improperly rated"),
    (SPAM_OR_NOT_ART, "Spammy Content"),
    (COPYRIGHT_CLAIMED, "Copyright Claimed"),
    (EXPLICIT_PHOTOGRAPHS, "Explicit Photographs"),
    (ILLEGAL_CONTENT, "Illegal Content"),
)

FLAG_LOOKUP = dict(FLAG_REASONS)

# Reasons that will get content purged, with a hash kept in order to prevent re-upload.
PURGE_REASONS = {ILLEGAL_CONTENT, EXPLICIT_PHOTOGRAPHS}

# Reasons that aren't grounds for removal in and of themselves, but which can
# result in disciplinary action.
RESTORABLE_REASONS = {SPAM_OR_NOT_ART, COPYRIGHT_CLAIMED}

# Reasons that won't get content removed, but may result in disciplinary action if
# multiple or flagrant issues arise for a user.
CATEGORIZATION_REASONS = {IMPROPERLY_TAGGED, IMPROPERLY_RATED}
