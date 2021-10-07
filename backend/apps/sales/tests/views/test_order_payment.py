from datetime import date
from decimal import Decimal
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from ddt import ddt
from django.test import override_settings
from django.utils import timezone
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status

from apps.lib.models import Subscription, SALE_UPDATE, Notification, REFERRAL_PORTRAIT_CREDIT, REFERRAL_LANDSCAPE_CREDIT
from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import UserFactory
from apps.sales.authorize import CardInfo, AddressInfo, AuthorizeException
from apps.sales.models import PAYMENT_PENDING, REVIEW, IN_PROGRESS, TransactionRecord
from apps.sales.tests.factories import DeliverableFactory, add_adjustment, CreditCardTokenFactory, RevisionFactory
from apps.sales.tests.test_utils import TransactionCheckMixin


@override_settings(
    SERVICE_STATIC_FEE=Decimal('0.50'), SERVICE_PERCENTAGE_FEE=Decimal('4'),
    PREMIUM_STATIC_BONUS=Decimal('0.25'), PREMIUM_PERCENTAGE_BONUS=Decimal('4'),
)
@ddt
class TestOrderPayment(TransactionCheckMixin, APITestCase):
    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_saved_card(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=deliverable.order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        card = CreditCardTokenFactory.create(user=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
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

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_landscape(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            order__seller__landscape_paid_through=(timezone.now() + relativedelta(days=5)).date(),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=deliverable.order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        card = CreditCardTokenFactory.create(user=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': card.id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(deliverable, user, landscape=True)

    @freeze_time('2018-08-01 12:00:00')
    @patch('apps.sales.utils.card_token_from_transaction')
    @patch('apps.sales.utils.charge_card')
    def test_pay_order_new_card(self, mock_charge_card, mock_create_token):
        user = UserFactory.create(authorize_token='6969')
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        mock_create_token.return_value = '5634'
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
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

    @freeze_time('2018-08-01 12:00:00')
    @patch('apps.sales.utils.card_token_from_transaction')
    @patch('apps.sales.utils.charge_card')
    def test_pay_order_new_card_four_digit_year(self, mock_charge_card, mock_create_token):
        user = UserFactory.create(authorize_token='6969')
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        mock_create_token.return_value = '5634'
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'number': '4111111111111111',
                'zip': '64345',
                'first_name': 'Fox',
                'last_name': 'Piacenti',
                'country': 'US',
                'amount': '12.00',
                'cvv': '100',
                'exp_date': '08/2025',
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

    @freeze_time('2020-08-02')
    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_weights_set(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            product__task_weight=1, product__expected_turnaround=1,
            adjustment_task_weight=3, adjustment_expected_turnaround=2
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=deliverable.order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.task_weight, 1)
        self.assertEqual(deliverable.expected_turnaround, 1)
        self.assertEqual(deliverable.adjustment_task_weight, 3)
        self.assertEqual(deliverable.adjustment_expected_turnaround, 2)
        self.assertEqual(deliverable.dispute_available_on, date(year=2020, month=8, day=6))

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_revisions_exist(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            revisions_hidden=True,
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        RevisionFactory.create(deliverable=deliverable)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        self.assertFalse(deliverable.revisions_hidden)
        self.assertFalse(deliverable.final_uploaded)

    @patch('apps.sales.utils.charge_saved_card')
    @freeze_time('2018-08-01 12:00:00')
    def test_pay_order_final_uploaded(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            revisions_hidden=True, final_uploaded=True,
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        RevisionFactory.create(deliverable=deliverable)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, REVIEW)
        self.assertFalse(deliverable.revisions_hidden)
        self.assertTrue(deliverable.final_uploaded)
        self.assertEqual(deliverable.auto_finalize_on, date(2018, 8, 3))


    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_credit_referrals(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        user.referred_by = UserFactory.create()
        user.save()
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            order__seller__referred_by=UserFactory.create()
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        self.assertFalse(user.bought_shield_on)
        self.assertFalse(user.sold_shield_on)
        subscription = Subscription.objects.get(subscriber=deliverable.order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(deliverable, user)
        deliverable.order.seller.refresh_from_db()
        deliverable.order.buyer.refresh_from_db()
        portrait_notification = Notification.objects.filter(event__type=REFERRAL_PORTRAIT_CREDIT)
        landscape_notification = Notification.objects.filter(event__type=REFERRAL_LANDSCAPE_CREDIT)
        self.assertEqual(portrait_notification.count(), 1)
        self.assertEqual(landscape_notification.count(), 1)
        portrait_notification = portrait_notification.first()
        landscape_notification = landscape_notification.first()
        self.assertEqual(portrait_notification.user, deliverable.order.buyer.referred_by)
        self.assertEqual(portrait_notification.event.target, deliverable.order.buyer.referred_by)
        self.assertEqual(landscape_notification.user, deliverable.order.seller.referred_by)
        self.assertEqual(landscape_notification.event.target, deliverable.order.seller.referred_by)
        self.assertTrue(deliverable.order.seller.sold_shield_on)
        self.assertTrue(deliverable.order.buyer.bought_shield_on)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_no_escrow(self, _mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            escrow_disabled=True
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_cvv_missing(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # noinspection PyTypeChecker
        self.assertRaises(TransactionRecord.DoesNotExist, TransactionRecord.objects.get, remote_id='36985214745')

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_cvv_already_verified(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user, cvv_verified=True).id,
                'amount': '12.00',
                'cvv': '100'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(deliverable, user)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_failed_transaction(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.side_effect = AuthorizeException("It failed!")
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
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
            payer=user, payee=deliverable.order.seller,
        )
        self.assertEqual(escrow.status, TransactionRecord.FAILURE)
        self.assertEqual(escrow.targets.filter(content_type__model='deliverable').get().target, deliverable)
        self.assertEqual(escrow.targets.filter(content_type__model='invoice').get().target, deliverable.invoice)
        self.assertEqual(escrow.amount, Money('10.29', 'USD'))
        self.assertEqual(escrow.payer, user)
        self.assertEqual(escrow.response_message, "It failed!")
        self.assertEqual(escrow.payee, deliverable.order.seller)
        fee = TransactionRecord.objects.get(
            source=TransactionRecord.CARD, destination=TransactionRecord.UNPROCESSED_EARNINGS,
        )
        self.assertEqual(fee.status, TransactionRecord.FAILURE)
        self.assertEqual(fee.targets.filter(content_type__model='deliverable').get().target, deliverable)
        self.assertEqual(fee.targets.filter(content_type__model='invoice').get().target, deliverable.invoice)
        self.assertEqual(fee.amount, Money('1.71', 'USD'))
        self.assertEqual(fee.payer, user)
        self.assertIsNone(fee.payee)


    @patch('apps.sales.utils.charge_card')
    def test_pay_order_new_card_failed_transaction(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.side_effect = AuthorizeException("It failed!")
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
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
            payer=user, payee=deliverable.order.seller,
        )
        self.assertEqual(escrow.status, TransactionRecord.FAILURE)
        self.assertEqual(escrow.targets.filter(content_type__model='deliverable').get().target, deliverable)
        self.assertEqual(escrow.targets.filter(content_type__model='invoice').get().target, deliverable.invoice)
        self.assertEqual(escrow.amount, Money('10.29', 'USD'))
        self.assertEqual(escrow.payer, user)
        self.assertEqual(escrow.response_message, "It failed!")
        self.assertEqual(escrow.payee, deliverable.order.seller)
        fee = TransactionRecord.objects.get(
            source=TransactionRecord.CARD, destination=TransactionRecord.UNPROCESSED_EARNINGS,
        )
        self.assertEqual(fee.status, TransactionRecord.FAILURE)
        self.assertEqual(fee.targets.filter(content_type__model='deliverable').get().target, deliverable)
        self.assertEqual(fee.targets.filter(content_type__model='invoice').get().target, deliverable.invoice)
        self.assertEqual(fee.amount, Money('1.71', 'USD'))
        self.assertEqual(fee.payer, user)
        self.assertIsNone(fee.payee)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_amount_changed(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '10.00',
                'cvv': '234'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_wrong_card(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create().id,
                'amount': '12.00',
                'cvv': '345'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_outsider(self, mock_charge_card):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '123'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_seller_fail(self, mock_charge_card):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            order__seller=user2,
        )
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=user).id,
                'amount': '12.00',
                'cvv': '567'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TransactionRecord.objects.all().count(), 0)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_staffer(self, mock_charge_card):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'card_id': CreditCardTokenFactory.create(user=deliverable.order.buyer).id,
                'amount': '12.00',
                'cvv': '467',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(deliverable, deliverable.order.buyer)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_create_guest(self, mock_charge_card):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            order__buyer=None, order__customer_email='test@example.com',
        )
        self.assertIsNone(deliverable.order.buyer)
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertTrue(deliverable.order.buyer.guest)
        self.check_transactions(
            deliverable, deliverable.order.buyer, remote_id='', auth_code='', source=TransactionRecord.CASH_DEPOSIT,
        )

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_fail_no_guest_email(self, mock_charge_card):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            order__buyer=None,
        )
        self.assertIsNone(deliverable.order.buyer)
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_charge_card.return_value = '36985214745'
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'No buyer is set for this order, nor is there a customer email set.')

    def test_pay_order_staffer_cash(self):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(deliverable, deliverable.order.buyer, remote_id='', auth_code='', source=TransactionRecord.CASH_DEPOSIT)

    def test_pay_order_buyer_cash_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'cash': True,
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.sales.utils.transaction_details')
    def test_pay_order_staffer_remote_id(self, mock_details):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        deliverable = DeliverableFactory.create(
            status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        mock_details.return_value = {
            'auth_code': 'ABC123',
            'auth_amount': Money('12.00', 'USD'),
        }
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'remote_id': '36985214745',
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_transactions(deliverable, deliverable.order.buyer)

    def test_pay_order_buyer_remote_id_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
            {
                'remote_id': '36985214745',
                'amount': '12.00',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.sales.utils.charge_saved_card')
    def test_pay_order_table_order(self, mock_charge_card):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__buyer=user, status=PAYMENT_PENDING, product__base_price=Money('10.00', 'USD'),
            table_order=True
        )
        add_adjustment(deliverable, Money('2.00', 'USD'))
        subscription = Subscription.objects.get(subscriber=deliverable.order.seller, type=SALE_UPDATE)
        self.assertTrue(subscription.email)
        mock_charge_card.return_value = ('36985214745', 'ABC123')
        card = CreditCardTokenFactory.create(user=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/pay/',
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
