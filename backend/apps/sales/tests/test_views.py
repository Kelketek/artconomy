from unittest.mock import patch, call

from authorize import AuthorizeError
from ddt import data, unpack, ddt
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, TestCase
from django.utils import timezone
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money, Decimal
from rest_framework import status

from apps.lib.abstract_models import ADULT, MATURE
from apps.lib.models import DISPUTE, Comment, Subscription, SALE_UPDATE, Notification, REFERRAL_PORTRAIT_CREDIT, \
    REFERRAL_LANDSCAPE_CREDIT
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories import TagFactory
from apps.profiles.models import ImageAsset, User
from apps.profiles.tests.factories import CharacterFactory, UserFactory, ImageAssetFactory
from apps.profiles.tests.helpers import gen_image
from apps.sales.models import Order, CreditCardToken, Product, PaymentRecord, OrderToken
from apps.sales.tests.factories import OrderFactory, CreditCardTokenFactory, ProductFactory, RevisionFactory, \
    PaymentRecordFactory, BankAccountFactory, PlaceholderSaleFactory, OrderTokenFactory

from apps.lib.models import COMMENT, REVISION_UPLOADED

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
        user = UserFactory.create()
        self.login(user)
        included_orders = [
            OrderFactory.create(status=order_status, **self.factory_kwargs(user)) for order_status in included
        ]
        [OrderFactory.create(status=order_status, **self.factory_kwargs(user)) for order_status in excluded]
        response = self.client.get(self.make_url(user, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(included_orders))
        for order in included_orders:
            self.assertIDInList(order, response.data['results'])

    @data(*categories)
    def test_not_logged_in(self, category):
        user = UserFactory.create()
        response = self.client.get('/api/sales/v1/account/{}/orders/{}/'.format(user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*categories)
    def test_outsider(self, category):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.get('/api/sales/v1/account/{}/orders/{}/'.format(user.username, category))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @data(*categories)
    def test_staff_user(self, category):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get('/api/sales/v1/account/{}/orders/{}/'.format(user.username, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestOrderLists(TestOrderListBase, APITestCase):
    def make_url(self, user, category):
        return '/api/sales/v1/account/{}/orders/{}/'.format(user.username, category)

    def factory_kwargs(self, user):
        return {'buyer': user}


class TestSalesLists(TestOrderListBase, APITestCase):
    def make_url(self, user, category):
        return '/api/sales/v1/account/{}/sales/{}/'.format(user.username, category)

    def factory_kwargs(self, user):
        return {'seller': user}


class TestCasesLists(TestOrderListBase, APITestCase):
    def make_url(self, user, category):
        return '/api/sales/v1/account/{}/cases/{}/'.format(user.username, category)

    def factory_kwargs(self, user):
        user.is_staff = True
        user.save()
        return {'arbitrator': user}


class TestCardManagement(APITestCase):
    @freeze_time('2018-01-01')
    @patch('apps.sales.models.sauce')
    def test_add_card(self, card_api):
        user = UserFactory.create()
        self.login(user)
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], user.id)
        card = CreditCardToken.objects.get(user=user)
        self.assertEqual(card.payment_id, '12345|6789')

    @patch('apps.sales.models.sauce')
    def test_add_card_primary_exists(self, card_api):
        user = UserFactory.create()
        self.login(user)
        primary_card = CreditCardTokenFactory(user=user)
        user.primary_card = primary_card
        user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], False)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(CreditCardToken.objects.filter(user=user).count(), 2)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, primary_card.id)

    @patch('apps.sales.models.sauce')
    def test_add_card_new_primary(self, card_api):
        user = UserFactory.create()
        self.login(user)
        card = CreditCardTokenFactory(user=user)
        user.primary_card = card
        user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
                'make_primary': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(CreditCardToken.objects.filter(user=user).count(), 2)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, response.data['id'])

    @patch('apps.sales.models.sauce')
    def test_card_add_not_logged_in(self, card_api):
        user = UserFactory.create()
        primary_card = CreditCardTokenFactory(user=user)
        user.primary_card = primary_card
        user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.models.sauce')
    def test_add_card_outsider(self, card_api):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        primary_card = CreditCardTokenFactory(user=user)
        user.primary_card = primary_card
        user.save()
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time('2018-01-01')
    @patch('apps.sales.models.sauce')
    def test_add_card_staffer(self, card_api):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['card_type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(response.data['last_four'], '1111')
        card = CreditCardToken.objects.get(user=user)
        self.assertEqual(card.payment_id, '12345|6789')

    @freeze_time('2018-01-01')
    @patch('apps.sales.models.sauce')
    @patch('apps.sales.views.renew')
    def test_add_card_renew(self, mock_renew, card_api):
        user = UserFactory.create()
        user.portrait_enabled = True
        user.save()
        self.login(user)
        card_api.card.return_value.save.return_value.uid = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'card_number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_renew.delay.assert_called_with(user.id, 'portrait')

    def test_make_primary(self):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.login(user)
        user.refresh_from_db()
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/{}/primary/'.format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, cards[2].id)
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(
            user.username, cards[3].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, cards[3].id)

    def test_make_primary_not_logged_in(self):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/{}/primary/'.format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/{}/primary/'.format(user.username, cards[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_make_primary_wrong_card(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.login(user)
        user.refresh_from_db()
        response = self.client.post('/api/sales/v1/account/{}/cards/{}/primary/'.format(
            user.username, CreditCardTokenFactory.create(user=user2).id
        ))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_card_listing(self):
        user = UserFactory.create()
        self.login(user)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data['results'])

    def test_card_listing_not_logged_in(self):
        user = UserFactory.create()
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_listing_staffer(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        response = self.client.get('/api/sales/v1/account/{}/cards/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for card in cards:
            self.assertIDInList(card, response.data['results'])

    def test_card_removal(self):
        user = UserFactory.create()
        self.login(user)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)

    def test_card_removal_not_logged_in(self):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    def test_card_removal_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    def test_card_removal_staff(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.assertEqual(cards[0].active, True)
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, False)
        cards[0].refresh_from_db()
        self.assertEqual(cards[0].active, True)


class TestProduct(APITestCase):
    def test_product_listing_logged_in(self):
        user = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        hidden = ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        for product in products:
            self.assertIDInList(product, response.data['results'])
        self.assertIDInList(hidden, response.data['results'])

    def test_create_product(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'price': '2.50',
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], '3.00')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_free(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'price': '0',
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], '3.00')
        self.assertEqual(result['price'], '0.00')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(MINIMUM_PRICE=Decimal('1.00'))
    def test_create_product_minimum_unmet(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'price': '0.50',
            }
        )
        result = response.data
        self.assertEqual(result['price'], ['Must be at least $1.00'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(MINIMUM_PRICE=Decimal('1.00'))
    def test_create_product_minimum_irrelevant(self):
        user = UserFactory.create(escrow_disabled=True)
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'price': '0.50',
            }
        )
        result = response.data
        self.assertEqual(result['price'], '0.50')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_not_logged_in(self):
        user = UserFactory.create()
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'price': '2.50',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'price': '2.50',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_staff(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'rating': MATURE,
                'expected_turnaround': 3,
                'price': '2.50',
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], '3.00')
        self.assertEqual(result['rating'], MATURE)
        self.assertEqual(result['price'], '2.50')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_listing_not_logged_in(self):
        user = UserFactory.create()
        products = [ProductFactory.create(user=user) for __ in range(3)]
        ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_listing_other_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        for product in products:
            self.assertIDInList(product, response.data['results'])

    def test_product_listing_staff(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        hidden = ProductFactory.create(user=user, hidden=True)
        ProductFactory.create(user=user, active=False)
        response = self.client.get('/api/sales/v1/account/{}/products/'.format(user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        for product in products:
            self.assertIDInList(product, response.data['results'])
        self.assertIDInList(hidden, response.data['results'])

    def test_product_delete(self):
        user = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)

    def test_product_delete_not_logged_in(self):
        user = UserFactory.create()
        products = [ProductFactory.create(user=user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_wrong_product(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        products = [ProductFactory.create(user=user2) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete('/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        products[1].refresh_from_db()
        self.assertTrue(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 1)

    def test_product_delete_staffer(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        products = [ProductFactory.create(user=user) for __ in range(3)]
        OrderFactory.create(product=products[1])
        self.assertTrue(products[1].active)
        response = self.client.delete(
            '/api/sales/v1/account/{}/products/{}/'.format(user.username, products[1].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(
            '/api/sales/v1/account/{}/products/{}/'.format(user.username, products[2].id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        products[1].refresh_from_db()
        self.assertFalse(products[1].active)
        self.assertEqual(Product.objects.filter(id=products[2].id).count(), 0)


@ddt
class TestOrder(APITestCase):
    def test_place_order(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        characters = [
            CharacterFactory.create(user=user),
            CharacterFactory.create(user=user, private=True),
            CharacterFactory.create(user=user2, open_requests=True)
        ]
        character_ids = [character.id for character in characters]
        product = ProductFactory.create(task_weight=5, expected_turnaround=3)
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
        order = Order.objects.get(id=response.data['id'])
        # These should be set at the point of payment.
        self.assertEqual(order.task_weight, 0)
        self.assertEqual(order.expected_turnaround, 0)

    def test_place_order_unavailable(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        characters = [
            CharacterFactory.create(user=user).id,
            CharacterFactory.create(user=user, private=True).id,
            CharacterFactory.create(user=user2, open_requests=True).id
        ]
        product = ProductFactory.create(task_weight=500)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0], 'This product is not available at this time.')

    def test_place_order_token(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        characters = [
            CharacterFactory.create(user=user),
            CharacterFactory.create(user=user, private=True),
            CharacterFactory.create(user=user2, open_requests=True)
        ]
        character_ids = [character.id for character in characters]
        token = OrderTokenFactory.create(product__task_weight=500)
        product = token.product
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(
                product.user.username, product.id, token.activation_code
            ),
            {
                'details': 'Draw me some porn!',
                'characters': character_ids,
                'order_token': token.activation_code,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['details'], 'Draw me some porn!')
        self.assertEqual(sorted(response.data['characters']), sorted(character_ids))
        for character in characters:
            self.assertTrue(character.shared_with.filter(username=response.data['seller']['username']).exists())
        self.assertEqual(response.data['product'], product.id)
        self.assertEqual(response.data['status'], Order.NEW)
        self.assertRaises(OrderToken.DoesNotExist, token.refresh_from_db)

    def test_place_order_token_failure(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        characters = [
            CharacterFactory.create(user=user).id,
            CharacterFactory.create(user=user, private=True).id,
            CharacterFactory.create(user=user2, open_requests=True).id
        ]
        product = ProductFactory.create(task_weight=500)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/?order_token=123'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters,
                'order_token': '123'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0], 'The order token you provided is expired, revoked, or invalid.')

    def test_place_order_hidden(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        characters = [
            CharacterFactory.create(user=user).id,
            CharacterFactory.create(user=user, private=True).id,
            CharacterFactory.create(user=user2, open_requests=True).id
        ]
        product = ProductFactory.create(hidden=True)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': characters
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], ['This product is not available at this time.'])

    def test_place_order_hidden_token(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        characters = [
            CharacterFactory.create(user=user),
            CharacterFactory.create(user=user, private=True),
            CharacterFactory.create(user=user2, open_requests=True)
        ]
        token = OrderTokenFactory.create(product__task_weight=500, product__hidden=True)
        product = token.product
        character_ids = [character.id for character in characters]
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'characters': character_ids,
                'order_token': token.activation_code
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['details'], 'Draw me some porn!')
        self.assertEqual(response.data['characters'], character_ids)
        for character in characters:
            self.assertTrue(character.shared_with.filter(username=response.data['seller']['username']).exists())
        self.assertEqual(response.data['product'], product.id)
        self.assertEqual(response.data['status'], Order.NEW)
        self.assertRaises(OrderToken.DoesNotExist, token.refresh_from_db)

    def test_order_view_seller(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user)
        response = self.client.get(
            '/api/sales/v1/order/{}/'.format(order.id),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)

    def test_order_view_buyer(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(buyer=user)
        response = self.client.get(
            '/api/sales/v1/order/{}/'.format(order.id),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)

    def test_order_view_outsider(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create()
        response = self.client.get(
            '/api/sales/v1/order/{}/'.format(order.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_order(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.adjustment, Money('2.03', 'USD'))

    def test_accept_order(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/accept/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.adjustment, Money('2.03', 'USD'))

    def test_adjust_order_too_low(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, product__price=Money('15.00', 'USD'))
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
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user2, buyer=user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_order_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user2)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_order_not_logged_in(self):
        user = UserFactory.create()
        order = OrderFactory.create(seller=user)
        response = self.client.patch(
            '/api/sales/v1/order/{}/adjust/'.format(order.id),
            {
                'adjustment': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_adjust_order_staff(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        order = OrderFactory.create(seller=user)
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
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.QUEUED)
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
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user2, buyer=user, status=Order.QUEUED)
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
        user = UserFactory.create()
        self.login(user)
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
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
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
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.QUEUED)
        response = self.client.post(
            '/api/sales/v1/order/{}/cancel/'.format(order.id),
            {
                'stream_link': 'https://streaming.artconomy.com/'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time('2012-08-01')
    def test_revision_upload(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        order = Order.objects.get(id=order.id)
        self.assertIsNone(order.auto_finalize_on)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        # Filling revisions should not mark as complete automatically.
        order.refresh_from_db()
        self.assertEqual(order.auto_finalize_on, None)
        self.assertEqual(order.status, Order.IN_PROGRESS)

    @freeze_time('2012-08-01')
    def test_final_revision_upload(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        order = Order.objects.get(id=order.id)
        self.assertEqual(order.auto_finalize_on, date(2012, 8, 6))
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        # Filling revisions should not mark as complete automatically.
        self.assertEqual(order.auto_finalize_on, date(2012, 8, 6))
        self.assertEqual(order.status, Order.REVIEW)

    @freeze_time('2012-08-01')
    def test_final_revision_upload_dispute(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.DISPUTED, revisions=1)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.DISPUTED)

    @freeze_time('2012-08-01')
    def test_final_revision_upload_escrow_disabled(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1, escrow_disabled=True)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        order = Order.objects.get(id=order.id)
        self.assertIsNone(order.auto_finalize_on)
        self.assertEqual(order.status, Order.COMPLETED)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time('2012-08-01')
    def test_order_mark_complete(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1)
        RevisionFactory.create(order=order)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/complete/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.REVIEW)
        self.assertEqual(order.auto_finalize_on, date(2012, 8, 3))
        self.assertTrue(order.final_uploaded)

    def test_order_mark_completed_payment_pending(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.PAYMENT_PENDING, revisions=1, final_uploaded=False)
        RevisionFactory.create(order=order)
        order.refresh_from_db()
        response = self.client.post(
            '/api/sales/v1/order/{}/complete/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.PAYMENT_PENDING)
        self.assertTrue(order.final_uploaded)

    @freeze_time('2012-08-01')
    def test_order_mark_complete_escrow_disabled(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1, escrow_disabled=True)
        RevisionFactory.create(order=order)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/complete/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.COMPLETED)
        self.assertIsNone(order.auto_finalize_on)

    @freeze_time('2012-08-01')
    def test_order_mark_complete_no_revisions(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1, escrow_disabled=True)
        self.assertEqual(order.status, Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/complete/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)

    @freeze_time('2012-08-01')
    def test_order_reopen(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            seller=user, status=Order.REVIEW, revisions=1, auto_finalize_on=date(2012, 8, 6)
        )
        RevisionFactory.create(order=order)
        order.refresh_from_db()
        response = self.client.post(
            '/api/sales/v1/order/{}/reopen/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        self.assertIsNone(order.auto_finalize_on)

    @freeze_time('2012-08-01')
    def test_order_reopen_escrow_disabled(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            seller=user, status=Order.COMPLETED, revisions=1, escrow_disabled=True
        )
        RevisionFactory.create(order=order)
        order.refresh_from_db()
        response = self.client.post(
            '/api/sales/v1/order/{}/reopen/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        self.assertIsNone(order.auto_finalize_on)

    def test_revision_upload_buyer_fail(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(buyer=user, status=Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_upload_outsider_fail(self):
        user = UserFactory.create()
        self.login(user)
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
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': SimpleUploadedFile('bloo-oo.jpg', gen_image()),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], staffer.username)
        self.assertEqual(response.data['rating'], ADULT)

    def test_revision_upload_final(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1, revisions_hidden=True)
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
                'final': True
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

    @data(Order.IN_PROGRESS, Order.NEW, Order.PAYMENT_PENDING, Order.REVIEW)
    def test_delete_revision(self, order_status):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=order_status)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 0)

    def test_delete_revision_reactivate(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.REVIEW, final_uploaded=True)
        revision = RevisionFactory.create(order=order)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(order.status, Order.IN_PROGRESS)
        self.assertFalse(order.final_uploaded)

    @data(Order.COMPLETED, Order.DISPUTED)
    def test_delete_revision_locked(self, order_status):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=order_status)
        revision = RevisionFactory.create(order=order)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_revision_buyer_fail(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(buyer=user, status=Order.IN_PROGRESS)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 1)

    def test_delete_revision_outsider_fail(self):
        user = UserFactory.create()
        self.login(user)
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
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS)
        revision = RevisionFactory.create(order=order)
        self.assertEqual(order.revision_set.all().count(), 1)
        response = self.client.delete(
            '/api/sales/v1/order/{}/revisions/{}/'.format(order.id, revision.id)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        order.refresh_from_db()
        self.assertEqual(order.revision_set.all().count(), 0)

    def test_list_revisions_hidden(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(buyer=user, revisions_hidden=True)
        response = self.client.get(
            '/api/sales/v1/order/{}/revisions/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_revisions_unhidden(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(buyer=user, revisions_hidden=False)
        response = self.client.get(
            '/api/sales/v1/order/{}/revisions/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_revisions_hidden_seller(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, revisions_hidden=True)
        response = self.client.get(
            '/api/sales/v1/order/{}/revisions/'.format(order.id)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('apps.sales.models.sauce')
    def test_pay_order(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        subscription = Subscription.objects.get(subscriber=order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
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
        self.assertEqual(record.payer, user)
        self.assertEqual(record.payee, None)

    @patch('apps.sales.models.sauce')
    def test_pay_order_weights_set(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD'), product__task_weight=1, product__expected_turnaround=2,
            adjustment_task_weight=3, adjustment_expected_turnaround=4
        )
        subscription = Subscription.objects.get(subscriber=order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        order = Order.objects.get(id=order.id)
        self.assertEqual(order.task_weight, 1)
        self.assertEqual(order.expected_turnaround, 2)
        self.assertEqual(order.adjustment_task_weight, 3)
        self.assertEqual(order.adjustment_expected_turnaround, 4)

    @patch('apps.sales.models.sauce')
    def test_pay_order_revisions_exist(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            revisions_hidden=True,
            adjustment=Money('2.00', 'USD')
        )
        RevisionFactory.create(order=order)
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        self.assertFalse(order.revisions_hidden)
        self.assertFalse(order.final_uploaded)

    @patch('apps.sales.models.sauce')
    @freeze_time('2018-08-01')
    def test_pay_order_final_uploaded(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            revisions_hidden=True, final_uploaded=True,
            adjustment=Money('2.00', 'USD')
        )
        RevisionFactory.create(order=order)
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        order.refresh_from_db()
        self.assertEqual(order.status, Order.REVIEW)
        self.assertFalse(order.revisions_hidden)
        self.assertTrue(order.final_uploaded)
        self.assertEqual(order.auto_finalize_on, date(2018, 8, 3))

    def test_order_get_rating_buyer(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(order.buyer)
        response = self.client.get(
            '/api/sales/v1/order/{}/rating/'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_seller(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(order.seller)
        response = self.client.get(
            '/api/sales/v1/order/{}/rating/'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_staff_buyer_end(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get(
            '/api/sales/v1/order/{}/rating/?end=buyer'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_staff_seller_end(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get(
            '/api/sales/v1/order/{}/rating/?end=seller'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_outsider(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(UserFactory.create())
        response = self.client.get(
            '/api/sales/v1/order/{}/rating/?end=seller'.format(order.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_get_rating_not_logged_in(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        response = self.client.get(
            '/api/sales/v1/order/{}/rating/?end=seller'.format(order.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.models.sauce')
    def test_pay_order_credit_referrals(self, card_api):
        user = UserFactory.create()
        self.login(user)
        user.referred_by = UserFactory.create()
        user.save()
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD'), product__user__referred_by=UserFactory.create()
        )
        self.assertFalse(user.bought_shield_on)
        self.assertFalse(user.sold_shield_on)
        subscription = Subscription.objects.get(subscriber=order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        record = PaymentRecord.objects.get(txn_id='Trans123')
        order.seller.refresh_from_db()
        order.buyer.refresh_from_db()
        portrait_notification = Notification.objects.filter(event__type=REFERRAL_PORTRAIT_CREDIT)
        landscape_notification = Notification.objects.filter(event__type=REFERRAL_LANDSCAPE_CREDIT)
        self.assertEqual(portrait_notification.count(), 1)
        self.assertEqual(landscape_notification.count(), 1)
        portrait_notification = portrait_notification.first()
        landscape_notification = landscape_notification.first()
        self.assertEqual(portrait_notification.user, order.buyer.referred_by)
        self.assertEqual(portrait_notification.event.target, order.buyer.referred_by)
        self.assertEqual(landscape_notification.user, order.seller.referred_by)
        self.assertEqual(landscape_notification.event.target, order.seller.referred_by)
        self.assertTrue(order.seller.sold_shield_on)
        self.assertTrue(order.buyer.bought_shield_on)
        self.assertEqual(record.status, PaymentRecord.SUCCESS)
        self.assertEqual(record.source, PaymentRecord.CARD)
        self.assertEqual(record.escrow_for, order.seller)
        self.assertEqual(record.target, order)
        self.assertEqual(record.amount, Money('12.00', 'USD'))
        self.assertEqual(record.payer, user)
        self.assertEqual(record.payee, None)

    @patch('apps.sales.models.sauce')
    def test_pay_order_no_escrow(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD'), escrow_disabled=True
        )
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.models.sauce')
    def test_pay_order_cvv_missing(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(PaymentRecord.DoesNotExist, PaymentRecord.objects.get, txn_id='Trans123')

    @patch('apps.sales.models.sauce')
    def test_pay_order_cvv_already_verified(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user, cvv_verified=True).id,
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
        self.assertEqual(record.payer, user)
        self.assertEqual(record.payee, None)

    @patch('apps.sales.models.sauce')
    def test_pay_order_failed_transaction(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.side_effect = AuthorizeError("It failed!")
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
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
        self.assertEqual(record.payer, user)
        self.assertEqual(record.response_message, "It failed!")
        self.assertEqual(record.payee, None)

    @patch('apps.sales.models.sauce')
    def test_pay_order_amount_changed(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '10.00',
                'cvv': '234'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order_wrong_card(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
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
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '123'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order_seller_fail(self, card_api):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD'), seller=user2,
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '567'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PaymentRecord.objects.all().count(), 0)

    @patch('apps.sales.models.sauce')
    def test_pay_order_staffer(self, card_api):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, price=Money('10.00', 'USD'),
            adjustment=Money('2.00', 'USD')
        )
        card_api.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
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
        self.assertEqual(record.payer, user)
        self.assertEqual(record.payee, None)

    def test_place_order_unpermitted_character(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        characters = [
            CharacterFactory.create(user=user2, private=True).id,
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
        user2 = UserFactory.create()
        characters = [
            CharacterFactory.create(user=user2, private=True).id,
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
        self.seller = UserFactory.create()
        self.buyer = UserFactory.create()
        self.staffer = UserFactory.create(is_staff=True)
        characters = [
            CharacterFactory.create(user=self.buyer, name='Pictured', primary_asset=ImageAssetFactory.create()),
            CharacterFactory.create(user=self.buyer, private=True, name='Unpictured1', primary_asset=None),
            CharacterFactory.create(
                user=UserFactory.create(), open_requests=True, name='Unpictured2', primary_asset=None
            )
        ]
        self.order = OrderFactory.create(
            seller=self.seller, buyer=self.buyer, price=Money('5.00', 'USD'),
            adjustment_task_weight=1, adjustment_expected_turnaround=2, product__task_weight=3,
            product__expected_turnaround=4
        )
        self.order.characters.add(*characters)
        self.final = RevisionFactory.create(order=self.order, rating=ADULT)
        self.url = '/api/sales/v1/order/{}/'.format(self.order.id)

    def state_assertion(
            self, user_attr, url_ext='', target_response_code=status.HTTP_200_OK, initial_status=None, method='post',
            target_status=None
    ):
        if initial_status is not None:
            self.order.status = initial_status
            self.order.save()
        self.login(getattr(self, user_attr))
        response = getattr(self.client, method)(self.url + url_ext)
        self.assertEqual(response.status_code, target_response_code)
        if target_status is not None:
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, target_status)

    def test_accept_order(self):
        self.state_assertion('seller', 'accept/', method='patch')

    def test_accept_order_buyer_fail(self):
        self.state_assertion('buyer', 'accept/', status.HTTP_403_FORBIDDEN, method='patch')

    def test_accept_order_outsider(self):
        self.state_assertion('outsider', 'accept/', status.HTTP_403_FORBIDDEN, method='patch')

    def test_accept_order_staffer(self):
        self.state_assertion('staffer', 'accept/', method='patch')

    def test_cancel_order(self):
        self.state_assertion('seller', 'cancel/', initial_status=Order.NEW)

    def test_cancel_order_buyer(self):
        self.state_assertion('buyer', 'cancel/', initial_status=Order.PAYMENT_PENDING)

    def test_cancel_order_outsider_fail(self):
        self.state_assertion('outsider', 'cancel/', status.HTTP_403_FORBIDDEN, initial_status=Order.PAYMENT_PENDING)

    def test_cancel_order_staffer(self):
        self.state_assertion('staffer', 'cancel/', initial_status=Order.PAYMENT_PENDING)

    def test_mark_paid_order_buyer_fail(self):
        self.order.escrow_disabled = True
        self.order.save()
        self.state_assertion('buyer', 'mark-paid/', status.HTTP_403_FORBIDDEN, initial_status=Order.PAYMENT_PENDING)

    def test_mark_paid_order_seller(self):
        self.order.escrow_disabled = True
        self.assertTrue(self.order.revisions_hidden)
        self.order.save()
        self.final.delete()
        self.state_assertion('seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING, target_status=Order.QUEUED)
        self.order.refresh_from_db()
        self.assertFalse(self.order.revisions_hidden)

    def test_mark_paid_order_final_uploaded(self):
        self.order.escrow_disabled = True
        self.order.final_uploaded = True
        self.order.save()
        self.state_assertion(
            'seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING, target_status=Order.COMPLETED
        )

    def test_mark_paid_revisions_exist(self):
        self.order.escrow_disabled = True
        self.order.save()
        RevisionFactory.create(order=self.order)
        self.state_assertion(
            'seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING, target_status=Order.IN_PROGRESS
        )

    def test_mark_paid_task_weights(self):
        self.order.escrow_disabled = True
        self.order.save()
        self.assertEqual(self.order.adjustment_task_weight, 1)
        self.assertEqual(self.order.adjustment_expected_turnaround, 2)
        self.assertEqual(self.order.task_weight, 0)
        self.assertEqual(self.order.expected_turnaround, 0)
        self.state_assertion('seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING)
        self.order.refresh_from_db()
        self.assertEqual(self.order.adjustment_task_weight, 1)
        self.assertEqual(self.order.adjustment_expected_turnaround, 2)
        self.assertEqual(self.order.task_weight, 3)
        self.assertEqual(self.order.expected_turnaround, 4)

    def test_mark_paid_order_staffer(self):
        self.order.escrow_disabled = True
        self.order.save()
        self.state_assertion('staffer', 'mark-paid/', initial_status=Order.PAYMENT_PENDING)

    @override_settings(STANDARD_PERCENTAGE_FEE=Decimal('10'), STANDARD_STATIC_FEE=Decimal('1.00'))
    @patch('apps.sales.tasks.withdraw_all.delay')
    def test_approve_order_buyer(self, mock_withdraw):
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
        self.assertEqual(fee.amount, Money('1.50', 'USD'))
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
        mock_withdraw.assert_called_with(self.order.seller.id)

    def test_publish_order(self):
        self.order.status = Order.COMPLETED
        self.order.save()
        self.login(self.buyer)
        response = self.client.post(
            self.url + 'publish/',
            {'title': 'This is a test', 'caption': 'A testy test'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset = ImageAsset.objects.get(order=self.order)
        self.assertEqual(asset.rating, ADULT)
        self.assertEqual(asset.order, self.order)
        self.assertEqual(asset.owner, self.order.buyer)
        self.assertEqual(asset.title, 'This is a test')
        self.assertEqual(asset.caption, 'A testy test')
        self.assertEqual(self.order.characters.get(name='Unpictured1').primary_asset, asset)
        self.assertIsNone(self.order.characters.get(name='Unpictured2').primary_asset)
        self.assertNotEqual(self.order.characters.get(name='Pictured').primary_asset, asset)

    def test_publish_order_buyer_hidden(self):
        self.order.private = True
        self.order.status = Order.COMPLETED
        self.order.save()
        self.login(self.buyer)
        response = self.client.post(
            self.url + 'publish/',
            {'title': 'This is a test', 'caption': 'A testy test'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        asset = ImageAsset.objects.get(order=self.order)
        self.assertEqual(asset.rating, ADULT)
        self.assertEqual(asset.order, self.order)
        self.assertEqual(asset.owner, self.order.buyer)
        self.assertEqual(asset.private, True)
        self.assertEqual(asset.title, 'This is a test')
        self.assertEqual(asset.caption, 'A testy test')
        self.assertEqual(self.order.characters.get(name='Unpictured1').primary_asset, None)
        self.assertEqual(self.order.characters.get(name='Unpictured2').primary_asset, None)
        self.assertNotEqual(self.order.characters.get(name='Pictured').primary_asset, asset)

    @patch('apps.sales.utils.recall_notification')
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
        mock_recall.assert_has_calls([call(DISPUTE, self.order)])
        self.order.refresh_from_db()
        self.assertEqual(self.order.disputed_on, None)
        record.refresh_from_db()
        self.assertTrue(record.finalized)

    @patch('apps.sales.utils.recall_notification')
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
        for mock_call in mock_recall.call_args_list:
            self.assertNotEqual(mock_call[0], DISPUTE)
        self.order.refresh_from_db()
        self.assertEqual(self.order.disputed_on, target_time)
        record.refresh_from_db()
        self.assertTrue(record.finalized)

    @patch('apps.sales.models.sauce')
    @override_settings(
        PREMIUM_PERCENTAGE_FEE=Decimal('5'), PREMIUM_STATIC_FEE=Decimal('0.10')
    )
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
            escrow_for=self.order.seller,
            type=PaymentRecord.REFUND,
            amount=Money('14.15', 'USD')
        )
        PaymentRecord.objects.get(
            status=PaymentRecord.SUCCESS,
            payee=None, payer=self.order.seller,
            amount=Money('.85', 'USD')
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
        self.assertEqual(Subscription.objects.filter(
            subscriber=self.staffer, object_id=self.order.id, content_type=ContentType.objects.get_for_model(Order),
            type__in=[COMMENT, REVISION_UPLOADED], email=True,
        ).count(), 2)

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

    def test_file_dispute_buyer(self):
        self.state_assertion('buyer', 'dispute/', status.HTTP_200_OK, initial_status=Order.IN_PROGRESS)

    @freeze_time('2019-01-01')
    def test_file_dispute_buyer_too_early(self):
        self.order.dispute_available_on = date(year=2019, month=5, day=3)
        self.order.save()
        self.state_assertion('buyer', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=Order.IN_PROGRESS)

    @freeze_time('2019-01-01')
    def test_file_dispute_buyer_enough_time(self):
        self.order.dispute_available_on = date(year=2019, month=5, day=3)
        self.order.save()
        self.state_assertion('buyer', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=Order.IN_PROGRESS)

    def test_file_dispute_seller(self):
        self.state_assertion('seller', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    def test_file_dispute_outsider_fail(self):
        self.state_assertion('outsider', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)


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
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
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
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
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
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
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
        self.assertEqual(len(response.data['results']), 7)
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
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 7)
        response = self.client.get('/api/sales/v1/account/{}/transactions/available/'.format(self.user2.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)


@patch('apps.sales.views.initiate_withdraw')
@patch('apps.sales.views.perform_transfer')
class TestPerformWithdraw(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
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
        user = UserFactory.create()
        accounts = [BankAccountFactory.create(user=user) for _ in range(3)]
        BankAccountFactory.create(user=user, deleted=True)
        [BankAccountFactory.create() for _ in range(3)]
        self.login(user)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), len(accounts))

    def test_bank_listing_staff(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 200)

    def test_bank_listing_wrong_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 403)


class TestBankManager(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.account = BankAccountFactory.create(user=self.user)

    @patch('apps.sales.views.destroy_bank_account')
    def test_bank_account_destroy(self, _mock_destroy_account):
        self.login(self.user)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 204)

    def test_bank_account_destroy_wrong_user(self):
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)

    @patch('apps.sales.views.destroy_bank_account')
    def test_bank_account_destroy_staffer(self, _mock_destroy_account):
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 204)

    def test_bank_account_destroy_not_logged_in(self):
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)


class TestAccountBalance(APITestCase):
    @patch('apps.sales.serializers.available_balance')
    @patch('apps.sales.serializers.escrow_balance')
    def test_account_balance(self, mock_escrow_balance, mock_available_balance):
        user = UserFactory.create()
        self.login(user)
        mock_available_balance.return_value = Decimal('100.00')
        mock_escrow_balance.return_value = Decimal('50.00')
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], '100.00')
        self.assertEqual(response.data['escrow'], '50.00')

    @patch('apps.sales.serializers.available_balance')
    @patch('apps.sales.serializers.escrow_balance')
    def test_account_balance_staff(self, mock_escrow_balance, mock_available_balance):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        mock_available_balance.return_value = Decimal('100.00')
        mock_escrow_balance.return_value = Decimal('50.00')
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], '100.00')
        self.assertEqual(response.data['escrow'], '50.00')

    def test_account_balance_wrong_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 403)

    def test_account_balance_not_logged_in(self):
        user = UserFactory.create()
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 403)


class TestProductSearch(APITestCase):
    def test_query_not_logged_in(self):
        # Search term matches.
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat product 2')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(name='Test3', task_weight=5, user__load=2, user__max_load=10)
        # Hidden products
        ProductFactory.create(name='TestHidden', hidden=True)
        hidden = ProductFactory.create(name='Wat2 hidden', hidden=True)
        hidden.tags.add(tag)
        ProductFactory.create(name='Test4 overload', task_weight=5, user__load=10, user__max_load=10)
        maxed = ProductFactory.create(name='Test5 maxed', max_parallel=2)
        OrderFactory.create(product=maxed, status=Order.IN_PROGRESS)
        OrderFactory.create(product=maxed, status=Order.QUEUED)
        overloaded = ProductFactory.create(name='Test6 overloaded', task_weight=1, user__max_load=5)
        PlaceholderSaleFactory.create(task_weight=5, seller=overloaded.user)
        ProductFactory.create(name='Test commissions closed', user__commissions_closed=True)
        overloaded.user.refresh_from_db()

        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)

    def test_query_logged_in(self):
        # Search term matches.
        user = UserFactory.create()
        user2 = UserFactory.create()
        product1 = ProductFactory.create(name='Test1')
        product2 = ProductFactory.create(name='Wat')
        tag = TagFactory.create(name='test')
        product2.tags.add(tag)
        product3 = ProductFactory.create(name='Test3', task_weight=5)
        # Overweighted.
        ProductFactory.create(name='Test4', task_weight=100, user=user)
        product4 = ProductFactory.create(name='Test5', max_parallel=2, user=user)
        OrderFactory.create(product=product4)
        OrderFactory.create(product=product4)
        # Product from blocked user. Shouldn't be in results.
        ProductFactory.create(name='Test Blocked', user=user2)
        user.blocking.add(user2)

        ProductFactory.create(user__commissions_closed=True)
        PlaceholderSaleFactory.create(task_weight=1, seller=user)

        user.max_load = 10
        user.load = 2
        user.save()
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertIDInList(product4, response.data['results'])
        self.assertEqual(len(response.data['results']), 4)

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
        OrderFactory.create(product=overloaded, status=Order.IN_PROGRESS)
        OrderFactory.create(product=overloaded, status=Order.QUEUED)

        user = UserFactory.create()
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)

    def test_blocked(self):
        product = ProductFactory.create(name='Test1')
        user = UserFactory.create()
        user.blocking.add(product.user)
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertEqual(len(response.data['results']), 0)

    def test_personal(self):
        user = UserFactory.create()
        listed = ProductFactory.create(user=user, name='Test')
        listed2 = ProductFactory.create(user=user, name='Test2', hidden=True)
        listed3 = ProductFactory.create(user=user, task_weight=999, name='Test3')
        # Inactive.
        ProductFactory.create(user=user, active=False, name='Test4')
        # Wrong user.
        ProductFactory.create(name='Test5')
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/mine/', {'q': 'test'})
        self.assertIDInList(listed, response.data['results'])
        self.assertIDInList(listed2, response.data['results'])
        self.assertIDInList(listed3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)


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
        # Max load reached.
        self.assertEqual(user.load, 10)
        self.assertTrue(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order2 = OrderFactory.create(task_weight=5, status=Order.NEW, product__user=user)
        user.refresh_from_db()
        # Now we have an order in a new state. This shouldn't undo the disability.
        self.assertEqual(user.load, 10)
        self.assertTrue(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order.status = Order.COMPLETED
        order.save()
        user.refresh_from_db()
        # We have reduced the load, but never took care of the new order, so commissions are still disabled.
        self.assertEqual(user.load, 5)
        self.assertTrue(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        order2.status = Order.CANCELLED
        order2.save()
        order.save()
        # Cancalled the new order, so now the load is within parameters and there are no outstanding new orders.
        user.refresh_from_db()
        self.assertEqual(user.load, 5)
        self.assertFalse(user.commissions_disabled)
        self.assertFalse(user.commissions_closed)
        # Closing commissions should disable them as well.
        user.commissions_closed = True
        user.save()
        self.assertTrue(user.commissions_closed)
        self.assertTrue(user.commissions_disabled)
        user.commissions_closed = False
        order.status = Order.NEW
        order.save()
        # Unclosing commissions shouldn't enable commissions if they still have an outstanding order.
        user.refresh_from_db()
        user.commissions_closed = False
        user.save()
        self.assertFalse(user.commissions_closed)
        self.assertTrue(user.commissions_disabled)
        order.status = Order.CANCELLED
        order.save()
        # We should be clear again.
        user.refresh_from_db()
        self.assertFalse(user.commissions_closed)
        self.assertFalse(user.commissions_disabled)
        Product.objects.all().delete()
        # Make a product too big for the user to complete. Should close the user.
        product = ProductFactory.create(user=user, task_weight=20)
        user.refresh_from_db()
        self.assertFalse(user.commissions_closed)
        self.assertTrue(user.commissions_disabled)
        # And dropping it should open them back up.
        product.task_weight = 1
        product.save()
        user.refresh_from_db()
        self.assertFalse(user.commissions_closed)
        self.assertFalse(user.commissions_disabled)


class TestPremium(APITestCase):
    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @freeze_time('2017-11-10')
    @patch('apps.sales.models.sauce')
    def test_portrait(self, mock_sauce):
        user = UserFactory.create()
        self.login(user)
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post('/api/sales/v1/premium/', {'service': 'portrait', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        user.refresh_from_db()
        self.assertTrue(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 12, 10))
        self.assertFalse(user.landscape_enabled)
        self.assertIsNone(user.landscape_paid_through)
        mock_sauce.saved_card.return_value.capture.assert_called_with(Decimal('2.00'), cvv=None)

    @freeze_time('2017-11-10')
    @override_settings(LANDSCAPE_PRICE=Decimal('6.00'))
    @patch('apps.sales.models.sauce')
    def test_landscape(self, mock_sauce):
        user = UserFactory.create()
        self.login(user)
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post('/api/sales/v1/premium/', {'service': 'landscape', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        user.refresh_from_db()
        self.assertFalse(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 12, 10))
        self.assertTrue(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 12, 10))
        mock_sauce.saved_card.return_value.capture.assert_called_with(Decimal('6.00'), cvv=None)

    @freeze_time('2017-11-10')
    @override_settings(LANDSCAPE_PRICE=Decimal('6.00'), PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.models.sauce')
    def test_upgrade(self, mock_sauce):
        user = UserFactory.create()
        self.login(user)
        user.portrait_paid_through = date(2017, 11, 15)
        user.portrait_enabled = True
        user.save()
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post('/api/sales/v1/premium/', {'service': 'landscape', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        user.refresh_from_db()
        self.assertFalse(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 12, 10))
        self.assertTrue(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 12, 10))
        mock_sauce.saved_card.return_value.capture.assert_called_with(Decimal('4.00'), cvv=None)

    @freeze_time('2017-11-10')
    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.models.sauce')
    def test_reenable_portrait(self, mock_sauce):
        user = UserFactory.create()
        self.login(user)
        user.portrait_paid_through = date(2017, 11, 15)
        user.portrait_enabled = False
        user.save()
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post('/api/sales/v1/premium/', {'service': 'portrait', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 11, 15))
        self.assertFalse(user.landscape_enabled)
        self.assertIsNone(user.landscape_paid_through)
        mock_sauce.saved_card.return_value.capture.assert_not_called()

    @freeze_time('2017-11-10')
    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.models.sauce')
    def test_enable_portrait_after_landscape(self, mock_sauce):
        user = UserFactory.create()
        self.login(user)
        user.landscape_paid_through = date(2017, 11, 15)
        user.landscape_enabled = False
        user.save()
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_sauce.saved_card.return_value.capture.return_value.uid = 'Trans123'
        response = self.client.post('/api/sales/v1/premium/', {'service': 'portrait', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 11, 15))
        self.assertFalse(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 11, 15))
        mock_sauce.saved_card.return_value.capture.assert_not_called()


class TestCancelPremium(APITestCase):
    def test_cancel(self):
        user = UserFactory.create()
        self.login(user)
        user.portrait_paid_through = date(2017, 11, 15)
        user.landscape_enabled = True
        user.portrait_enabled = True
        user.landscape_paid_through = date(2017, 11, 18)
        user.save()
        response = self.client.post('/api/sales/v1/cancel-premium/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.portrait_enabled)
        self.assertFalse(user.landscape_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 11, 15))
        self.assertEqual(user.landscape_paid_through, date(2017, 11, 18))


class TestCreateInvoice(APITestCase):
    def test_create_invoice_no_bank_configured(self):
        user = UserFactory.create()
        self.login(user)
        user.bank_account_status = None
        user.save()
        response = self.client.post('/api/sales/v1/create-invoice/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invoice(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.bank_account_status = User.HAS_US_ACCOUNT
        user.save()
        product = ProductFactory.create(
            user=user, price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2
        )
        response = self.client.post('/api/sales/v1/create-invoice/', {
            'complete': False,
            'product': product.id,
            'buyer': user2.id,
            'price': '5.00',
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'expected_turnaround': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertEqual(response.data['buyer']['id'], user2.id)
        # Handled by serializer method. Maybe should be changed?
        self.assertEqual(response.data['price'], Decimal('3.00'))
        self.assertEqual(response.data['adjustment'], '2.00')
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(response.data['private'], False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], '2.00')
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['price'], '3.00')
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], '2.00')

        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.price, Money('3.00', 'USD'))
        self.assertIsNone(order.claim_token)

    def test_create_invoice_email(self):
        user = UserFactory.create()
        self.login(user)
        user.bank_account_status = User.HAS_US_ACCOUNT
        user.save()
        product = ProductFactory.create(
            user=user, price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2
        )
        response = self.client.post('/api/sales/v1/create-invoice/', {
            'complete': False,
            'product': product.id,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'private': True,
            'task_weight': 3,
            'expected_turnaround': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertIsNone(response.data['buyer'])
        # Handled by serializer method. Maybe should be changed?
        self.assertEqual(response.data['price'], Decimal('3.00'))
        self.assertEqual(response.data['adjustment'], '2.00')
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], '2.00')
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['price'], '3.00')
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], '2.00')

        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.price, Money('3.00', 'USD'))
        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_escrow_disabled(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.bank_account_status = User.NO_US_ACCOUNT
        user.save()
        product = ProductFactory.create(
            user=user, price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2
        )
        response = self.client.post('/api/sales/v1/create-invoice/', {
            'complete': False,
            'product': product.id,
            'buyer': user2.id,
            'price': '5.00',
            'task_weight': 3,
            'details': 'bla bla',
            'private': True,
            'expected_turnaround': 4,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertEqual(response.data['buyer']['id'], user2.id)
        # Handled by serializer method. Maybe should be changed?
        self.assertEqual(response.data['price'], Decimal('3.00'))
        self.assertEqual(response.data['adjustment'], '2.00')
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['details'], 'bla bla')
        self.assertTrue(response.data['private'])
        self.assertEqual(response.data['adjustment_expected_turnaround'], '2.00')
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['price'], '3.00')
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], '2.00')

        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.price, Money('3.00', 'USD'))
        self.assertIsNone(order.claim_token)
