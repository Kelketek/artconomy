"""artconomy URL Configuration
"""
from django.conf.urls import url

from apps.sales.views import ProductListAPI, ProductManager, PlaceOrder, \
    OrderRetrieve, OrderAccept, OrderCancel, OrderList, SalesList, OrderComments, CardList, CardManager, \
    MakePrimary, AdjustOrder, MakePayment, OrderRevisions, DeleteOrderRevision, OrderStart

urlpatterns = [
    url(r'^v1/(?P<username>[-\w]+)/products/$', ProductListAPI.as_view(), name='product_list'),
    url(r'^v1/(?P<username>[-\w]+)/products/(?P<product>\d+)/$', ProductManager.as_view(), name='product_manager'),
    url(r'^v1/(?P<username>[-\w]+)/products/(?P<product>\d+)/order/$', PlaceOrder.as_view(), name='place_order'),
    url(r'^v1/(?P<username>[-\w]+)/orders/$', OrderList.as_view(), name='list_orders'),
    url(r'^v1/(?P<username>[-\w]+)/sales/$', SalesList.as_view(), name='list_sales'),
    url(r'^v1/(?P<username>[-\w]+)/cards/$', CardList.as_view(), name='list_cards'),
    url(r'^v1/(?P<username>[-\w]+)/cards/(?P<card_id>\d+)/$', CardManager.as_view(), name='card_manager'),
    url(r'^v1/(?P<username>[-\w]+)/cards/(?P<card_id>\d+)/primary/$', MakePrimary.as_view(), name='card_primary'),
    url(r'^v1/order/(?P<order_id>\d+)/$', OrderRetrieve.as_view(), name='order'),
    url(r'^v1/order/(?P<order_id>\d+)/comments/$', OrderComments.as_view(), name='order_comments'),
    url(r'^v1/order/(?P<order_id>\d+)/revisions/$', OrderRevisions.as_view(), name='order_revisions'),
    url(
        r'^v1/order/(?P<order_id>\d+)/revisions/(?P<revision_id>\d+)/$',
        DeleteOrderRevision.as_view(),
        name='delete_revision'
    ),
    url(r'^v1/order/(?P<order_id>\d+)/accept/$', OrderAccept.as_view(), name='accept_order'),
    url(r'^v1/order/(?P<order_id>\d+)/start/$', OrderStart.as_view(), name='start_order'),
    url(r'^v1/order/(?P<order_id>\d+)/adjust/$', AdjustOrder.as_view(), name='adjust_order'),
    url(r'^v1/order/(?P<order_id>\d+)/cancel/$', OrderCancel.as_view(), name='cancel_order'),
    url(r'^v1/order/(?P<order_id>\d+)/pay/$', MakePayment.as_view(), name='make_payment'),
]
