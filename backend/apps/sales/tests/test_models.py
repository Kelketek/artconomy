from decimal import Decimal
from unittest.mock import patch, Mock

from django.test import TestCase
from moneyed import Money

from apps.lib.models import NEW_PRODUCT
from apps.profiles.tests.factories import UserFactory, SubmissionFactory
from apps.sales.models import TransactionRecord, Order
from apps.sales.tests.factories import RatingFactory, PromoFactory, TransactionRecordFactory, ProductFactory, OrderFactory, \
    CreditCardTokenFactory, RevisionFactory


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


class TestTransactionRecord(TestCase):
    def test_string(self):
        record = TransactionRecordFactory.create(payer__username='Dude', payee__username='Chick')
        self.assertEqual(str(record), 'Successful: $10.00 from Dude [Credit Card] to Chick [Escrow] for None')

    @patch('apps.sales.models.refund_transaction')
    def test_default_refund(self, mock_refund_transaction):
        card = CreditCardTokenFactory.create(last_four='1234')
        record = TransactionRecordFactory.create(card=card)
        mock_refund_transaction.return_value = '5678'
        record.refund()
        mock_refund_transaction.assert_called_with(record.remote_id, '1234', Decimal('10.00'))

    def test_refund_account(self):
        record = TransactionRecordFactory.create(source=TransactionRecord.ACH_MISC_FEES)
        with self.assertRaises(NotImplementedError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'Account refunds are not yet implemented.')

    def test_refund_failed(self):
        record = TransactionRecordFactory.create(status=TransactionRecord.FAILURE)
        with self.assertRaises(ValueError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'Cannot refund a failed transaction.')

    def test_refund_wrong_type(self):
        record = TransactionRecordFactory.create(source=TransactionRecord.BANK)
        with self.assertRaises(NotImplementedError) as context_manager:
            record.refund()
        self.assertEqual(str(context_manager.exception), 'ACH Refunds are not implemented.')

    def test_refund_escrow(self):
        record = TransactionRecordFactory.create(source=TransactionRecord.ESCROW)
        with self.assertRaises(ValueError) as context_manager:
            record.refund()
        self.assertEqual(
            str(context_manager.exception),
            'Cannot refund an escrow sourced payment. Are you sure you grabbed the right payment object?',
        )


class TestOrder(TestCase):
    def test_total(self):
        order = OrderFactory.create(product__price=Money(5, 'USD'), price=None)
        self.assertEqual(order.total(), Money('5.00', 'USD'))
        order.price = Money('4.00', 'USD')
        self.assertEqual(order.total(), Money('4.00', 'USD'))
        order.adjustment = Money('6.00', 'USD')
        self.assertEqual(order.total(), Money('10.00', 'USD'))

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