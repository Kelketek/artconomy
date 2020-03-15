from decimal import Decimal
from unittest.mock import patch, Mock

from ddt import data, unpack, ddt
from django.core import mail
from django.test import override_settings
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status

from apps.lib.models import Comment
from apps.lib.test_resources import APITestCase, PermissionsTestCase, MethodAccessMixin
from apps.lib.tests.factories import TagFactory, AssetFactory
from apps.profiles.models import User, HAS_US_ACCOUNT, NO_US_ACCOUNT, UNSET
from apps.profiles.tests.factories import UserFactory, SubmissionFactory
from apps.sales.authorize import AuthorizeException, CardInfo, AddressInfo
from apps.sales.models import (
    Order, CreditCardToken, Product, TransactionRecord, ADD_ON, BASE_PRICE, NEW, COMPLETED, IN_PROGRESS,
    PAYMENT_PENDING,
    REVIEW, QUEUED, DISPUTED, CANCELLED, DELIVERABLE_STATUSES, REFUNDED, Deliverable)
from apps.sales.tests.factories import DeliverableFactory, CreditCardTokenFactory, ProductFactory, RevisionFactory, \
    RatingFactory, OrderFactory, ReferenceFactory
from apps.sales.views import (
    CurrentOrderList, CurrentSalesList, CurrentCasesList,
    CancelledOrderList,
    ArchivedOrderList,
    CancelledSalesList,
    ArchivedSalesList,
    CancelledCasesList,
    ArchivedCasesList,
    ProductList)

order_scenarios = (
    {
        'category': 'current',
        'included': (NEW, IN_PROGRESS, DISPUTED, REVIEW, PAYMENT_PENDING, QUEUED),
    },
    {
        'category': 'archived',
        'included': (COMPLETED,),
    },
    {
        'category': 'cancelled',
        'included': (REFUNDED, CANCELLED),
    }
)

categories = [scenario['category'] for scenario in order_scenarios]


@ddt
class TestOrderListBase(object):
    @unpack
    @data(*order_scenarios)
    def test_fetch_orders(self, category, included):
        if self.rebuild_fixtures:
            self.rebuild_fetch()
        user = User.objects.get(username='Fox')
        self.login(user)
        response = self.client.get(self.make_url(user, category))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for order in response.data['results']:
            self.assertIn(Deliverable.objects.filter(order_id=order['id']).first().status, included)
        self.assertEqual(len(response.data['results']), len(included))

    def rebuild_fetch(self):
        user = UserFactory.create(username='Fox')
        kwargs = self.factory_kwargs(user)
        [DeliverableFactory.create(status=order_status, **kwargs) for order_status in [x for x, y in DELIVERABLE_STATUSES]]
        self.save_fixture(self.fixture_list[0])


class TestOrderLists(TestOrderListBase, APITestCase):
    fixture_list = ['order-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/orders/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {'order__buyer': user, 'order__seller': UserFactory.create()}


class TestSaleLists(TestOrderListBase, APITestCase):
    fixture_list = ['sale-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/sales/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {'order__seller': user, 'order__buyer': UserFactory.create()}


class TestCaseLists(TestOrderListBase, APITestCase):
    fixture_list = ['case-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/cases/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        user.is_staff = True
        user.save()
        return {'arbitrator': user, 'order__buyer': UserFactory.create(), 'order__seller': UserFactory.create()}


order_passes = {**MethodAccessMixin.passes, 'get': ['user', 'staff']}


class TestCurrentOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CurrentOrderList


class TestCancelledOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CancelledOrderList


class TestArchivedOrderListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = ArchivedOrderList


class TestCurrentSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CurrentSalesList


class TestCancelledSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = CancelledSalesList


class TestArchivedSalesListPermissions(MethodAccessMixin, PermissionsTestCase):
    passes = order_passes
    kwargs = {'username': 'Test'}
    view_class = ArchivedSalesList


class StaffUserList:
    def test_self(self):
        request = self.factory.get('/')
        request.user = self.user
        self.check_perms(request, self.user)

    def test_self_staff(self):
        request = self.factory.get('/')
        request.user = self.user
        request.user.is_staff = True
        self.check_perms(request, self.user, fails=False)


staff_order_passes = {**order_passes, 'get': ['staff']}


class TestCurrentCasesListPermissions(PermissionsTestCase, StaffUserList, MethodAccessMixin):
    passes = staff_order_passes
    kwargs = {'username': 'Test'}
    view_class = CurrentCasesList


class TestCancelledCasesListPermissions(PermissionsTestCase, StaffUserList, MethodAccessMixin):
    passes = staff_order_passes
    kwargs = {'username': 'Test'}
    view_class = CancelledCasesList


class TestArchivedCasesListPermissions(PermissionsTestCase, StaffUserList, MethodAccessMixin):
    passes = staff_order_passes
    kwargs = {'username': 'Test'}
    view_class = ArchivedCasesList


class TestSamples(APITestCase):
    def test_sample_list(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        response = self.client.get(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['submission']['id'], submission.id)

    def test_destroy_sample(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        linked = Product.samples.through.objects.get(submission=submission, product=product)
        self.login(product.user)
        response = self.client.delete(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/{linked.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(product.samples.all().count(), 0)

    def test_destroy_sample_primary(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        product.samples.add(submission)
        product.primary_submission = submission
        product.save()
        linked = Product.samples.through.objects.get(submission=submission, product=product)
        self.login(product.user)
        response = self.client.delete(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/{linked.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(product.samples.all().count(), 0)
        product.refresh_from_db()
        self.assertIsNone(product.primary_submission)

    def test_add_sample(self):
        product = ProductFactory.create()
        submission = SubmissionFactory.create()
        submission.artists.add(product.user)
        self.login(product.user)
        response = self.client.post(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/samples/',
            {'submission_id': submission.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['submission']['id'], submission.id)

class TestCardManagement(APITestCase):
    @freeze_time('2018-01-01 12:00:00')
    @patch('apps.sales.models.create_customer_profile')
    @patch('apps.sales.models.create_card')
    def test_add_card(self, mock_create_card, mock_create_customer_profile):
        mock_create_customer_profile.return_value = '5643'
        user = UserFactory.create(authorize_token='')
        self.login(user)
        mock_create_card.return_value = '567453'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], user.id)
        card = CreditCardToken.objects.get(user=user)
        self.assertEqual(card.payment_id, '567453')
        user.refresh_from_db()
        self.assertEqual(user.authorize_token, '5643')
        mock_create_card.assert_called_with(
            CardInfo(number='4111111111111111', exp_month=2, exp_year=2034, cvv='555'),
            AddressInfo(country='US', postal_code='44444', first_name='Jim', last_name='Bob'),
            '5643',
        )
        mock_create_customer_profile.expect_called_with(user.email)

    @freeze_time('2018-01-01 12:00:00')
    @patch('apps.sales.models.create_customer_profile')
    @patch('apps.sales.models.create_card')
    def test_add_card_error(self, mock_create_card, mock_create_customer_profile):
        user = UserFactory.create(authorize_token='')
        self.login(user)
        mock_create_customer_profile.side_effect = AuthorizeException('Wat')
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Wat')
        mock_create_card.assert_not_called()

    @patch('apps.sales.models.create_customer_profile')
    @patch('apps.sales.models.create_card')
    def test_add_card_primary_exists(self, mock_create_card, _mock_create_customer_profile):
        user = UserFactory.create(authorize_token='12345')
        self.login(user)
        primary_card = CreditCardTokenFactory(user=user)
        user.primary_card = primary_card
        user.save()
        mock_create_card.return_value = '64858'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 1)
        self.assertEqual(response.data['primary'], False)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(CreditCardToken.objects.filter(user=user).count(), 2)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, primary_card.id)

    @patch('apps.sales.models.create_customer_profile')
    @patch('apps.sales.models.create_card')
    def test_add_card_new_primary(self, mock_create_card, mock_create_customer_profile):
        user = UserFactory.create(authorize_token='12345')
        self.login(user)
        card = CreditCardTokenFactory(user=user)
        user.primary_card = card
        user.save()
        mock_create_card.return_value = '6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
                'make_primary': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(CreditCardToken.objects.filter(user=user).count(), 2)
        user.refresh_from_db()
        self.assertEqual(user.primary_card.id, response.data['id'])
        self.assertFalse(mock_create_customer_profile.called)

    @patch('apps.sales.models.create_customer_profile')
    @patch('apps.sales.models.create_card')
    def test_card_add_not_logged_in(self, mock_create_card, _mock_create_customer_profile):
        user = UserFactory.create()
        primary_card = CreditCardTokenFactory(user=user)
        user.primary_card = primary_card
        user.save()
        mock_create_card.return_value = '12345|6789'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.models.create_customer_profile')
    @patch('apps.sales.models.create_card')
    def test_add_card_outsider(self, mock_card_api, mock_create_customer_profile):
        mock_create_customer_profile.return_value = '2345'
        mock_card_api.return_value = '1234'
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        primary_card = CreditCardTokenFactory(user=user)
        user.primary_card = primary_card
        user.save()
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time('2018-01-01 12:00:00')
    @patch('apps.sales.models.create_customer_profile')
    @patch('apps.sales.models.create_card')
    def test_add_card_staffer(self, mock_create_card, mock_create_customer_profile):
        mock_create_customer_profile.return_value = '1234'
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        mock_create_card.return_value = '6543'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'security_code': '555',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 1)
        self.assertEqual(response.data['primary'], True)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(response.data['last_four'], '1111')
        card = CreditCardToken.objects.get(user=user)
        self.assertEqual(card.payment_id, '6543')

    @freeze_time('2018-01-01 12:00:00')
    @patch('apps.sales.models.create_card')
    @patch('apps.sales.views.renew')
    def test_add_card_renew_portrait(self, mock_renew, mock_create_card):
        user = UserFactory.create()
        user.portrait_enabled = True
        user.save()
        self.login(user)
        mock_create_card.return_value = '923047'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_renew.delay.assert_called_with(user.id, 'portrait')
        mock_create_card.assert_called_with(
            CardInfo(number='4111111111111111', exp_month=2, exp_year=2034, cvv='555'),
            AddressInfo(country='US', postal_code='44444', first_name='Jim', last_name='Bob'),
            user.authorize_token,
        )

    @freeze_time('2018-01-01 12:00:00')
    @patch('apps.sales.models.create_card')
    @patch('apps.sales.views.renew')
    def test_add_card_renew_landscape(self, mock_renew, mock_create_card):
        user = UserFactory.create()
        user.portrait_enabled = True
        user.landscape_enabled = True
        user.save()
        self.login(user)
        mock_create_card.return_value = '923047'
        response = self.client.post(
            '/api/sales/v1/account/{}/cards/'.format(user.username),
            {
                'first_name': 'Jim',
                'last_name': 'Bob',
                'country': 'US',
                'number': '4111 1111 1111 1111',
                'exp_date': '02/34',
                'zip': '44444',
                'cvv': '555',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_renew.delay.assert_called_with(user.id, 'landscape')
        mock_create_card.assert_called_with(
            CardInfo(number='4111111111111111', exp_month=2, exp_year=2034, cvv='555'),
            AddressInfo(country='US', postal_code='44444', first_name='Jim', last_name='Bob'),
            user.authorize_token,
        )

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
            self.assertIDInList(card, response.data)

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
            self.assertIDInList(card, response.data)

    @patch('apps.sales.authorize.execute')
    def test_card_removal(self, _mock_execute):
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

    @patch('apps.sales.authorize.execute')
    def test_card_removal_new_primary(self, _mock_execute):
        old_card = CreditCardTokenFactory.create()
        new_card = CreditCardTokenFactory.create(user=old_card.user)
        user = old_card.user
        user.primary_card = new_card
        user.save()
        self.login(user)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, new_card.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertEqual(user.primary_card, old_card)

    @patch('apps.sales.authorize.execute')
    def test_card_removal_not_logged_in(self, _mock_execute):
        user = UserFactory.create()
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    @patch('apps.sales.authorize.execute')
    def test_card_removal_outsider(self, _mock_execute):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        cards = [CreditCardTokenFactory(user=user) for __ in range(4)]
        self.assertEqual(cards[2].active, True)
        response = self.client.delete('/api/sales/v1/account/{}/cards/{}/'.format(user.username, cards[2].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        cards[2].refresh_from_db()
        self.assertEqual(cards[2].active, True)

    @patch('apps.sales.authorize.execute')
    def test_card_removal_staff(self, _mock_execute):
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


class TestProductListPermissions(PermissionsTestCase, MethodAccessMixin):
    passes = {**MethodAccessMixin.passes}
    passes['get'] = ['user', 'staff', 'outsider', 'anonymous']
    passes['post'] = ['user', 'staff']
    view_class = ProductList

    def get_object(self):
        product = Mock()
        product.user = self.user
        return product


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
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3.00)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_free(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 0,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3.00)
        self.assertEqual(result['base_price'], 0.00)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(MINIMUM_PRICE=Decimal('1.00'))
    def test_create_product_minimum_unmet(self):
        user = UserFactory.create()
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 0.50,
            }
        )
        result = response.data
        self.assertEqual(result['base_price'], ['Must be at least $1.00'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(MINIMUM_PRICE=Decimal('1.00'))
    def test_create_product_minimum_irrelevant(self):
        user = UserFactory.create(artist_profile__escrow_disabled=True)
        self.login(user)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 0.50,
            }
        )
        result = response.data
        self.assertEqual(result['base_price'], 0.50)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_not_logged_in(self):
        user = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=user)
        self.login(user2)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_staff(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        asset = AssetFactory.create(uploaded_by=staffer)
        self.login(staffer)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/'.format(user.username),
            {
                'description': 'I will draw you a porn.',
                'file': str(asset.id),
                'name': 'Pornographic refsheet',
                'revisions': 2,
                'task_weight': 2,
                'expected_turnaround': 3,
                'base_price': 2.50,
            }
        )
        result = response.data
        self.assertEqual(result['description'], 'I will draw you a porn.')
        self.assertEqual(result['name'], 'Pornographic refsheet')
        self.assertEqual(result['revisions'], 2)
        self.assertEqual(result['task_weight'], 2)
        self.assertEqual(result['expected_turnaround'], 3.00)
        self.assertEqual(result['base_price'], 2.50)
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

    def test_product_inventory(self):
        product = ProductFactory.create(track_inventory=True)
        response = self.client.get(f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_set_product_inventory_not_logged_in(self):
        product = ProductFactory.create(track_inventory=True)
        response = self.client.patch(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/',
            {'count': 3}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_product_inventory_wrong_user(self):
        product = ProductFactory.create(track_inventory=True)
        self.login(UserFactory.create())
        response = self.client.patch(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/',
            {'count': 3}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_product_inventory(self):
        product = ProductFactory.create(track_inventory=True)
        self.login(product.user)
        response = self.client.patch(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/',
            {'count': 3}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_product_inventory_no_tracking(self):
        product = ProductFactory.create(track_inventory=False)
        response = self.client.get(f'/api/sales/v1/account/{product.user.username}/products/{product.id}/inventory/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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


class TestComment(APITestCase):
    def test_make_comment(self):
        deliverable = DeliverableFactory.create()
        self.login(deliverable.order.buyer)
        response = self.client.post(
            '/api/lib/v1/comments/sales.Deliverable/{}/'.format(deliverable.id),
            {'text': 'test comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = response.data
        self.assertEqual(comment['text'], 'test comment')
        self.assertEqual(comment['user']['username'], deliverable.order.buyer.username)
        Comment.objects.get(id=comment['id'])


class TestProductSearch(APITestCase):
    def test_query_not_logged_in(self):
        if self.rebuild_fixtures:
            ProductFactory.create(name='Test1')
            product2 = ProductFactory.create(name='Wat product 2')
            tag = TagFactory.create(name='test')
            product2.tags.add(tag)
            ProductFactory.create(
                name='Test3', task_weight=5, user__artist_profile__load=2, user__artist_profile__max_load=10,
            )
            # Hidden products
            ProductFactory.create(name='TestHidden', hidden=True)
            hidden = ProductFactory.create(name='Wat2 hidden', hidden=True)
            hidden.tags.add(tag)
            ProductFactory.create(
                name='Test4 overload', task_weight=5, user__artist_profile__load=10, user__artist_profile__max_load=10,
            )
            maxed = ProductFactory.create(name='Test5 maxed', max_parallel=2)
            DeliverableFactory.create(order__product=maxed, status=IN_PROGRESS)
            DeliverableFactory.create(order__product=maxed, status=QUEUED)
            maxed.refresh_from_db()
            overloaded = ProductFactory.create(name='Test6 overloaded', task_weight=1, user__artist_profile__max_load=5)
            DeliverableFactory.create(order__seller=overloaded.user, task_weight=7, status=IN_PROGRESS)
            ProductFactory.create(name='Test commissions closed', user__artist_profile__commissions_closed=True)
            overloaded.user.refresh_from_db()
            # for user in User.objects.filter(products__isnull=False):
            #     update_availability(user, user.artist_profile.load, user.artist_profile.commissions_closed)
            self.save_fixture('search-not-logged-in')
        else:
            self.load_fixture('search-not-logged-in')

        product1, product2, product3 = Product.objects.filter(
            name__in=['Test1', 'Wat product 2', 'Test3']
        ).order_by('id').values_list('id', flat=True)


        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)

    def test_query_logged_in(self):
        if self.rebuild_fixtures:
            user = UserFactory.create(username='Fox')
            user2 = UserFactory.create()
            ProductFactory.create(name='Test1')
            product2 = ProductFactory.create(name='Wat')
            tag = TagFactory.create(name='test')
            product2.tags.add(tag)
            ProductFactory.create(name='Test3', task_weight=5)
            # Overweighted.
            ProductFactory.create(name='Test4', task_weight=100, user=user)
            product4 = ProductFactory.create(name='Test5', max_parallel=2, user=user)
            DeliverableFactory.create(order__product=product4)
            DeliverableFactory.create(order__product=product4)
            # Product from blocked user. Shouldn't be in results.
            ProductFactory.create(name='Test Blocked', user=user2)
            user.blocking.add(user2)

            ProductFactory.create(user__artist_profile__commissions_closed=True)

            user.artist_profile.max_load = 10
            user.artist_profile.load = 2
            user.artist_profile.save()
            self.save_fixture('search-logged-in')
        else:
            self.load_fixture('search-logged-in')

        user = User.objects.get(username='Fox')
        self.login(user)
        product1, product2, product3, product4 = Product.objects.filter(name__in=[
            'Test1', 'Wat', 'Test3', 'Test5'
        ]).order_by('id').values_list('id', flat=True)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertIDInList(product4, response.data['results'])
        self.assertEqual(len(response.data['results']), 4)

    def test_query_different_user(self):
        if self.rebuild_fixtures:
            ProductFactory.create(name='Test1')
            product2 = ProductFactory.create(name='Wat')
            tag = TagFactory.create(name='test')
            product2.tags.add(tag)
            ProductFactory.create(
                name='Test3', task_weight=5, user__artist_profile__load=2, user__artist_profile__max_load=10
            )
            # Hidden products
            ProductFactory.create(name='Test4', hidden=True)
            hidden = ProductFactory.create(name='Wat2', hidden=True)
            hidden.tags.add(tag)
            ProductFactory.create(
                name='Test5', task_weight=5, user__artist_profile__load=8, user__artist_profile__max_load=10,
            )
            overloaded = ProductFactory.create(name='Test6', max_parallel=2)
            ProductFactory.create(user__artist_profile__commissions_closed=True)
            DeliverableFactory.create(order__product=overloaded, status=IN_PROGRESS)
            DeliverableFactory.create(order__product=overloaded, status=QUEUED)

            UserFactory.create(username='Fox')
            self.save_fixture('search-different-user')
        else:
            self.load_fixture('search-different-user')

        user = User.objects.get(username='Fox')
        product1, product2, product3 = Product.objects.filter(
            name__in=['Test1', 'Wat', 'Test3']
        ).order_by('id').values_list('id', flat=True)
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertIDInList(product1, response.data['results'])
        self.assertIDInList(product2, response.data['results'])
        self.assertIDInList(product3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)

    def test_blocked(self):
        if self.rebuild_fixtures:
            product = ProductFactory.create(name='Test1')
            user = UserFactory.create(username='Fox')
            user.blocking.add(product.user)
            self.save_fixture('search-blocked')
        else:
            self.load_fixture('search-blocked')
        user = User.objects.get(username='Fox')
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/', {'q': 'test'})
        self.assertEqual(len(response.data['results']), 0)

    def test_personal(self):
        if self.rebuild_fixtures:
            user = UserFactory.create(username='Fox')
            ProductFactory.create(user=user, name='Test')
            ProductFactory.create(user=user, name='Test2', hidden=True)
            ProductFactory.create(user=user, task_weight=999, name='Test3')
            # Inactive.
            ProductFactory.create(user=user, active=False, name='Test4')
            # Wrong user.
            ProductFactory.create(name='Test5')
            self.save_fixture('search-personal')
        else:
            self.load_fixture('search-personal')

        user = User.objects.get(username='Fox')
        listed, listed2, listed3 = Product.objects.filter(
            name__in=['Test', 'Test2', 'Test3']
        ).order_by('id').values_list('id', flat=True)
        self.login(user)
        response = self.client.get('/api/sales/v1/search/product/Fox/', {'q': 'test'})
        self.assertIDInList(listed, response.data['results'])
        self.assertIDInList(listed2, response.data['results'])
        self.assertIDInList(listed3, response.data['results'])
        self.assertEqual(len(response.data['results']), 3)


class TestPremium(APITestCase):
    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @freeze_time('2017-11-10 12:00:00')
    @patch('apps.sales.views.charge_saved_card')
    def test_portrait(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post('/api/sales/v1/premium/', {'service': 'portrait', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 12, 10))
        self.assertFalse(user.landscape_enabled)
        self.assertIsNone(user.landscape_paid_through)
        mock_charge_card.assert_called_with(
            payment_id=card.payment_id, profile_id=card.profile_id, amount=Decimal('2.00'), cvv=None
        )

    @freeze_time('2017-11-10 12:00:00')
    @override_settings(LANDSCAPE_PRICE=Decimal('6.00'))
    @patch('apps.sales.views.charge_saved_card')
    def test_landscape(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post('/api/sales/v1/premium/', {'service': 'landscape', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 12, 10))
        self.assertTrue(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 12, 10))
        mock_charge_card.assert_called_with(
            payment_id=card.payment_id, profile_id=card.profile_id, amount=Decimal('6.00'), cvv=None
        )

    @freeze_time('2017-11-10 12:00:00')
    @override_settings(LANDSCAPE_PRICE=Decimal('6.00'), PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.views.charge_saved_card')
    def test_upgrade(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        user.portrait_paid_through = date(2017, 11, 15)
        user.portrait_enabled = True
        user.save()
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post('/api/sales/v1/premium/', {'service': 'landscape', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 12, 10))
        self.assertTrue(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 12, 10))
        mock_charge_card.assert_called_with(
            profile_id=card.profile_id, payment_id=card.payment_id, amount=Decimal('4.00'), cvv=None,
        )

    @freeze_time('2017-11-10 12:00:00')
    @override_settings(LANDSCAPE_PRICE=Decimal('6.00'), PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.views.charge_saved_card')
    def test_upgrade_card_failure(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        user.portrait_paid_through = date(2017, 11, 15)
        user.portrait_enabled = True
        user.save()
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post('/api/sales/v1/premium/', {'service': 'landscape', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertFalse(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 12, 10))
        self.assertTrue(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 12, 10))
        mock_charge_card.assert_called_with(
            profile_id=card.profile_id, payment_id=card.payment_id, amount=Decimal('4.00'), cvv=None,
        )

    @freeze_time('2017-11-10 12:00:00')
    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.views.charge_saved_card')
    def test_reenable_portrait(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        user.portrait_paid_through = date(2017, 11, 15)
        user.portrait_enabled = False
        user.save()
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_charge_card.return_value = '36985214745'
        response = self.client.post('/api/sales/v1/premium/', {'service': 'portrait', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 11, 15))
        self.assertFalse(user.landscape_enabled)
        self.assertIsNone(user.landscape_paid_through)
        mock_charge_card.assert_not_called()

    @freeze_time('2017-11-10 12:00:00')
    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @patch('apps.sales.views.charge_saved_card')
    def test_enable_portrait_after_landscape(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        user.landscape_paid_through = date(2017, 11, 15)
        user.landscape_enabled = False
        user.save()
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_charge_card.return_value = '36985214745'
        response = self.client.post('/api/sales/v1/premium/', {'service': 'portrait', 'card_id': card.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.portrait_enabled)
        self.assertEqual(user.portrait_paid_through, date(2017, 11, 15))
        self.assertFalse(user.landscape_enabled)
        self.assertEqual(user.landscape_paid_through, date(2017, 11, 15))
        mock_charge_card.assert_not_called()


class TestCancelPremium(APITestCase):
    def test_cancel(self):
        user = UserFactory.create()
        self.login(user)
        user.portrait_paid_through = date(2017, 11, 15)
        user.landscape_enabled = True
        user.portrait_enabled = True
        user.landscape_paid_through = date(2017, 11, 18)
        user.save()
        response = self.client.post(f'/api/sales/v1/account/{user.username}/cancel-premium/')
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
        user.artist_profile.bank_account_status = UNSET
        user.artist_profile.save()
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invoice(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = HAS_US_ACCOUNT
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], PAYMENT_PENDING)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(order.private, False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['revisions_hidden'])
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(order.product, product)

        deliverable = Deliverable.objects.get(id=response.data['id'])
        item = deliverable.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money('2.00', 'USD'))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        item = deliverable.line_items.get(type=BASE_PRICE)
        self.assertEqual(item.amount, Money('3.00', 'USD'))
        self.assertEqual(item.priority, 0)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        self.assertIsNone(order.claim_token)

    def test_create_invoice_table_product(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = HAS_US_ACCOUNT
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1, table_product=True,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '15.00',
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'revisions': 3,
            'paid': False,
            'hold': False,
            'expected_turnaround': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], PAYMENT_PENDING)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(order.private, False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['revisions_hidden'])
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(order.product, product)
        self.assertEqual(order.product.base_price, Money('3.00', 'USD'))
        self.assertEqual(order.product.task_weight, 5)
        self.assertEqual(order.product.expected_turnaround, 2.00)
        self.assertEqual(order.product.revisions, 1)

        deliverable = Deliverable.objects.get(id=response.data['id'])
        # Actual price will be $8-- $3 plus the $5 static fee. Setting the order price to $15 will make a $7 adjustment.
        item = deliverable.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money('7.00', 'USD'))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        item = deliverable.line_items.get(type=BASE_PRICE)
        self.assertEqual(item.amount, Money('3.00', 'USD'))
        self.assertEqual(item.priority, 0)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        self.assertIsNone(order.claim_token)

    def test_create_invoice_email(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = HAS_US_ACCOUNT
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'private': True,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(order.product, product)
        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_completed(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = HAS_US_ACCOUNT
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': True,
            'product': product.id,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'private': True,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
            'paid': False,
            'hold': False,
        })
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data['adjustment_task_weight'], -5)
        self.assertEqual(response.data['adjustment_expected_turnaround'], -2)
        self.assertEqual(response.data['adjustment_revisions'], -1)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(order.product, product)

        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_no_product(self):
        user = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = HAS_US_ACCOUNT
        user.artist_profile.save()
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': None,
            'buyer': 'test@example.com',
            'price': '5.00',
            'details': 'oh',
            'private': True,
            'task_weight': 2,
            'paid': False,
            'hold': False,
            'revisions': 3,
            'expected_turnaround': 4
        }, format='json')
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.seller, user)
        self.assertIsNone(order.buyer)
        self.assertEqual(response.data['adjustment_task_weight'], 0)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 0)
        self.assertEqual(response.data['adjustment_revisions'], 0)
        self.assertEqual(response.data['task_weight'], 2)
        self.assertEqual(response.data['revisions'], 3)
        self.assertEqual(response.data['details'], 'oh')
        self.assertEqual(response.data['expected_turnaround'], 4)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertIsNone(order.product)

        self.assertEqual(order.customer_email, 'test@example.com')
        self.assertTrue(order.claim_token)

    def test_create_invoice_escrow_disabled(self):
        user = UserFactory.create(artist_mode=True)
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = NO_US_ACCOUNT
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'task_weight': 3,
            'details': 'bla bla',
            'private': True,
            'revisions': 3,
            'expected_turnaround': 4,
            'hold': False,
            'paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['details'], 'bla bla')
        self.assertTrue(order.private)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(order.product, product)
        self.assertIsNone(order.claim_token)

    def test_create_invoice_paid(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = HAS_US_ACCOUNT
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': False,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'paid': True,
            'hold': False,
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], QUEUED)
        self.assertEqual(response.data['details'], 'wat')
        self.assertFalse(order.private)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertFalse(response.data['revisions_hidden'])
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(order.product, product)
        self.assertIsNone(order.claim_token)

    def test_create_invoice_paid_and_completed(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        user.artist_profile.bank_account_status = HAS_US_ACCOUNT
        user.artist_profile.save()
        product = ProductFactory.create(
            user=user, base_price=Money('3.00', 'USD'), task_weight=5, expected_turnaround=2,
            revisions=1,
        )
        response = self.client.post(f'/api/sales/v1/account/{user.username}/create-invoice/', {
            'completed': True,
            'product': product.id,
            'buyer': user2.username,
            'price': '5.00',
            'paid': True,
            'hold': False,
            'details': 'wat',
            'private': False,
            'task_weight': 3,
            'revisions': 3,
            'expected_turnaround': 4
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=response.data['order']['id'])
        self.assertEqual(order.seller, user)
        self.assertEqual(order.buyer, user2)
        self.assertEqual(response.data['status'], IN_PROGRESS)
        self.assertEqual(response.data['details'], 'wat')
        self.assertFalse(order.private)
        self.assertEqual(response.data['adjustment_task_weight'], -5)
        self.assertEqual(response.data['adjustment_expected_turnaround'], -2)
        self.assertEqual(response.data['adjustment_revisions'], -1)
        self.assertFalse(response.data['revisions_hidden'])
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(order.product, product)
        self.assertIsNone(order.claim_token)


class TestLists(APITestCase):
    def test_new_products(self):
        user = UserFactory.create()
        product = ProductFactory.create(user=user)
        response = self.client.get('/api/sales/v1/new-products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], product.id)

    def test_who_is_open(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create()
        response = self.client.get('/api/sales/v1/who-is-open/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        user.watching.add(product.user)
        response = self.client.get('/api/sales/v1/who-is-open/')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], product.id)

    def test_rating_list(self):
        user = UserFactory.create()
        rating = RatingFactory.create(target=user)
        response = self.client.get(f'/api/sales/v1/account/{user.username}/ratings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], rating.id)

    def test_featured_products(self):
        ProductFactory.create(active=False, featured=True)
        active_product = ProductFactory.create(active=True, featured=True)
        ProductFactory.create(active=True, featured=True, hidden=True)
        response = self.client.get('/api/sales/v1/featured-products/')
        self.assertEqual(len(response.data['results']), 1)
        self.assertIDInList(active_product, response.data['results'])


class TestSalesStats(APITestCase):
    def test_sales_stats(self):
        user = UserFactory.create()
        self.login(user)
        response = self.client.get(f'/api/sales/v1/account/{user.username}/sales/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPremiumInfo(APITestCase):
    @override_settings(PREMIUM_PERCENTAGE_BONUS=Decimal('69'))
    def test_premium_info(self):
        response = self.client.get(f'/api/sales/v1/pricing-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['premium_percentage_bonus'], Decimal('69'))


class TestOrderAuth(APITestCase):
    def test_anon_to_existing_guest(self):
        order = OrderFactory.create(buyer=UserFactory.create(
            email='wat@localhost', guest_email='test@example.com', guest=True,
            username='__3'
        ))
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.buyer.id)

    def test_anon_to_new_guest(self):
        order = OrderFactory.create(buyer=None, customer_email='test@example.com')
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['guest_email'], 'test@example.com')
        self.assertEqual(response.data['email'][-9:], 'localhost')
        order.refresh_from_db()
        self.assertEqual(response.data['id'], order.buyer.id)

    def test_anon_chown_attempt(self):
        order = OrderFactory.create(buyer=None, customer_email='test@example.com')
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seller_chown_attempt(self):
        order = OrderFactory.create(buyer=None, customer_email='test@example.com')
        self.login(order.seller)
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_chown_no_guest(self):
        order = OrderFactory.create(buyer=None, customer_email='test@example.com')
        user = UserFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': order.claim_token,
                'id': order.id,
                'chown': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.buyer, user)
        self.assertIsNone(order.claim_token)
        self.assertEqual(order.customer_email, '')

    def test_order_already_claimed(self):
        order = OrderFactory.create()
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': '97uh97',
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_revisiting(self):
        order = OrderFactory.create(buyer=UserFactory.create(
            email='wat@localhost', guest_email='test@example.com', guest=True,
            username='__3'
        ))
        self.login(order.buyer)
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': '97uh97',
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], '__3')

    def test_invalid_token(self):
        order = OrderFactory.create(buyer=UserFactory.create(
            email='wat@localhost', guest_email='test@example.com', guest=True,
            username='__3'
        ))
        response = self.client.post(
            '/api/sales/v1/order-auth/',
            {
                'claim_token': '97uh97',
                'id': order.id,
                'chown': False,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestOrderOutputs(APITestCase):
    def test_order_outputs_get(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        submission = SubmissionFactory.create(deliverable=deliverable)
        response = self.client.get(f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(submission, response.data)

    def test_order_outputs_post(self):
        deliverable = DeliverableFactory.create(status=COMPLETED, final_uploaded=True)
        RevisionFactory.create(deliverable=deliverable)
        self.login(deliverable.order.buyer)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(deliverable.outputs.all().count(), 1)
        output = deliverable.outputs.all()[0]
        self.assertEqual(output.deliverable, deliverable)

    def test_order_output_exists(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        deliverable.outputs.add(SubmissionFactory.create(deliverable=deliverable, owner=deliverable.order.buyer))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/outputs/', {
                'caption': 'Stuff',
                'tags': ['Things', 'wat'],
                'title': 'Hi!'
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deliverable.outputs.all().count(), 1)


class TestOrderInvite(APITestCase):
    def test_order_invite_no_buyer(self):
        order = OrderFactory.create(buyer=None, customer_email='test@example.com')
        self.login(order.seller)
        request = self.client.post(f'/api/sales/v1/order/{order.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox[0].subject, f'You have a new invoice from {order.seller.username}!')
        self.assertIn('This artist should', mail.outbox[0].body)

    def test_order_invite_buyer_not_guest(self):
        order = OrderFactory.create(customer_email='test@example.com')
        self.login(order.seller)
        request = self.client.post(f'/api/sales/v1/order/{order.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_order_invite_buyer_guest(self):
        order = OrderFactory.create(
            buyer__guest=True, buyer__guest_email='test@wat.com',
        )
        self.login(order.seller)
        order.customer_email = 'test@example.com'
        order.save()
        request = self.client.post(f'/api/sales/v1/order/{order.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox[0].subject, f'Claim Link for order #{order.id}.')
        self.assertIn('resend your claim link', mail.outbox[0].body)
        order.refresh_from_db()
        self.assertEqual(order.buyer.guest_email, 'test@example.com')

    def test_order_invite_email_not_set(self):
        order = OrderFactory.create(buyer=None, customer_email='')
        self.login(order.seller)
        request = self.client.post(f'/api/sales/v1/order/{order.id}/invite/')
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)


class TestReferences(APITestCase):
    def test_upload_reference(self):
        deliverable = DeliverableFactory.create()
        asset = AssetFactory.create(uploaded_by=deliverable.order.seller)
        self.login(deliverable.order.seller)
        response = self.client.post(f'/api/sales/v1/references/', {
            'file': asset.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_attach_reference(self):
        deliverable = DeliverableFactory.create()
        reference = ReferenceFactory.create(owner=deliverable.order.seller)
        self.login(deliverable.order.seller)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/references/',
            {'reference_id': reference.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_references(self):
        deliverable = DeliverableFactory.create()
        deliverable.reference_set.add(ReferenceFactory.create(), ReferenceFactory.create(), ReferenceFactory.create())
        self.login(deliverable.order.buyer)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/references/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        # Should be unpaginated.
        self.assertNotIn('results', response.data)
