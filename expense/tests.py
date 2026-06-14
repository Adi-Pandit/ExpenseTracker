from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import localdate
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import Account, Expense, Notification, RecurringExpense
from .services import generate_due_recurring_expenses


class RecurringExpenseEndpointTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="recurring-user",
            email="recurring@example.com",
            password="test-password",
        )
        self.account = Account.objects.create(
            owner=self.user,
            name="Primary account",
            account_type=Account.AccountType.BANK,
            opening_balance=10000,
        )
        self.client.force_authenticate(self.user)

    def test_create_recurring_rule_does_not_process_expense_notifications(self):
        today = localdate()

        response = self.client.post(
            reverse("expense:api-recurring"),
            {
                "amount": 5000,
                "currency": self.user.base_currency,
                "account": str(self.account.id),
                "notes": "Monthly rent",
                "frequency": RecurringExpense.Frequency.MONTHLY,
                "start_date": today.isoformat(),
                "next_run_date": today.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RecurringExpense.objects.filter(owner=self.user).count(), 1)
        self.assertFalse(Notification.objects.filter(owner=self.user).exists())

    def test_generated_recurring_expense_processes_notifications(self):
        today = localdate()
        RecurringExpense.objects.create(
            owner=self.user,
            account=self.account,
            amount=5000,
            currency=self.user.base_currency,
            notes="Monthly rent",
            frequency=RecurringExpense.Frequency.MONTHLY,
            start_date=today,
            next_run_date=today,
        )

        created_count = generate_due_recurring_expenses(run_date=today)

        self.assertEqual(created_count, 1)
        expense = Expense.objects.get(owner=self.user)
        notification_types = set(
            Notification.objects.filter(owner=self.user, expense=expense).values_list(
                "notification_type", flat=True
            )
        )
        self.assertEqual(
            notification_types,
            {
                Notification.NotificationType.LARGE_EXPENSE,
                Notification.NotificationType.OVERSPENDING,
            },
        )


class ExpenseNotificationEndpointTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="expense-user",
            email="expense@example.com",
            password="test-password",
        )
        self.account = Account.objects.create(
            owner=self.user,
            name="Cash",
            account_type=Account.AccountType.CASH,
            opening_balance=10000,
        )
        self.client.force_authenticate(self.user)

    @patch("expense.serializers.convert_amount", return_value=(1.0, 1500.0))
    def test_create_expense_processes_notifications(self, _convert_amount):
        response = self.client.post(
            reverse("expense:api-expenses"),
            {
                "amount": 1500,
                "currency": self.user.base_currency,
                "account": str(self.account.id),
                "date": localdate().isoformat(),
                "notes": "Large purchase",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.get(owner=self.user)
        notification_types = set(
            Notification.objects.filter(owner=self.user, expense=expense).values_list(
                "notification_type", flat=True
            )
        )
        self.assertEqual(
            notification_types,
            {
                Notification.NotificationType.LARGE_EXPENSE,
                Notification.NotificationType.OVERSPENDING,
            },
        )


class FilterValidationEndpointTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="filter-user",
            email="filter@example.com",
            password="test-password",
        )
        self.client.force_authenticate(self.user)

    def assert_bad_request(self, url, params):
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expense_filters_reject_invalid_uuid(self):
        self.assert_bad_request(
            reverse("expense:api-expenses"),
            {"account": "not-a-uuid"},
        )

    def test_expense_filters_reject_invalid_date(self):
        self.assert_bad_request(
            reverse("expense:api-expenses"),
            {"start_date": "2026-99-99"},
        )

    def test_export_filters_reject_invalid_amount(self):
        self.assert_bad_request(
            reverse("expense:api-export-query"),
            {"type": "csv", "min_amount": "not-a-number"},
        )

    def test_account_filters_reject_invalid_balance(self):
        self.assert_bad_request(
            reverse("expense:api-accounts"),
            {"min_balance": "not-a-number"},
        )

    def test_recurring_filters_reject_invalid_boolean(self):
        self.assert_bad_request(
            reverse("expense:api-recurring"),
            {"is_active": "maybe"},
        )

    def test_notification_filters_reject_invalid_type(self):
        self.assert_bad_request(
            reverse("expense:api-notifications"),
            {"notification_type": "unknown"},
        )

    def test_expense_filters_reject_reversed_ranges(self):
        self.assert_bad_request(
            reverse("expense:api-expenses"),
            {
                "start_date": "2026-06-10",
                "end_date": "2026-06-01",
                "min_amount": 100,
                "max_amount": 10,
            },
        )
