"""artconomy URL Configuration
"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.sales import views

app_name = 'sales'

urlpatterns = [
    path('v1/new-products/', views.NewProducts.as_view(), name='new_products'),
    path('v1/featured-products/', views.FeaturedProducts.as_view(), name='new_products'),
    path('v1/highly-rated/', views.HighlyRatedProducts.as_view(), name='highly_rated'),
    path('v1/low-price/', views.LowPriceProducts.as_view(), name='low_price_products'),
    path('v1/new-artist-products/', views.NewArtistProducts.as_view(), name='new_artist_products'),
    path('v1/lgbt/', views.LgbtProducts.as_view(), name='new_artist_products'),
    path('v1/artists-of-color/', views.ArtistsOfColor.as_view(), name='new_artist_products'),
    path('v1/random/', views.RandomProducts.as_view(), name='new_artist_products'),
    path('v1/who-is-open/', views.WhoIsOpen.as_view(), name='who_is_open'),
    path('v1/pricing-info/', views.PremiumInfo.as_view(), name='pricing_info'),
    path('v1/premium/', views.Premium.as_view(), name='premium'),
    path('v1/premium/intent/', views.PremiumPaymentIntent.as_view(), name='premium_intent'),
    path('v1/references/', views.References.as_view(), name='references'),
    path('v1/stripe-webhooks/', csrf_exempt(views.StripeWebhooks.as_view()), name='stripe_webhooks', kwargs={'connect': False}),
    path('v1/stripe-webhooks/connect/', csrf_exempt(views.StripeWebhooks.as_view()), name='stripe_webhooks_connect', kwargs={'connect': True}),
    path('v1/stripe-countries/', views.StripeCountries.as_view(), name='stripe_countries'),
    # Pinterest requires the file name to have .csv on the end of it. We should see about doing a batch processing job
    # to dump completed files in a consistent place instead.
    path('v1/pinterest-catalog/', views.PinterestCatalog.as_view(), name='pinterest_catalog'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/outputs/', views.DeliverableOutputs.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/characters/', views.DeliverableCharacterList.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/', views.DeliverableRevisions.as_view(), name='deliverable_revisions'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/line-items/', views.DeliverableLineItems.as_view(), name='deliverable_line_items'),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/line-items/<int:line_item_id>/',
        views.LineItemManager.as_view(),
        name='line_item_manager',
    ),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/<int:revision_id>/',
        views.RevisionManager.as_view(),
        name='delete_revision'
    ),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/references/',
        views.DeliverableReferences.as_view(),
        name='deliverable_references'
    ),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/references/<reference_id>/',
        views.ReferenceManager.as_view(),
        name='deliverable_reference'
    ),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/accept/', views.DeliverableAccept.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/start/', views.DeliverableStart.as_view(), name='start_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/cancel/', views.DeliverableCancel.as_view(), name='cancel_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/mark-paid/', views.MarkPaid.as_view(), name='mark_paid'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/pay/', views.MakePayment.as_view(), name='make_payment'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/approve/', views.ApproveFinal.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/dispute/', views.StartDispute.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/claim/', views.ClaimDispute.as_view(), name='deliverable_claim_dispute'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/complete/', views.MarkComplete.as_view(), name='deliverable_complete'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/reopen/', views.ReOpen.as_view(), name='deliverable_reopen'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/refund/', views.DeliverableRefund.as_view(), name='deliverable_refund'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/', views.DeliverableManager.as_view(), name='deliverable'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/rate/buyer/', views.RateBuyer.as_view(), name='deliverable_rate_buyer'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/rate/seller/', views.RateSeller.as_view(), name='deliverable_rate_seller'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/payment-intent/', views.DeliverablePaymentIntent.as_view(), name='deliverable_payment_intent'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/invite/', views.DeliverableInvite.as_view(), name='order_invite'),
    path('v1/order/<int:order_id>/deliverables/', views.OrderDeliverables.as_view(), name='order_deliverables'),
    path('v1/order/<int:order_id>/', views.OrderManager.as_view(), name='order'),
    path('v1/search/product/', views.ProductSearch.as_view(), name='product_search'),
    path('v1/search/product/<username>/', views.PersonalProductSearch.as_view(), name='personal_product_search'),
    path('v1/account/<username>/broadcast/', views.Broadcast.as_view(), name='broadcast'),
    path('v1/account/<username>/cancel-premium/', views.CancelPremium.as_view(), name='cancel_premium'),
    path('v1/account/<username>/products/', views.ProductList.as_view(), name='product_list'),
    path('v1/account/<username>/products/<int:product>/', views.ProductManager.as_view(), name='product_manager'),
    path('v1/account/<username>/products/<int:product>/clear-waitlist/', views.ClearWaitlist.as_view(), name='clear_waitlist'),
    path('v1/account/<username>/products/<int:product>/feature/', views.FeatureProduct.as_view(),
         name='feature_product'),
    path('v1/account/<username>/products/<int:product>/inventory/', views.ProductInventoryManager.as_view(),
         name='feature_product'),
    path(
        'v1/account/<username>/products/<int:product>/recommendations/',
        views.ProductRecommendations.as_view(),
        name='product_recommendations'
    ),
    path(
        'v1/account/<username>/products/<int:product>/samples/',
        views.ProductSamples.as_view(),
        name='product_sample'
    ),
    path(
        'v1/account/<username>/products/<int:product>/samples/<int:tag_id>/',
        views.ProductSampleManager.as_view(),
        name='product_sample_tags'
    ),
    path('v1/account/<username>/create-invoice/', views.CreateInvoice.as_view(), name='create_invoice'),
    path('v1/account/<username>/ratings/', views.RatingList.as_view(), name='rating_list'),
    path('v1/account/<username>/products/<int:product>/order/', views.PlaceOrder.as_view(), name='place_order'),
    path('v1/account/<username>/orders/waiting/', views.WaitingOrderList.as_view(), name='waiting_orders'),
    path('v1/account/<username>/orders/current/', views.CurrentOrderList.as_view(), name='current_orders'),
    path('v1/account/<username>/orders/archived/', views.ArchivedOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/orders/cancelled/', views.CancelledOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/queue/', views.PublicSalesQueue.as_view(), name='public_queue'),
    path('v1/account/<username>/sales/stats/', views.SalesStats.as_view(), name='sales_stats'),
    path('v1/account/<username>/sales/current/', views.CurrentSalesList.as_view(), name='current_sales'),
    path('v1/account/<username>/sales/archived/', views.ArchivedSalesList.as_view(), name='archived_sales'),
    path('v1/account/<username>/sales/cancelled/', views.CancelledSalesList.as_view(), name='cancelled_sales'),
    path('v1/account/<username>/sales/waiting/', views.SearchWaiting.as_view(), name='waiting_sales'),
    path('v1/account/<username>/cases/current/', views.CurrentCasesList.as_view(), name='current_cases'),
    path('v1/account/<username>/cases/archived/', views.ArchivedCasesList.as_view(), name='archived_cases'),
    path('v1/account/<username>/cases/cancelled/', views.CancelledCasesList.as_view(), name='cancelled_cases'),
    path('v1/account/<username>/cards/', views.CardList.as_view(), name='list_cards'),
    path('v1/account/<username>/cards/stripe/', views.CardList.as_view(), name='list_cards', kwargs={'stripe': True}),
    path('v1/account/<username>/cards/stripe/<int:card_id>/', views.CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/authorize/', views.CardList.as_view(), name='list_cards', kwargs={'authorize': True}),
    path('v1/account/<username>/cards/authorize/<int:card_id>/', views.CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/setup-intent/', views.SetupIntent.as_view, name='setup_intent'),
    path('v1/account/<username>/cards/<int:card_id>/', views.CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/<int:card_id>/primary/', views.MakePrimary.as_view(), name='card_primary'),
    path('v1/account/<username>/balance/', views.AccountBalance.as_view(), name='account_balance'),
    path('v1/account/<username>/stripe-accounts/', views.StripeAccounts.as_view(), name='stripe_account_list'),
    path('v1/account/<username>/stripe-accounts/link/', views.StripeAccountLink.as_view(), name='stripe_account_link'),
    path('v1/account/<username>/banks/', views.BankAccounts.as_view(), name='bank_list'),
    path('v1/account/<username>/banks/fee-check/', views.WillIncurBankFee.as_view(), name='bank_fee_check'),
    path('v1/account/<username>/banks/<int:account>/', views.BankManager.as_view(), name='bank_manager'),
    path('v1/account/<username>/account-status/', views.AccountStatus.as_view(), name='account_status'),
    path('v1/account/<username>/transactions/', views.AccountHistory.as_view(), name='account_history'),
    path('v1/account/<username>/reports/payout/', views.UserPayoutReportCSV.as_view(), name='account_payouts'),
    path(
        'v1/account/<username>/commissions-status-image/',
        views.CommissionStatusImage.as_view(),
        name='commissions-status-image'
    ),
    path('v1/order-auth/', views.OrderAuth.as_view(), name='order_auth'),
    path('v1/reports/customer-holdings/', views.CustomerHoldings.as_view(), name='customer_holdings_report'),
    path('v1/reports/customer-holdings/csv/', views.CustomerHoldingsCSV.as_view(), name='customer_holdings_report_csv'),
    path('v1/reports/order-values/csv/', views.OrderValues.as_view(), name='order_values_csv'),
    path('v1/reports/subscription-report/csv/', views.SubscriptionReportCSV.as_view(), name='subscription_report_csv'),
    path('v1/reports/payout-report/csv/', views.PayoutReportCSV.as_view(), name='payout_report_csv'),
    path('v1/reports/dwolla-report/csv/', views.DwollaSetupFees.as_view(), name='dwolla_report_csv'),
]
