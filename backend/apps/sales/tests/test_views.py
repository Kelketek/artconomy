from ddt import data, unpack, ddt
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time
from mock import patch
from rest_framework import status

from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import CharacterFactory
from apps.profiles.tests.helpers import gen_image
from apps.sales.models import Order, CreditCardToken, Product
from apps.sales.tests.factories import OrderFactory, CreditCardTokenFactory, ProductFactory

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


class TestProduct(APITestCase):
    def test_product_listing_logged_in(self):
        self.login(self.user)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        hidden = ProductFactory.create(user=self.user, hidden=True)
        ProductFactory.create(user=self.user, active=False)
        response = self.client.get('/api/sales/v1/{}/products/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        for product in products:
            self.assertIDInList(product, response.data['results'])
        self.assertIDInList(hidden, response.data['results'])

    def test_create_product(self):
        self.login(self.user)
        response = self.client.post(
            '/api/sales/v1/{}/products/'.format(self.user.username),
            {
                'category': Product.REFERENCE,
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3)
        self.assertEqual(result['category'], Product.REFERENCE)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_not_logged_in(self):
        response = self.client.post(
            '/api/sales/v1/{}/products/'.format(self.user.username),
            {
                'category': Product.REFERENCE,
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_wrong_user(self):
        self.login(self.user2)
        response = self.client.post(
            '/api/sales/v1/{}/products/'.format(self.user.username),
            {
                'category': Product.REFERENCE,
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_staff(self):
        self.login(self.staffer)
        response = self.client.post(
            '/api/sales/v1/{}/products/'.format(self.user.username),
            {
                'category': Product.REFERENCE,
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3)
        self.assertEqual(result['category'], Product.REFERENCE)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_listing_not_logged_in(self):
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        ProductFactory.create(user=self.user, hidden=True)
        ProductFactory.create(user=self.user, active=False)
        response = self.client.get('/api/sales/v1/{}/products/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_listing_other_user(self):
        self.login(self.user2)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        ProductFactory.create(user=self.user, hidden=True)
        ProductFactory.create(user=self.user, active=False)
        response = self.client.get('/api/sales/v1/{}/products/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_listing_staff(self):
        self.login(self.staffer)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        hidden = ProductFactory.create(user=self.user, hidden=True)
        ProductFactory.create(user=self.user, active=False)
        response = self.client.get('/api/sales/v1/{}/products/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        for product in products:
            self.assertIDInList(product, response.data['results'])
        self.assertIDInList(hidden, response.data['results'])

    def test_product_delete(self):
        self.login(self.user)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)

    def test_product_delete_not_logged_in(self):
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_wrong_user(self):
        self.login(self.user2)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_wrong_product(self):
        self.login(self.user)
        products = [ProductFactory.create(user=self.user2) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_staffer(self):
        self.login(self.staffer)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete('/api/sales/v1/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)


class TestOrder(APITestCase):
    def test_place_order(self):
        self.login(self.user)
        characters = [
            CharacterFactory.create(user=self.user).id,
            CharacterFactory.create(user=self.user, private=True).id,
            CharacterFactory.create(user=self.user2, open_requests=True).id
        ]
        product = ProductFactory.create()
        response = self.client.post(
            '/api/sales/v1/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['details'], 'Draw me some porn!')
        self.assertEqual(response.data['characters'], characters)
        self.assertEqual(response.data['product'], product.id)
        self.assertEqual(response.data['status'], Order.NEW)

    def test_place_order_hidden(self):
        self.login(self.user)
        characters = [
            CharacterFactory.create(user=self.user).id,
            CharacterFactory.create(user=self.user, private=True).id,
            CharacterFactory.create(user=self.user2, open_requests=True).id
        ]
        product = ProductFactory.create(hidden=True)
        response = self.client.post(
            '/api/sales/v1/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_adjust_order(self):
        raise AssertionError

    def test_adjust_order_buyer_fail(self):
        raise AssertionError

    def test_adjust_order_wrong_user(self):
        raise AssertionError

    def test_adjust_order_staff(self):
        raise AssertionError

    def test_accept_order(self):
        raise AssertionError

    def test_accept_order_buyer_fail(self):
        raise AssertionError

    def test_accept_order_wrong_user(self):
        raise AssertionError

    def test_accept_order_staffer(self):
        raise AssertionError

    def test_pay_order_amount_changed(self):
        raise AssertionError

    def test_pay_order_wrong_user(self):
        raise AssertionError

    def test_pay_order_seller_fail(self):
        raise AssertionError

    def test_pay_order_staffer(self):
        raise AssertionError

    def test_in_progress_buyer_fail(self):
        raise AssertionError

    def test_in_progress_wrong_user(self):
        raise AssertionError

    def test_place_order_unpermitted_character(self):
        self.login(self.user)
        characters = [
            CharacterFactory.create(user=self.user2, private=True).id,
        ]
        product = ProductFactory.create()
        response = self.client.post(
            '/api/sales/v1/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_place_order_not_logged_in(self):
        characters = [
            CharacterFactory.create(user=self.user2, private=True).id,
        ]
        product = ProductFactory.create()
        response = self.client.post(
            '/api/sales/v1/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
