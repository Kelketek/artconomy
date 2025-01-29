####
# Processor selection constants.
####

STRIPE = "stripe"

AUTHORIZE = "authorize"

PROCESSOR_CHOICES = (
    # Note: We don't use Authorize.net anymore, but we keep record of old
    # transactions which did.
    (AUTHORIZE, "EVO Authorize.net"),
    (STRIPE, "Stripe"),
)

####
# Line Item constants.
####

BASE_PRICE = 0
ADD_ON = 1
SHIELD = 2
BONUS = 3
TIP = 4
TABLE_SERVICE = 5
TAX = 6
EXTRA = 7
PREMIUM_SUBSCRIPTION = 8
OTHER_FEE = 9
DELIVERABLE_TRACKING = 10
# Similar fee to shield, but when we're not handling escrow, such as after-order tips.
PROCESSING = 11
# Used when we're syncing from an outside invoice, but there's a discrepency. Paper over
# it by adding a static amount line item that handles the difference.
RECONCILIATION = 12

PRIORITY_MAP = {
    BASE_PRICE: 0,
    ADD_ON: 100,
    PREMIUM_SUBSCRIPTION: 110,
    DELIVERABLE_TRACKING: 115,
    OTHER_FEE: 120,
    TIP: 200,
    SHIELD: 300,
    BONUS: 300,
    TABLE_SERVICE: 300,
    PROCESSING: 300,
    EXTRA: 400,
    TAX: 600,
    RECONCILIATION: 1000,
}

LINE_ITEM_TYPES = (
    (BASE_PRICE, "Base Price"),
    (ADD_ON, "Add on or Discount"),
    (DELIVERABLE_TRACKING, "Deliverable Tracking Fee"),
    (OTHER_FEE, "Other fee"),
    (SHIELD, "Shield"),
    (BONUS, "Bonus"),
    (TIP, "Tip"),
    (TABLE_SERVICE, "Table Service"),
    (EXTRA, "Extra"),
    (TAX, "Tax"),
    (PREMIUM_SUBSCRIPTION, "Premium Subscription"),
    (PROCESSING, "Processing Fee"),
    (RECONCILIATION, "Reconciliation"),
)

LINE_ITEM_TYPES_TABLE = dict(LINE_ITEM_TYPES)

####
# Invoice constants.
####

DRAFT = 0
OPEN = 1
PAID = 2
VOID = 5

INVOICE_STATUSES = (
    (DRAFT, "Draft"),
    (OPEN, "Open"),
    (PAID, "Paid"),
    (VOID, "Void"),
)

SALE = 0
# Used when upgrading service plans
SUBSCRIPTION = 1
# Used for monthly billing costs
TERM = 2
# Used for tips, which are made after the main invoice
# has already been closed, or else independently.
TIPPING = 3
# Vendor invoices are invoices where we (as the platform) are paying a vendor for a
# service unrelated to commissions. NOTE: These invoices should not be paid by card,
# per Stripe's terms of service. They must be paid with Stripe funds.
VENDOR = 4

INVOICE_TYPES = (
    (SALE, "Sale"),
    (SUBSCRIPTION, "Subscription"),
    (TERM, "Term"),
    (TIPPING, "Tip"),
    (VENDOR, "Vendor"),
)

####
# Deliverable Constants
####

# In the user's waitlist
WAITING = 0
NEW = 1
PAYMENT_PENDING = 2
QUEUED = 3
IN_PROGRESS = 4
REVIEW = 5
CANCELLED = 6
DISPUTED = 7
COMPLETED = 8
REFUNDED = 9
# Order was placed, but user doesn't have access to it because they've hit their plan
# max.
LIMBO = 10
# Like cancelled, but for those orders which never made it out of limbo.
MISSED = 11

DELIVERABLE_STATUSES = (
    (WAITING, "Waiting List"),
    (NEW, "New"),
    (PAYMENT_PENDING, "Payment Pending"),
    (QUEUED, "Queued"),
    (IN_PROGRESS, "In Progress"),
    (REVIEW, "Review"),
    (CANCELLED, "Cancelled"),
    (DISPUTED, "Disputed"),
    (COMPLETED, "Completed"),
    (REFUNDED, "Refunded"),
    (LIMBO, "Limbo"),
    (MISSED, "Missed"),
)

PAID_STATUSES = (QUEUED, IN_PROGRESS, REVIEW, REFUNDED, COMPLETED)
WEIGHTED_STATUSES = (IN_PROGRESS, PAYMENT_PENDING, QUEUED)
# Used for counting against 'Max simultaneous orders'
CONCURRENCY_STATUSES = (NEW, PAYMENT_PENDING, QUEUED, IN_PROGRESS, DISPUTED, REVIEW)
# For all statuses where the artist has made some commitment they're seeing through.
WORK_IN_PROGRESS_STATUSES = (PAYMENT_PENDING, QUEUED, IN_PROGRESS, DISPUTED, REVIEW)
# Used for determining if a user has made a purchase, or is in the process of making
# one. Considers cases where the customer cancelled their order as not a purchase.
PURCHASED_STATUSES = (NEW, IN_PROGRESS, QUEUED, REVIEW, COMPLETED, DISPUTED, REFUNDED)


####
# Credit Card Constants
####

VISA = 1
MASTERCARD = 2
AMEX = 3
DISCOVER = 4
DINERS = 5
UNIONPAY = 6
JCB = 8
UNKNOWN = 9

CARD_TYPES = (
    (VISA, "Visa"),
    (MASTERCARD, "Mastercard"),
    (AMEX, "American Express"),
    (DISCOVER, "Discover"),
    (DINERS, "Diners Club"),
    (UNIONPAY, "UnionPay"),
)

TYPE_TRANSLATION = {
    "amex": AMEX,
    "discover": DISCOVER,
    "mc": MASTERCARD,
    "diners": DINERS,
    "visa": VISA,
    "mastercard": MASTERCARD,
    "unionpay": UNIONPAY,
}

# Status types
SUCCESS = 0
FAILURE = 1
PENDING = 2

TRANSACTION_STATUSES = (
    (SUCCESS, "Successful"),
    (FAILURE, "Failed"),
    (PENDING, "Pending"),
)

####
# Transaction constants
####

# Account types
CARD = 300
BANK = 301
ESCROW = 302
HOLDINGS = 303
# DEPRECATED: This used to be true and is no longer so. We now determine at the time of
# payment whether the amount to be taken is more or less due to landscape service.
# OLD NOTE, NO LONGER CORRECT: All fees put the difference for premium bonus into
# reserve until an order is complete. When complete, these amounts are deposited into
# either the cash account of Artconomy, or added to the user's holdings.
RESERVE = 304
# Earnings for which we have not yet subtracted card/bank transfer fees. DEPRECATED:
# Use FUND instead.
UNPROCESSED_EARNINGS = 305
# These two fee types will be used to keep track of fees that have been paid out to card
# processors.
CARD_TRANSACTION_FEES = 306
CARD_MISC_FEES = 307

# Fees from performing ACH transactions
ACH_TRANSACTION_FEES = 308
# Fees for other ACH-related items, like customer onboarding fees.
ACH_MISC_FEES = 309

# Tax held here until order finalized
MONEY_HOLE_STAGE = 310

# Where taxes go
MONEY_HOLE = 311

# Similar to money hole, when money is stolen and there's no getting it back,
# but a private actor instead of a public one. :/
FRAUD_LOSS = 312

# Staging account where the actual transaction coming in (like a card payment) is sent
# before splitting into different accounts from there.
FUND = 313

# For when a customer gives us cash, like at an event.
CASH_DEPOSIT = 407


# These next accounts are used to generate reports about what money was actually
# deposited into the payee's currency for tax purposes.

# The balance of this account will always be negative (or zero) and potentially
# incalculable because the currency could vary.
PAYOUT_MIRROR_SOURCE = 500
# The balance of this account will always be positive (or zero) and potentially
# incalculable because the currency could vary.
PAYOUT_MIRROR_DESTINATION = 501

ACCOUNT_TYPES = (
    (FUND, "Fund"),
    (CARD, "Credit Card"),
    (BANK, "Bank Account"),
    (ESCROW, "Escrow"),
    (HOLDINGS, "Finalized Earnings, available for withdraw"),
    (
        PAYOUT_MIRROR_SOURCE,
        "(Local Currency) Finalized Earnings, available for withdraw",
    ),
    (PAYOUT_MIRROR_DESTINATION, "(Local Currency) Bank Account"),
    (RESERVE, "Contingency reserve"),
    (CARD_TRANSACTION_FEES, "Card transaction fees"),
    (CARD_MISC_FEES, "Other card fees"),
    (CASH_DEPOSIT, "Cash deposit"),
    (ACH_TRANSACTION_FEES, "ACH Transaction fees"),
    (ACH_MISC_FEES, "Other ACH fees"),
    (MONEY_HOLE_STAGE, "Tax staging"),
    (MONEY_HOLE, "Tax"),
    (FRAUD_LOSS, "Fraud loss"),
)

# Transaction types
SHIELD_FEE = 400
ESCROW_HOLD = 401
ESCROW_RELEASE = 402
ESCROW_REFUND = 403
SUBSCRIPTION_DUES = 404
SUBSCRIPTION_REFUND = 405
CASH_WITHDRAW = 406
THIRD_PARTY_FEE = 408
# The extra money earned for subscribing to premium services and completing a sale.
PREMIUM_BONUS = 409
# 'Catch all' for any transfers between accounts.
INTERNAL_TRANSFER = 410
THIRD_PARTY_REFUND = 411
# For when we make a mistake and need to correct it somehow.
CORRECTION = 412
# For fees levied at conventions
TABLE_HANDLING = 413
TAXES = 414
# For things like inventory items sold at tables alongside the commission, like a pop
# socket.
EXTRA_ITEM = 415
# For times when we're manually sending money to others for specific services that the
# platform itself is paying for.
VENDOR_PAYMENT = 416
PAYOUT_REVERSAL = 417
# Used on items where we collect a slight processing fee, but not shield-level.
PROCESSING_FEE = 418
# For tips. Given a slightly different name to make sure it's a distinct value from the
# TIP and TIPPING consts.
TIP_SEND = 419
# Client charges a card or sends cash as one transaction before forking elsewhere.
FUNDING = 420

CATEGORIES = (
    (FUNDING, "Funding"),
    (SHIELD_FEE, "Artconomy Service Fee"),
    (PROCESSING_FEE, "Processing fee (non-shield)"),
    (ESCROW_HOLD, "Escrow hold"),
    (ESCROW_RELEASE, "Escrow release"),
    (ESCROW_REFUND, "Escrow refund"),
    (SUBSCRIPTION_DUES, "Subscription dues"),
    (SUBSCRIPTION_REFUND, "Refund for subscription dues"),
    (CASH_WITHDRAW, "Cash withdrawal"),
    (THIRD_PARTY_FEE, "Third party fee"),
    (PREMIUM_BONUS, "Premium service bonus"),
    (INTERNAL_TRANSFER, "Internal Transfer"),
    (THIRD_PARTY_REFUND, "Third party refund"),
    (EXTRA_ITEM, "Extra item"),
    (CORRECTION, "Correction"),
    (TABLE_SERVICE, "Table Service"),
    (TAXES, "Taxes"),
    (VENDOR_PAYMENT, "Vendor Payment"),
    (PAYOUT_REVERSAL, "Payout Reversal"),
    (TIP_SEND, "Tip"),
)


DEFAULT_TYPE_TO_CATEGORY_MAP = {
    BONUS: SHIELD_FEE,
    SHIELD: SHIELD_FEE,
    PROCESSING: PROCESSING_FEE,
    OTHER_FEE: THIRD_PARTY_FEE,
    TABLE_SERVICE: TABLE_HANDLING,
    TAX: TAXES,
    ADD_ON: ESCROW_HOLD,
    BASE_PRICE: ESCROW_HOLD,
    TIP: TIP_SEND,
    EXTRA: EXTRA_ITEM,
    PREMIUM_SUBSCRIPTION: SUBSCRIPTION_DUES,
    DELIVERABLE_TRACKING: SUBSCRIPTION_DUES,
}
