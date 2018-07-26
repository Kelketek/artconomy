from decimal import Decimal

from django.test import TestCase, override_settings

from apps.profiles.tests.factories import UserFactory


class TestUser(TestCase):
    @override_settings(STANDARD_PERCENTAGE_FEE=Decimal('1'), STANDARD_STATIC_FEE=Decimal('1.00'))
    def test_standard_fees(self):
        user = UserFactory.create()
        self.assertEqual(user.static_fee, Decimal('1.00'))
        self.assertEqual(user.percentage_fee, Decimal('1'))
