from ddt import data, unpack, ddt
from rest_framework import status

from apps.lib.test_resources import APITestCase
from apps.sales.models import Order
from apps.sales.tests.factories import OrderFactory

order_scenarios = (
    {
        'category': 'current',
        'included': (Order.NEW, Order.IN_PROGRESS, Order.DISPUTED, Order.REVIEW),
        'excluded': (Order.CANCELLED, Order.COMPLETED)
    },
    {
        'category': 'archived',
        'included': (Order.COMPLETED, Order.COMPLETED),
        'excluded': (Order.NEW, Order.IN_PROGRESS, Order.DISPUTED, Order.REVIEW, Order.CANCELLED)
    },
    {
        'category': 'cancelled',
        'included': (Order.CANCELLED, Order.CANCELLED),
        'excluded': (Order.NEW, Order.IN_PROGRESS, Order.COMPLETED, Order.REVIEW, Order.DISPUTED)
    }
)


@ddt
class TestOrderLists(APITestCase):
    @unpack
    @data(*order_scenarios)
    def test_fetch_orders(self, category, included, excluded):
        self.login(self.user)
        included_orders = [OrderFactory.create(buyer=self.user, status=order_status) for order_status in included]
        [OrderFactory.create(buyer=self.user, status=order_status) for order_status in excluded]
        response = self.client.get('/api/sales/v1/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(included_orders))
        for order in included_orders:
            self.assertIDInList(order, response.data['results'])

    @data(*[scenario['category'] for scenario in order_scenarios])
    def test_not_logged_in(self, category):
        response = self.client.get('/api/sales/v1/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*[scenario['category'] for scenario in order_scenarios])
    def test_wrong_user(self, category):
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*[scenario['category'] for scenario in order_scenarios])
    def test_staff_user(self, category):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

@ddt
class TestSalesLists(APITestCase):
    @unpack
    @data(*order_scenarios)
    def test_fetch_sales(self, category, included, excluded):
        self.login(self.user)
        included_orders = [OrderFactory.create(seller=self.user, status=order_status) for order_status in included]
        [OrderFactory.create(seller=self.user, status=order_status) for order_status in excluded]
        response = self.client.get('/api/sales/v1/{}/sales/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(included_orders))
        for order in included_orders:
            self.assertIDInList(order, response.data['results'])

    @data(*[scenario['category'] for scenario in order_scenarios])
    def test_not_logged_in(self, category):
        response = self.client.get('/api/sales/v1/{}/sales/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*[scenario['category'] for scenario in order_scenarios])
    def test_wrong_user(self, category):
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/{}/sales/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*[scenario['category'] for scenario in order_scenarios])
    def test_staff_user(self, category):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/{}/sales/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
