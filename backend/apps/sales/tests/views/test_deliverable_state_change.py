from decimal import Decimal
from unittest.mock import patch, call

from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status

from apps.lib.abstract_models import ADULT
from apps.lib.models import DISPUTE, Subscription, COMMENT, REVISION_UPLOADED, ref_for_instance
from apps.lib.test_resources import SignalsDisabledMixin, APITestCase
from apps.profiles.models import User
from apps.profiles.tests.factories import UserFactory, CharacterFactory, SubmissionFactory
from apps.sales.authorize import AuthorizeException
from apps.sales.models import Revision, idempotent_lines, QUEUED, NEW, PAYMENT_PENDING, COMPLETED, IN_PROGRESS, \
    TransactionRecord, REVIEW, DISPUTED, Order, Deliverable, WAITING
from apps.sales.tests.factories import DeliverableFactory, RevisionFactory, LineItemFactory, TransactionRecordFactory, \
    CreditCardTokenFactory


@patch('apps.sales.views.notify')
class TestDeliverableStateChange(SignalsDisabledMixin, APITestCase):
    fixture_list = ['deliverable-state-change']

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
            self.deliverable = DeliverableFactory.create(
                order__seller=self.seller, order__buyer=self.buyer, product__base_price=Money('5.00', 'USD'),
                adjustment_task_weight=1, adjustment_expected_turnaround=2, product__task_weight=3,
                product__expected_turnaround=4
            )
            self.deliverable.characters.add(*characters)
            self.final = RevisionFactory.create(deliverable=self.deliverable, rating=ADULT, owner=self.seller)
            self.save_fixture('deliverable-state-change')

        self.final = Revision.objects.all()[0]
        self.deliverable = self.final.deliverable
        self.url = '/api/sales/v1/order/{}/deliverables/{}/'.format(self.deliverable.order.id, self.deliverable.id)
        self.outsider, self.seller, self.buyer, self.staffer = User.objects.order_by('id')[:4]

    def state_assertion(
            self, user_attr, url_ext='', target_response_code=status.HTTP_200_OK, initial_status=None, method='post',
            target_status=None
    ):
        if initial_status is not None:
            self.deliverable.status = initial_status
            self.deliverable.save()
        self.login(getattr(self, user_attr))
        response = getattr(self.client, method)(self.url + url_ext)
        try:
            self.assertEqual(response.status_code, target_response_code)
        except AssertionError:
            raise AssertionError(
                f'Expected response code {target_response_code} but got {response.status_code}. Data: {response.data}',
            )
        if target_status is not None:
            self.deliverable.refresh_from_db()
            self.assertEqual(self.deliverable.status, target_status)

    def test_accept_deliverable(self, _mock_notify):
        self.state_assertion('seller', 'accept/')

    def test_accept_deliverable_waitlist(self, _mock_notify):
        idempotent_lines(self.deliverable)
        self.state_assertion('seller', 'accept/', initial_status=WAITING, target_status=PAYMENT_PENDING)

    def test_accept_deliverable_send_email(self, _mock_notify):
        self.deliverable.order.buyer = None
        self.deliverable.order.customer_email = 'test_customer@example.com'
        self.deliverable.order.save()
        Subscription.objects.all().delete()
        self.state_assertion('seller', 'accept/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f'You have a new invoice from {self.deliverable.order.seller.username}!')

    def test_accept_deliverable_buyer_fail(self, _mock_notify):
        self.state_assertion('buyer', 'accept/', status.HTTP_403_FORBIDDEN)

    def test_accept_deliverable_outsider(self, _mock_notify):
        self.state_assertion('outsider', 'accept/', status.HTTP_403_FORBIDDEN)

    def test_accept_deliverable_staffer(self, _mock_notify):
        self.state_assertion('staffer', 'accept/')

    def test_accept_deliverable_free(self, _mock_notify):
        item = LineItemFactory.create(deliverable=self.deliverable, amount=-self.deliverable.product.base_price)
        idempotent_lines(self.deliverable)
        self.state_assertion('seller', 'accept/')
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, QUEUED)
        self.assertFalse(self.deliverable.revisions_hidden)
        self.assertTrue(self.deliverable.escrow_disabled)

    def test_in_progress(self, _mock_notify):
        self.deliverable.stream_link = 'https://google.com/'
        self.state_assertion('seller', 'start/', initial_status=QUEUED)

    def test_cancel_deliverable(self, _mock_notify):
        self.state_assertion('seller', 'cancel/', initial_status=NEW)

    def test_cancel_deliverable_buyer(self, _mock_notify):
        self.state_assertion('buyer', 'cancel/', initial_status=PAYMENT_PENDING)

    def test_cancel_deliverable_outsider_fail(self, _mock_notify):
        self.state_assertion('outsider', 'cancel/', status.HTTP_403_FORBIDDEN, initial_status=PAYMENT_PENDING)

    def test_cancel_deliverable_staffer(self, _mock_notify):
        self.state_assertion('staffer', 'cancel/', initial_status=PAYMENT_PENDING)

    def test_mark_paid_deliverable_buyer_fail(self, _mock_notify):
        self.deliverable.escrow_disabled = True
        self.deliverable.save()
        self.state_assertion('buyer', 'mark-paid/', status.HTTP_403_FORBIDDEN, initial_status=PAYMENT_PENDING)

    def test_mark_paid_deliverable_seller(self, _mock_notify):
        self.deliverable.escrow_disabled = True
        self.assertTrue(self.deliverable.revisions_hidden)
        self.deliverable.save()
        self.final.delete()
        self.state_assertion('seller', 'mark-paid/', initial_status=PAYMENT_PENDING, target_status=QUEUED)
        self.deliverable.refresh_from_db()
        self.assertFalse(self.deliverable.revisions_hidden)

    def test_mark_paid_disables_escrow(self, _mock_notify):
        self.assertFalse(self.deliverable.escrow_disabled)
        self.assertTrue(self.deliverable.revisions_hidden)
        self.deliverable.save()
        self.final.delete()
        self.state_assertion('seller', 'mark-paid/', initial_status=PAYMENT_PENDING, target_status=QUEUED)
        self.deliverable.refresh_from_db()
        self.assertFalse(self.deliverable.revisions_hidden)
        self.assertTrue(self.deliverable.escrow_disabled)

    def test_mark_paid_deliverable_final_uploaded(self, _mock_notify):
        self.deliverable.escrow_disabled = True
        self.deliverable.final_uploaded = True
        self.deliverable.save()
        self.state_assertion(
            'seller', 'mark-paid/', initial_status=PAYMENT_PENDING, target_status=COMPLETED
        )

    def test_mark_paid_revisions_exist(self, _mock_notify):
        self.deliverable.escrow_disabled = True
        self.deliverable.save()
        RevisionFactory.create(deliverable=self.deliverable)
        self.state_assertion(
            'seller', 'mark-paid/', initial_status=PAYMENT_PENDING, target_status=IN_PROGRESS
        )

    def test_mark_paid_task_weights(self, _mock_notify):
        self.deliverable.escrow_disabled = True
        self.deliverable.save()
        self.assertEqual(self.deliverable.adjustment_task_weight, 1)
        self.assertEqual(self.deliverable.adjustment_expected_turnaround, 2)
        self.assertEqual(self.deliverable.task_weight, 0)
        self.assertEqual(self.deliverable.expected_turnaround, 0)
        self.state_assertion('seller', 'mark-paid/', initial_status=PAYMENT_PENDING)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.adjustment_task_weight, 1)
        self.assertEqual(self.deliverable.adjustment_expected_turnaround, 2)
        self.assertEqual(self.deliverable.task_weight, 3)
        self.assertEqual(self.deliverable.expected_turnaround, 4)

    def test_mark_paid_deliverable_staffer(self, _mock_notify):
        self.deliverable.escrow_disabled = True
        self.deliverable.save()
        self.state_assertion('staffer', 'mark-paid/', initial_status=PAYMENT_PENDING)

    @override_settings(SERVICE_PERCENTAGE_FEE=Decimal('10'), SERVICE_STATIC_FEE=Decimal('1.00'))
    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.tasks.withdraw_all.delay')
    def test_approve_deliverable_buyer(self, mock_withdraw, mock_bonus_amount, _mock_notify):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            amount=Money('15.00', 'USD'),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_bonus_amount.return_value = Money('5.00', 'USD')
        self.state_assertion('buyer', 'approve/', initial_status=REVIEW)
        record.refresh_from_db()
        records = TransactionRecord.objects.all()
        self.assertEqual(records.count(), 3)
        payment = records.get(payee=self.deliverable.order.seller, source=TransactionRecord.ESCROW)
        self.assertEqual(payment.amount, Money('15.00', 'USD'))
        self.assertEqual(payment.payer, self.deliverable.order.seller)
        self.assertEqual(payment.status, TransactionRecord.SUCCESS)
        self.assertEqual(payment.destination, TransactionRecord.HOLDINGS)
        bonus = records.get(
            payee__isnull=True, payer__isnull=True, source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
        )
        self.assertEqual(bonus.amount, Money('5.00', 'USD'))
        self.assertEqual(bonus.category, TransactionRecord.SHIELD_FEE)
        mock_withdraw.assert_called_with(self.deliverable.order.seller.id)

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.recall_notification')
    def test_approve_deliverable_recall_notification(self, mock_recall, mock_bonus_amount, _mock_notify):
        target_time = timezone.now()
        self.deliverable.disputed_on = target_time
        self.deliverable.save()
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            destination=TransactionRecord.ESCROW,
            source=TransactionRecord.CARD,
            category=TransactionRecord.ESCROW_HOLD,
            amount=Money('15.00', 'USD'),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        self.state_assertion('buyer', 'approve/', initial_status=DISPUTED)
        mock_recall.assert_has_calls([call(DISPUTE, self.deliverable)])
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.disputed_on, None)

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.recall_notification')
    def test_approve_deliverable_staffer_no_recall_notification(self, mock_recall, mock_bonus_amount, _mock_notify):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            destination=TransactionRecord.ESCROW,
            source=TransactionRecord.CARD,
            category=TransactionRecord.ESCROW_HOLD,
            amount=Money('15.00', 'USD'),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        target_time = timezone.now()
        self.deliverable.disputed_on = target_time
        self.deliverable.save()
        self.state_assertion('staffer', 'approve/', initial_status=DISPUTED)
        for mock_call in mock_recall.call_args_list:
            self.assertNotEqual(mock_call[0], DISPUTE)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.disputed_on, target_time)

    @override_settings(
        TABLE_PERCENTAGE_FEE=Decimal('15'), TABLE_STATIC_FEE=Decimal('2.00'),
    )
    @patch('apps.sales.tasks.withdraw_all.delay')
    def test_approve_table_deliverable(self, mock_withdraw, _mock_notify):
        self.deliverable.product.base_price = Money('15.00', 'USD')
        self.deliverable.product.save()
        self.deliverable.table_order = True
        self.deliverable.status = NEW
        self.deliverable.save()
        idempotent_lines(self.deliverable)
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            amount=Money('15.00', 'USD'),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        record2 = TransactionRecordFactory.create(
            payee=None,
            payer=self.deliverable.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.RESERVE,
            amount=Money('2.00', 'USD'),
        )
        record2.targets.add(ref_for_instance(self.deliverable))
        record3 = TransactionRecordFactory.create(
            payee=None,
            payer=self.deliverable.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.MONEY_HOLE_STAGE,
            amount=Money('3.00', 'USD'),
        )
        record3.targets.add(ref_for_instance(self.deliverable))
        self.state_assertion('buyer', 'approve/', initial_status=REVIEW)
        record.refresh_from_db()
        records = TransactionRecord.objects.all()
        self.assertEqual(records.count(), 6)
        payment = records.get(payee=self.deliverable.order.seller, source=TransactionRecord.ESCROW)
        self.assertEqual(payment.amount, Money('15.00', 'USD'))
        self.assertEqual(payment.payer, self.deliverable.order.seller)
        self.assertEqual(payment.status, TransactionRecord.SUCCESS)
        self.assertEqual(payment.destination, TransactionRecord.HOLDINGS)
        service_fee = records.get(
            payee__isnull=True, payer__isnull=True, source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
        )
        self.assertEqual(service_fee.amount, Money('2.00', 'USD'))
        self.assertEqual(service_fee.category, TransactionRecord.TABLE_SERVICE)
        mock_withdraw.assert_called_with(self.deliverable.order.seller.id)

    @patch('apps.sales.utils.refund_transaction')
    def test_refund_escrow_disabled(self, mock_refund_transaction, _mock_notify):
        self.deliverable.escrow_disabled = True
        self.deliverable.save()
        self.state_assertion('seller', 'refund/', initial_status=DISPUTED)
        mock_refund_transaction.assert_not_called()

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.refund_transaction')
    @override_settings(
        PREMIUM_PERCENTAGE_FEE=Decimal('5'), PREMIUM_STATIC_FEE=Decimal('0.10')
    )
    def test_refund_card_seller(self, mock_refund_transaction, mock_bonus_amount, _mock_notify):
        card = CreditCardTokenFactory.create()
        record = TransactionRecordFactory.create(
            card=card,
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            amount=Money('15.00', 'USD'),
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            remote_id='1234',
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_refund_transaction.return_value = ('123', 'ABC456')
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        self.state_assertion('seller', 'refund/', initial_status=DISPUTED)
        refund_transaction = TransactionRecord.objects.get(
            status=TransactionRecord.SUCCESS,
            payee=self.deliverable.order.buyer, payer=self.deliverable.order.seller,
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
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            source=TransactionRecord.CARD,
            destination=TransactionRecord.ESCROW,
            card=card,
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_refund_transaction.side_effect = AuthorizeException(
            "It failed"
        )
        self.state_assertion('seller', 'refund/', status.HTTP_400_BAD_REQUEST, initial_status=DISPUTED)
        TransactionRecord.objects.get(
            response_message="It failed", status=TransactionRecord.FAILURE,
            payee=self.deliverable.order.buyer, payer=self.deliverable.order.seller,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.CARD,
            category=TransactionRecord.ESCROW_REFUND,
        )

    @patch('apps.sales.utils.refund_transaction')
    def test_refund_cash_only(self, mock_refund_transaction, _mock_notify):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            source=TransactionRecord.CASH_DEPOSIT,
            destination=TransactionRecord.ESCROW,
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_refund_transaction.side_effect = AuthorizeException(
            "It failed"
        )
        self.state_assertion('seller', 'refund/', status.HTTP_200_OK, initial_status=IN_PROGRESS)
        mock_refund_transaction.assert_not_called()
        TransactionRecord.objects.get(
            response_message="", status=TransactionRecord.SUCCESS,
            payee=self.deliverable.order.buyer, payer=self.deliverable.order.seller,
            source=TransactionRecord.ESCROW,
            destination=TransactionRecord.CASH_DEPOSIT,
            category=TransactionRecord.ESCROW_REFUND,
        )

    def test_refund_card_buyer(self, _mock_notify):
        self.state_assertion('buyer', 'refund/', status.HTTP_403_FORBIDDEN, initial_status=DISPUTED)

    def test_refund_card_outsider(self, _mock_notify):
        self.state_assertion('outsider', 'refund/', status.HTTP_403_FORBIDDEN, initial_status=DISPUTED)

    @patch('apps.sales.utils.get_bonus_amount')
    @patch('apps.sales.utils.refund_transaction')
    def test_refund_card_staffer(self, mock_refund_transaction, mock_bonus_amount, _mock_notify):
        card = CreditCardTokenFactory.create()
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            card=card,
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_refund_transaction.return_value = ('123', '87HSIF')
        mock_bonus_amount.return_value = Money('2.50')
        self.state_assertion('staffer', 'refund/', initial_status=DISPUTED)
        record.refresh_from_db()
        TransactionRecord.objects.get(
            payer=None, payee=None, source=TransactionRecord.RESERVE,
            destination=TransactionRecord.UNPROCESSED_EARNINGS,
            amount=Money('2.50')
        )


    def test_approve_deliverable_seller_fail(self, _mock_notify):
        self.state_assertion('seller', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=REVIEW)

    def test_approve_deliverable_outsider_fail(self, _mock_notify):
        self.state_assertion('outsider', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=REVIEW)

    def test_approve_deliverable_seller(self, _mock_notify):
        self.state_assertion('seller', 'approve/', status.HTTP_403_FORBIDDEN, initial_status=REVIEW)

    @patch('apps.sales.utils.get_bonus_amount')
    def test_approve_deliverable_staffer(self, mock_bonus_amount, _mock_notify):
        record = TransactionRecordFactory.create(
            payee=self.deliverable.order.seller,
            payer=self.deliverable.order.buyer,
            amount=Money('15.00', 'USD'),
        )
        record.targets.add(ref_for_instance(self.deliverable))
        mock_bonus_amount.return_value = Money('2.50', 'USD')
        self.state_assertion('staffer', 'approve/', initial_status=REVIEW)
        record.refresh_from_db()


    def test_claim_deliverable_staffer(self, _mock_notify):
        self.state_assertion('staffer', 'claim/', initial_status=DISPUTED)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.arbitrator, self.staffer)
        self.assertEqual(Subscription.objects.filter(
            subscriber=self.staffer, object_id=self.deliverable.id,
            content_type=ContentType.objects.get_for_model(Deliverable),
            type__in=[COMMENT, REVISION_UPLOADED], email=True,
        ).count(), 2)

    def test_claim_deliverable_staffer_claimed_already(self, _mock_notify):
        arbitrator = UserFactory.create(is_staff=True)
        self.deliverable.arbitrator = arbitrator
        self.deliverable.save()
        self.state_assertion('staffer', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=DISPUTED)
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.arbitrator, arbitrator)

    def test_claim_deliverable_buyer(self, _mock_notify):
        self.state_assertion('buyer', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=DISPUTED)

    def test_claim_deliverable_seller(self, _mock_notify):
        self.state_assertion('seller', 'claim/', status.HTTP_403_FORBIDDEN, initial_status=DISPUTED)

    @freeze_time('2019-02-01 12:00:00')
    def test_file_dispute_buyer_enough_time(self, _mock_notify):
        self.deliverable.dispute_available_on = date(year=2019, month=1, day=1)
        self.deliverable.save()
        self.state_assertion('buyer', 'dispute/', status.HTTP_200_OK, initial_status=IN_PROGRESS)

    @freeze_time('2019-01-01 12:00:00')
    def test_file_dispute_buyer_too_early(self, _mock_notify):
        self.deliverable.dispute_available_on = date(year=2019, month=5, day=3)
        self.deliverable.save()
        self.state_assertion('buyer', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=IN_PROGRESS)

    def test_file_dispute_seller(self, _mock_notify):
        self.state_assertion('seller', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=REVIEW)

    def test_file_dispute_outsider_fail(self, _mock_notify):
        self.state_assertion('outsider', 'dispute/', status.HTTP_403_FORBIDDEN, initial_status=REVIEW)
