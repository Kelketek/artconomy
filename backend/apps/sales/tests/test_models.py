from decimal import Decimal
from unittest.mock import patch, Mock

from ddt import ddt, unpack, data
from django.test import TestCase, override_settings
from moneyed import Money

from apps.lib.models import NEW_PRODUCT
from apps.profiles.models import NO_US_ACCOUNT, HAS_US_ACCOUNT
from apps.profiles.tests.factories import UserFactory, SubmissionFactory
from apps.sales.models import TransactionRecord, Order, BASE_PRICE, SHIELD, BONUS, TABLE_SERVICE, TAX
from apps.sales.tests.factories import RatingFactory, PromoFactory, TransactionRecordFactory, ProductFactory, \
    OrderFactory, \
    CreditCardTokenFactory, RevisionFactory, LineItemFactory


class TestRating(TestCase):
    def test_set_stars(self):
        user = UserFactory.create()
        rater = UserFactory.create()
        RatingFactory.create(target=user, stars=2, rater=rater)
        RatingFactory.create(target=user, stars=5, rater=rater)
        RatingFactory.create(target=user, stars=4, rater=rater)
        user.refresh_from_db()
        self.assertEqual(user.stars, Decimal('3.67'))


class TestPromo(TestCase):
    def test_promo_string(self):
        promo = PromoFactory.create(code='Wat')
        self.assertEqual(str(promo), 'WAT')


DESCRIPTION_VALUES = (
    {'price': Decimal('5.00'), 'prefix': '[Starts at $5.00] - ', 'escrow_disabled': False},
    {'price': Decimal('0'), 'prefix': '[Starts at FREE] - ', 'escrow_disabled': False},
    {'price': Decimal('0'), 'prefix': '[Starts at FREE] - ', 'escrow_disabled': True},
    {'price': Decimal('1.1'), 'prefix': '[Starts at $1.10] - ', 'escrow_disabled': True},
)


@ddt
class TestProduct(TestCase):
    def test_can_reference(self):
        user = UserFactory.create()
        product = ProductFactory.create(user=user)
        other = UserFactory.create()
        self.assertTrue(product.can_reference_asset(user))
        self.assertFalse(product.can_reference_asset(other))

    @patch('apps.sales.models.recall_notification')
    def test_recall(self, mock_recall_notification):
        user = UserFactory.create()
        product = ProductFactory.create(hidden=False, user=user)
        mock_recall_notification.assert_not_called()
        product.hidden = True
        product.save()
        mock_recall_notification.assert_called_with(NEW_PRODUCT, user, {'product': product.id}, unique_data=True)

    def test_notification_display(self):
        request = Mock()
        request.user = UserFactory.create()
        context = {'request': request}
        product = ProductFactory.create(user=request.user, primary_submission=SubmissionFactory.create())
        data = product.notification_display(context)
        self.assertEqual(data['id'], product.primary_submission.id)

    @unpack
    @data(*DESCRIPTION_VALUES)
    def test_preview_description(self, price: Decimal, prefix: str, escrow_disabled: bool):
        account_status = NO_US_ACCOUNT if escrow_disabled else HAS_US_ACCOUNT
        product = ProductFactory.create(
            base_price=price, description='Test **Test** *Test*',
        )
        product.user.artist_profile.bank_status = account_status
        product.user.artist_profile.escrow_disabled = escrow_disabled
        product.user.artist_profile.save()
        self.assertTrue(
            product.preview_description.startswith(prefix),
            msg=f'{repr(product.preview_description)} does not start with {repr(prefix)}.',
        )
        self.assertTrue(
            product.preview_description.endswith('Test Test Test'),
            msg=f"{repr(product.preview_description)} does not end with 'Test Test Test'."
        )


class TestTransactionRecord(TestCase):
    def test_string(self):
        record = TransactionRecordFactory.create(payer__username='Dude', payee__username='Chick')
        self.assertEqual(str(record), 'Successful: $10.00 from Dude [Credit Card] to Chick [Escrow] for None')

    @patch('apps.sales.models.warn')
    @patch('apps.sales.models.refund_transaction')
    def test_default_refund(self, mock_refund_transaction, _mock_warn):
        card = CreditCardTokenFactory.create(last_four='1234')
        record = TransactionRecordFactory.create(card=card)
        mock_refund_transaction.return_value = '5678'
        record.refund()
        mock_refund_transaction.assert_called_with(record.remote_id, '1234', Decimal('10.00'))

    @patch('apps.sales.models.warn')
    def test_refund_account(self, _mock_warn):
        record = TransactionRecordFactory.create(source=TransactionRecord.ACH_MISC_FEES)
        with self.assertRaises(NotImplementedError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'Account refunds are not yet implemented.')

    @patch('apps.sales.models.warn')
    def test_refund_failed(self, _mock_warn):
        record = TransactionRecordFactory.create(status=TransactionRecord.FAILURE)
        with self.assertRaises(ValueError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'Cannot refund a failed transaction.')

    @patch('apps.sales.models.warn')
    def test_refund_wrong_type(self, _mock_warn):
        record = TransactionRecordFactory.create(source=TransactionRecord.BANK)
        with self.assertRaises(NotImplementedError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'ACH Refunds are not implemented.')

    @patch('apps.sales.models.warn')
    def test_refund_escrow(self, _mock_warn):
        record = TransactionRecordFactory.create(source=TransactionRecord.ESCROW)
        with self.assertRaises(ValueError) as context_manager:
            record.refund()
        self.assertEqual(
            str(context_manager.exception),
            'Cannot refund an escrow sourced payment. Are you sure you grabbed the right payment object?',
        )


@override_settings(
    SERVICE_PERCENTAGE_FEE=Decimal('5'),
    SERVICE_STATIC_FEE=Decimal('.25'),
    PREMIUM_PERCENTAGE_BONUS=Decimal('4'),
    PREMIUM_STATIC_BONUS=Decimal('.10'),
    TABLE_PERCENTAGE_FEE=Decimal('20'),
    TABLE_STATIC_FEE=Decimal('2.00'),
    TABLE_TAX=Decimal('8'),
)
class TestOrder(TestCase):
    def test_total(self):
        order = OrderFactory.create(product__base_price=Money(5, 'USD'))
        self.assertEqual(order.total(), Money('5.00', 'USD'))
        LineItemFactory.create(order=order, amount=Money('2.00', 'USD'))
        self.assertEqual(order.total(), Money('7.00', 'USD'))

    def order_and_context(self):
        order = OrderFactory.create()
        order.arbitrator = UserFactory.create()
        order.save()
        request = Mock()
        request.user = order.arbitrator
        context = {'request': request}
        return order, context

    def test_notification_name(self):
        order, context = self.order_and_context()
        self.assertEqual(f'Case #{order.id}', order.notification_name(context))
        order.buyer = order.arbitrator
        order.arbitrator = None
        self.assertEqual(f'Order #{order.id}', order.notification_name(context))

    def test_notification_link(self):
        order, context = self.order_and_context()
        self.assertEqual(
            {'name': 'Case', 'params': {'orderId': order.id, 'username': context['request'].user.username}},
            order.notification_link(context),
        )
        order.buyer = order.arbitrator
        order.arbitrator = None
        order.save()
        self.assertEqual(
            {'name': 'Order', 'params': {'orderId': order.id, 'username': context['request'].user.username}},
            order.notification_link(context),
        )

    def test_notification_display(self):
        order, context = self.order_and_context()
        order.product.primary_submission = SubmissionFactory.create()
        output = order.notification_display(context)
        self.assertEqual(output['id'], order.product.primary_submission.id)
        self.assertEqual(output['title'], order.product.primary_submission.title)

    def test_notification_display_revision(self):
        order, context = self.order_and_context()
        order.product.primary_submission = SubmissionFactory.create()
        order.revisions_hidden = False
        revision = RevisionFactory.create(order=order)
        output = order.notification_display(context)
        self.assertEqual(output['id'], revision.id)
        self.assertIn(revision.file.file.name, output['file']['full'])

    def test_create_line_items_escrow(self):
        order = OrderFactory.create(product__base_price=Money('15.00', 'USD'))
        base_price = order.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money('15.00', 'USD'))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        shield = order.line_items.get(type=SHIELD)
        self.assertEqual(shield.percentage, Decimal('5'))
        self.assertEqual(shield.amount, Money('.25', 'USD'))
        self.assertTrue(shield.cascade_percentage)
        self.assertTrue(shield.cascade_amount)
        bonus = order.line_items.get(type=BONUS)
        self.assertEqual(bonus.percentage, Decimal('4'))
        self.assertEqual(bonus.amount, Money('.10', 'USD'))
        self.assertTrue(bonus.cascade_percentage)
        self.assertTrue(bonus.cascade_amount)
        self.assertEqual(bonus.priority, shield.priority)
        self.assertEqual(order.line_items.all().count(), 3)

    def test_create_line_items_non_escrow(self):
        order = OrderFactory.create(product__base_price=Money('15.00', 'USD'), escrow_disabled=True)
        base_price = order.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money('15.00', 'USD'))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        self.assertEqual(order.line_items.all().count(), 1)

    def test_create_line_items_table_service(self):
        order = OrderFactory.create(product__base_price=Money('15.00', 'USD'), table_order=True)
        base_price = order.line_items.get(type=BASE_PRICE)
        self.assertEqual(base_price.amount, Money('15.00', 'USD'))
        self.assertEqual(base_price.percentage, 0)
        self.assertEqual(base_price.priority, 0)
        table_service = order.line_items.get(type=TABLE_SERVICE)
        self.assertEqual(table_service.percentage, Decimal('20'))
        self.assertEqual(table_service.amount, Money('2.00', 'USD'))
        self.assertTrue(table_service.cascade_percentage)
        self.assertFalse(table_service.cascade_amount)
        set_on_fire = order.line_items.get(type=TAX)
        self.assertEqual(set_on_fire.percentage, Decimal('8'))
        self.assertEqual(set_on_fire.amount, Money('0.00', 'USD'))
        self.assertEqual(order.line_items.all().count(), 3)


class TestCreditCardToken(TestCase):
    def test_string(self):
        card = CreditCardTokenFactory.create(last_four='1234')
        self.assertEqual(str(card), 'Visa ending in 1234')
        card.active = False
        self.assertEqual(str(card), 'Visa ending in 1234 (Deleted)')

    def test_no_delete(self):
        card = CreditCardTokenFactory.create()
        self.assertRaises(RuntimeError, card.delete)


class TestRevision(TestCase):
    def test_can_reference(self):
        user = UserFactory.create()
        buyer = UserFactory.create()
        revision = RevisionFactory.create(owner=user, order__seller=user, order__product__user=user, order__buyer=buyer)
        other = UserFactory.create()
        self.assertTrue(revision.can_reference_asset(revision.owner))
        self.assertFalse(revision.can_reference_asset(other))
        self.assertFalse(revision.can_reference_asset(buyer))
        revision.order.status = Order.COMPLETED
        self.assertTrue(revision.can_reference_asset(buyer))
