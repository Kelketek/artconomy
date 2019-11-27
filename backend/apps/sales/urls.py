"""artconomy URL Configuration
"""
from django.urls import path
from apps.sales import views

app_name = 'sales'

urlpatterns = [
    path('v1/new-products/', views.NewProducts.as_view(), name='new_products'),
    path('v1/featured-products/', views.FeaturedProducts.as_view(), name='new_products'),
    path('v1/highly-rated/', views.HighlyRatedProducts.as_view(), name='highly_rated'),
    path('v1/low-price/', views.LowPriceProducts.as_view(), name='low_price_products'),
    path('v1/new-artist-products/', views.NewArtistProducts.as_view(), name='new_artist_products'),
    path('v1/random/', views.RandomProducts.as_view(), name='new_artist_products'),
    path('v1/who-is-open/', views.WhoIsOpen.as_view(), name='who_is_open'),
    path('v1/pricing-info/', views.PremiumInfo.as_view(), name='pricing_info'),
    path('v1/premium/', views.Premium.as_view(), name='premium'),
    path('v1/order/<int:order_id>/outputs/', views.OrderOutputs.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/characters/', views.OrderCharacterList.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/revisions/', views.OrderRevisions.as_view(), name='order_revisions'),
    path(
        'v1/order/<int:order_id>/revisions/<int:revision_id>/',
        views.DeleteOrderRevision.as_view(),
        name='delete_revision'
    ),
    path('v1/order/<int:order_id>/accept/', views.OrderAccept.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/start/', views.OrderStart.as_view(), name='start_order'),
    path('v1/order/<int:order_id>/cancel/', views.OrderCancel.as_view(), name='cancel_order'),
    path('v1/order/<int:order_id>/mark-paid/', views.MarkPaid.as_view(), name='mark_paid'),
    path('v1/order/<int:order_id>/pay/', views.MakePayment.as_view(), name='make_payment'),
    path('v1/order/<int:order_id>/approve/', views.ApproveFinal.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/dispute/', views.StartDispute.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/claim/', views.ClaimDispute.as_view(), name='order_claim'),
    path('v1/order/<int:order_id>/complete/', views.MarkComplete.as_view(), name='order_complete'),
    path('v1/order/<int:order_id>/invite/', views.OrderInvite.as_view(), name='order_invite'),
    path('v1/order/<int:order_id>/reopen/', views.ReOpen.as_view(), name='order_reopen'),
    path('v1/order/<int:order_id>/refund/', views.OrderRefund.as_view(), name='order_refund'),
    path('v1/order/<int:order_id>/rate/buyer/', views.RateBuyer.as_view(), name='order_rate_buyer'),
    path('v1/order/<int:order_id>/rate/seller/', views.RateSeller.as_view(), name='order_rate_seller'),
    path('v1/order/<int:order_id>/', views.OrderManager.as_view(), name='order'),
    path('v1/search/product/', views.ProductSearch.as_view(), name='product_search'),
    path('v1/search/product/mine/', views.PersonalProductSearch.as_view(), name='personal_product_search'),
    path('v1/account/<username>/cancel-premium/', views.CancelPremium.as_view(), name='cancel_premium'),
    path('v1/account/<username>/products/', views.ProductList.as_view(), name='product_list'),
    path('v1/account/<username>/products/<int:product>/', views.ProductManager.as_view(), name='product_manager'),
    path('v1/account/<username>/products/<int:product>/feature/', views.FeatureProduct.as_view(),
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
    path('v1/account/<username>/orders/current/', views.CurrentOrderList.as_view(), name='current_orders'),
    path('v1/account/<username>/orders/archived/', views.ArchivedOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/orders/cancelled/', views.CancelledOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/sales/stats/', views.SalesStats.as_view(), name='sales_stats'),
    path('v1/account/<username>/sales/current/', views.CurrentSalesList.as_view(), name='current_sales'),
    path('v1/account/<username>/sales/archived/', views.ArchivedSalesList.as_view(), name='archived_sales'),
    path('v1/account/<username>/sales/cancelled/', views.CancelledSalesList.as_view(), name='cancelled_sales'),
    path('v1/account/<username>/cases/current/', views.CurrentCasesList.as_view(), name='current_cases'),
    path('v1/account/<username>/cases/archived/', views.ArchivedCasesList.as_view(), name='archived_cases'),
    path('v1/account/<username>/cases/cancelled/', views.CancelledCasesList.as_view(), name='cancelled_cases'),
    path('v1/account/<username>/cards/', views.CardList.as_view(), name='list_cards'),
    path('v1/account/<username>/cards/<int:card_id>/', views.CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/<int:card_id>/primary/', views.MakePrimary.as_view(), name='card_primary'),
    path('v1/account/<username>/balance/', views.AccountBalance.as_view(), name='account_balance'),
    path('v1/account/<username>/banks/', views.BankAccounts.as_view(), name='bank_list'),
    path('v1/account/<username>/banks/<int:account>/', views.BankManager.as_view(), name='bank_manager'),
    path('v1/account/<username>/account-status/', views.AccountStatus.as_view(), name='account_status'),
    path('v1/account/<username>/transactions/', views.AccountHistory.as_view(), name='account_history'),
    path(
        'v1/account/<username>/commissions-status-image/',
        views.CommissionStatusImage.as_view(),
        name='commissions-status-image'
    ),
    path('v1/order-auth/', views.OrderAuth.as_view(), name='order_auth'),
    path('v1/reports/overview/', views.OverviewReport.as_view(), name='overview_report'),
    path('v1/reports/customer_holdings/', views.CustomerHoldings.as_view(), name='customer_holdings_report'),
]
