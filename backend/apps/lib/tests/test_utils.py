from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from apps.lib.models import FAVORITE, Notification
from apps.lib.utils import notify, recall_notification
from apps.profiles.models import ImageAsset
from apps.profiles.tests.factories import ImageAssetFactory


class NotificationsTestCase(TestCase):
    def test_basic(self):
        # Implicitly creates subscription for uploader.
        asset = ImageAssetFactory.create()
        notify(FAVORITE, target=asset, data={'users': []})
        notification = Notification.objects.get(user=asset.uploaded_by)
        self.assertEqual(notification.event.type, FAVORITE)
        self.assertEqual(notification.read, False)
        self.assertEqual(notification.event.content_type, ContentType.objects.get_for_model(ImageAsset))
        self.assertEqual(notification.event.object_id, asset.id)
        self.assertEqual(notification.event.data, {'users': []})

    @freeze_time('2018-01-01')
    def test_unique(self):
        asset = ImageAssetFactory.create()
        notify(FAVORITE, target=asset, data={'users': []})
        notification = Notification.objects.get(user=asset.uploaded_by)
        event = notification.event
        notification.read = True
        notification.save()
        self.assertEqual(event.date.year, 2018)
        self.assertEqual(event.data, {'users': []})
        with freeze_time('2012-08-04'):
            notify(FAVORITE, target=asset, data={'users': [1, 2, 3]}, unique=True)
            event.refresh_from_db()
            notification.refresh_from_db()
            self.assertEqual(event.date.year, 2018)
            self.assertEqual(event.data, {'users': [1, 2, 3]})
            self.assertTrue(notification.read)

    @freeze_time('2018-01-01')
    def test_unique_mark_unread(self):
        asset = ImageAssetFactory.create()
        notify(FAVORITE, target=asset, data={'users': []})
        notification = Notification.objects.get(user=asset.uploaded_by)
        notification.read = True
        notification.save()
        event = notification.event
        self.assertEqual(event.date.year, 2018)
        self.assertEqual(event.data, {'users': []})
        with freeze_time('2012-08-04'):
            notify(FAVORITE, target=asset, data={'users': [1, 2, 3]}, unique=True, mark_unread=True)
            event.refresh_from_db()
            notification.refresh_from_db()
            self.assertEqual(event.date.year, 2012)
            self.assertEqual(event.data, {'users': [1, 2, 3]})
            self.assertFalse(notification.read)

    def test_unique_data(self):
        asset = ImageAssetFactory.create()
        notify(FAVORITE, target=asset, data={'users': []})
        notification = Notification.objects.get(user=asset.uploaded_by)
        event = notification.event
        notification.read = True
        notification.save()
        # Unique data primarily for singleton events.
        event.recalled = True
        event.save()
        self.assertEqual(event.date.year, 2018)
        self.assertEqual(event.data, {'users': []})
        with freeze_time('2012-08-04'):
            notify(FAVORITE, target=asset, data={'users': []}, unique_data=True)
            event.refresh_from_db()
            notification.refresh_from_db()
            self.assertEqual(event.date.year, 2018)
            self.assertEqual(event.data, {'users': []})
            self.assertTrue(notification.read)
            self.assertFalse(event.recalled)

    def test_unique_data_no_update_nonmatch(self):
        asset = ImageAssetFactory.create()
        notify(FAVORITE, target=asset, data={'users': []})
        notification = Notification.objects.get(user=asset.uploaded_by)
        event = notification.event
        notification.read = True
        notification.save()
        self.assertEqual(event.date.year, 2018)
        self.assertEqual(event.data, {'users': []})
        with freeze_time('2012-08-04'):
            notify(FAVORITE, target=asset, data={'users': [1, 2, 3]}, unique_data=True)
            event.refresh_from_db()
            notification.refresh_from_db()
            self.assertEqual(event.date.year, 2018)
            self.assertEqual(event.data, {'users': []})
            self.assertTrue(notification.read)
        notification2 = Notification.objects.exclude(id=event.id)[0]
        self.assertEqual(notification2.event.data, {'users': [1, 2, 3]})
        self.assertEqual(notification2.event.date.year, 2012)

    @freeze_time('2018-01-01')
    def test_time_override(self):
        asset = ImageAssetFactory.create()
        notify(FAVORITE, target=asset, data={'users': []})
        notification = Notification.objects.get(user=asset.uploaded_by)
        event = notification.event
        notification.read = True
        notification.save()
        self.assertEqual(event.date.year, 2018)
        self.assertEqual(event.data, {'users': []})
        with freeze_time('2012-08-04'):
            notify(
                FAVORITE, target=asset, data={'users': [1, 2, 3]}, unique=True,
                time_override=timezone.now().replace(day=10)
            )
            event.refresh_from_db()
            notification.refresh_from_db()
            self.assertEqual(event.date.year, 2012)
            self.assertEqual(event.date.day, 10)
            self.assertEqual(event.data, {'users': [1, 2, 3]})
            self.assertTrue(notification.read)

    def test_recall_notification(self):
        asset = ImageAssetFactory.create()
        notify(FAVORITE, target=asset, data={'users': []})
        notification = Notification.objects.get(user=asset.uploaded_by)
        self.assertEqual(notification.event.recalled, False)
        recall_notification(FAVORITE, target=asset)
        notification.event.refresh_from_db()
        self.assertEqual(notification.event.recalled, True)
