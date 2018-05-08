from unittest.mock import patch

from authorize import AuthorizeError
from ddt import data, unpack, ddt
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money, Decimal
from rest_framework import status

from apps.lib.abstract_models import ADULT, MATURE
from apps.lib.models import DISPUTE, Comment
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories import TagFactory
from apps.profiles.models import ImageAsset
from apps.profiles.tests.factories import CharacterFactory, UserFactory, ImageAssetFactory
from apps.profiles.tests.helpers import gen_image
from apps.sales.models import Order, CreditCardToken, Product, PaymentRecord
from apps.sales.tests.factories import OrderFactory, CreditCardTokenFactory, ProductFactory, RevisionFactory, \
    PaymentRecordFactory, BankAccountFactory, CharacterTransferFactory, PlaceholderSaleFactory

order_scenarios = (
    {
        'category': 'current',
        'included': (Order.NEW, Order.IN_PROGRESS, Order.DISPUTED, Order.REVIEW),
        'excluded': (Order.CANCELLED, Order.COMPLETED, Order.REFUNDED)
    },
    {
        'category': 'archived',
        'included': (Order.COMPLETED, Order.COMPLETED),
        'excluded': (Order.NEW, Order.IN_PROGRESS, Order.DISPUTED, Order.REVIEW, Order.CANCELLED, Order.REFUNDED)
    },
    {
        'category': 'cancelled',
        'included': (Order.REFUNDED, Order.CANCELLED),
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
        included_orders = [
            OrderFactory.create(status=order_status, **self.factory_kwargs()) for order_status in included
        ]
        [OrderFactory.create(status=order_status, **self.factory_kwargs()) for order_status in excluded]
        response = self.client.get(self.make_url(category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(included_orders))
        for order in included_orders:
            self.assertIDInList(order, response.data['results'])

    @data(*categories)
    def test_not_logged_in(self, category):
        response = self.client.get('/api/sales/v1/account/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*categories)
    def test_outsider(self, category):
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/account/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*categories)
    def test_staff_user(self, category):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/account/{}/orders/{}/'.format(self.user.username, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrderLists(TestOrderListBase, APITestCase):
    def make_url(self, category):
        return '/api/sales/v1/account/{}/orders/{}/'.format(self.user.username, category)

    def factory_kwargs(self):
        return {'buyer': self.user}


class TestSalesLists(TestOrderListBase, APITestCase):
    def make_url(self, category):
        return '/api/sales/v1/account/{}/sales/{}/'.format(self.user.username, category)

    def factory_kwargs(self):
        return {'seller': self.user}


class TestCasesLists(TestOrderListBase, APITestCase):
    def make_url(self, category):
        return '/api/sales/v1/account/{}/cases/{}/'.format(self.user.username, category)

    def factory_kwargs(self):
        self.user.is_staff = True
        self.user.save()
        return {'arbitrator': self.user}


class TestCardManagement(APITestCase):
    @freeze_time('2018-01-01')
    @patch('apps.sales.models.sauce')
    def test_add_card(self, card_api):
        self.login(self.user)
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(self.user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
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
            '/api/sales/v1/account/{}/cards/'.format(self.user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
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
            '/api/sales/v1/account/{}/cards/'.format(self.user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
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
            '/api/sales/v1/account/{}/cards/'.format(self.user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.models.sauce')
    def test_add_card_outsider(self, card_api):
        self.login(self.user2)
        primary_card = CreditCardTokenFactory(user=self.user)
        self.user.primary_card = primary_card
        self.user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(self.user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
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
            '/api/sales/v1/account/{}/cards/'.format(self.user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
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
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertEqual(self.user.primary_card.id, cards[2].id)
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(self.user.username, cards[3].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertEqual(self.user.primary_card.id, cards[3].id)

    def test_make_primary_not_logged_in(self):
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_outsider(self):
        self.login(self.user2)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_wrong_card(self):
        [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.login(self.user)
        self.user.refresh_from_db()
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(
            self.user.username, CreditCardTokenFactory.create(user=self.user2).id
        ))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_card_listing(self):
        self.login(self.user)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data['results'])

    def test_card_listing_not_logged_in(self):
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_listing_staffer(self):
        self.login(self.staffer)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data['results'])

    def test_card_removal(self):
        self.login(self.user)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)

    def test_card_removal_not_logged_in(self):
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    def test_card_removal_outsider(self):
        self.login(self.user2)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(self.user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    def test_card_removal_staff(self):
        self.login(self.staffer)
        cards = [CreditCardTokenFactory(user=self.user) for __ in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(self.user.username, cards[2].id))
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
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        for product in products:
            self.assertIDInList(product, response.data['results'])
        self.assertIDInList(hidden, response.data['results'])

    def test_create_product(self):
        self.login(self.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(self.user.username),
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
        self.assertEqual(result['expected_turnaround'], '3.00')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_not_logged_in(self):
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(self.user.username),
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

    def test_create_product_outsider(self):
        self.login(self.user2)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(self.user.username),
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
            '/api/sales/v1/account/{}/products/'.format(self.user.username),
            {
                'category': Product.REFERENCE,
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'rating': MATURE,
                'expected_turnaround': 3,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], '3.00')
        self.assertEqual(result['rating'], MATURE)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_listing_not_logged_in(self):
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        ProductFactory.create(user=self.user, hidden=True)
        ProductFactory.create(user=self.user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_listing_other_user(self):
        self.login(self.user2)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        ProductFactory.create(user=self.user, hidden=True)
        ProductFactory.create(user=self.user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_listing_staff(self):
        self.login(self.staffer)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        hidden = ProductFactory.create(user=self.user, hidden=True)
        ProductFactory.create(user=self.user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(self.user.username))
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
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)

    def test_product_delete_not_logged_in(self):
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_outsider(self):
        self.login(self.user2)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_wrong_product(self):
        self.login(self.user)
        products = [ProductFactory.create(user=self.user2) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_staffer(self):
        self.login(self.staffer)
        products = [ProductFactory.create(user=self.user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(self.user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)


class TestOrder(APITestCase):
    def test_place_order(self):
        self.login(self.user)
        characters = [
            CharacterFactory.create(user=self.user),
            CharacterFactory.create(user=self.user, private=True),
            CharacterFactory.create(user=self.user2, open_requests=True)
        ]
        character_ids = [character.id for character in characters]
        product = ProductFactory.create()
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': character_ids
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['details'], 'Draw me some porn!')
        self.assertEqual(response.data['characters'], character_ids)
        for character in characters:
            self.assertTrue(character.shared_with.filter(username=response.data['seller']['username']).exists())
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
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_adjust_order(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.adjustment, Money('2.03', 'USD'))

    def test_adjust_order_too_low(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, product__price=Money('15.00', 'USD'))
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '-14.50'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        self.assertEqual(order.adjustment, Money('0', 'USD'))

    def test_adjust_order_buyer_fail(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user2, buyer=self.user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_order_outsider(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user2)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_order_not_logged_in(self):
        order = OrderFactory.create(seller=self.user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_order_staff(self):
        self.login(self.staffer)
        order = OrderFactory.create(seller=self.user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.adjustment, Money('2.03', 'USD'))

    def test_in_progress(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, status=Order.QUEUED)
        response = self.client.patch(
            '/api/sales/v1/order/{}/start/'.format(order.id),
            {
                'stream_link': 'https://streaming.artconomy.com/'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.stream_link, 'https://streaming.artconomy.com/')

    def test_in_progress_buyer_fail(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user2, buyer=self.user, status=Order.QUEUED)
        response = self.client.patch(
            '/api/sales/v1/order/{}/start/'.format(order.id),
            {
                'stream_link': 'https://streaming.artconomy.com/'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.stream_link, '')

    def test_in_progress_outsider_fail(self):
        self.login(self.user)
        order = OrderFactory.create(status=Order.QUEUED)
        response = self.client.patch(
            '/api/sales/v1/order/{}/start/'.format(order.id),
            {
                'stream_link': 'https://streaming.artconomy.com/'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.stream_link, '')

    def test_in_progress_staffer(self):
        self.login(self.staffer)
        order = OrderFactory.create(status=Order.QUEUED)
        response = self.client.patch(
            '/api/sales/v1/order/{}/start/'.format(order.id),
            {
                'stream_link': 'https://streaming.artconomy.com/'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.stream_link, 'https://streaming.artconomy.com/')

    def test_no_cancel_queued(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, status=Order.QUEUED)
        response = self.client.post(
            '/api/sales/v1/order/{}/cancel/'.format(order.id),
            {
                'stream_link': 'https://streaming.artconomy.com/'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_upload(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, status=Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertEqual(response.data['rating'], ADULT)

    def test_revision_upload_buyer_fail(self):
        self.login(self.user)
        order = OrderFactory.create(buyer=self.user, status=Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_upload_outsider_fail(self):
        self.login(self.user)
        order = OrderFactory.create(status=Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_upload_staffer(self):
        self.login(self.staffer)
        order = OrderFactory.create(seller=self.user, status=Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], self.staffer.username)
        self.assertEqual(response.data['rating'], ADULT)

    def test_revision_upload_final(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, status=Order.IN_PROGRESS, revisions=2)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.REVIEW)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.REVIEW)

    def test_delete_revision(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, status=Order.IN_PROGRESS)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 0)

    def test_delete_revision_reactivate(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, status=Order.REVIEW)
        revision = RevisionFactory.create(order=order)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(order.status, Order.IN_PROGRESS)

    def test_delete_revision_locked(self):
        self.login(self.user)
        order = OrderFactory.create(seller=self.user, status=Order.COMPLETED)
        revision = RevisionFactory.create(order=order)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.status = Order.DISPUTED
        order.save()
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_revision_buyer_fail(self):
        self.login(self.user)
        order = OrderFactory.create(buyer=self.user, status=Order.IN_PROGRESS)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 1)

    def test_delete_revision_outsider_fail(self):
        self.login(self.user)
        order = OrderFactory.create(status=Order.IN_PROGRESS)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 1)

    def test_delete_revision_not_logged_in_fail(self):
        order = OrderFactory.create(status=Order.IN_PROGRESS)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 1)

    def test_delete_revision_staffer(self):
        self.login(self.staffer)
        order = OrderFactory.create(seller=self.user, status=Order.IN_PROGRESS)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order(self, card_api):
        self.login(self.user)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        record = PaymentRecord.objects.get(txn_id='Trans123')
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.source, PaymentRecord.CARD)
        self.assertEqual(record.escrow_for, order.seller)
        self.assertEqual(record.target, order)
        self.assertEqual(record.amount, Money('12.00', 'USD'))
        self.assertEqual(record.payer, self.user)
        self.assertEqual(record.payee, None)

    @patch('apps.sales.models.sauce')
    def test_pay_order_cvv_missing(self, card_api):
        self.login(self.user)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user).id,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(PaymentRecord.DoesNotExist, PaymentRecord.objects.get, txn_id='Trans123')

    @patch('apps.sales.models.sauce')
    def test_pay_order_cvv_already_verified(self, card_api):
        self.login(self.user)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user, cvv_verified=True).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        record = PaymentRecord.objects.get(txn_id='Trans123')
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.source, PaymentRecord.CARD)
        self.assertEqual(record.escrow_for, order.seller)
        self.assertEqual(record.target, order)
        self.assertEqual(record.amount, Money('12.00', 'USD'))
        self.assertEqual(record.payer, self.user)
        self.assertEqual(record.payee, None)

    @patch('apps.sales.models.sauce')
    def test_pay_order_failed_transaction(self, card_api):
        self.login(self.user)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.side_effect = AuthorizeError("It failed!")
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user).id,
                'amount': '12.00',
                'cvv': '123'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        record = PaymentRecord.objects.get(object_id=order.id)
        self.assertEqual(record.status, PaymentRecord.FAILURE)
        self.assertEqual(record.source, PaymentRecord.CARD)
        self.assertEqual(record.escrow_for, order.seller)
        self.assertEqual(record.target, order)
        self.assertEqual(record.amount, Money('12.00', 'USD'))
        self.assertEqual(record.payer, self.user)
        self.assertEqual(record.response_message, "It failed!")
        self.assertEqual(record.payee, None)

    @patch('apps.sales.models.sauce')
    def test_pay_order_amount_changed(self, card_api):
        self.login(self.user)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user).id,
                'amount': '10.00',
                'cvv': '234'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order_wrong_card(self, card_api):
        self.login(self.user)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create().id,
                'amount': '12.00',
                'cvv': '345'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order_outsider(self, card_api):
        self.login(self.user2)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user).id,
                'amount': '12.00',
                'cvv': '123'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order_seller_fail(self, card_api):
        self.login(self.user2)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD'), seller=self.user2,
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user).id,
                'amount': '12.00',
                'cvv': '567'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order_staffer(self, card_api):
        self.login(self.user)
        order = OrderFactory.create(
            buyer=self.user, status=Order.QUEUED, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=self.user).id,
                'amount': '12.00',
                'cvv': '467'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        record = PaymentRecord.objects.get(txn_id='Trans123')
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.source, PaymentRecord.CARD)
        self.assertEqual(record.escrow_for, order.seller)
        self.assertEqual(record.target, order)
        self.assertEqual(record.amount, Money('12.00', 'USD'))
        self.assertEqual(record.payer, self.user)
        self.assertEqual(record.payee, None)

    def test_place_order_unpermitted_character(self):
        self.login(self.user)
        characters = [
            CharacterFactory.create(user=self.user2, private=True).id,
        ]
        product = ProductFactory.create()
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
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
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestOrderStateChange(APITestCase):
    def setUp(self):
        super().setUp()
        self.outsider = UserFactory.create()
        self.seller = self.user
        self.buyer = self.user2
        characters = [
            CharacterFactory.create(user=self.buyer, name='Pictured', primary_asset=ImageAssetFactory.create()),
            CharacterFactory.create(user=self.buyer, private=True, name='Unpictured1', primary_asset=None),
            CharacterFactory.create(user=self.buyer, open_requests=True, name='Unpictured2', primary_asset=None),
        ]
        self.order = OrderFactory.create(seller=self.user, buyer=self.buyer, price=Money('5.00', 'USD'))
        self.order.characters.add(*characters)
        self.final = RevisionFactory.create(order=self.order, rating=ADULT)
        self.url = '/api/sales/v1/order/{}/'.format(self.order.id)

    def state_assertion(self, user_attr, url_ext='', target_response_code=status.HTTP_200_OK, initial_status=None):
        if initial_status is not None:
            self.order.status = initial_status
            self.order.save()
        self.login(getattr(self, user_attr))
        response = self.client.post(self.url + url_ext)
        self.assertEqual(response.status_code, target_response_code)

    def test_accept_order(self):
        self.state_assertion('seller', 'accept/')

    def test_accept_order_buyer_fail(self):
        self.state_assertion('buyer', 'accept/', status.HTTP_403_FORBIDDEN)

    def test_accept_order_outsider(self):
        self.state_assertion('outsider', 'accept/', status.HTTP_403_FORBIDDEN)

    def test_accept_order_staffer(self):
        self.state_assertion('staffer', 'accept/')

    def test_cancel_order(self):
        self.state_assertion('seller', 'cancel/', initial_status=Order.NEW)

    def test_cancel_order_buyer(self):
        self.state_assertion('buyer', 'cancel/', initial_status=Order.PAYMENT_PENDING)

    def test_cancel_order_outsider_fail(self):
        self.state_assertion('outsider', 'cancel/', status.HTTP_403_FORBIDDEN, initial_status=Order.PAYMENT_PENDING)

    def test_cancel_order_staffer(self):
        self.state_assertion('staffer', 'cancel/', initial_status=Order.PAYMENT_PENDING)

    def test_approve_order_buyer(self):
        record = PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller,
            amount=Money('15.00', 'USD'),
            finalized=False,
        )
        self.state_assertion('buyer', 'approve/', initial_status=Order.REVIEW)
        record.refresh_from_db()
        self.assertTrue(record.finalized)
        records = PaymentRecord.objects.all()
        self.assertEqual(records.count(), 3)
        fee = records.get(payee=None, escrow_for__isnull=True)
        self.assertEqual(fee.amount, Money('.50', 'USD'))
        self.assertEqual(fee.payer, self.order.seller)
        self.assertEqual(fee.escrow_for, None)
        self.assertEqual(fee.status, PaymentRecord.SUCCESS)
        self.assertEqual(fee.source, PaymentRecord.ACCOUNT)
        payment = records.get(payee=self.order.seller)
        self.assertEqual(payment.amount, Money('5.00', 'USD'))
        self.assertEqual(payment.payer, None)
        self.assertEqual(payment.escrow_for, None)
        self.assertEqual(payment.status, PaymentRecord.SUCCESS)
        self.assertEqual(payment.source, PaymentRecord.ESCROW)
        asset = ImageAsset.objects.get(order=self.order)
        self.assertEqual(asset.rating, ADULT)
        self.assertEqual(asset.order, self.order)
        self.assertEqual(asset.owner, self.order.buyer)
        self.assertEqual(self.order.characters.get(name='Unpictured1').primary_asset, asset)
        self.assertEqual(self.order.characters.get(name='Unpictured2').primary_asset, asset)
        self.assertNotEqual(self.order.characters.get(name='Pictured').primary_asset, asset)

    def test_approve_order_buyer_hidden(self):
        self.order.private = True
        self.order.save()
        record = PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller,
            amount=Money('15.00', 'USD'),
            finalized=False,
        )
        self.state_assertion('buyer', 'approve/', initial_status=Order.REVIEW)
        records = PaymentRecord.objects.all()
        self.assertEqual(records.count(), 3)
        record.refresh_from_db()
        self.assertTrue(record.finalized)
        fee = records.get(payee=None, escrow_for__isnull=True)
        self.assertEqual(fee.amount, Money('.50', 'USD'))
        self.assertEqual(fee.payer, self.order.seller)
        self.assertEqual(fee.escrow_for, None)
        self.assertEqual(fee.status, PaymentRecord.SUCCESS)
        self.assertEqual(fee.source, PaymentRecord.ACCOUNT)
        payment = records.get(payee=self.order.seller)
        self.assertEqual(payment.amount, Money('5.00', 'USD'))
        self.assertEqual(payment.payer, None)
        self.assertEqual(payment.escrow_for, None)
        self.assertEqual(payment.status, PaymentRecord.SUCCESS)
        self.assertEqual(payment.source, PaymentRecord.ESCROW)
        asset = ImageAsset.objects.get(order=self.order)
        self.assertEqual(asset.rating, ADULT)
        self.assertEqual(asset.order, self.order)
        self.assertEqual(asset.owner, self.order.buyer)
        self.assertEqual(asset.private, True)
        self.assertEqual(self.order.characters.get(name='Unpictured1').primary_asset, None)
        self.assertEqual(self.order.characters.get(name='Unpictured2').primary_asset, None)
        self.assertNotEqual(self.order.characters.get(name='Pictured').primary_asset, asset)

    @patch('apps.sales.views.recall_notification')
    def test_approve_order_recall_notification(self, mock_recall):
        target_time = timezone.now()
        self.order.disputed_on = target_time
        self.order.save()
        record = PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller,
            amount=Money('15.00', 'USD'),
            finalized=False,
        )
        self.state_assertion('buyer', 'approve/', initial_status=Order.DISPUTED)
        mock_recall.assert_called_with(DISPUTE, self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.disputed_on, None)
        record.refresh_from_db()
        self.assertTrue(record.finalized)

    @patch('apps.sales.views.recall_notification')
    def test_approve_order_staffer_no_recall_notification(self, mock_recall):
        record = PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller,
            amount=Money('15.00', 'USD'),
            finalized=False,
        )
        target_time = timezone.now()
        self.order.disputed_on = target_time
        self.order.save()
        self.state_assertion('staffer', 'approve/', initial_status=Order.DISPUTED)
        mock_recall.assert_not_called()
        self.order.refresh_from_db()
        self.assertEqual(self.order.disputed_on, target_time)
        record.refresh_from_db()
        self.assertTrue(record.finalized)

    @patch('apps.sales.models.sauce')
    @override_settings(REFUND_FEE=Decimal('5.00'))
    def test_refund_card_seller(self, mock_sauce):
        record = PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller,
            amount=Money('15.00', 'USD'),
            finalized=False,
        )
        mock_sauce.transaction.return_value.credit.return_value.uid = '123'
        self.state_assertion('seller', 'refund/', initial_status=Order.DISPUTED)
        record.refresh_from_db()
        self.assertTrue(record.finalized)
        PaymentRecord.objects.get(
            status=PaymentRecord.SUCCESS,
            payee=self.order.buyer, payer=None,
            source=PaymentRecord.ESCROW,
            type=PaymentRecord.REFUND,
            amount=Money('15.00', 'USD')
        )
        PaymentRecord.objects.get(
            status=PaymentRecord.SUCCESS,
            payee=None, payer=self.order.seller,
            amount=Money('5.00', 'USD')
        )


    @patch('apps.sales.models.sauce')
    def test_refund_card_seller_error(self, mock_sauce):
        PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller
        )
        mock_sauce.transaction.return_value.credit.side_effect = AuthorizeError(
            "It failed"
        )
        self.state_assertion('seller', 'refund/', status.HTTP_400_BAD_REQUEST, initial_status=Order.DISPUTED)
        PaymentRecord.objects.get(
            response_message="It failed", status=PaymentRecord.FAILURE,
            payee=self.order.buyer, payer=None,
            source=PaymentRecord.ESCROW,
            type=PaymentRecord.REFUND,
        )

    def test_refund_card_buyer(self):
        self.state_assertion('buyer', 'refund/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)

    def test_refund_card_outsider(self):
        self.state_assertion('outsider', 'refund/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)

    @patch('apps.sales.models.sauce')
    def test_refund_card_staffer(self, mock_sauce):
        record = PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller,
            finalized=False,
        )
        mock_sauce.transaction.return_value.credit.return_value.uid = '123'
        self.state_assertion('staffer', 'refund/', initial_status=Order.DISPUTED)
        record.refresh_from_db()
        self.assertTrue(record.finalized)

    def test_approve_order_seller_fail(self):
        self.state_assertion('seller', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    def test_approve_order_outsider_fail(self):
        self.state_assertion('outsider', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    def test_approve_order_seller(self):
        self.state_assertion('seller', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    def test_approve_order_staffer(self):
        record = PaymentRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            escrow_for=self.order.seller,
            amount=Money('15.00', 'USD'),
            finalized=False,
        )
        self.state_assertion('staffer', 'approve/', initial_status=Order.REVIEW)
        record.refresh_from_db()
        self.assertTrue(record.finalized)

    def test_claim_order_staffer(self):
        self.state_assertion('staffer', 'claim/', initial_status=Order.DISPUTED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.arbitrator, self.staffer)

    def test_claim_order_staffer_claimed_already(self):
        arbitrator = UserFactory.create(is_staff=True)
        self.order.arbitrator = arbitrator
        self.order.save()
        self.state_assertion('staffer', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.arbitrator, arbitrator)

    def test_claim_order_buyer(self):
        self.state_assertion('buyer', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)

    def test_claim_order_seller(self):
        self.state_assertion('seller', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)


class TestComment(APITestCase):
    def test_make_comment(self):
        order = OrderFactory.create()
        self.login(order.buyer)
        response = self.client.post(
            '/api/sales/v1/order/{}/comments/'.format(order.id),
            {'text': 'test comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = response.data
        self.assertEqual(comment['text'], 'test comment')
        self.assertEqual(comment['user']['username'], order.buyer.username)
        Comment.objects.get(id=comment['id'])


class TestHistoryViews(APITestCase):
    def setUp(self):
        super().setUp()
        self.account = BankAccountFactory.create(user=self.user)
        self.card = CreditCardTokenFactory.create()
        self.orders = [OrderFactory.create(buyer=self.user2, seller=self.user) for i in range(3)]
        self.escrow_holds = [
            PaymentRecordFactory.create(
                amount=Money(amount, 'USD'),
                type=PaymentRecord.SALE,
                payer=self.user2,
                payee=None,
                source=PaymentRecord.CARD,
                card=self.card,
                escrow_for=self.user,
            )
            for amount, order in zip(('5.00', '10.00', '15.00'), self.orders)
        ]
        self.escrow_releases = [
            PaymentRecordFactory.create(
                amount=Money(amount, 'USD'),
                payer=None,
                payee=self.user,
                source=PaymentRecord.ESCROW,
                type=PaymentRecord.TRANSFER,
            )
            for amount, order in zip(('5.00', '10.00'), self.orders)
        ]
        self.withdraws = [
            PaymentRecordFactory.create(
                amount=Money(amount, 'USD'),
                payer=self.user,
                payee=None,
                target=self.account,
                source=PaymentRecord.ACCOUNT,
                type=PaymentRecord.DISBURSEMENT_SENT,
            )
            for amount in (1, 2, 3, 4)
        ]

    def test_purchase_history(self):
        self.login(self.user)
        response = self.client.get('/api/sales/v1/account/{}/transactions/purchases/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/account/{}/transactions/purchases/'.format(self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        for result in response.data['results']:
            self.assertEqual(result['card']['id'], self.card.id)

    def test_purchase_history_wrong_user(self):
        self.login(self.user)
        response = self.client.get('/api/sales/v1/account/{}/transactions/purchases/'.format(self.user2.username))
        self.assertEqual(response.status_code, 403)

    def test_purchase_history_not_logged_in(self):
        response = self.client.get('/api/sales/v1/account/{}/transactions/purchases/'.format(self.user2.username))
        self.assertEqual(response.status_code, 403)

    def test_purchase_history_staff(self):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/account/{}/transactions/purchases/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        response = self.client.get('/api/sales/v1/account/{}/transactions/purchases/'.format(self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        for result in response.data['results']:
            self.assertEqual(result['card']['id'], self.card.id)

    def test_escrow_history(self):
        self.login(self.user)
        response = self.client.get('/api/sales/v1/account/{}/transactions/escrow/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        for result in response.data['results']:
            self.assertIsNone(result['card'])
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/account/{}/transactions/escrow/'.format(self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_escrow_history_wrong_user(self):
        self.login(self.user)
        response = self.client.get('/api/sales/v1/account/{}/transactions/escrow/'.format(self.user2.username))
        self.assertEqual(response.status_code, 403)

    def test_escrow_history_wrong_not_logged_in(self):
        response = self.client.get('/api/sales/v1/account/{}/transactions/escrow/'.format(self.user2.username))
        self.assertEqual(response.status_code, 403)

    def test_escrow_history_staff(self):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/account/{}/transactions/escrow/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        for result in response.data['results']:
            self.assertIsNone(result['card'])
        response = self.client.get('/api/sales/v1/account/{}/transactions/escrow/'.format(self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_available_history(self):
        self.login(self.user)
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 6)
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_available_history_wrong_user(self):
        self.login(self.user)
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user2.username))
        self.assertEqual(response.status_code, 403)

    def test_available_history_not_logged_in(self):
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user2.username))
        self.assertEqual(response.status_code, 403)

    def test_available_history_staff(self):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 6)
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)


@patch('apps.sales.views.initiate_withdraw')
@patch('apps.sales.views.perform_transfer')
class TestPerformWithdraw(APITestCase):
    def setUp(self):
        super().setUp()
        self.account = BankAccountFactory.create(user=self.user)
        PaymentRecordFactory.create(
            payee=self.user,
            payer=None,
            amount=Money('20.00', 'USD'),
            type=PaymentRecord.TRANSFER,
            source=PaymentRecord.ESCROW
        )

    def test_withdraw(self, _mock_transfer, _mock_withdraw):
        self.login(self.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/withdraw/'.format(self.user.username),
            {'bank': self.account.id, 'amount': '5.00'}
        )
        self.assertEqual(response.status_code, 204)

    def test_withdraw_wrong_account(self, _mock_transfer, _mock_withdraw):
        self.login(self.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/withdraw/'.format(self.user.username),
            {'bank': BankAccountFactory.create().id, 'amount': '5.00'}
        )
        self.assertEqual(response.status_code, 403)

    def test_withdraw_deleted_account(self, _mock_transfer, _mock_withdraw):
        self.account.deleted = True
        self.account.save()
        self.login(self.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/withdraw/'.format(self.user.username),
            {'bank': self.account.id, 'amount': '5.00'}
        )
        self.assertEqual(response.status_code, 400)

    def test_withdraw_not_logged_in(self, _mock_transfer, _mock_withdraw):
        response = self.client.post(
            '/api/sales/v1/account/{}/withdraw/'.format(self.user.username),
            {'bank': BankAccountFactory.create().id, 'amount': '5.00'}
        )
        self.assertEqual(response.status_code, 403)

    def test_withdraw_too_little(self, _mock_transfer, _mock_withdraw):
        # Checking for too much is tested in initiate_withdraw
        self.login(self.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/withdraw/'.format(self.user.username),
            {'bank': self.account.id, 'amount': '0.50'}
        )
        self.assertEqual(response.status_code, 400)


class TestBankAccounts(APITestCase):
    def test_bank_listing(self):
        accounts = [BankAccountFactory.create(user=self.user) for _ in range(3)]
        BankAccountFactory.create(user=self.user, deleted=True)
        [BankAccountFactory.create() for _ in range(3)]
        self.login(self.user)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), len(accounts))

    def test_bank_listing_staff(self):
        self.login(self.staffer)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)

    def test_bank_listing_wrong_user(self):
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(self.user.username))
        self.assertEqual(response.status_code, 403)


class TestBankManager(APITestCase):
    def setUp(self):
        super().setUp()
        self.account = BankAccountFactory.create(user=self.user)

    @patch('apps.sales.views.destroy_bank_account')
    def test_bank_account_destroy(self, _mock_destroy_account):
        self.login(self.user)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 204)

    def test_bank_account_destroy_wrong_user(self):
        self.login(self.user2)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)

    @patch('apps.sales.views.destroy_bank_account')
    def test_bank_account_destroy_staffer(self, _mock_destroy_account):
        self.login(self.staffer)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 204)

    def test_bank_account_destroy_not_logged_in(self):
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)


class TestAccountBalance(APITestCase):
    @patch('apps.sales.serializers.available_balance')
    @patch('apps.sales.serializers.escrow_balance')
    def test_account_balance(self, mock_escrow_balance, mock_available_balance):
        self.login(self.user)
        mock_available_balance.return_value = Decimal('100.00')
        mock_escrow_balance.return_value = Decimal('50.00')
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], 100)
        self.assertEqual(response.data['escrow'], 50)

    @patch('apps.sales.serializers.available_balance')
    @patch('apps.sales.serializers.escrow_balance')
    def test_account_balance_staff(self, mock_escrow_balance, mock_available_balance):
        self.login(self.staffer)
        mock_available_balance.return_value = Decimal('100.00')
        mock_escrow_balance.return_value = Decimal('50.00')
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], 100)
        self.assertEqual(response.data['escrow'], 50)

    def test_account_balance_wrong_user(self):
        self.login(self.user2)
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(self.user.username))
        self.assertEqual(response.status_code, 403)

    def test_account_balance_not_logged_in(self):
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(self.user.username))
        self.assertEqual(response.status_code, 403)


class TestProductSearch(APITestCase):
    def test_query_not_logged_in(self):
        # Search term matches.
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(name='Test3', task_weight=5, user__load=2, user__max_load=10)
        # Hidden products
        ProductFactory.create(name='Test3', hidden=True)
        hidden = ProductFactory.create(name='Wat2', hidden=True)
        hidden.tags.add(tag)
        ProductFactory.create(name='Test4', task_weight=5, user__load=10, user__max_load=10)
        maxed = ProductFactory.create(name='Test5', max_parallel=2)
        OrderFactory.create(product=maxed, status=Order.IN_PROGRESS)
        OrderFactory.create(product=maxed, status=Order.QUEUED)
        overloaded = ProductFactory.create(name='Test6', task_weight=1, user__max_load=5)
        PlaceholderSaleFactory.create(task_weight=5, seller=overloaded.user)
        ProductFactory.create(user__commissions_closed=True)
        ProductFactory.create(user__commissions_disabled=True)
        overloaded.user.refresh_from_db()

        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)

    def test_query_logged_in(self):
        # Search term matches.
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(name='Test3', task_weight=5)
        product4 = ProductFactory.create(name='Test4', hidden=True, user=self.user)
        product5 = ProductFactory.create(name='Wat2', hidden=True, user=self.user)
        product5.tags.add(tag)
        product6 = ProductFactory.create(name='Test5', task_weight=100, user=self.user)
        product7 = ProductFactory.create(name='Test7', max_parallel=2, user=self.user)
        OrderFactory.create(product=product7)
        OrderFactory.create(product=product7)
        ProductFactory.create(user__commissions_closed=True)
        ProductFactory.create(user__commissions_disabled=True)
        PlaceholderSaleFactory.create(task_weight=1, seller=self.user)

        self.user.max_load = 10
        self.user.load = 2
        self.user.save()
        self.login(self.user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertIDInList(product4, response.data['results'])
        self.assertIDInList(product5, response.data['results'])
        self.assertIDInList(product6, response.data['results'])
        self.assertIDInList(product7, response.data['results'])
        self.assertEqual(len(response.data['results']), 7)

    def test_query_different_user(self):
        # Search term matches.
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(name='Test3', task_weight=5, user__load=2, user__max_load=10)
        # Hidden products
        ProductFactory.create(name='Test3', hidden=True)
        hidden = ProductFactory.create(name='Wat2', hidden=True)
        hidden.tags.add(tag)
        ProductFactory.create(name='Test4', task_weight=5, user__load=8, user__max_load=10)
        overloaded = ProductFactory.create(name='Test5', max_parallel=2)
        ProductFactory.create(user__commissions_closed=True)
        ProductFactory.create(user__commissions_disabled=True)
        OrderFactory.create(product=overloaded, status=Order.IN_PROGRESS)
        OrderFactory.create(product=overloaded, status=Order.QUEUED)

        self.login(self.user2)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)


class TestTransfer(APITestCase):
    def test_create_transfer(self):
        character = CharacterFactory.create(user=self.user)
        self.login(self.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/transfer/character/{}/'.format(
                self.user.username,
                character.name
            ),
            {
                'buyer': self.user2.id,
                'price': 0
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)

    @patch('apps.sales.models.sauce')
    def test_character_transfer_pay(self, card_api):
        transfer = CharacterTransferFactory.create()
        card = CreditCardTokenFactory.create(user=transfer.buyer, cvv_verified=True)
        self.login(transfer.buyer)
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/transfer/character/{}/pay/'.format(transfer.id),
            {
                'amount': transfer.price.amount,
                'card_id': card.id,
                'cvv': ''
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    @patch('apps.sales.models.sauce')
    def test_character_transfer_pay_fail_seller(self, card_api):
        transfer = CharacterTransferFactory.create()
        card = CreditCardTokenFactory.create(user=transfer.buyer, cvv_verified=True)
        self.login(transfer.seller)
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/transfer/character/{}/pay/'.format(transfer.id),
            {
                'amount': transfer.price.amount,
                'card_id': card.id,
                'cvv': ''
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLoadAdjustment(TestCase):
    def test_load_changes(self):
        user = UserFactory.create(max_load=10)
        OrderFactory.create(task_weight=5, status=Order.QUEUED, product__user=user)
        user.refresh_from_db()
        self.assertEqual(user.load, 5)
        self.assertFalse(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order = OrderFactory.create(task_weight=5, status=Order.NEW, product__user=user)
        user.refresh_from_db()
        self.assertEqual(user.load, 5)
        self.assertFalse(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order.status = Order.QUEUED
        order.save()
        user.refresh_from_db()
        self.assertEqual(user.load, 10)
        self.assertFalse(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order2 = OrderFactory.create(task_weight=5, status=Order.NEW, product__user=user)
        user.refresh_from_db()
        self.assertEqual(user.load, 10)
        self.assertFalse(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order.status = Order.COMPLETED
        order.save()
        user.refresh_from_db()
        self.assertEqual(user.load, 5)
        self.assertTrue(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order2.status = Order.CANCELLED
        order2.save()
        order.save()
        user.refresh_from_db()
        self.assertEqual(user.load, 5)
        self.assertFalse(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
