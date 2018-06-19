"""artconomy URL Configuration
"""
from django.urls import path

from apps.sales.views import ProductList, ProductManager, PlaceOrder, \
    OrderRetrieve, OrderAccept, OrderCancel, CurrentOrderList, CurrentSalesList, OrderComments, CardList, CardManager, \
    MakePrimary, AdjustOrder, MakePayment, OrderRevisions, DeleteOrderRevision, OrderStart, ApproveFinal, \
    ArchivedOrderList, CancelledOrderList, ArchivedSalesList, CancelledSalesList, ProductExamples, StartDispute, \
    OrderRefund, ClaimDispute, CurrentCasesList, ArchivedCasesList, CancelledCasesList, AccountBalance, \
    BankAccounts, ProductTag, ProductSearch, PerformWithdraw, BankManager, PurchaseHistory, EscrowHistory, \
    AvailableHistory, CreateCharacterTransfer, RetrieveCharacterTransfer, CharacterTransferAssets, AcceptCharTransfer, \
    CancelCharTransfer, CharactersInbound, CharactersOutbound, CharactersArchive, NewProducts, WhoIsOpen, \
    CurrentPlaceholderSalesList, PlaceholderManager, SalesStats, PublishFinal, RateOrder, RatingList, PremiumInfo, \
    Premium, CancelPremium

app_name = 'sales'

urlpatterns = [
    path('v1/new-products/', NewProducts.as_view(), name='new_products'),
    path('v1/who-is-open/', WhoIsOpen.as_view(), name='who_is_open'),
    path('v1/pricing-info/', PremiumInfo.as_view(), name='pricing_info'),
    path('v1/premium/', Premium.as_view(), name='premium'),
    path('v1/cancel-premium/', CancelPremium.as_view(), name='cancel_premium'),
    path('v1/order/<int:order_id>/comments/', OrderComments.as_view(), name='order_comments'),
    path('v1/order/<int:order_id>/revisions/', OrderRevisions.as_view(), name='order_revisions'),
    path(
        'v1/order/<int:order_id>/revisions/<int:revision_id>/',
        DeleteOrderRevision.as_view(),
        name='delete_revision'
    ),
    path('v1/order/<int:order_id>/accept/', OrderAccept.as_view(), name='accept_order'),
    path('v1/order/<int:order_id>/start/', OrderStart.as_view(), name='start_order'),
    path('v1/order/<int:order_id>/adjust/', AdjustOrder.as_view(), name='adjust_order'),
    path('v1/order/<int:order_id>/cancel/', OrderCancel.as_view(), name='cancel_order'),
    path('v1/order/<int:order_id>/pay/', MakePayment.as_view(), name='make_payment'),
    path('v1/order/<int:order_id>/approve/', ApproveFinal.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/dispute/', StartDispute.as_view(), name='approve_final'),
    path('v1/order/<int:order_id>/claim/', ClaimDispute.as_view(), name='order_claim'),
    path('v1/order/<int:order_id>/refund/', OrderRefund.as_view(), name='order_refund'),
    path('v1/order/<int:order_id>/publish/', PublishFinal.as_view(), name='order_publish'),
    path('v1/order/<int:order_id>/rating/', RateOrder.as_view(), name='order_rate'),
    path('v1/order/<int:order_id>/', OrderRetrieve.as_view(), name='order'),
    path('v1/search/product/', ProductSearch.as_view(), name='product_search'),
    path('v1/account/<username>/products/', ProductList.as_view(), name='product_list'),
    path('v1/account/<username>/products/<int:product>/', ProductManager.as_view(), name='product_manager'),
    path('v1/account/<username>/products/<int:product>/tag/', ProductTag.as_view(), name='product_tag'),
    path(
        'v1/account/<username>/products/<int:product>/examples/',
        ProductExamples.as_view(),
        name='product_examples'
    ),
    path('v1/account/<username>/ratings/', RatingList.as_view(), name='rating_list'),
    path('v1/account/<username>/products/<int:product>/order/', PlaceOrder.as_view(), name='place_order'),
    path('v1/account/<username>/orders/current/', CurrentOrderList.as_view(), name='current_orders'),
    path('v1/account/<username>/orders/archived/', ArchivedOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/orders/cancelled/', CancelledOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/sales/stats/', SalesStats.as_view(), name='sales_stats'),
    path('v1/account/<username>/sales/current/', CurrentSalesList.as_view(), name='current_sales'),
    path('v1/account/<username>/sales/archived/', ArchivedSalesList.as_view(), name='archived_sales'),
    path('v1/account/<username>/sales/cancelled/', CancelledSalesList.as_view(), name='cancelled_sales'),
    path(
        'v1/account/<username>/sales/current/placeholders/',
        CurrentPlaceholderSalesList.as_view(),
        name='current_placeholder_sales'
    ),
    path(
        'v1/account/<username>/sales/archived/placeholders/',
        ArchivedOrderList.as_view(),
        name='archived_placeholder_sales'
    ),
    path(
        'v1/account/<username>/sales/placeholder/<int:placeholder_id>/',
        PlaceholderManager.as_view(),
        name='placeholder_manager'
    ),
    path('v1/account/<username>/cases/current/', CurrentCasesList.as_view(), name='current_cases'),
    path('v1/account/<username>/cases/archived/', ArchivedCasesList.as_view(), name='archived_cases'),
    path('v1/account/<username>/cases/cancelled/', CancelledCasesList.as_view(), name='cancelled_cases'),
    path('v1/account/<username>/cards/', CardList.as_view(), name='list_cards'),
    path('v1/account/<username>/cards/<int:card_id>/', CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/<int:card_id>/primary/', MakePrimary.as_view(), name='card_primary'),
    path('v1/account/<username>/balance/', AccountBalance.as_view(), name='account_balance'),
    path('v1/account/<username>/banks/', BankAccounts.as_view(), name='bank_list'),
    path('v1/account/<username>/banks/<int:account>/', BankManager.as_view(), name='bank_manager'),
    path('v1/account/<username>/withdraw/', PerformWithdraw.as_view(), name='perform_withdraw'),
    path('v1/account/<username>/transactions/purchases/', PurchaseHistory.as_view(), name='purchase_history'),
    path('v1/account/<username>/transactions/escrow/', EscrowHistory.as_view(), name='escrow_history'),
    path('v1/account/<username>/transactions/available/', AvailableHistory.as_view(), name='available_history'),
    path(
        'v1/account/<username>/transfer/character/<character>/',
        CreateCharacterTransfer.as_view(),
        name='character_transfer_create'
    ),
    path(
        'v1/account/<username>/transfers/character/inbound/',
        CharactersInbound.as_view(),
        name='characters_inbound'
    ),
    path(
        'v1/account/<username>/transfers/character/outbound/',
        CharactersOutbound.as_view(),
        name='characters_outbound'
    ),
    path(
        'v1/account/<username>/transfers/character/archive/',
        CharactersArchive.as_view(),
        name='characters_archive'
    ),
    path(
        'v1/transfer/character/<int:transfer_id>/',
        RetrieveCharacterTransfer.as_view(),
        name='retrieve_character_transfer'
    ),
    path(
        'v1/transfer/character/<int:transfer_id>/pay/',
        AcceptCharTransfer.as_view(),
        name='accept_character_transfer'
    ),
    path(
        'v1/transfer/character/<int:transfer_id>/cancel/',
        CancelCharTransfer.as_view(),
        name='accept_character_transfer'
    ),
    path(
        'v1/transfer/character/<int:transfer_id>/assets/',
        CharacterTransferAssets.as_view(),
        name='character_transfer_assets'
    ),
]
