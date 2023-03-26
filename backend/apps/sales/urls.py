"""artconomy URL Configuration
"""
from django.urls import path, register_converter
from django.views.decorators.csrf import csrf_exempt
from short_stuff.django.converters import ShortCodeConverter

from apps.sales.views import main
from apps.sales.views import reports
from apps.sales.views import stripe_views
from apps.sales.views import webhooks

app_name = 'sales'

register_converter(ShortCodeConverter, 'short_code')


urlpatterns = [
    path('v1/new-products/', main.NewProducts.as_view(), name='new_products'),
    path('v1/featured-products/', main.FeaturedProducts.as_view(), name='new_products'),
    path('v1/highly-rated/', main.HighlyRatedProducts.as_view(), name='highly_rated'),
    path('v1/low-price/', main.LowPriceProducts.as_view(), name='low_price_products'),
    path('v1/new-artist-products/', main.NewArtistProducts.as_view(), name='new_artist_products'),
    path('v1/lgbt/', main.LgbtProducts.as_view(), name='new_artist_products'),
    path('v1/artists-of-color/', main.ArtistsOfColor.as_view(), name='new_artist_products'),
    path('v1/random/', main.RandomProducts.as_view(), name='new_artist_products'),
    path('v1/who-is-open/', main.WhoIsOpen.as_view(), name='who_is_open'),
    path('v1/pricing-info/', main.PricingInfo.as_view(), name='pricing_info'),
    path('v1/service-plans/', main.Plans.as_view(), name='service_plans'),
    path('v1/recent-invoices/', main.TableInvoices.as_view(), name='recent_invoice'),
    path('v1/references/', main.References.as_view(), name='references'),
    path('v1/table/products/', main.TableProducts.as_view(), name='table_products'),
    path('v1/table/orders/', main.TableOrders.as_view(), name='table_orders'),
    path('v1/stripe-webhooks/', csrf_exempt(webhooks.StripeWebhooks.as_view()), name='stripe_webhooks', kwargs={'connect': False}),
    path('v1/create-anonymous-invoice/', main.CreateAnonymousInvoice.as_view(), name='create_anonymous_invoice'),
    path('v1/stripe-webhooks/connect/', csrf_exempt(webhooks.StripeWebhooks.as_view()), name='stripe_webhooks_connect', kwargs={'connect': True}),
    path('v1/stripe-readers/', stripe_views.StripeReaders.as_view(), name='stripe_readers'),
    path('v1/stripe-countries/', stripe_views.StripeCountries.as_view(), name='stripe_countries'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/outputs/', main.DeliverableOutputs.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/characters/', main.DeliverableCharacterList.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/', main.DeliverableRevisions.as_view(), name='deliverable_revisions'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/line-items/', main.DeliverableLineItems.as_view(), name='deliverable_line_items'),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/line-items/<int:line_item_id>/',
        main.DeliverableLineItemManager.as_view(),
        name='line_item_manager',
    ),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/<int:revision_id>/',
        main.RevisionManager.as_view(),
        name='delete_revision'
    ),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/<int:revision_id>/approve/',
        main.ApproveRevision.as_view(),
        name='approve_revision'
    ),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/references/',
        main.DeliverableReferences.as_view(),
        name='deliverable_references'
    ),
    path(
        'v1/order/<int:order_id>/deliverables/<int:deliverable_id>/references/<reference_id>/',
        main.ReferenceManager.as_view(),
        name='deliverable_reference'
    ),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/accept/', main.DeliverableAccept.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/waitlist/', main.WaitlistOrder.as_view(), name='waitlist'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/start/', main.DeliverableStart.as_view(), name='start_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/cancel/', main.DeliverableCancel.as_view(), name='cancel_order'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/mark-paid/', main.MarkPaid.as_view(), name='mark_paid'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/approve/', main.ApproveFinal.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/dispute/', main.StartDispute.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/claim/', main.ClaimDispute.as_view(), name='deliverable_claim_dispute'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/complete/', main.MarkComplete.as_view(), name='deliverable_complete'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/reopen/', main.ReOpen.as_view(), name='deliverable_reopen'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/refund/', main.DeliverableRefund.as_view(), name='deliverable_refund'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/', main.DeliverableManager.as_view(), name='deliverable'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/rate/buyer/', main.RateBuyer.as_view(), name='deliverable_rate_buyer'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/rate/seller/', main.RateSeller.as_view(), name='deliverable_rate_seller'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/invite/', main.DeliverableInvite.as_view(), name='order_invite'),
    path('v1/order/<int:order_id>/deliverables/<int:deliverable_id>/issue-tip-invoice/', main.IssueTipInvoice.as_view(), name='issue_tip_invoices'),
    path('v1/order/<int:order_id>/deliverables/', main.OrderDeliverables.as_view(), name='order_deliverables'),
    path('v1/order/<int:order_id>/', main.OrderManager.as_view(), name='order'),
    path('v1/search/product/', main.ProductSearch.as_view(), name='product_search'),
    path('v1/search/product/<username>/', main.PersonalProductSearch.as_view(), name='personal_product_search'),
    path('v1/account/<username>/premium/intent/', stripe_views.PremiumPaymentIntent.as_view(), name='premium_intent'),
    path('v1/account/<username>/broadcast/', main.Broadcast.as_view(), name='broadcast'),
    path('v1/account/<username>/cancel-premium/', main.CancelPremium.as_view(), name='cancel_premium'),
    path('v1/account/<username>/products/', main.ProductList.as_view(), name='product_list'),
    path('v1/account/<username>/products/<int:product>/', main.ProductManager.as_view(), name='product_manager'),
    path('v1/account/<username>/products/<int:product>/clear-waitlist/', main.ClearWaitlist.as_view(), name='clear_waitlist'),
    path('v1/account/<username>/products/<int:product>/feature/', main.FeatureProduct.as_view(),
         name='feature_product'),
    path('v1/account/<username>/products/<int:product>/inventory/', main.ProductInventoryManager.as_view(),
         name='feature_product'),
    path(
        'v1/account/<username>/products/<int:product>/recommendations/',
        main.ProductRecommendations.as_view(),
        name='product_recommendations'
    ),
    path(
        'v1/account/<username>/products/<int:product>/samples/',
        main.ProductSamples.as_view(),
        name='product_sample'
    ),
    path(
        'v1/account/<username>/products/<int:product>/samples/<int:tag_id>/',
        main.ProductSampleManager.as_view(),
        name='product_sample_tags'
    ),
    path('v1/account/<username>/create-invoice/', main.CreateInvoice.as_view(), name='create_invoice'),
    path('v1/account/<username>/ratings/', main.RatingList.as_view(), name='rating_list'),
    path('v1/account/<username>/products/<int:product>/order/', main.PlaceOrder.as_view(), name='place_order'),
    path('v1/account/<username>/orders/waiting/', main.WaitingOrderList.as_view(), name='waiting_orders'),
    path('v1/account/<username>/orders/current/', main.CurrentOrderList.as_view(), name='current_orders'),
    path('v1/account/<username>/orders/archived/', main.ArchivedOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/orders/cancelled/', main.CancelledOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/queue/', main.PublicSalesQueue.as_view(), name='public_queue'),
    path('v1/account/<username>/sales/stats/', main.SalesStats.as_view(), name='sales_stats'),
    path('v1/account/<username>/sales/current/', main.CurrentSalesList.as_view(), name='current_sales'),
    path('v1/account/<username>/sales/archived/', main.ArchivedSalesList.as_view(), name='archived_sales'),
    path('v1/account/<username>/sales/cancelled/', main.CancelledSalesList.as_view(), name='cancelled_sales'),
    path('v1/account/<username>/sales/waiting/', main.SearchWaiting.as_view(), name='waiting_sales'),
    path('v1/account/<username>/cases/current/', main.CurrentCasesList.as_view(), name='current_cases'),
    path('v1/account/<username>/cases/archived/', main.ArchivedCasesList.as_view(), name='archived_cases'),
    path('v1/account/<username>/cases/cancelled/', main.CancelledCasesList.as_view(), name='cancelled_cases'),
    path('v1/account/<username>/cases/waiting/', main.WaitingCasesList.as_view(), name='cancelled_cases'),
    path('v1/account/<username>/cards/', main.CardList.as_view(), name='list_cards'),
    path('v1/account/<username>/cards/stripe/', main.CardList.as_view(), name='list_cards', kwargs={'stripe': True}),
    path('v1/account/<username>/cards/stripe/<int:card_id>/', main.CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/setup-intent/', stripe_views.SetupIntent.as_view(), name='setup_intent'),
    path('v1/account/<username>/cards/<int:card_id>/', main.CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/<int:card_id>/primary/', main.MakePrimary.as_view(), name='card_primary'),
    path('v1/account/<username>/balance/', main.AccountBalance.as_view(), name='account_balance'),
    path('v1/account/<username>/set-plan/', main.SetPlan.as_view(), name='set_plan'),
    path('v1/account/<username>/stripe-accounts/', stripe_views.StripeAccounts.as_view(), name='stripe_account_list'),
    path('v1/account/<username>/stripe-accounts/link/', stripe_views.StripeAccountLink.as_view(), name='stripe_account_link'),
    path('v1/account/<username>/account-status/', main.AccountStatus.as_view(), name='account_status'),
    path('v1/account/<username>/transactions/', main.AccountHistory.as_view(), name='account_history'),
    path('v1/account/<username>/reports/payout/', reports.UserPayoutReportCSV.as_view(), name='account_payouts'),
    path('v1/account/<username>/invoices/', main.UserInvoices.as_view(), name='user_invoices'),
    path(
        'v1/account/<username>/commissions-status-image/',
        main.CommissionStatusImage.as_view(),
        name='commissions-status-image',
    ),
    path('v1/invoice/<short_code:invoice>/', main.InvoiceDetail.as_view(), name='invoice_detail'),
    path('v1/invoice/<short_code:invoice>/pay/', main.InvoicePayment.as_view(), name='invoice_payment'),
    path('v1/invoice/<short_code:invoice>/finalize/', main.FinalizeInvoice.as_view(), name='invoice_finalize'),
    path('v1/invoice/<short_code:invoice>/void/', main.VoidInvoice.as_view(), name='invoice_void'),
    path('v1/invoice/<short_code:invoice>/payment-intent/', stripe_views.InvoicePaymentIntent.as_view(), name='invoice_detail'),
    path(
        'v1/invoice/<short_code:invoice>/stripe-process-present-card/',
        stripe_views.ProcessPresentCard.as_view(),
        name='invoice_stripe_process_present_card',
    ),
    path('v1/invoice/<short_code:invoice>/line-items/', main.InvoiceLineItems.as_view(), name='invoice_line_items'),
    path('v1/invoice/<short_code:invoice>/transaction-records/', main.InvoiceTransactions.as_view(), name='invoice_transactions'),
    path('v1/invoice/<short_code:invoice>/line-items/<int:line_item>/', main.InvoiceLineItemManager.as_view(), name='line_item_manager'),
    path('v1/order-auth/', main.OrderAuth.as_view(), name='order_auth'),
    path('v1/reports/customer-holdings/csv/', reports.CustomerHoldingsCSV.as_view(), name='customer_holdings_report_csv'),
    path('v1/reports/order-values/csv/', reports.OrderValues.as_view(), name='order_values_csv'),
    path('v1/reports/subscription-report/csv/', reports.SubscriptionReportCSV.as_view(), name='subscription_report_csv'),
    path('v1/reports/payout-report/csv/', reports.PayoutReportCSV.as_view(), name='payout_report_csv'),
    path('v1/reports/tip-report/csv/', reports.TipReportCSV.as_view(), name='tip_report_csv'),
    path('v1/reports/unaffiliated-sales/csv/', reports.UnaffiliatedSaleReportCSV.as_view(), name='unaffiliated_sales_csv'),
]
