from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import localdate
from rest_framework import status
from rest_framework.test import APITestCase

from expense.models import Account, Expense


class DashboardEndpointTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="dashboard-user",
            email="dashboard@example.com",
            password="test-password",
        )
        self.account = Account.objects.create(
            owner=self.user,
            name="Cash",
            account_type=Account.AccountType.CASH,
            opening_balance=10000,
        )
        self.client.force_authenticate(self.user)

    def test_summary_endpoint_returns_dashboard_payload(self):
        response = self.client.get(reverse("dashboard:summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_month"]["total_spend"], 0)
        self.assertEqual(response.data["last_month"]["total_spend"], 0)

    def test_trends_endpoint_returns_daily_expenses(self):
        response = self.client.get(reverse("dashboard:trends"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("daily_expenses", response.data)
        self.assertGreater(len(response.data["daily_expenses"]), 0)

    def test_categories_endpoint_returns_category_breakdown(self):
        response = self.client.get(reverse("dashboard:categories"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_spend"], 0)
        self.assertEqual(response.data["breakdown"], [])

    def test_summary_ranks_top_expenses_by_converted_amount(self):
        Expense.objects.create(
            owner=self.user,
            account=self.account,
            amount=1000,
            currency="JPY",
            exchange_rate=0.01,
            converted_amount=10,
            date=localdate(),
            notes="Large raw amount",
        )
        highest_converted = Expense.objects.create(
            owner=self.user,
            account=self.account,
            amount=100,
            currency="USD",
            exchange_rate=2,
            converted_amount=200,
            date=localdate(),
            notes="Largest base-currency expense",
        )

        response = self.client.get(reverse("dashboard:summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["top_expenses"][0]["id"],
            str(highest_converted.id),
        )


class DashboardRecentTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="recent-user",
            email="recent@example.com",
            password="test-password",
        )
        self.account = Account.objects.create(
            owner=self.user,
            name="Cash",
            account_type=Account.AccountType.CASH,
        )
        self.client.force_authenticate(self.user)

    def _create_expense(self, notes="Test"):
        return Expense.objects.create(
            owner=self.user, account=self.account,
            amount=Decimal("100"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("100"),
            date=localdate(), notes=notes,
        )

    def test_recent_endpoint_returns_empty_list_with_no_expenses(self):
        response = self.client.get(reverse("dashboard:recent"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["recent_transactions"], [])

    def test_recent_endpoint_returns_transactions(self):
        self._create_expense(notes="My purchase")
        response = self.client.get(reverse("dashboard:recent"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["recent_transactions"]), 1)
        self.assertEqual(response.data["recent_transactions"][0]["notes"], "My purchase")

    def test_recent_endpoint_includes_expected_fields(self):
        self._create_expense()
        response = self.client.get(reverse("dashboard:recent"))
        transaction = response.data["recent_transactions"][0]
        for field in ("id", "amount", "currency", "converted_amount", "date", "notes"):
            self.assertIn(field, transaction)

    def test_recent_endpoint_returns_at_most_10_transactions(self):
        for i in range(15):
            self._create_expense(notes=f"Expense {i}")
        response = self.client.get(reverse("dashboard:recent"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["recent_transactions"]), 10)

    def test_recent_endpoint_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("dashboard:recent"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardInsightsTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="insights-user",
            email="insights@example.com",
            password="test-password",
        )
        self.client.force_authenticate(self.user)

    def test_insights_endpoint_returns_200(self):
        response = self.client.get(reverse("dashboard:insights"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_insights_response_has_period_and_insights_keys(self):
        response = self.client.get(reverse("dashboard:insights"))
        self.assertIn("period", response.data)
        self.assertIn("insights", response.data)

    def test_insights_contains_at_least_one_insight(self):
        response = self.client.get(reverse("dashboard:insights"))
        self.assertGreater(len(response.data["insights"]), 0)

    def test_each_insight_has_required_fields(self):
        response = self.client.get(reverse("dashboard:insights"))
        for insight in response.data["insights"]:
            self.assertIn("rule", insight)
            self.assertIn("message", insight)
            self.assertIn("severity", insight)

    def test_insights_endpoint_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("dashboard:insights"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
