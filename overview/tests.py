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
