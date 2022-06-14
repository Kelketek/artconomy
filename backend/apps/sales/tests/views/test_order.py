from decimal import Decimal
from unittest import expectedFailure
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from ddt import ddt, data
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from django.utils.datetime_safe import date
from freezegun import freeze_time
from moneyed import Money
from rest_framework import status

from apps.lib.abstract_models import ADULT, MATURE, GENERAL
from apps.lib.models import Event, SALE_UPDATE, ORDER_UPDATE, WAITLIST_UPDATED, Subscription, COMMENT
from apps.lib.test_resources import APITestCase
from apps.lib.tests.factories import AssetFactory
from apps.profiles.models import VERIFIED, User
from apps.profiles.tests.factories import UserFactory, CharacterFactory, SubmissionFactory
from apps.profiles.utils import create_guest_user
from apps.sales.models import Deliverable, Order, NEW, ADD_ON, TransactionRecord, TIP, SHIELD, QUEUED, IN_PROGRESS, \
    REVIEW, DISPUTED, COMPLETED, PAYMENT_PENDING, BASE_PRICE, EXTRA, Revision, LineItem, ServicePlan
from apps.sales.tests.factories import ProductFactory, DeliverableFactory, add_adjustment, RevisionFactory, \
    LineItemFactory, ServicePlanFactory
from apps.sales.tests.test_utils import TransactionCheckMixin


@override_settings(
    SERVICE_STATIC_FEE=Decimal('0.50'), SERVICE_PERCENTAGE_FEE=Decimal('4'),
    PREMIUM_STATIC_BONUS=Decimal('0.25'), PREMIUM_PERCENTAGE_BONUS=Decimal('4'),
)
@ddt
class TestOrder(TransactionCheckMixin, APITestCase):
    def setUp(self):
        self.landscape = ServicePlanFactory(name='Landscape')

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
                'rating': ADULT,
                'characters': character_ids
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable = Deliverable.objects.get(id=response.data['default_path']['params']['deliverableId'])
        order = Order.objects.get(id=response.data['id'])
        for character in characters:
            self.assertTrue(character.shared_with.filter(username=order.seller.username).exists())
        self.assertEqual(order.deliverables.get().product, product)
        self.assertEqual(deliverable.status, NEW)
        self.assertEqual(deliverable.details, 'Draw me some porn!')
        # These should be set at the point of payment.
        self.assertEqual(deliverable.task_weight, 0)
        self.assertEqual(deliverable.expected_turnaround, 0)

    def test_place_order_references(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create(task_weight=5, expected_turnaround=3)
        asset_ids = [AssetFactory.create(uploaded_by=user).id for _ in range(3)]
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'rating': ADULT,
                'references': asset_ids,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable = Deliverable.objects.get(id=response.data['default_path']['params']['deliverableId'])
        for asset_id in asset_ids:
            self.assertTrue(deliverable.reference_set.filter(file__id=asset_id).exists())

    def test_place_order_references_disallowed(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create(task_weight=5, expected_turnaround=3)
        asset_ids = [AssetFactory.create(uploaded_by=None).id for _ in range(3)]
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'rating': ADULT,
                'references': asset_ids,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('references', response.data)

    def test_place_order_references_anon(self):
        product = ProductFactory.create(task_weight=5, expected_turnaround=3)
        asset_ids = [str(AssetFactory.create(uploaded_by=None).id) for _ in range(3)]
        # Forcibly set the cache key here.
        for asset_id in asset_ids:
            cache.set(f'upload_grant_{self.client.session.session_key}-to-{asset_id}', True, timeout=10)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'email': 'test@example.com',
                'rating': ADULT,
                'references': asset_ids,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable = Deliverable.objects.get(id=response.data['default_path']['params']['deliverableId'])
        for asset_id in asset_ids:
            self.assertTrue(deliverable.reference_set.filter(file__id=asset_id).exists())

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
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_place_order_waitlisted_product(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create(task_weight=5, expected_turnaround=3, wait_list=True)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Event.objects.filter(type=SALE_UPDATE).exists())
        self.assertTrue(Event.objects.filter(type=WAITLIST_UPDATED).exists())
        self.assertTrue(Event.objects.filter(type=ORDER_UPDATE).exists())
        product.user.refresh_from_db()
        self.assertEqual(product.user.artist_profile.load, 0)
        self.assertTrue(Order.objects.get(id=response.data['id']).deliverables.first().invoice.total())

    def test_place_order_waitlisted_product_email(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create(task_weight=5, expected_turnaround=3, wait_list=True)
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 2)

    @patch('apps.sales.views.views.login')
    def test_place_order_table_product(self, mock_login):
        user = UserFactory.create(is_staff=True)
        self.login(user)
        product = ProductFactory.create(table_product=True)
        self.assertEqual(len(mail.outbox), 0)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'email': 'test_table_order@example.com',
                'details': 'Draw me some porn!',
                'rating': ADULT,
            }
        )
        mock_login.assert_not_called()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 2)
        User.objects.get(guest_email='test_table_order@example.com', guest=True)
        deliverable = Order.objects.get(id=response.data['id']).deliverables.get()
        self.assertTrue(deliverable.table_order)

    def test_place_order_inventory_product_out_of_stock(self):
        user = UserFactory.create()
        self.login(user)
        product = ProductFactory.create(task_weight=5, expected_turnaround=3, track_inventory=True)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'This product is not in stock.')
        self.assertEqual(Order.objects.all().count(), 0)

    @expectedFailure
    def test_place_order_own_product(self):
        product = ProductFactory.create()
        self.login(product.user)
        response = self.client.post(
            '/api/sales/v1/account/{}/products/{}/order/'.format(product.user.username, product.id),
            {
                'details': 'Draw me some porn!',
                'rating': ADULT,
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
                'characters': characters,
                'rating': ADULT,
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
                'characters': characters,
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'This product is not available at this time.')

    def test_deliverable_view_seller(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], deliverable.id)

    def test_deliverable_view_buyer(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__buyer=user)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], deliverable.id)

    def test_deliverable_view_outsider(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create()
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_line_items(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_add_line_item(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable.refresh_from_db()
        line_item = deliverable.invoice.line_items.get(type=ADD_ON)
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))
        self.assertEqual(line_item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(line_item.destination_user, user)

    def test_add_line_item_too_low(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, product__base_price=Money('15.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': ADD_ON,
                'amount': '-14.50',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        deliverable.refresh_from_db()
        self.assertFalse(deliverable.invoice.line_items.filter(type=ADD_ON).exists())

    def test_add_line_item_buyer_fail(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user2, order__buyer=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
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
        deliverable = DeliverableFactory.create(order__seller=user2, order__buyer=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': TIP,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable.refresh_from_db()
        line_item = deliverable.invoice.line_items.get(type=TIP)
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))
        self.assertEqual(line_item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(line_item.destination_user, user2)

    def test_update_tip_buyer(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user2, order__buyer=user)
        LineItemFactory.create(
            invoice=deliverable.invoice, type=TIP, amount=Money('5.00', 'USD'), destination_user=user2,
        )
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': TIP,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable.refresh_from_db()
        line_item = deliverable.invoice.line_items.get(type=TIP)
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))
        self.assertEqual(line_item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(line_item.destination_user, user2)

    def test_no_base_percentage(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user2, order__buyer=user)
        LineItemFactory.create(invoice=deliverable.invoice, type=TIP, amount=Money('5.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': BASE_PRICE,
                'amount': '2.03',
                'percentage': 5,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_base_price(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        deliverable = DeliverableFactory.create(order__seller=user2, order__buyer=user, product=None)
        deliverable.invoice.line_items.filter(type=BASE_PRICE).update(amount=Money('100.00', 'USD'))
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': BASE_PRICE,
                'amount': '15.00',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        line_item = deliverable.invoice.line_items.get(type=BASE_PRICE)
        self.assertEqual(line_item.amount, Money('15.00', 'USD'))

    def test_add_line_item_outsider(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user2)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_line_item_not_logged_in(self):
        user = UserFactory.create()
        deliverable = DeliverableFactory.create(order__seller=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
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
        deliverable = DeliverableFactory.create(order__seller=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/',
            {
                'type': ADD_ON,
                'amount': '2.03',
                'percentage': 0,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable.refresh_from_db()
        line_item = deliverable.invoice.line_items.get(type=ADD_ON)
        self.assertEqual(line_item.amount, Money('2.03', 'USD'))
        self.assertEqual(line_item.destination_account, TransactionRecord.ESCROW)
        self.assertEqual(line_item.destination_user, user)

    def test_edit_line_item(self):
        deliverable = DeliverableFactory.create()
        line_item = add_adjustment(deliverable, Money('5.00', 'USD'))
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/{line_item.id}/',
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
        deliverable = DeliverableFactory.create()
        line_item = add_adjustment(deliverable, Money('5.00', 'USD'))
        self.login(deliverable.order.buyer)
        response = self.client.patch(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/{line_item.id}/',
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
        deliverable = DeliverableFactory.create(status=QUEUED)
        line_item = add_adjustment(deliverable, Money('5.00', 'USD'))
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/{line_item.id}/',
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
        deliverable = DeliverableFactory.create()
        line_item = add_adjustment(deliverable, Money('5.00', 'USD'))
        self.login(deliverable.order.seller)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/{line_item.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_delete_extra_line_item(self):
        deliverable = DeliverableFactory.create()
        line_item = add_adjustment(deliverable, Money('5.00', 'USD'))
        line_item.type = EXTRA
        line_item.save()
        staff = UserFactory.create(is_staff=True)
        self.login(staff)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/{line_item.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_line_item_buyer_fail(self):
        deliverable = DeliverableFactory.create()
        line_item = add_adjustment(deliverable, Money('5.00', 'USD'))
        self.login(deliverable.order.buyer)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/line-items/{line_item.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_cancel_queued(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=QUEUED)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/cancel/',
            {
                'stream_link': 'https://streaming.artconomy.com/'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_listing(self):
        deliverable = DeliverableFactory.create(status=QUEUED, revisions_hidden=False)
        self.login(deliverable.order.buyer)
        revision = RevisionFactory.create(deliverable=deliverable)
        submission = SubmissionFactory.create(deliverable=deliverable, revision=revision)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['submissions'][0], {'owner_id': submission.owner.id, 'id': submission.id})

    @freeze_time('2012-08-01 12:00:00')
    def test_revision_upload(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__seller=user, status=QUEUED, revisions=1, rating=ADULT, arbitrator=UserFactory.create(),
        )
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['deliverable'], deliverable.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        deliverable.refresh_from_db()
        self.assertIsNone(deliverable.auto_finalize_on)
        self.assertEqual(deliverable.status, IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['deliverable'], deliverable.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        # Filling revisions should not mark as complete automatically.
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.auto_finalize_on, None)
        self.assertEqual(deliverable.status, IN_PROGRESS)
        subscription = Subscription.objects.get(
            object_id=response.data['id'],
            content_type=ContentType.objects.get_for_model(Revision),
            type=COMMENT,
            subscriber=user,
        )
        self.assertTrue(subscription.email)
        subscription = Subscription.objects.get(
            object_id=response.data['id'],
            content_type=ContentType.objects.get_for_model(Revision),
            type=COMMENT,
            subscriber=deliverable.order.buyer,
        )
        self.assertTrue(subscription.email)
        subscription = Subscription.objects.get(
            object_id=response.data['id'],
            content_type=ContentType.objects.get_for_model(Revision),
            type=COMMENT,
            subscriber=deliverable.arbitrator,
        )
        self.assertTrue(subscription.email)


    @freeze_time('2012-08-01 12:00:00')
    def test_final_revision_upload(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=IN_PROGRESS, revisions=1, rating=MATURE)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['deliverable'], deliverable.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], MATURE)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.auto_finalize_on, date(2012, 8, 6))
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deliverable.refresh_from_db()
        # Filling revisions should not mark as complete automatically.
        self.assertEqual(deliverable.auto_finalize_on, date(2012, 8, 6))
        self.assertEqual(deliverable.status, REVIEW)

    @freeze_time('2012-08-01 12:00:00')
    def test_final_revision_upload_dispute(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=DISPUTED, revisions=1)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['deliverable'], deliverable.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], GENERAL)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, DISPUTED)

    @freeze_time('2012-08-01 12:00:00')
    def test_final_revision_upload_escrow_disabled(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__seller=user, status=IN_PROGRESS, revisions=1, escrow_disabled=True, rating=ADULT,
        )
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['deliverable'], deliverable.id)
        self.assertEqual(response.data['owner'], user.username)
        self.assertEqual(response.data['rating'], ADULT)
        deliverable.refresh_from_db()
        self.assertIsNone(deliverable.auto_finalize_on)
        self.assertEqual(deliverable.status, COMPLETED)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @freeze_time('2012-08-01 12:00:00')
    def test_order_mark_complete(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=IN_PROGRESS, revisions=1)
        RevisionFactory.create(deliverable=deliverable)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/complete/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, REVIEW)
        self.assertEqual(deliverable.auto_finalize_on, date(2012, 8, 3))
        self.assertTrue(deliverable.final_uploaded)

    @freeze_time('2012-08-01 12:00:00')
    @patch('apps.sales.utils.finalize_deliverable')
    def test_order_mark_complete_trusted_finalize(self, mock_finalize):
        user = UserFactory.create(service_plan_paid_through=timezone.now() + relativedelta(months=1), trust_level=VERIFIED, service_plan=self.landscape)
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=IN_PROGRESS, revisions=1)
        RevisionFactory.create(deliverable=deliverable)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/complete/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertTrue(deliverable.trust_finalized)
        self.assertEqual(deliverable.auto_finalize_on, date(2012, 8, 3))
        self.assertTrue(deliverable.final_uploaded)

    def test_order_mark_completed_payment_pending(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=PAYMENT_PENDING, revisions=1, final_uploaded=False)
        RevisionFactory.create(deliverable=deliverable)
        deliverable.refresh_from_db()
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/complete/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, PAYMENT_PENDING)
        self.assertTrue(deliverable.final_uploaded)

    @freeze_time('2012-08-01 12:00:00')
    def test_order_mark_complete_escrow_disabled(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=IN_PROGRESS, revisions=1, escrow_disabled=True)
        RevisionFactory.create(deliverable=deliverable)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/complete/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, COMPLETED)
        self.assertIsNone(deliverable.auto_finalize_on)

    @freeze_time('2012-08-01 12:00:00')
    def test_order_mark_complete_no_revisions(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=IN_PROGRESS, revisions=1, escrow_disabled=True)
        self.assertEqual(deliverable.status, IN_PROGRESS)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/complete/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)

    @freeze_time('2012-08-01 12:00:00')
    def test_order_reopen(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__seller=user, status=REVIEW, revisions=1, auto_finalize_on=date(2012, 8, 6)
        )
        RevisionFactory.create(deliverable=deliverable)
        deliverable.refresh_from_db()
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/reopen/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        self.assertIsNone(deliverable.auto_finalize_on)

    @freeze_time('2012-08-01 12:00:00')
    def test_order_reopen_escrow_disabled(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__seller=user, status=COMPLETED, revisions=1, escrow_disabled=True
        )
        RevisionFactory.create(deliverable=deliverable)
        deliverable.refresh_from_db()
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/reopen/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        self.assertIsNone(deliverable.auto_finalize_on)

    def test_revision_upload_buyer_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__buyer=user, status=IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revision_upload_outsider_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(status=IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
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
        deliverable = DeliverableFactory.create(order__seller=user, status=IN_PROGRESS, rating=ADULT)
        asset = AssetFactory.create(uploaded_by=staffer)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['deliverable'], deliverable.id)
        self.assertEqual(response.data['owner'], staffer.username)
        self.assertEqual(response.data['rating'], ADULT)

    def test_revision_upload_final(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(
            order__seller=user, status=IN_PROGRESS, revisions=1, revisions_hidden=True, rating=ADULT,
        )
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, IN_PROGRESS)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'rating': ADULT,
                'final': True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, REVIEW)
        asset = AssetFactory.create(uploaded_by=user)
        response = self.client.post(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
            {
                'file': str(asset.id),
                'rating': ADULT,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.status, REVIEW)

    @data(IN_PROGRESS, NEW, PAYMENT_PENDING, REVIEW)
    def test_delete_revision(self, order_status):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=order_status)
        revision = RevisionFactory.create(deliverable=deliverable)
        self.assertEqual(deliverable.revision_set.all().count(), 1)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/{revision.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.revision_set.all().count(), 0)

    def test_delete_revision_reactivate(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=REVIEW, final_uploaded=True)
        revision = RevisionFactory.create(deliverable=deliverable)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/{revision.id}/',
        )
        deliverable.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deliverable.status, IN_PROGRESS)
        self.assertFalse(deliverable.final_uploaded)

    @data(COMPLETED, DISPUTED)
    def test_delete_revision_locked(self, order_status):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, status=order_status)
        revision = RevisionFactory.create(deliverable=deliverable)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/{revision.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_revision_buyer_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__buyer=user, status=IN_PROGRESS)
        revision = RevisionFactory.create(deliverable=deliverable)
        self.assertEqual(deliverable.revision_set.all().count(), 1)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/{revision.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.revision_set.all().count(), 1)

    def test_delete_revision_outsider_fail(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(status=IN_PROGRESS)
        revision = RevisionFactory.create(deliverable=deliverable)
        self.assertEqual(deliverable.revision_set.all().count(), 1)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/{revision.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.revision_set.all().count(), 1)

    def test_delete_revision_not_logged_in_fail(self):
        deliverable = DeliverableFactory.create(status=IN_PROGRESS)
        revision = RevisionFactory.create(deliverable=deliverable)
        self.assertEqual(deliverable.revision_set.all().count(), 1)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/{revision.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.revision_set.all().count(), 1)

    def test_delete_revision_staffer(self):
        user = UserFactory.create()
        staffer = UserFactory.create(is_staff=True)
        self.login(staffer)
        deliverable = DeliverableFactory.create(order__seller=user, status=IN_PROGRESS)
        revision = RevisionFactory.create(deliverable=deliverable)
        self.assertEqual(deliverable.revision_set.all().count(), 1)
        response = self.client.delete(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/{revision.id}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        deliverable.refresh_from_db()
        self.assertEqual(deliverable.revision_set.all().count(), 0)

    def test_list_revisions_hidden(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__buyer=user, revisions_hidden=True)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_revisions_unhidden(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__buyer=user, revisions_hidden=False)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_revisions_hidden_seller(self):
        user = UserFactory.create()
        self.login(user)
        deliverable = DeliverableFactory.create(order__seller=user, revisions_hidden=True)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/revisions/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_buyer(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(deliverable.order.buyer)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/rate/seller/',
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_seller(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        line_item = LineItemFactory.create(invoice=deliverable.invoice)
        self.login(deliverable.order.seller)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/rate/buyer/',
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_staff_buyer_end(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        line_item = LineItemFactory.create(invoice=deliverable.invoice)
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/rate/buyer/',
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_staff_seller_end(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(UserFactory.create(is_staff=True))
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/rate/seller/',
        )
        self.assertIsNone(response.data['stars'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_get_rating_outsider(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        self.login(UserFactory.create())
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/rate/seller/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_get_rating_not_logged_in(self):
        deliverable = DeliverableFactory.create(status=COMPLETED)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/rate/seller/',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
                'rating': ADULT,
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
                'rating': ADULT,
                'email': 'stuff@example.com',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable = Deliverable.objects.get(id=response.data['default_path']['params']['deliverableId'])
        self.assertEqual(deliverable.characters.all().count(), 0)
        self.assertEqual(deliverable.order.buyer.guest_email, 'stuff@example.com')

    def test_place_order_guest_user(self):
        user = create_guest_user('stuff@example.com')
        user.set_password('Test')
        user.save()
        product = ProductFactory.create()
        self.login(user)
        response = self.client.post(
            f'/api/sales/v1/account/{product.user.username}/products/{product.id}/order/',
            {
                'details': 'Draw me some porn!',
                'rating': ADULT,
                'email': 'stuff@example.com',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable = Deliverable.objects.get(id=response.data['default_path']['params']['deliverableId'])
        self.assertEqual(deliverable.characters.all().count(), 0)
        self.assertEqual(deliverable.order.buyer, user)

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
                'rating': ADULT,
                'email': 'stuff2@example.com',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deliverable = Deliverable.objects.get(id=response.data['default_path']['params']['deliverableId'])
        self.assertEqual(deliverable.characters.all().count(), 0)
        self.assertEqual(deliverable.order.buyer.guest_email, 'stuff2@example.com')
        user.refresh_from_db()
        self.assertNotEqual(deliverable.order.buyer, user)

    def test_character_list(self):
        deliverable = DeliverableFactory.create()
        character = CharacterFactory.create()
        deliverable.characters.add(character)
        self.login(deliverable.order.buyer)
        response = self.client.get(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/characters/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['character']['id'], character.id)

    def test_adjust_task_weight(self):
        deliverable = DeliverableFactory.create(adjustment_task_weight=0)
        self.login(deliverable.order.seller)
        response = self.client.patch(
            f'/api/sales/v1/order/{deliverable.order.id}/deliverables/{deliverable.id}/',
            {'adjustment_task_weight': 4},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['adjustment_task_weight'], 4)