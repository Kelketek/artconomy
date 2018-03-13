"""artconomy URL Configuration
"""
from django.urls import path

from apps.sales.views import ProductListAPI, ProductManager, PlaceOrder, \
    OrderRetrieve, OrderAccept, OrderCancel, CurrentOrderList, CurrentSalesList, OrderComments, CardList, CardManager, \
    MakePrimary, AdjustOrder, MakePayment, OrderRevisions, DeleteOrderRevision, OrderStart, ApproveFinal, \
    ArchivedOrderList, CancelledOrderList, ArchivedSalesList, CancelledSalesList, ProductExamples, StartDispute, \
    OrderRefund, ClaimDispute, CurrentCasesList, ArchivedCasesList, CancelledCasesList, AccountBalance, \
    BankAccounts, ProductTag, ProductSearch, PerformWithdraw, BankManager

app_name = 'sales'

urlpatterns = [
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
    path('v1/order/<int:order_id>/', OrderRetrieve.as_view(), name='order'),
    path('v1/search/product/', ProductSearch.as_view(), name='product_search'),
    path('v1/account/<username>/products/', ProductListAPI.as_view(), name='product_list'),
    path('v1/account/<username>/products/<int:product>/', ProductManager.as_view(), name='product_manager'),
    path('v1/account/<username>/products/<int:product>/tag/', ProductTag.as_view(), name='product_tag'),
    path(
        'v1/account/<username>/products/<int:product>/examples/',
        ProductExamples.as_view(),
        name='product_examples'
    ),
    path('v1/account/<username>/products/<int:product>/order/', PlaceOrder.as_view(), name='place_order'),
    path('v1/account/<username>/orders/current/', CurrentOrderList.as_view(), name='current_orders'),
    path('v1/account/<username>/orders/archived/', ArchivedOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/orders/cancelled/', CancelledOrderList.as_view(), name='archived_orders'),
    path('v1/account/<username>/sales/current/', CurrentSalesList.as_view(), name='current_sales'),
    path('v1/account/<username>/sales/archived/', ArchivedSalesList.as_view(), name='archived_sales'),
    path('v1/account/<username>/sales/cancelled/', CancelledSalesList.as_view(), name='cancelled_sales'),
    path('v1/account/<username>/cases/current/', CurrentCasesList.as_view(), name='current_cases'),
    path('v1/account/<username>/cases/archived/', ArchivedCasesList.as_view(), name='archived_cases'),
    path('v1/account/<username>/cases/cancelled/', CancelledCasesList.as_view(), name='cancelled_cases'),
    path('v1/account/<username>/sales/', CurrentSalesList.as_view(), name='current_sales'),
    path('v1/account/<username>/cards/', CardList.as_view(), name='list_cards'),
    path('v1/account/<username>/cards/<int:card_id>/', CardManager.as_view(), name='card_manager'),
    path('v1/account/<username>/cards/<int:card_id>/primary/', MakePrimary.as_view(), name='card_primary'),
    path('v1/account/<username>/balance/', AccountBalance.as_view(), name='account_balance'),
    path('v1/account/<username>/banks/', BankAccounts.as_view(), name='account_balance'),
    path('v1/account/<username>/banks/<int:account>/', BankManager.as_view(), name='bank_manager'),
    path('v1/account/<username>/withdraw/', PerformWithdraw.as_view(), name='perform_withdraw')
]
