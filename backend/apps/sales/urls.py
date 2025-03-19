"""artconomy URL Configuration"""

from apps.sales.views import main, reports, stripe_views, webhooks
from django.urls import path, register_converter
from django.views.decorators.csrf import csrf_exempt
from short_stuff.django.converters import ShortCodeConverter

app_name = "sales"

register_converter(ShortCodeConverter, "short_code")


urlpatterns = [
    path("new-products/", main.NewProducts.as_view(), name="new_products"),
    path("featured-products/", main.FeaturedProducts.as_view(), name="new_products"),
    path("random-top-seller/", main.RandomTopSeller.as_view(), name="top_sellers"),
    path("highly-rated/", main.HighlyRatedProducts.as_view(), name="highly_rated"),
    path("low-price/", main.LowPriceProducts.as_view(), name="low_price_products"),
    path(
        "new-artist-products/",
        main.NewArtistProducts.as_view(),
        name="new_artist_products",
    ),
    path("lgbt/", main.LgbtProducts.as_view(), name="new_artist_products"),
    path(
        "artists-of-color/",
        main.ArtistsOfColor.as_view(),
        name="new_artist_products",
    ),
    path("cart/", main.UpdateCart.as_view(), name="update_cart"),
    path("random/", main.RandomProducts.as_view(), name="new_artist_products"),
    path("who-is-open/", main.WhoIsOpen.as_view(), name="who_is_open"),
    path("pricing-info/", main.PricingInfo.as_view(), name="pricing_info"),
    path("service-plans/", main.Plans.as_view(), name="service_plans"),
    path("vendor-invoices/", main.VendorInvoices.as_view(), name="vendor_invoices"),
    path("table-invoices/", main.TableInvoices.as_view(), name="table_invoices"),
    path("references/", main.References.as_view(), name="references"),
    path("table/products/", main.TableProducts.as_view(), name="table_products"),
    path("table/orders/", main.TableOrders.as_view(), name="table_orders"),
    path(
        "stripe-webhooks/",
        csrf_exempt(webhooks.StripeWebhooks.as_view()),
        name="stripe_webhooks",
        kwargs={"connect": False},
    ),
    path(
        "paypal-webhooks/<short_code:config_id>/",
        webhooks.PaypalWebhooks.as_view(),
        name="paypal_webhooks",
    ),
    path(
        "create-vendor-invoice/",
        main.CreateVendorInvoice.as_view(),
        name="create_vendor_invoice",
    ),
    path(
        "create-anonymous-invoice/",
        main.CreateAnonymousInvoice.as_view(),
        name="create_anonymous_invoice",
    ),
    path(
        "stripe-webhooks/connect/",
        csrf_exempt(webhooks.StripeWebhooks.as_view()),
        name="stripe_webhooks_connect",
        kwargs={"connect": True},
    ),
    path(
        "stripe-readers/",
        stripe_views.StripeReaders.as_view(),
        name="stripe_readers",
    ),
    path(
        "stripe-countries/",
        stripe_views.StripeCountries.as_view(),
        name="stripe_countries",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/outputs/",
        main.DeliverableOutputs.as_view(),
        name="deliverable_outputs",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/characters/",
        main.DeliverableCharacterList.as_view(),
        name="deliverable_character_list",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/",
        main.DeliverableRevisions.as_view(),
        name="deliverable_revisions",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/line-items/",
        main.DeliverableLineItems.as_view(),
        name="deliverable_line_items",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/line-items/<int:line_item_id>/",
        main.DeliverableLineItemManager.as_view(),
        name="line_item_manager",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/<int:revision_id>/",
        main.RevisionManager.as_view(),
        name="delete_revision",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/revisions/<int:revision_id>/approve/",
        main.ApproveRevision.as_view(),
        name="approve_revision",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/references/",
        main.DeliverableReferences.as_view(),
        name="deliverable_references",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/references/<reference_id>/",
        main.ReferenceManager.as_view(),
        name="deliverable_reference",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/accept/",
        main.DeliverableAccept.as_view(),
        name="accept_order",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/waitlist/",
        main.WaitlistOrder.as_view(),
        name="waitlist",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/make-new/",
        main.MakeNew.as_view(),
        name="make_new",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/start/",
        main.DeliverableStart.as_view(),
        name="start_order",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/cancel/",
        main.DeliverableCancel.as_view(),
        name="cancel_order",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/mark-paid/",
        main.MarkPaid.as_view(),
        name="mark_paid",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/approve/",
        main.ApproveFinal.as_view(),
        name="approve_final",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/dispute/",
        main.StartDispute.as_view(),
        name="approve_final",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/claim/",
        main.ClaimDispute.as_view(),
        name="deliverable_claim_dispute",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/complete/",
        main.MarkComplete.as_view(),
        name="deliverable_complete",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/reopen/",
        main.ReOpen.as_view(),
        name="deliverable_reopen",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/refund/",
        main.DeliverableRefund.as_view(),
        name="deliverable_refund",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/",
        main.DeliverableManager.as_view(),
        name="deliverable",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/rate/buyer/",
        main.RateBuyer.as_view(),
        name="deliverable_rate_buyer",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/rate/seller/",
        main.RateSeller.as_view(),
        name="deliverable_rate_seller",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/invite/",
        main.DeliverableInvite.as_view(),
        name="order_invite",
    ),
    path(
        "order/<int:order_id>/deliverables/<int:deliverable_id>/issue-tip-invoice/",
        main.IssueTipInvoice.as_view(),
        name="issue_tip_invoices",
    ),
    path(
        "order/<int:order_id>/deliverables/",
        main.OrderDeliverables.as_view(),
        name="order_deliverables",
    ),
    path("order/<int:order_id>/", main.OrderManager.as_view(), name="order"),
    path("search/product/", main.ProductSearch.as_view(), name="product_search"),
    path(
        "search/product/<username>/",
        main.PersonalProductSearch.as_view(),
        name="personal_product_search",
    ),
    path(
        "account/<username>/paypal/",
        main.PaypalSettings.as_view(),
        name="paypal_settings",
    ),
    path(
        "account/<username>/paypal/templates/",
        main.PaypalTemplates.as_view(),
        name="paypal_settings",
    ),
    path(
        "account/<username>/premium/intent/",
        stripe_views.PremiumPaymentIntent.as_view(),
        name="premium_intent",
    ),
    path("account/<username>/broadcast/", main.Broadcast.as_view(), name="broadcast"),
    path(
        "account/<username>/cancel-premium/",
        main.CancelPremium.as_view(),
        name="cancel_premium",
    ),
    path(
        "account/<username>/products/",
        main.ProductList.as_view(),
        name="product_list",
    ),
    path(
        "account/<username>/products/<int:product>/",
        main.ProductManager.as_view(),
        name="product_manager",
    ),
    path(
        "account/<username>/products/manage/",
        main.ProductList.as_view(),
        kwargs={"manage": True},
        name="product_list",
    ),
    path(
        "account/<username>/products/manage/<int:product>/",
        main.ProductManager.as_view(),
        name="product_manager",
    ),
    path(
        "account/<username>/products/manage/<int:product>/up/",
        main.StoreShift.as_view(),
        kwargs={"delta": 1},
        name="store_shift_up",
    ),
    path(
        "account/<username>/products/manage/<int:product>/down/",
        main.StoreShift.as_view(),
        kwargs={"delta": -1},
        name="store_shift_down",
    ),
    path(
        "account/<username>/products/<int:product>/clear-waitlist/",
        main.ClearWaitlist.as_view(),
        name="clear_waitlist",
    ),
    path(
        "account/<username>/products/<int:product>/feature/",
        main.FeatureProduct.as_view(),
        name="feature_product",
    ),
    path(
        "account/<username>/products/<int:product>/inventory/",
        main.ProductInventoryManager.as_view(),
        name="feature_product",
    ),
    path(
        "account/<username>/products/<int:product>/recommendations/",
        main.ProductRecommendations.as_view(),
        name="product_recommendations",
    ),
    path(
        "account/<username>/products/<int:product>/samples/",
        main.ProductSamples.as_view(),
        name="product_sample",
    ),
    path(
        "account/<username>/products/<int:product>/samples/<short_code:tag_id>/",
        main.ProductSampleManager.as_view(),
        name="product_sample_tags",
    ),
    path(
        "account/<username>/create-invoice/",
        main.CreateInvoice.as_view(),
        name="create_invoice",
    ),
    path("account/<username>/ratings/", main.RatingList.as_view(), name="rating_list"),
    path(
        "account/<username>/products/<int:product>/order/",
        main.PlaceOrder.as_view(),
        name="place_order",
    ),
    path(
        "account/<username>/orders/waiting/",
        main.WaitingOrderList.as_view(),
        name="waiting_orders",
    ),
    path(
        "account/<username>/orders/current/",
        main.CurrentOrderList.as_view(),
        name="current_orders",
    ),
    path(
        "account/<username>/orders/archived/",
        main.ArchivedOrderList.as_view(),
        name="archived_orders",
    ),
    path(
        "account/<username>/orders/cancelled/",
        main.CancelledOrderList.as_view(),
        name="archived_orders",
    ),
    path(
        "account/<username>/queue/",
        main.PublicSalesQueue.as_view(),
        name="public_queue",
    ),
    path(
        "account/<username>/sales/stats/",
        main.SalesStats.as_view(),
        name="sales_stats",
    ),
    path(
        "account/<username>/sales/current/",
        main.CurrentSalesList.as_view(),
        name="current_sales",
    ),
    path(
        "account/<username>/sales/archived/",
        main.ArchivedSalesList.as_view(),
        name="archived_sales",
    ),
    path(
        "account/<username>/sales/cancelled/",
        main.CancelledSalesList.as_view(),
        name="cancelled_sales",
    ),
    path(
        "account/<username>/sales/waiting/",
        main.WaitingSalesList.as_view(),
        name="waiting_sales",
    ),
    path(
        "account/<username>/cases/current/",
        main.CurrentCasesList.as_view(),
        name="current_cases",
    ),
    path(
        "account/<username>/cases/archived/",
        main.ArchivedCasesList.as_view(),
        name="archived_cases",
    ),
    path(
        "account/<username>/cases/cancelled/",
        main.CancelledCasesList.as_view(),
        name="cancelled_cases",
    ),
    path(
        "account/<username>/cases/waiting/",
        main.WaitingCasesList.as_view(),
        name="cancelled_cases",
    ),
    path("account/<username>/cards/", main.CardList.as_view(), name="list_cards"),
    path(
        "account/<username>/cards/stripe/",
        main.CardList.as_view(),
        name="list_cards",
        kwargs={"stripe": True},
    ),
    path(
        "account/<username>/cards/stripe/<int:card_id>/",
        main.CardManager.as_view(),
        name="card_manager",
    ),
    path(
        "account/<username>/cards/setup-intent/",
        stripe_views.SetupIntent.as_view(),
        name="setup_intent",
    ),
    path(
        "account/<username>/cards/<int:card_id>/",
        main.CardManager.as_view(),
        name="card_manager",
    ),
    path(
        "account/<username>/cards/<int:card_id>/primary/",
        main.MakePrimary.as_view(),
        name="card_primary",
    ),
    path(
        "account/<username>/balance/",
        main.AccountBalance.as_view(),
        name="account_balance",
    ),
    path("account/<username>/set-plan/", main.SetPlan.as_view(), name="set_plan"),
    path(
        "account/<username>/stripe-accounts/",
        stripe_views.StripeAccounts.as_view(),
        name="stripe_account_list",
    ),
    path(
        "account/<username>/stripe-accounts/link/",
        stripe_views.StripeAccountLink.as_view(),
        name="stripe_account_link",
    ),
    path(
        "account/<username>/stripe-accounts/dashboard-link/",
        stripe_views.StripeDashboardLink.as_view(),
        name="stripe_account_dashboard_link",
    ),
    path(
        "account/<username>/account-status/",
        main.AccountStatus.as_view(),
        name="account_status",
    ),
    path(
        "account/<username>/transactions/",
        main.AccountHistory.as_view(),
        name="account_history",
    ),
    path(
        "account/<username>/invoices/",
        main.UserInvoices.as_view(),
        name="user_invoices",
    ),
    path(
        "account/<username>/commissions-status-image/",
        main.CommissionStatusImage.as_view(),
        name="commissions-status-image",
    ),
    path(
        "invoice/<short_code:invoice>/",
        main.InvoiceDetail.as_view(),
        name="invoice_detail",
    ),
    path(
        "invoice/<short_code:invoice>/pay/",
        main.InvoicePayment.as_view(),
        name="invoice_payment",
    ),
    path(
        "invoice/<short_code:invoice>/finalize/",
        main.FinalizeInvoice.as_view(),
        name="invoice_finalize",
    ),
    path(
        "invoice/<short_code:invoice>/void/",
        main.VoidInvoice.as_view(),
        name="invoice_void",
    ),
    path(
        "invoice/<short_code:invoice>/payment-intent/",
        stripe_views.InvoicePaymentIntent.as_view(),
        name="invoice_intent",
    ),
    path(
        "invoice/<short_code:invoice>/stripe-process-present-card/",
        stripe_views.ProcessPresentCard.as_view(),
        name="invoice_stripe_process_present_card",
    ),
    path(
        "invoice/<short_code:invoice>/line-items/",
        main.InvoiceLineItems.as_view(),
        name="invoice_line_items",
    ),
    path(
        "invoice/<short_code:invoice>/transaction-records/",
        main.InvoiceTransactions.as_view(),
        name="invoice_transactions",
    ),
    path(
        "invoice/<short_code:invoice>/line-items/<int:line_item>/",
        main.InvoiceLineItemManager.as_view(),
        name="line_item_manager",
    ),
    path("order-auth/", main.OrderAuth.as_view(), name="order_auth"),
    path(
        "reports/customer-holdings/csv/",
        reports.CustomerHoldingsCSV.as_view(),
        name="customer_holdings_report_csv",
    ),
    path(
        "reports/order-values/csv/",
        reports.OrderValues.as_view(),
        name="order_values_csv",
    ),
    path(
        "reports/subscription-report/csv/",
        reports.SubscriptionReportCSV.as_view(),
        name="subscription_report_csv",
    ),
    path(
        "reports/payout-report/csv/",
        reports.PayoutReportCSV.as_view(),
        name="payout_report_csv",
    ),
    path(
        "reports/reconciliation-report/csv/",
        reports.ReconciliationReport.as_view(),
        name="reconciliation_report_csv",
    ),
    path(
        "reports/tip-report/csv/",
        reports.TipReportCSV.as_view(),
        name="tip_report_csv",
    ),
    path(
        "reports/unaffiliated-sales/csv/",
        reports.UnaffiliatedSaleReportCSV.as_view(),
        name="unaffiliated_sales_csv",
    ),
    path(
        "reports/troubled-deliverables/",
        reports.TroubledDeliverables.as_view(),
    ),
]
