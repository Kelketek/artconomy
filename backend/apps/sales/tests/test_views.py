from unittest.mock import patch, call, Mock

from dateutil.relativedelta import relativedelta
from ddt import data, unpack, ddt
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import override_settings, TestCase
from django.utils import timezone
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money, Decimal
from rest_framework import status
from short_stuff import slugify

from apps.lib.abstract_models import ADULT, MATURE, GENERAL
from apps.lib.models import DISPUTE, Comment, Subscription, SALE_UPDATE, Notification, REFERRAL_PORTRAIT_CREDIT, \
    REFERRAL_LANDSCAPE_CREDIT
from apps.lib.test_resources import APITestCase, PermissionsTestCase, MethodAccessMixin, SignalsDisabledMixin
from apps.lib.tests.factories import TagFactory, AssetFactory
from apps.profiles.models import User, HAS_US_ACCOUNT, NO_US_ACCOUNT, UNSET, VERIFIED
from apps.profiles.tests.factories import CharacterFactory, UserFactory, SubmissionFactory
from apps.profiles.utils import create_guest_user
from apps.sales.authorize import AuthorizeException, CardInfo, AddressInfo
from apps.sales.models import (
    Order, CreditCardToken, Product, TransactionRecord, Revision,
    BankAccount, ADD_ON, BASE_PRICE, idempotent_lines, TIP, SHIELD)
from apps.sales.tests.factories import OrderFactory, CreditCardTokenFactory, ProductFactory, RevisionFactory, \
    TransactionRecordFactory, BankAccountFactory, RatingFactory, add_adjustment, LineItemFactory
from apps.sales.utils import PENDING
from apps.sales.views import (
    CurrentOrderList, CurrentSalesList, CurrentCasesList,
    CancelledOrderList,
    ArchivedOrderList,
    CancelledSalesList,
    ArchivedSalesList,
    CancelledCasesList,
    ArchivedCasesList,
    ProductList,
    AccountHistory)

from apps.lib.models import COMMENT, REVISION_UPLOADED

order_scenarios = (
    {
        'category': 'current',
        'included': (Order.NEW, Order.IN_PROGRESS, Order.DISPUTED, Order.REVIEW, Order.PAYMENT_PENDING, Order.QUEUED),
    },
    {
        'category': 'archived',
        'included': (Order.COMPLETED,),
    },
    {
        'category': 'cancelled',
        'included': (Order.REFUNDED, Order.CANCELLED),
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
            self.assertIn(order['status'], included)
        self.assertEqual(len(response.data['results']), len(included))

    def rebuild_fetch(self):
        user = UserFactory.create(username='Fox')
        kwargs = self.factory_kwargs(user)
        [OrderFactory.create(status=order_status, **kwargs) for order_status in [x for x, y in Order.STATUSES]]
        self.save_fixture(self.fixture_list[0])


class TestOrderLists(TestOrderListBase, APITestCase):
    fixture_list = ['order-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/orders/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {'buyer': user, 'seller': UserFactory.create()}


class TestSaleLists(TestOrderListBase, APITestCase):
    fixture_list = ['sale-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/sales/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        return {'seller': user, 'buyer': UserFactory.create()}


class TestCaseLists(TestOrderListBase, APITestCase):
    fixture_list = ['case-list']

    @staticmethod
    def make_url(user, category):
        return '/api/sales/v1/account/{}/cases/{}/'.format(user.username, category)

    @staticmethod
    def factory_kwargs(user):
        user.is_staff = True
        user.save()
        return {'arbitrator': user, 'buyer': UserFactory.create(), 'seller': UserFactory.create()}


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


@override_settings(
    SERVICE_STATIC_FEE=Decimal('0.50'), SERVICE_PERCENTAGE_FEE=Decimal('4'),
    PREMIUM_STATIC_BONUS=Decimal('0.25'), PREMIUM_PERCENTAGE_BONUS=Decimal('4'),
)
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
        for character in characters:
            self.assertTrue(character.shared_with.filter(username=response.data['seller']['username']).exists())
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['status'], Order.NEW)
        order = Order.objects.get(id=response.data['id'])
        # These should be set at the point of payment.
        self.assertEqual(order.task_weight, 0)
        self.assertEqual(order.expected_turnaround, 0)

    def test_place_order_inventory_product(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create(task_weight=5, expected_turnaround=3, track_inventory=True)
        product.inventory.count = 1
        product.inventory.save()
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_place_order_inventory_product_out_of_stock(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create(task_weight=5, expected_turnaround=3, track_inventory=True)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'This product is not in stock.')
        self.assertEqual(Order.objects.all().count(), 0)

    def test_place_order_own_product(self):
        product = ProductFactory.create()
        self.login(product.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'This product is not available at this time.')

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'This product is not available at this time.')

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

    def test_add_line_item(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/line-items/'.format(order.id),
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        line_item = order.line_items.get(type=ADD_ON)
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))
        self.assertEqual(line_item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(line_item.destination_user, user)

    def test_add_line_item_too_low(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, product__base_price=Money('15.00', 'USD'))
        response = self.client.post(
            '/api/sales/v1/order/{}/line-items/'.format(order.id),
            {
                'type': ADD_ON,
                'amount': '-14.50',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        self.assertFalse(order.line_items.filter(type=ADD_ON).exists())

    def test_add_line_item_buyer_fail(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user2, buyer=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/line-items/'.format(order.id),
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data)

    def test_add_tip_buyer(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user2, buyer=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/line-items/'.format(order.id),
            {
                'type': TIP,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        line_item = order.line_items.get(type=TIP)
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))
        self.assertEqual(line_item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(line_item.destination_user, user2)

    def test_add_line_item_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user2)
        response = self.client.post(
            '/api/sales/v1/order/{}/line-items/'.format(order.id),
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_line_item_not_logged_in(self):
        user = UserFactory.create()
        order = OrderFactory.create(seller=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/line-items/'.format(order.id),
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_line_item_staff(self):
        staffer = UserFactory.create(is_staff=True)
        user = UserFactory.create()
        self.login(staffer)
        order = OrderFactory.create(seller=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/line-items/'.format(order.id),
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        line_item = order.line_items.get(type=ADD_ON)
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))
        self.assertEqual(line_item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(line_item.destination_user, user)

    def test_edit_line_item(self):
        order = OrderFactory.create()
        line_item = add_adjustment(order, Money('5.00', 'USD'))
        self.login(order.seller)
        response = self.client.patch(
            f'/api/sales/v1/order/{order.id}/line-items/{line_item.id}/',
            {
                # Should be ignored.
                'type': SHIELD,
                'amount': '2.03',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line_item.refresh_from_db()
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))


    def test_edit_line_item_buyer_fail(self):
        order = OrderFactory.create()
        line_item = add_adjustment(order, Money('5.00', 'USD'))
        self.login(order.buyer)
        response = self.client.patch(
            f'/api/sales/v1/order/{order.id}/line-items/{line_item.id}/',
            {
                # Should be ignored.
                'type': SHIELD,
                'amount': '2.03',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        line_item.refresh_from_db()
        self.assertEqual(line_item.amount, Money('5.00', 'USD'))

    def test_edit_line_item_wrong_status(self):
        order = OrderFactory.create(status=Order.QUEUED)
        line_item = add_adjustment(order, Money('5.00', 'USD'))
        self.login(order.seller)
        response = self.client.patch(
            f'/api/sales/v1/order/{order.id}/line-items/{line_item.id}/',
            {
                # Should be ignored.
                'type': SHIELD,
                'amount': '2.03'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        line_item.refresh_from_db()
        self.assertEqual(line_item.amount, Money('5.00', 'USD'))


    def test_delete_line_item(self):
        order = OrderFactory.create()
        line_item = add_adjustment(order, Money('5.00', 'USD'))
        self.login(order.seller)
        response = self.client.delete(
            f'/api/sales/v1/order/{order.id}/line-items/{line_item.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_line_item_buyer_fail(self):
        order = OrderFactory.create()
        line_item = add_adjustment(order, Money('5.00', 'USD'))
        self.login(order.buyer)
        response = self.client.delete(
            f'/api/sales/v1/order/{order.id}/line-items/{line_item.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    @freeze_time('2012-08-01 12:00:00')
    def test_revision_upload(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.QUEUED, revisions=1, rating=ADULT)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        order = Order.objects.get(id=order.id)
        self.assertIsNone(order.auto_finalize_on)
        self.assertEqual(order.status, Order.IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
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

    @freeze_time('2012-08-01 12:00:00')
    def test_final_revision_upload(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, revisions=1, rating=MATURE)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], MATURE)
        order = Order.objects.get(id=order.id)
        self.assertEqual(order.auto_finalize_on, date(2012, 8, 6))
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        # Filling revisions should not mark as complete automatically.
        self.assertEqual(order.auto_finalize_on, date(2012, 8, 6))
        self.assertEqual(order.status, Order.REVIEW)

    @freeze_time('2012-08-01 12:00:00')
    def test_final_revision_upload_dispute(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(seller=user, status=Order.DISPUTED, revisions=1)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], GENERAL)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.DISPUTED)

    @freeze_time('2012-08-01 12:00:00')
    def test_final_revision_upload_escrow_disabled(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            seller=user, status=Order.IN_PROGRESS, revisions=1, escrow_disabled=True, rating=ADULT,
        )
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
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
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time('2012-08-01 12:00:00')
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

    @freeze_time('2012-08-01 12:00:00')
    @patch('apps.sales.utils.finalize_order')
    def test_order_mark_complete_trusted_finalize(self, mock_finalize):
        user = UserFactory.create(landscape_paid_through=timezone.now() + relativedelta(months=1), trust_level=VERIFIED)
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
        self.assertTrue(order.trust_finalized)
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

    @freeze_time('2012-08-01 12:00:00')
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

    @freeze_time('2012-08-01 12:00:00')
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

    @freeze_time('2012-08-01 12:00:00')
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

    @freeze_time('2012-08-01 12:00:00')
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
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_upload_outsider_fail(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(status=Order.IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_upload_staffer(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        order = OrderFactory.create(seller=user, status=Order.IN_PROGRESS, rating=ADULT)
        asset = AssetFactory.create(uploaded_by=staffer)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(response.data['owner'], staffer.username)
        self.assertEqual(response.data['rating'], ADULT)

    def test_revision_upload_final(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            seller=user, status=Order.IN_PROGRESS, revisions=1, revisions_hidden=True, rating=ADULT,
        )
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
                'rating': ADULT,
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.REVIEW)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/revisions/'.format(order.id),
            {
                'file': str(asset.id),
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

    def check_transactions(self, order, user, remote_id='36985214745', source=TransactionRecord.CARD):
        escrow = TransactionRecord.objects.get(
            remote_id=remote_id, source=source, destination=TransactionRecord.ESCROW,
        )
        self.assertEqual(escrow.target, order)
        self.assertEqual(escrow.amount, Money('10.29', 'USD'))
        self.assertEqual(escrow.payer, user)
        self.assertEqual(escrow.payee, order.seller)

        fee = TransactionRecord.objects.get(
            remote_id=remote_id, source=source, destination=TransactionRecord.RESERVE,
        )
        self.assertEqual(fee.status, TransactionRecord.SUCCESS)
        self.assertEqual(fee.target, order)
        self.assertEqual(fee.amount, Money('1.71', 'USD'))
        self.assertEqual(fee.payer, user)
        self.assertIsNone(fee.payee)

        unprocessed = TransactionRecord.objects.get(remote_id=remote_id, source=TransactionRecord.RESERVE, destination=TransactionRecord.UNPROCESSED_EARNINGS)
        self.assertEqual(unprocessed.status, TransactionRecord.SUCCESS)
        self.assertEqual(unprocessed.target, order)
        self.assertEqual(unprocessed.amount, Money('.98', 'USD'))
        self.assertIsNone(unprocessed.payer)
        self.assertIsNone(unprocessed.payee)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_saved_card(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = '36985214745'
        card = CreditCardTokenFactory.create(user=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': card.id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_charge_card.assert_called_with(
            payment_id=card.payment_id, profile_id=card.profile_id, amount=Decimal('12.00'), cvv='100',
        )

    @freeze_time('2018-08-01 12:00:00')
    @patch('apps.sales.views.card_token_from_transaction')
    @patch('apps.sales.views.charge_card')
    def test_pay_order_new_card(self, mock_charge_card, mock_create_token):
        user = UserFactory.create(authorize_token='6969')
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        mock_create_token.return_value = '5634'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'number': '4111111111111111',
                'zip': '64345',
                'first_name': 'Fox',
                'last_name': 'Piacenti',
                'country': 'US',
                'amount': '12.00',
                'cvv': '100',
                'exp_date': '08/25',
                'make_primary': True,
                'save_card': True,
                'card_id': None,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        card_info = CardInfo(number='4111111111111111', exp_month=8, exp_year=2025, cvv='100')
        address_info = AddressInfo(first_name='Fox', last_name='Piacenti', country='US', postal_code='64345')
        mock_charge_card.assert_called_with(
            card_info, address_info, Decimal('12.00'),
        )
        card = user.credit_cards.all()[0]
        self.assertTrue(card.active)
        self.assertEqual(card.profile_id, '6969')
        self.assertEqual(card.payment_id, '5634')

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_weights_set(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            product__task_weight=1, product__expected_turnaround=2,
            adjustment_task_weight=3, adjustment_expected_turnaround=4
        )
        add_adjustment(order, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=order.id)
        self.assertEqual(order.task_weight, 1)
        self.assertEqual(order.expected_turnaround, 2)
        self.assertEqual(order.adjustment_task_weight, 3)
        self.assertEqual(order.adjustment_expected_turnaround, 4)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_revisions_exist(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            revisions_hidden=True,
        )
        add_adjustment(order, Money('2.00', 'USD'))
        RevisionFactory.create(order=order)
        mock_charge_card.return_value = '36985214745'
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

    @patch('apps.sales.views.charge_saved_card')
    @freeze_time('2018-08-01 12:00:00')
    def test_pay_order_final_uploaded(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            revisions_hidden=True, final_uploaded=True,
        )
        add_adjustment(order, Money('2.00', 'USD'))
        RevisionFactory.create(order=order)
        mock_charge_card.return_value = '36985214745'
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
            '/api/sales/v1/order/{}/rate/seller/'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_seller(self):
        line_item = LineItemFactory.create(order__status=Order.COMPLETED)
        order = line_item.order
        self.login(order.seller)
        response = self.client.get(
            '/api/sales/v1/order/{}/rate/buyer/'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_staff_buyer_end(self):
        line_item = LineItemFactory.create(order__status=Order.COMPLETED)
        order = line_item.order
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get(
            '/api/sales/v1/order/{}/rate/buyer/'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_staff_seller_end(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get(
            '/api/sales/v1/order/{}/rate/seller/'.format(order.id),
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_outsider(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(UserFactory.create())
        response = self.client.get(
            '/api/sales/v1/order/{}/rate/seller/'.format(order.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_get_rating_not_logged_in(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        response = self.client.get(
            '/api/sales/v1/order/{}/rate/seller/'.format(order.id),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_credit_referrals(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        user.referred_by = UserFactory.create()
        user.save()
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            product__user__referred_by=UserFactory.create()
        )
        add_adjustment(order, Money('2.00', 'USD'))
        self.assertFalse(user.bought_shield_on)
        self.assertFalse(user.sold_shield_on)
        subscription = Subscription.objects.get(subscriber=order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(order, user)
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

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_no_escrow(self, _mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            escrow_disabled=True
        )
        add_adjustment(order, Money('2.00', 'USD'))
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_cvv_missing(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # noinspection PyTypeChecker
        self.assertRaises(TransactionRecord.DoesNotExist, TransactionRecord.objects.get, remote_id='36985214745')

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_cvv_already_verified(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user, cvv_verified=True).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(order, user)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_failed_transaction(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.side_effect = AuthorizeException("It failed!")
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '123'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        escrow = TransactionRecord.objects.get(
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            payer=user, payee=order.seller,
        )
        self.assertEqual(escrow.status, TransactionRecord.FAILURE)
        self.assertEqual(escrow.target, order)
        self.assertEqual(escrow.amount, Money('10.29', 'USD'))
        self.assertEqual(escrow.payer, user)
        self.assertEqual(escrow.response_message, "It failed!")
        self.assertEqual(escrow.payee, order.seller)
        fee = TransactionRecord.objects.get(
            source=TransactionRecord.CARD, destination=TransactionRecord.RESERVE,
        )
        self.assertEqual(fee.status, TransactionRecord.FAILURE)
        self.assertEqual(fee.target, order)
        self.assertEqual(fee.amount, Money('1.71', 'USD'))
        self.assertEqual(fee.payer, user)
        self.assertIsNone(fee.payee)


    @patch('apps.sales.views.charge_card')
    def test_pay_order_new_card_failed_transaction(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.side_effect = AuthorizeException("It failed!")
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'number': '4111111111111111',
                'zip': '64345',
                'first_name': 'Fox',
                'last_name': 'Piacenti',
                'country': 'US',
                'amount': '12.00',
                'cvv': '100',
                'exp_date': '08/25',
                'make_primary': True,
                'save_card': True,
                'card_id': None,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        escrow = TransactionRecord.objects.get(
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            payer=user, payee=order.seller,
        )
        self.assertEqual(escrow.status, TransactionRecord.FAILURE)
        self.assertEqual(escrow.target, order)
        self.assertEqual(escrow.amount, Money('10.29', 'USD'))
        self.assertEqual(escrow.payer, user)
        self.assertEqual(escrow.response_message, "It failed!")
        self.assertEqual(escrow.payee, order.seller)
        fee = TransactionRecord.objects.get(
            source=TransactionRecord.CARD, destination=TransactionRecord.RESERVE,
        )
        self.assertEqual(fee.status, TransactionRecord.FAILURE)
        self.assertEqual(fee.target, order)
        self.assertEqual(fee.amount, Money('1.71', 'USD'))
        self.assertEqual(fee.payer, user)
        self.assertIsNone(fee.payee)


    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_amount_changed(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '10.00',
                'cvv': '234'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_wrong_card(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create().id,
                'amount': '12.00',
                'cvv': '345'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_outsider(self, mock_charge_card):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '123'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_seller_fail(self, mock_charge_card):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            seller=user2,
        )
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '567'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_staffer(self, mock_charge_card):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        order = OrderFactory.create(
            status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': CreditCardTokenFactory.create(user=order.buyer).id,
                'amount': '12.00',
                'cvv': '467',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(order, order.buyer)

    def test_pay_order_staffer_cash(self):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        order = OrderFactory.create(
            status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(order, order.buyer, remote_id='', source=TransactionRecord.CASH_DEPOSIT)

    def test_pay_order_buyer_cash_fail(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pay_order_staffer_remote_id(self):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        order = OrderFactory.create(
            status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'remote_id': '36985214745',
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(order, order.buyer)

    def test_pay_order_buyer_remote_id_fail(self):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(order, Money('2.00', 'USD'))
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'remote_id': '36985214745',
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.sales.views.charge_saved_card')
    def test_pay_order_table_order(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        order = OrderFactory.create(
            buyer=user, status=Order.PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            table_order=True
        )
        add_adjustment(order, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = '36985214745'
        card = CreditCardTokenFactory.create(user=user)
        response = self.client.post(
            '/api/sales/v1/order/{}/pay/'.format(order.id),
            {
                'card_id': card.id,
                'amount': '17.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_charge_card.assert_called_with(
            payment_id=card.payment_id, profile_id=card.profile_id, amount=Decimal('17.00'), cvv='100',
        )

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
                'characters': characters,
                'email': 'stuff@example.com',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.characters.all().count(), 0)
        self.assertEqual(order.buyer.guest_email, 'stuff@example.com')

    def test_place_order_guest_user(self):
        user = create_guest_user('stuff@example.com')
        user.set_password('Test')
        user.save()
        product = ProductFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'email': 'stuff@example.com',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.characters.all().count(), 0)
        self.assertEqual(order.buyer, user)

    def test_place_order_guest_user_new_email(self):
        user = create_guest_user('stuff@example.com')
        user.set_password('Test')
        user.save()
        product = ProductFactory.create()
        self.login(user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'email': 'stuff2@example.com',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.characters.all().count(), 0)
        self.assertEqual(order.buyer.guest_email, 'stuff2@example.com')
        user.refresh_from_db()
        self.assertNotEqual(order.buyer, user)


@patch('apps.sales.views.notify')
class TestOrderStateChange(SignalsDisabledMixin, APITestCase):
    fixture_list = ['order-state-change']

    def setUp(self):
        super().setUp()
        if self.rebuild_fixtures:
            self.outsider = UserFactory.create(username='Outsider', email='outsider@example.com')
            self.seller = UserFactory.create(username='Seller', email='seller@example.com')
            self.buyer = UserFactory.create(username='Buyer', email='buyer@example.com')
            self.staffer = UserFactory.create(is_staff=True, username='Staffer', email='staff@example.com')
            characters = [
                CharacterFactory.create(
                    user=self.buyer, name='Pictured', primary_submission=SubmissionFactory.create()
                ),
                CharacterFactory.create(user=self.buyer, private=True, name='Unpictured1', primary_submission=None),
                CharacterFactory.create(
                    user=UserFactory.create(), open_requests=True, name='Unpictured2', primary_submission=None
                )
            ]
            self.order = OrderFactory.create(
                seller=self.seller, buyer=self.buyer, product__base_price=Money('5.00', 'USD'),
                adjustment_task_weight=1, adjustment_expected_turnaround=2, product__task_weight=3,
                product__expected_turnaround=4
            )
            self.order.characters.add(*characters)
            self.final = RevisionFactory.create(order=self.order, rating=ADULT, owner=self.seller)
            self.save_fixture('order-state-change')

        self.final = Revision.objects.all()[0]
        self.order = self.final.order
        self.url = '/api/sales/v1/order/{}/'.format(self.order.id)
        self.outsider, self.seller, self.buyer, self.staffer = User.objects.order_by('id')[:4]

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

    def test_accept_order(self, _mock_notify):
        self.state_assertion('seller', 'accept/')

    def test_accept_order_buyer_fail(self, _mock_notify):
        self.state_assertion('buyer', 'accept/', status.HTTP_403_FORBIDDEN)

    def test_accept_order_outsider(self, _mock_notify):
        self.state_assertion('outsider', 'accept/', status.HTTP_403_FORBIDDEN)

    def test_accept_order_staffer(self, _mock_notify):
        self.state_assertion('staffer', 'accept/')

    def test_accept_order_free(self, _mock_notify):
        item = LineItemFactory.create(order=self.order, amount=-self.order.product.base_price)
        idempotent_lines(self.order)
        self.state_assertion('seller', 'accept/')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.QUEUED)
        self.assertFalse(self.order.revisions_hidden)
        self.assertTrue(self.order.escrow_disabled)

    def test_in_progress(self, _mock_notify):
        self.order.stream_link = 'https://google.com/'
        self.state_assertion('seller', 'start/', initial_status=Order.QUEUED)

    def test_cancel_order(self, _mock_notify):
        self.state_assertion('seller', 'cancel/', initial_status=Order.NEW)

    def test_cancel_order_buyer(self, _mock_notify):
        self.state_assertion('buyer', 'cancel/', initial_status=Order.PAYMENT_PENDING)

    def test_cancel_order_outsider_fail(self, _mock_notify):
        self.state_assertion('outsider', 'cancel/', status.HTTP_403_FORBIDDEN, initial_status=Order.PAYMENT_PENDING)

    def test_cancel_order_staffer(self, _mock_notify):
        self.state_assertion('staffer', 'cancel/', initial_status=Order.PAYMENT_PENDING)

    def test_mark_paid_order_buyer_fail(self, _mock_notify):
        self.order.escrow_disabled = True
        self.order.save()
        self.state_assertion('buyer', 'mark-paid/', status.HTTP_403_FORBIDDEN, initial_status=Order.PAYMENT_PENDING)

    def test_mark_paid_order_seller(self, _mock_notify):
        self.order.escrow_disabled = True
        self.assertTrue(self.order.revisions_hidden)
        self.order.save()
        self.final.delete()
        self.state_assertion('seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING, target_status=Order.QUEUED)
        self.order.refresh_from_db()
        self.assertFalse(self.order.revisions_hidden)

    def test_mark_paid_disables_escrow(self, _mock_notify):
        self.assertFalse(self.order.escrow_disabled)
        self.assertTrue(self.order.revisions_hidden)
        self.order.save()
        self.final.delete()
        self.state_assertion('seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING, target_status=Order.QUEUED)
        self.order.refresh_from_db()
        self.assertFalse(self.order.revisions_hidden)
        self.assertTrue(self.order.escrow_disabled)

    def test_mark_paid_order_final_uploaded(self, _mock_notify):
        self.order.escrow_disabled = True
        self.order.final_uploaded = True
        self.order.save()
        self.state_assertion(
            'seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING, target_status=Order.COMPLETED
        )

    def test_mark_paid_revisions_exist(self, _mock_notify):
        self.order.escrow_disabled = True
        self.order.save()
        RevisionFactory.create(order=self.order)
        self.state_assertion(
            'seller', 'mark-paid/', initial_status=Order.PAYMENT_PENDING, target_status=Order.IN_PROGRESS
        )

    def test_mark_paid_task_weights(self, _mock_notify):
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

    def test_mark_paid_order_staffer(self, _mock_notify):
        self.order.escrow_disabled = True
        self.order.save()
        self.state_assertion('staffer', 'mark-paid/', initial_status=Order.PAYMENT_PENDING)

    @override_settings(SERVICE_PERCENTAGE_FEE=Decimal('10'), SERVICE_STATIC_FEE=Decimal('1.00'))
    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.tasks.withdraw_all.delay')
    def test_approve_order_buyer(self, mock_withdraw, mock_bonus_amount, _mock_notify):
        record = TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            amount=Money('15.00', 'USD'),
        )
        mock_bonus_amount.return_value = Money('5.00', 'USD')
        self.state_assertion('buyer', 'approve/', initial_status=Order.REVIEW)
        record.refresh_from_db()
        records = TransactionRecord.objects.all()
        self.assertEqual(records.count(), 3)
        payment = records.get(payee=self.order.seller, source=TransactionRecord.ESCROW)
        self.assertEqual(payment.amount, Money('15.00', 'USD'))
        self.assertEqual(payment.payer, self.order.seller)
        self.assertEqual(payment.status, TransactionRecord.SUCCESS)
        self.assertEqual(payment.destination, TransactionRecord.HOLDINGS)
        bonus = records.get(
            payee__isnull=True, payer__isnull=True, source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
        )
        self.assertEqual(bonus.amount, Money('5.00', 'USD'))
        self.assertEqual(bonus.category, TransactionRecord.SHIELD_FEE)
        mock_withdraw.assert_called_with(self.order.seller.id)

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.recall_notification')
    def test_approve_order_recall_notification(self, mock_recall, mock_bonus_amount, _mock_notify):
        target_time = timezone.now()
        self.order.disputed_on = target_time
        self.order.save()
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            destination=TransactionRecord.ESCROW,
            source=TransactionRecord.CARD,
            category=TransactionRecord.ESCROW_HOLD,
            amount=Money('15.00', 'USD'),
        )
        self.state_assertion('buyer', 'approve/', initial_status=Order.DISPUTED)
        mock_recall.assert_has_calls([call(DISPUTE, self.order)])
        self.order.refresh_from_db()
        self.assertEqual(self.order.disputed_on, None)

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.recall_notification')
    def test_approve_order_staffer_no_recall_notification(self, mock_recall, mock_bonus_amount, _mock_notify):
        TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            destination=TransactionRecord.ESCROW,
            source=TransactionRecord.CARD,
            category=TransactionRecord.ESCROW_HOLD,
            amount=Money('15.00', 'USD'),
        )
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        target_time = timezone.now()
        self.order.disputed_on = target_time
        self.order.save()
        self.state_assertion('staffer', 'approve/', initial_status=Order.DISPUTED)
        for mock_call in mock_recall.call_args_list:
            self.assertNotEqual(mock_call[0], DISPUTE)
        self.order.refresh_from_db()
        self.assertEqual(self.order.disputed_on, target_time)

    @override_settings(
        TABLE_PERCENTAGE_FEE=Decimal('15'), TABLE_STATIC_FEE=Decimal('2.00'),
    )
    @patch('apps.sales.tasks.withdraw_all.delay')
    def test_approve_table_order(self, mock_withdraw, _mock_notify):
        self.order.product.base_price = Money('15.00', 'USD')
        self.order.product.save()
        self.order.table_order = True
        self.order.status = Order.NEW
        self.order.save()
        idempotent_lines(self.order)
        record = TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            amount=Money('15.00', 'USD'),
        )
        TransactionRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.RESERVE,
            amount=Money('2.00', 'USD'),
        )
        TransactionRecordFactory.create(
            target=self.order,
            payee=None,
            payer=self.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.MONEY_HOLE_STAGE,
            amount=Money('3.00', 'USD'),
        )
        self.state_assertion('buyer', 'approve/', initial_status=Order.REVIEW)
        record.refresh_from_db()
        records = TransactionRecord.objects.all()
        self.assertEqual(records.count(), 6)
        payment = records.get(payee=self.order.seller, source=TransactionRecord.ESCROW)
        self.assertEqual(payment.amount, Money('15.00', 'USD'))
        self.assertEqual(payment.payer, self.order.seller)
        self.assertEqual(payment.status, TransactionRecord.SUCCESS)
        self.assertEqual(payment.destination, TransactionRecord.HOLDINGS)
        service_fee = records.get(
            payee__isnull=True, payer__isnull=True, source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
        )
        self.assertEqual(service_fee.amount, Money('2.00', 'USD'))
        self.assertEqual(service_fee.category, TransactionRecord.TABLE_SERVICE)
        mock_withdraw.assert_called_with(self.order.seller.id)

    @patch('apps.sales.utils.refund_transaction')
    def test_refund_escrow_disabled(self, mock_refund_transaction, _mock_notify):
        self.order.escrow_disabled = True
        self.order.save()
        self.state_assertion('seller', 'refund/', initial_status=Order.DISPUTED)
        mock_refund_transaction.assert_not_called()

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.refund_transaction')
    @override_settings(
        PREMIUM_PERCENTAGE_FEE=Decimal('5'), PREMIUM_STATIC_FEE=Decimal('0.10')
    )
    def test_refund_card_seller(self, mock_refund_transaction, mock_bonus_amount, _mock_notify):
        card = CreditCardTokenFactory.create()
        TransactionRecordFactory.create(
            card=card,
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            amount=Money('15.00', 'USD'),
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            remote_id='1234',
        )
        mock_refund_transaction.return_value = '123'
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        self.state_assertion('seller', 'refund/', initial_status=Order.DISPUTED)
        refund_transaction = TransactionRecord.objects.get(
            status=TransactionRecord.SUCCESS,
            payee=self.order.buyer, payer=self.order.seller,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.CARD,
        )
        self.assertEqual(refund_transaction.amount, Money('15.00', 'USD'))
        self.assertEqual(refund_transaction.category, TransactionRecord.ESCROW_REFUND)
        self.assertEqual(refund_transaction.remote_id, '123')
        TransactionRecord.objects.get(
            payer=None, payee=None, source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
            amount=Money('2.50', 'USD')
        )

    @patch('apps.sales.utils.refund_transaction')
    def test_refund_card_seller_error(self, mock_refund_transaction, _mock_notify):
        card = CreditCardTokenFactory.create()
        TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            card=card,
        )
        mock_refund_transaction.side_effect = AuthorizeException(
            "It failed"
        )
        self.state_assertion('seller', 'refund/', status.HTTP_400_BAD_REQUEST, initial_status=Order.DISPUTED)
        TransactionRecord.objects.get(
            response_message="It failed", status=TransactionRecord.FAILURE,
            payee=self.order.buyer, payer=self.order.seller,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.CARD,
            category=TransactionRecord.ESCROW_REFUND,
        )

    @patch('apps.sales.utils.refund_transaction')
    def test_refund_cash_only(self, mock_refund_transaction, _mock_notify):
        TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            source=TransactionRecord.CASH_DEPOSIT,
            destination=TransactionRecord.ESCROW,
        )
        mock_refund_transaction.side_effect = AuthorizeException(
            "It failed"
        )
        self.state_assertion('seller', 'refund/', status.HTTP_200_OK, initial_status=Order.IN_PROGRESS)
        mock_refund_transaction.assert_not_called()
        TransactionRecord.objects.get(
            response_message="", status=TransactionRecord.SUCCESS,
            payee=self.order.buyer, payer=self.order.seller,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.CASH_DEPOSIT,
            category=TransactionRecord.ESCROW_REFUND,
        )

    def test_refund_card_buyer(self, _mock_notify):
        self.state_assertion('buyer', 'refund/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)

    def test_refund_card_outsider(self, _mock_notify):
        self.state_assertion('outsider', 'refund/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.refund_transaction')
    def test_refund_card_staffer(self, mock_refund_transaction, mock_bonus_amount, _mock_notify):
        card = CreditCardTokenFactory.create()
        record = TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            card=card,
        )
        mock_refund_transaction.return_value = '123'
        mock_bonus_amount.return_value = Money('2.50')
        self.state_assertion('staffer', 'refund/', initial_status=Order.DISPUTED)
        record.refresh_from_db()
        TransactionRecord.objects.get(
            payer=None, payee=None, source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
            amount=Money('2.50')
        )


    def test_approve_order_seller_fail(self, _mock_notify):
        self.state_assertion('seller', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    def test_approve_order_outsider_fail(self, _mock_notify):
        self.state_assertion('outsider', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    def test_approve_order_seller(self, _mock_notify):
        self.state_assertion('seller', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    @patch('apps.sales.utils.get_bonus_amount')
    def test_approve_order_staffer(self, mock_bonus_amount, _mock_notify):
        record = TransactionRecordFactory.create(
            target=self.order,
            payee=self.order.seller,
            payer=self.order.buyer,
            amount=Money('15.00', 'USD'),
        )
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        self.state_assertion('staffer', 'approve/', initial_status=Order.REVIEW)
        record.refresh_from_db()


    def test_claim_order_staffer(self, _mock_notify):
        self.state_assertion('staffer', 'claim/', initial_status=Order.DISPUTED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.arbitrator, self.staffer)
        self.assertEqual(Subscription.objects.filter(
            subscriber=self.staffer, object_id=self.order.id, content_type=ContentType.objects.get_for_model(Order),
            type__in=[COMMENT, REVISION_UPLOADED], email=True,
        ).count(), 2)

    def test_claim_order_staffer_claimed_already(self, _mock_notify):
        arbitrator = UserFactory.create(is_staff=True)
        self.order.arbitrator = arbitrator
        self.order.save()
        self.state_assertion('staffer', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.arbitrator, arbitrator)

    def test_claim_order_buyer(self, _mock_notify):
        self.state_assertion('buyer', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)

    def test_claim_order_seller(self, _mock_notify):
        self.state_assertion('seller', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=Order.DISPUTED)

    @freeze_time('2019-02-01 12:00:00')
    def test_file_dispute_buyer_enough_time(self, _mock_notify):
        self.order.dispute_available_on = date(year=2019, month=1, day=1)
        self.order.save()
        self.state_assertion('buyer', 'dispute/', status.HTTP_200_OK, initial_status=Order.IN_PROGRESS)

    @freeze_time('2019-01-01 12:00:00')
    def test_file_dispute_buyer_too_early(self, _mock_notify):
        self.order.dispute_available_on = date(year=2019, month=5, day=3)
        self.order.save()
        self.state_assertion('buyer', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=Order.IN_PROGRESS)

    def test_file_dispute_seller(self, _mock_notify):
        self.state_assertion('seller', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)

    def test_file_dispute_outsider_fail(self, _mock_notify):
        self.state_assertion('outsider', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=Order.REVIEW)


class TestComment(APITestCase):
    def test_make_comment(self):
        order = OrderFactory.create()
        self.login(order.buyer)
        response = self.client.post(
            '/api/lib/v1/comments/sales.Order/{}/'.format(order.id),
            {'text': 'test comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = response.data
        self.assertEqual(comment['text'], 'test comment')
        self.assertEqual(comment['user']['username'], order.buyer.username)
        Comment.objects.get(id=comment['id'])


history_passes = {**MethodAccessMixin.passes, 'get': ['user', 'staff']}


class TestAccountHistoryPermissions(PermissionsTestCase, MethodAccessMixin):
    passes = history_passes
    view_class = AccountHistory


class TestHistoryViews(SignalsDisabledMixin, APITestCase):
    def setUp(self):
        super().setUp()
        if self.rebuild_fixtures:
            self.provision_users()
            self.save_fixture('history-views')
        else:
            self.load_fixture('history-views')
        self.user = User.objects.get(username='Fox')
        self.user2 = User.objects.get(username='Amber')

    @staticmethod
    def provision_users():
        user = UserFactory.create(username='Fox')
        user2 = UserFactory.create(username='Amber')
        card = CreditCardTokenFactory.create()
        [
            TransactionRecordFactory.create(
                amount=Money(amount, 'USD'),
                category=TransactionRecord.ESCROW_HOLD,
                payer=user2,
                payee=user,
                source=TransactionRecord.CARD,
                destination=TransactionRecord.ESCROW,
                card=card,
            )
            for amount in ('5.00', '10.00', '15.00')
        ]
        [
            TransactionRecordFactory.create(
                amount=Money(amount, 'USD'),
                payer=user,
                payee=user,
                source=TransactionRecord.ESCROW,
                destination=TransactionRecord.HOLDINGS,
                category=TransactionRecord.ESCROW_RELEASE,
            )
            for amount in ('5.00', '10.00')
        ]
        [
            TransactionRecordFactory.create(
                amount=Money(amount, 'USD'),
                payer=user,
                payee=user,
                card=None,
                source=TransactionRecord.HOLDINGS,
                destination=TransactionRecord.BANK,
                category=TransactionRecord.CASH_WITHDRAW,
            )
            for amount in (1, 2, 3, 4)
        ]

    def test_purchase_history(self):
        self.login(self.user)
        response = self.client.get(f'/api/sales/v1/account/{self.user.username}/transactions/?account=300')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        self.login(self.user2)
        response = self.client.get(f'/api/sales/v1/account/{self.user2.username}/transactions/?account=300')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        for result in response.data['results']:
            self.assertTrue(result['card']['id'])

    def test_escrow_history(self):
        self.login(self.user)
        response = self.client.get(f'/api/sales/v1/account/{self.user.username}/transactions/?account=302')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        for result in response.data['results']:
            self.assertIsNone(result['card'])
        self.login(self.user2)
        response = self.client.get(f'/api/sales/v1/account/{self.user2.username}/transactions/?account=302')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_available_history(self):
        self.login(self.user)
        response = self.client.get(f'/api/sales/v1/account/{self.user.username}/transactions/?account=303')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 6)
        self.login(self.user2)
        response = self.client.get(f'/api/sales/v1/account/{self.user2.username}/transactions/?account=303')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)


class TestBankAccounts(APITestCase):
    def test_bank_listing(self):
        user = UserFactory.create()
        accounts = [BankAccountFactory.create(user=user) for _ in range(3)]
        BankAccountFactory.create(user=user, deleted=True)
        [BankAccountFactory.create() for _ in range(3)]
        self.login(user)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(accounts))

    @patch('apps.sales.views.make_dwolla_account')
    @patch('apps.sales.views.add_bank_account')
    @patch('apps.sales.views.account_balance')
    def test_bank_addition(self, mock_account_balance, mock_add_bank_account, _mock_make_dwolla_account):
        user = UserFactory.create()
        self.login(user)
        mock_add_bank_account.return_value = BankAccountFactory.create(user=user)
        mock_account_balance.return_value = Decimal('3.00')
        response = self.client.post(
            f'/api/sales/v1/account/{user.username}/banks/',
            {
                'type': BankAccount.CHECKING, 'account_number': '123434', 'routing_number': '123455666',
                'first_name': 'Jim', 'last_name': 'Bob',
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_account_balance.assert_called_with(user, TransactionRecord.HOLDINGS)
        mock_add_bank_account.assert_called_with(user, '123434', '123455666', BankAccount.CHECKING)

    @patch('apps.sales.views.make_dwolla_account')
    @patch('apps.sales.views.add_bank_account')
    def test_bank_addition_insufficient_funds(self, mock_add_bank_account, _mock_make_dwolla_account):
        user = UserFactory.create()
        self.login(user)
        mock_add_bank_account.return_value = BankAccountFactory.create(user=user)
        response = self.client.post(
            f'/api/sales/v1/account/{user.username}/banks/',
            {
                'type': BankAccount.CHECKING, 'account_number': '123434', 'routing_number': '123455666',
                'first_name': 'Jim', 'last_name': 'Bob',
            }, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'], 'You do not have sufficient balance to cover the $1.00 connection fee yet.',
        )

    def test_bank_listing_staff(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        response = self.client.get('/api/sales/v1/account/{}/banks/'.format(user.username))
        self.assertEqual(response.status_code, 403)

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
        self.assertEqual(response.status_code, 403)

    def test_bank_account_destroy_not_logged_in(self):
        response = self.client.delete('/api/sales/v1/account/{}/banks/{}/'.format(self.user.username, self.account.id))
        self.assertEqual(response.status_code, 403)


def mock_balance(obj, account_type, status_filter=None):
    if status_filter == PENDING:
        return Decimal('10.00')
    if account_type == TransactionRecord.HOLDINGS:
        return Decimal('100.00')
    return Decimal('50.00')


class TestAccountBalance(APITestCase):
    @patch('apps.sales.serializers.account_balance')
    def test_account_balance(self, mock_account_balance):
        user = UserFactory.create()
        self.login(user)
        mock_account_balance.side_effect = mock_balance
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], '100.00')
        self.assertEqual(response.data['escrow'], '50.00')

    @patch('apps.sales.serializers.account_balance')
    def test_account_balance_staff(self, mock_account_balance):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        mock_account_balance.side_effect = mock_balance
        response = self.client.get('/api/sales/v1/account/{}/balance/'.format(user.username))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available'], '100.00')
        self.assertEqual(response.data['escrow'], '50.00')
        self.assertEqual(response.data['pending'], '10.00')

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
            OrderFactory.create(product=maxed, status=Order.IN_PROGRESS)
            OrderFactory.create(product=maxed, status=Order.QUEUED)
            maxed.refresh_from_db()
            overloaded = ProductFactory.create(name='Test6 overloaded', task_weight=1, user__artist_profile__max_load=5)
            OrderFactory.create(seller=overloaded.user, task_weight=7, status=Order.IN_PROGRESS)
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
            OrderFactory.create(product=product4)
            OrderFactory.create(product=product4)
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
            OrderFactory.create(product=overloaded, status=Order.IN_PROGRESS)
            OrderFactory.create(product=overloaded, status=Order.QUEUED)

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


class TestLoadAdjustment(TestCase):
    def test_load_changes(self):
        user = UserFactory.create()
        user.artist_profile.max_load = 10
        user.artist_profile.save()
        OrderFactory.create(task_weight=5, status=Order.QUEUED, product__user=user)
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order = OrderFactory.create(task_weight=5, status=Order.NEW, product__user=user)
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order.status = Order.QUEUED
        order.save()
        user.refresh_from_db()
        # Max load reached.
        self.assertEqual(user.artist_profile.load, 10)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order2 = OrderFactory.create(task_weight=5, status=Order.NEW, product__user=user, seller=user)
        user.refresh_from_db()
        # Now we have an order in a new state. This shouldn't undo the disability.
        self.assertEqual(user.artist_profile.load, 10)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order.status = Order.COMPLETED
        order.save()
        user.refresh_from_db()
        # We have reduced the load, but never took care of the new order, so commissions are still disabled.
        self.assertEqual(user.artist_profile.load, 5)
        self.assertTrue(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        order2.status = Order.CANCELLED
        order2.save()
        order.save()
        # Cancalled the new order, so now the load is within parameters and there are no outstanding new orders.
        user.refresh_from_db()
        self.assertEqual(user.artist_profile.load, 5)
        self.assertFalse(user.artist_profile.commissions_disabled)
        self.assertFalse(user.artist_profile.commissions_closed)
        # Closing commissions should disable them as well.
        user.artist_profile.commissions_closed = True
        user.save()
        self.assertTrue(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        user.artist_profile.commissions_closed = False
        order.status = Order.NEW
        order.save()
        # Unclosing commissions shouldn't enable commissions if they still have an outstanding order.
        user.refresh_from_db()
        user.artist_profile.commissions_closed = False
        user.save()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        order.status = Order.CANCELLED
        order.save()
        # We should be clear again.
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertFalse(user.artist_profile.commissions_disabled)
        Product.objects.all().delete()
        # Make a product too big for the user to complete. Should close the user.
        product = ProductFactory.create(user=user, task_weight=20)
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertTrue(user.artist_profile.commissions_disabled)
        # And dropping it should open them back up.
        product.task_weight = 1
        product.save()
        user.refresh_from_db()
        self.assertFalse(user.artist_profile.commissions_closed)
        self.assertFalse(user.artist_profile.commissions_disabled)


class TestPremium(APITestCase):
    @override_settings(PORTRAIT_PRICE=Decimal('2.00'))
    @freeze_time('2017-11-10 12:00:00')
    @patch('apps.sales.views.charge_saved_card')
    def test_portrait(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        card = CreditCardTokenFactory.create(user=user, cvv_verified=True)
        mock_charge_card.return_value = '36985214745'
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
        mock_charge_card.return_value = '36985214745'
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
        mock_charge_card.return_value = '36985214745'
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
        mock_charge_card.return_value = '36985214745'
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
            'expected_turnaround': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertEqual(response.data['buyer']['id'], user2.id)
        self.assertEqual(response.data['status'], Order.PAYMENT_PENDING)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(response.data['private'], False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['revisions_hidden'])
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['base_price'], 3.00)
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], 2.00)
        self.assertEqual(response.data['product']['revisions'], 1)

        order = Order.objects.get(id=response.data['id'])
        item = order.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money('2.00', 'USD'))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        item = order.line_items.get(type=BASE_PRICE)
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
            'expected_turnaround': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertEqual(response.data['buyer']['id'], user2.id)
        self.assertEqual(response.data['status'], Order.PAYMENT_PENDING)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(response.data['private'], False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['revisions_hidden'])
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['base_price'], 3.00)
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], 2.00)
        self.assertEqual(response.data['product']['revisions'], 1)

        order = Order.objects.get(id=response.data['id'])
        # Actual price will be $8-- $3 plus the $5 static fee. Setting the order price to $15 will make a $7 adjustment.
        item = order.line_items.get(type=ADD_ON)
        self.assertEqual(item.amount, Money('7.00', 'USD'))
        self.assertEqual(item.priority, 100)
        self.assertEqual(item.destination_user, order.seller)
        self.assertEqual(item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(item.percentage, 0)
        item = order.line_items.get(type=BASE_PRICE)
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
            'expected_turnaround': 4
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertIsNone(response.data['buyer'])
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], 2.00)

        order = Order.objects.get(id=response.data['id'])
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
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertIsNone(response.data['buyer'])
        self.assertEqual(response.data['adjustment_task_weight'], -5)
        self.assertEqual(response.data['adjustment_expected_turnaround'], -2)
        self.assertEqual(response.data['adjustment_revisions'], -1)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], 2.00)

        order = Order.objects.get(id=response.data['id'])
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertIsNone(response.data['buyer'])
        self.assertEqual(response.data['adjustment_task_weight'], 0)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 0)
        self.assertEqual(response.data['adjustment_revisions'], 0)
        self.assertEqual(response.data['task_weight'], 2)
        self.assertEqual(response.data['revisions'], 3)
        self.assertEqual(response.data['details'], 'oh')
        self.assertEqual(response.data['expected_turnaround'], 4)
        self.assertFalse(response.data['escrow_disabled'])
        self.assertIsNone(response.data['product'])

        order = Order.objects.get(id=response.data['id'])
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
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertEqual(response.data['buyer']['id'], user2.id)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['details'], 'bla bla')
        self.assertTrue(response.data['private'])
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['base_price'], 3.00)
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], 2.00)

        order = Order.objects.get(id=response.data['id'])
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
            'expected_turnaround': 4
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertEqual(response.data['buyer']['id'], user2.id)
        self.assertEqual(response.data['status'], Order.QUEUED)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(response.data['private'], False)
        self.assertEqual(response.data['adjustment_task_weight'], -2)
        self.assertEqual(response.data['adjustment_expected_turnaround'], 2.00)
        self.assertEqual(response.data['adjustment_revisions'], 2)
        self.assertFalse(response.data['revisions_hidden'])
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['base_price'], 3.00)
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], 2.00)
        self.assertEqual(response.data['product']['revisions'], 1)

        order = Order.objects.get(id=response.data['id'])
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
        self.assertEqual(response.data['seller']['id'], user.id)
        self.assertEqual(response.data['buyer']['id'], user2.id)
        self.assertEqual(response.data['status'], Order.IN_PROGRESS)
        self.assertEqual(response.data['details'], 'wat')
        self.assertEqual(response.data['private'], False)
        self.assertEqual(response.data['adjustment_task_weight'], -5)
        self.assertEqual(response.data['adjustment_expected_turnaround'], -2)
        self.assertEqual(response.data['adjustment_revisions'], -1)
        self.assertFalse(response.data['revisions_hidden'])
        self.assertTrue(response.data['escrow_disabled'])
        self.assertEqual(response.data['product']['id'], product.id)
        self.assertEqual(response.data['product']['task_weight'], 5)
        self.assertEqual(response.data['product']['expected_turnaround'], 2.00)
        self.assertEqual(response.data['product']['revisions'], 1)

        order = Order.objects.get(id=response.data['id'])
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
                'claim_token': slugify(order.claim_token),
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
                'claim_token': slugify(order.claim_token),
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
                'claim_token': slugify(order.claim_token),
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
                'claim_token': slugify(order.claim_token),
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
                'claim_token': slugify(order.claim_token),
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
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(order.buyer)
        submission = SubmissionFactory.create(order=order)
        response = self.client.get(f'/api/sales/v1/order/{order.id}/outputs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIDInList(submission, response.data)

    def test_order_outputs_post(self):
        order = OrderFactory.create(status=Order.COMPLETED, final_uploaded=True)
        RevisionFactory.create(order=order)
        self.login(order.buyer)
        response = self.client.post(f'/api/sales/v1/order/{order.id}/outputs/', {
            'caption': 'Stuff',
            'tags': ['Things', 'wat'],
            'title': 'Hi!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.outputs.all().count(), 1)
        output = order.outputs.all()[0]
        self.assertEqual(output.order, order)

    def test_order_output_exists(self):
        order = OrderFactory.create(status=Order.COMPLETED)
        self.login(order.buyer)
        order.outputs.add(SubmissionFactory.create(order=order, owner=order.buyer))
        response = self.client.post(f'/api/sales/v1/order/{order.id}/outputs/', {
            'caption': 'Stuff',
            'tags': ['Things', 'wat'],
            'title': 'Hi!'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(order.outputs.all().count(), 1)


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
            buyer__guest=True, buyer__guest_email='test@wat.com', customer_email='test@example.com',
        )
        self.login(order.seller)
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
