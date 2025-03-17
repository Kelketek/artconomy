from decimal import Decimal
from unittest.mock import patch

from apps.lib.test_resources import (
    APITestCase,
    MethodAccessMixin,
    PermissionsTestCase,
    SignalsDisabledMixin,
)
from apps.lib.tests.test_utils import create_staffer
from apps.profiles.tests.factories import UserFactory
from apps.sales.constants import (
    PAYOUT_ACCOUNT,
    CARD,
    CASH_WITHDRAW,
    ESCROW,
    ESCROW_HOLD,
    ESCROW_RELEASE,
    HOLDINGS,
)
from apps.sales.tests.factories import CreditCardTokenFactory, TransactionRecordFactory
from apps.sales.utils import PENDING
from apps.sales.views.main import AccountHistory
from moneyed import Money

history_passes = {**MethodAccessMixin.passes, "get": ["user", "staff"]}


class TestAccountHistoryPermissions(PermissionsTestCase, MethodAccessMixin):
    passes = history_passes
    view_class = AccountHistory
    staff_powers = ["view_financials"]


class TestHistoryViews(SignalsDisabledMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(username="Fox")
        self.user2 = UserFactory.create(username="Amber")
        card = CreditCardTokenFactory.create()
        [
            TransactionRecordFactory.create(
                amount=Money(amount, "USD"),
                category=ESCROW_HOLD,
                payer=self.user2,
                payee=self.user,
                source=CARD,
                destination=ESCROW,
                card=card,
            )
            for amount in ("5.00", "10.00", "15.00")
        ]
        [
            TransactionRecordFactory.create(
                amount=Money(amount, "USD"),
                payer=self.user,
                payee=self.user,
                source=ESCROW,
                destination=HOLDINGS,
                category=ESCROW_RELEASE,
            )
            for amount in ("5.00", "10.00")
        ]
        [
            TransactionRecordFactory.create(
                amount=Money(amount, "USD"),
                payer=self.user,
                payee=self.user,
                card=None,
                source=HOLDINGS,
                destination=PAYOUT_ACCOUNT,
                category=CASH_WITHDRAW,
            )
            for amount in (1, 2, 3, 4)
        ]

    def test_purchase_history(self):
        self.login(self.user)
        response = self.client.get(
            f"/api/sales/v1/account/{self.user.username}/transactions/?account=300"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)
        self.login(self.user2)
        response = self.client.get(
            f"/api/sales/v1/account/{self.user2.username}/transactions/?account=300"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)
        for result in response.data["results"]:
            self.assertTrue(result["card"]["id"])

    def test_escrow_history(self):
        self.login(self.user)
        response = self.client.get(
            f"/api/sales/v1/account/{self.user.username}/transactions/?account=302"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)
        for result in response.data["results"]:
            self.assertIsNone(result["card"])
        self.login(self.user2)
        response = self.client.get(
            f"/api/sales/v1/account/{self.user2.username}/transactions/?account=302"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    def test_available_history(self):
        self.login(self.user)
        response = self.client.get(
            f"/api/sales/v1/account/{self.user.username}/transactions/?account=303"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 6)
        self.login(self.user2)
        response = self.client.get(
            f"/api/sales/v1/account/{self.user2.username}/transactions/?account=303"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)


class TestAccountBalance(APITestCase):
    @patch("apps.sales.serializers.account_balance")
    def test_account_balance(self, mock_account_balance):
        user = UserFactory.create()
        self.login(user)
        mock_account_balance.side_effect = mock_balance
        response = self.client.get(
            "/api/sales/v1/account/{}/balance/".format(user.username)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["available"], "100.00")
        self.assertEqual(response.data["escrow"], "50.00")

    @patch("apps.sales.serializers.account_balance")
    def test_account_balance_staff(self, mock_account_balance):
        user = UserFactory.create()
        staffer = create_staffer("view_financials")
        self.login(staffer)
        mock_account_balance.side_effect = mock_balance
        response = self.client.get(
            "/api/sales/v1/account/{}/balance/".format(user.username)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["available"], "100.00")
        self.assertEqual(response.data["escrow"], "50.00")

    def test_account_balance_wrong_user(self):
        user = UserFactory.create()
        user2 = UserFactory.create()
        self.login(user2)
        response = self.client.get(
            "/api/sales/v1/account/{}/balance/".format(user.username)
        )
        self.assertEqual(response.status_code, 403)

    def test_account_balance_not_logged_in(self):
        user = UserFactory.create()
        response = self.client.get(
            "/api/sales/v1/account/{}/balance/".format(user.username)
        )
        self.assertEqual(response.status_code, 403)


def mock_balance(obj, account_type, status_filter=None):
    if status_filter == PENDING:
        return Decimal("10.00")
    if account_type == HOLDINGS:
        return Decimal("100.00")
    return Decimal("50.00")
