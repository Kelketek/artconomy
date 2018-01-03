from ddt import data, unpack, ddt
from freezegun import freeze_time
from mock import patch, Mock
from rest_framework import status

from apps.lib.test_resources import APITestCase
from apps.sales.models import Order, CreditCardToken
from apps.sales.tests.factories import OrderFactory, CreditCardTokenFactory

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

categories = [scenario['category'] for scenario in order_scenarios]


@ddt
class TestOrderListBase(object):
    @unpack
    @data(*order_scenarios)
    def test_fetch_orders(self, category, included, excluded):
        self.login(self.user)
        included_orders = [OrderFactory.create(status=order_status, **self.factory_kwargs()) for order_status in included]
        [OrderFactory.create(status=order_status, **self.factory_kwargs()) for order_status in excluded]
        response = self.client.get(self.make_url(category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(included_orders))
        for order in included_orders:
            self.assertIDInList(order, response.data['results'])

    @data(*categories)
    def test_not_logged_in(self, category):
        response = self.client.get('/api/sales/v1/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*categories)
    def test_wrong_user(self, category):
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*categories)
    def test_staff_user(self, category):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrderLists(TestOrderListBase, APITestCase):
    def make_url(self, category):
        return '/api/sales/v1/{}/orders/{}/'.format(self.user.username, category)

    def factory_kwargs(self):
        return {'buyer': self.user}


class TestSalesLists(TestOrderListBase, APITestCase):
    def make_url(self, category):
        return '/api/sales/v1/{}/sales/{}/'.format(self.user.username, category)

    def factory_kwargs(self):
        return {'seller': self.user}


class TestCardManagement(APITestCase):
    @freeze_time('2018-01-01')
    @patch('apps.sales.models.sauce')
    def test_add_card(self, card_api):
        self.login(self.user)
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/{}/cards/'.format(self.user.username),
            {
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], self.user.id)
        card = CreditCardToken.objects.get(user=self.user)
        self.assertEqual(card.payment_id, '12345|6789')

    @patch('apps.sales.models.sauce')
    def test_add_card_primary_exists(self, card_api):
        self.login(self.user)
        primary_card = CreditCardTokenFactory(user=self.user)
        self.user.primary_card = primary_card
        self.user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/{}/cards/'.format(self.user.username),
            {
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], False)
        self.assertEqual(response.data['user']['id'], self.user.id)
        self.assertEqual(CreditCardToken.objects.filter(user=self.user).count(), 2)
        self.user.refresh_from_db()
        self.assertEqual(self.user.primary_card.id, primary_card.id)

    @patch('apps.sales.models.sauce')
    def test_add_card_new_primary(self, card_api):
        self.login(self.user)
        CreditCardTokenFactory(user=self.user)
        # Side effect may create primary card. Manually set None.
        self.user.primary_card = None
        self.user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/{}/cards/'.format(self.user.username),
            {
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], self.user.id)
        self.assertEqual(CreditCardToken.objects.filter(user=self.user).count(), 2)
        self.user.refresh_from_db()
        self.assertEqual(self.user.primary_card.id, response.data['id'])

    @patch('apps.sales.models.sauce')
    def test_card_add_not_logged_in(self, card_api):
        primary_card = CreditCardTokenFactory(user=self.user)
        self.user.primary_card = primary_card
        self.user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/{}/cards/'.format(self.user.username),
            {
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.models.sauce')
    def test_add_card_wrong_user(self, card_api):
        self.login(self.user2)
        primary_card = CreditCardTokenFactory(user=self.user)
        self.user.primary_card = primary_card
        self.user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/{}/cards/'.format(self.user.username),
            {
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time('2018-01-01')
    @patch('apps.sales.models.sauce')
    def test_add_card_staffer(self, card_api):
        self.login(self.staffer)
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/{}/cards/'.format(self.user.username),
            {
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], self.user.id)
        card = CreditCardToken.objects.get(user=self.user)
        self.assertEqual(card.payment_id, '12345|6789')

    def test_make_primary(self):
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.login(self.user)
        self.user.refresh_from_db()
        response = self.client.post('/api/sales/v1/{}/cards/{}/primary/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertEqual(self.user.primary_card.id, cards[2].id)
        response = self.client.post('/api/sales/v1/{}/cards/{}/primary/'.format(self.user.username, cards[3].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertEqual(self.user.primary_card.id, cards[3].id)

    def test_make_primary_not_logged_in(self):
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.post('/api/sales/v1/{}/cards/{}/primary/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_wrong_user(self):
        self.login(self.user2)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.post('/api/sales/v1/{}/cards/{}/primary/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_wrong_card(self):
        [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.login(self.user)
        self.user.refresh_from_db()
        response = self.client.post('/api/sales/v1/{}/cards/{}/primary/'.format(
            self.user.username, CreditCardTokenFactory.create(user=self.user2).id
        ))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_card_listing(self):
        self.login(self.user)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/{}/cards/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data['results'])

    def test_card_listing_not_logged_in(self):
        response = self.client.get('/api/sales/v1/{}/cards/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_listing_staffer(self):
        self.login(self.staffer)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/{}/cards/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data['results'])

    def test_card_removal(self):
        self.login(self.user)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/{}/cards/{}/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)

    def test_card_removal_not_logged_in(self):
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/{}/cards/{}/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    def test_card_removal_wrong_user(self):
        self.login(self.user2)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/{}/cards/{}/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    def test_card_removal_staff(self):
        self.login(self.staffer)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/{}/cards/{}/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)