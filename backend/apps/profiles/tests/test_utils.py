from unittest.mock import Mock

from django.test import TestCase
from django.utils.datetime_safe import date
from freezegun import freeze_time

from apps.lib.abstract_models import GENERAL, ADULT
from apps.lib.test_resources import APITestCase
from apps.profiles.tests.factories import UserFactory
from apps.profiles.utils import extend_portrait, extend_landscape, empty_user


class ExtendPremiumTest(TestCase):
    @freeze_time('2018-08-01')
    def test_extend_portrait_from_none(self):
        user = UserFactory.create()
        self.assertIsNone(user.portrait_paid_through)
        extend_portrait(user, months=1)
        self.assertEqual(user.portrait_paid_through, date(2018, 9, 1))
        self.assertIsNone(user.landscape_paid_through)

    @freeze_time('2018-08-01')
    def test_extend_portrait_from_past(self):
        user = UserFactory.create(portrait_paid_through=date(2018, 7, 5))
        extend_portrait(user, months=1)
        self.assertEqual(user.portrait_paid_through, date(2018, 9, 1))
        self.assertIsNone(user.landscape_paid_through)

    @freeze_time('2018-08-01')
    def test_extend_portrait_from_future(self):
        user = UserFactory.create(portrait_paid_through=date(2018, 9, 5))
        extend_portrait(user, months=1)
        self.assertEqual(user.portrait_paid_through, date(2018, 10, 5))
        self.assertIsNone(user.landscape_paid_through)

    @freeze_time('2018-08-01')
    def test_extend_landscape_from_none(self):
        user = UserFactory.create()
        self.assertIsNone(user.landscape_paid_through)
        extend_landscape(user, months=1)
        self.assertEqual(user.landscape_paid_through, date(2018, 9, 1))
        self.assertEqual(user.portrait_paid_through, date(2018, 9, 1))

    @freeze_time('2018-08-01')
    def test_extend_landscape_from_past(self):
        user = UserFactory.create(landscape_paid_through=date(2018, 7, 5))
        extend_landscape(user, months=1)
        self.assertEqual(user.portrait_paid_through, date(2018, 9, 1))
        self.assertEqual(user.landscape_paid_through, date(2018, 9, 1))

    @freeze_time('2018-08-01')
    def test_extend_landscape_from_future(self):
        user = UserFactory.create(landscape_paid_through=date(2018, 9, 5))
        extend_landscape(user, months=1)
        self.assertEqual(user.landscape_paid_through, date(2018, 10, 5))
        self.assertEqual(user.portrait_paid_through, date(2018, 10, 5))

    @freeze_time('2018-08-01')
    def test_extend_landscape_portrait_lags(self):
        user = UserFactory.create(landscape_paid_through=date(2018, 9, 5), portrait_paid_through=date(2018, 1, 1))
        extend_landscape(user, months=1)
        self.assertEqual(user.landscape_paid_through, date(2018, 10, 5))
        self.assertEqual(user.portrait_paid_through, date(2018, 10, 5))

    @freeze_time('2018-08-01')
    def test_extend_landscape_portrait_leads(self):
        user = UserFactory.create(landscape_paid_through=date(2018, 8, 5), portrait_paid_through=date(2018, 10, 1))
        extend_landscape(user, months=1)
        self.assertEqual(user.landscape_paid_through, date(2018, 9, 5))
        self.assertEqual(user.portrait_paid_through, date(2018, 10, 1))


class TestEmptyUser(APITestCase):
    def test_empty_user(self):
        request = Mock()
        request.sfw_mode = True
        request.rating = ADULT
        request.max_rating = GENERAL
        self.assertEqual(
            empty_user(request), {'blacklist': [], 'rating': ADULT, 'sfw_mode': True, 'username': '_'},
        )