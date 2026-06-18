import datetime
import io
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.timezone import localdate
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import Account, Category, Expense, Notification, RecurringExpense
from .services import generate_due_recurring_expenses, process_expense_notifications


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


class ExpenseCRUDTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="crud-user",
            email="crud@example.com",
            password="pass",
            base_currency="INR",
        )
        self.other_user = get_user_model().objects.create_user(
            username="crud-other",
            email="crudother@example.com",
            password="pass",
        )
        self.account = Account.objects.create(
            owner=self.user, name="Cash", account_type=Account.AccountType.CASH,
        )
        self.client.force_authenticate(self.user)

    def _payload(self, **overrides):
        data = {
            "amount": "100.00",
            "currency": "INR",
            "account": str(self.account.id),
            "date": localdate().isoformat(),
            "notes": "Test expense",
        }
        data.update(overrides)
        return data

    def _create_expense(self, **kwargs):
        defaults = {
            "owner": self.user,
            "account": self.account,
            "amount": Decimal("100"),
            "currency": "INR",
            "exchange_rate": Decimal("1"),
            "converted_amount": Decimal("100"),
            "date": localdate(),
        }
        defaults.update(kwargs)
        return Expense.objects.create(**defaults)

    def test_create_expense_returns_201(self):
        response = self.client.post(
            reverse("expense:api-expenses"), self._payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.filter(owner=self.user).count(), 1)

    def test_create_expense_sets_converted_amount_for_same_currency(self):
        response = self.client.post(
            reverse("expense:api-expenses"),
            self._payload(amount="250.00"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.get(owner=self.user)
        self.assertEqual(expense.converted_amount, Decimal("250.00"))

    def test_expense_list_returns_only_owner_expenses(self):
        other_account = Account.objects.create(
            owner=self.other_user, name="Other", account_type=Account.AccountType.CASH,
        )
        Expense.objects.create(
            owner=self.other_user, account=other_account,
            amount=Decimal("50"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("50"),
            date=localdate(),
        )
        self._create_expense()
        response = self.client.get(reverse("expense:api-expenses"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_expense_detail_returns_404_for_other_users_expense(self):
        other_account = Account.objects.create(
            owner=self.other_user, name="Other", account_type=Account.AccountType.CASH,
        )
        expense = Expense.objects.create(
            owner=self.other_user, account=other_account,
            amount=Decimal("100"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("100"),
            date=localdate(),
        )
        response = self.client.get(
            reverse("expense:api-expense-detail", kwargs={"pk": str(expense.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_expense_notes(self):
        expense = self._create_expense(notes="Original")
        response = self.client.patch(
            reverse("expense:api-expense-detail", kwargs={"pk": str(expense.id)}),
            {"notes": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.notes, "Updated")

    def test_delete_expense_returns_204(self):
        expense = self._create_expense()
        response = self.client.delete(
            reverse("expense:api-expense-detail", kwargs={"pk": str(expense.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Expense.objects.filter(pk=expense.id).exists())

    def test_future_date_is_rejected(self):
        future = (localdate() + datetime.timedelta(days=1)).isoformat()
        response = self.client.post(
            reverse("expense:api-expenses"), self._payload(date=future), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_amount_is_rejected(self):
        response = self.client.post(
            reverse("expense:api-expenses"), self._payload(amount="0"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AccountCRUDTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="acct-user", email="acct@example.com", password="pass",
        )
        self.client.force_authenticate(self.user)

    def test_create_account_returns_201(self):
        response = self.client.post(
            reverse("expense:api-accounts"),
            {"name": "Savings", "account_type": "bank", "opening_balance": "5000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_account_name_returns_400(self):
        Account.objects.create(
            owner=self.user, name="Savings", account_type=Account.AccountType.BANK,
        )
        response = self.client.post(
            reverse("expense:api-accounts"),
            {"name": "Savings", "account_type": "bank"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_balance_reflects_expenses(self):
        account = Account.objects.create(
            owner=self.user, name="Wallet", account_type=Account.AccountType.CASH,
            opening_balance=Decimal("1000"),
        )
        Expense.objects.create(
            owner=self.user, account=account,
            amount=Decimal("300"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("300"),
            date=localdate(),
        )
        response = self.client.get(reverse("expense:api-accounts"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        account_data = response.data["results"][0]
        self.assertEqual(
            Decimal(str(account_data["current_balance"])), Decimal("700.00")
        )

    def test_delete_account_with_linked_expenses_returns_409(self):
        account = Account.objects.create(
            owner=self.user, name="Linked", account_type=Account.AccountType.CASH,
        )
        Expense.objects.create(
            owner=self.user, account=account,
            amount=Decimal("50"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("50"),
            date=localdate(),
        )
        response = self.client.delete(
            reverse("expense:api-account-detail", kwargs={"pk": str(account.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Account.objects.filter(pk=account.id).exists())

    def test_delete_empty_account_returns_204(self):
        account = Account.objects.create(
            owner=self.user, name="Empty", account_type=Account.AccountType.CASH,
        )
        response = self.client.delete(
            reverse("expense:api-account-detail", kwargs={"pk": str(account.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Account.objects.filter(pk=account.id).exists())


class CategoryTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cat-user", email="cat@example.com", password="pass",
        )
        self.other_user = get_user_model().objects.create_user(
            username="cat-other", email="catother@example.com", password="pass",
        )
        self.client.force_authenticate(self.user)

    def test_list_includes_global_categories(self):
        Category.objects.create(name="Food", owner=None)
        response = self.client.get(reverse("expense:api-categories"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [c["name"] for c in response.data["results"]]
        self.assertIn("Food", names)

    def test_list_does_not_include_other_user_categories(self):
        Category.objects.create(name="Other Category", owner=self.other_user)
        response = self.client.get(reverse("expense:api-categories"))
        names = [c["name"] for c in response.data["results"]]
        self.assertNotIn("Other Category", names)

    def test_create_category_assigns_owner(self):
        response = self.client.post(
            reverse("expense:api-categories"), {"name": "Travel"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.get(name="Travel").owner, self.user)

    def test_cannot_delete_global_category(self):
        global_cat = Category.objects.create(name="Bills", owner=None)
        response = self.client.delete(
            reverse("expense:api-category-detail", kwargs={"pk": str(global_cat.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Category.objects.filter(pk=global_cat.id).exists())

    def test_can_delete_own_category(self):
        cat = Category.objects.create(name="Personal", owner=self.user)
        response = self.client.delete(
            reverse("expense:api-category-detail", kwargs={"pk": str(cat.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=cat.id).exists())


class RecurringExpenseCRUDTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="recur-crud",
            email="recurcrud@example.com",
            password="pass",
            base_currency="INR",
        )
        self.other_user = get_user_model().objects.create_user(
            username="recur-other",
            email="recurother@example.com",
            password="pass",
        )
        self.account = Account.objects.create(
            owner=self.user, name="Bank", account_type=Account.AccountType.BANK,
        )
        self.client.force_authenticate(self.user)

    def _payload(self, **overrides):
        today = localdate()
        data = {
            "amount": "200.00",
            "currency": "INR",
            "account": str(self.account.id),
            "notes": "Subscription",
            "frequency": RecurringExpense.Frequency.MONTHLY,
            "start_date": today.isoformat(),
            "next_run_date": today.isoformat(),
        }
        data.update(overrides)
        return data

    def test_create_recurring_expense_returns_201(self):
        response = self.client.post(
            reverse("expense:api-recurring"), self._payload(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_returns_only_owner_recurring_expenses(self):
        today = localdate()
        other_account = Account.objects.create(
            owner=self.other_user, name="OtherBank", account_type=Account.AccountType.BANK,
        )
        RecurringExpense.objects.create(
            owner=self.other_user, account=other_account,
            amount=Decimal("100"), currency="INR",
            frequency=RecurringExpense.Frequency.MONTHLY,
            start_date=today, next_run_date=today,
        )
        RecurringExpense.objects.create(
            owner=self.user, account=self.account,
            amount=Decimal("200"), currency="INR",
            frequency=RecurringExpense.Frequency.MONTHLY,
            start_date=today, next_run_date=today,
        )
        response = self.client.get(reverse("expense:api-recurring"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_deactivate_recurring_expense(self):
        today = localdate()
        recurring = RecurringExpense.objects.create(
            owner=self.user, account=self.account,
            amount=Decimal("300"), currency="INR",
            frequency=RecurringExpense.Frequency.MONTHLY,
            start_date=today, next_run_date=today,
        )
        response = self.client.patch(
            reverse("expense:api-recurring-detail", kwargs={"pk": str(recurring.id)}),
            {"is_active": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recurring.refresh_from_db()
        self.assertFalse(recurring.is_active)

    def test_generation_does_not_produce_duplicate_on_second_run(self):
        today = localdate()
        RecurringExpense.objects.create(
            owner=self.user, account=self.account,
            amount=Decimal("100"), currency="INR",
            frequency=RecurringExpense.Frequency.MONTHLY,
            start_date=today, next_run_date=today,
        )
        first_run = generate_due_recurring_expenses(run_date=today)
        second_run = generate_due_recurring_expenses(run_date=today)
        self.assertEqual(first_run, 1)
        self.assertEqual(second_run, 0)
        self.assertEqual(Expense.objects.filter(owner=self.user).count(), 1)


class NotificationTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="notif-user", email="notif@example.com", password="pass",
        )
        self.account = Account.objects.create(
            owner=self.user, name="Wallet", account_type=Account.AccountType.CASH,
        )
        self.client.force_authenticate(self.user)

    def _create_notification(self, **overrides):
        kwargs = {
            "owner": self.user,
            "notification_type": Notification.NotificationType.LARGE_EXPENSE,
            "title": "Test",
            "message": "Test message",
        }
        kwargs.update(overrides)
        return Notification.objects.create(**kwargs)

    def test_list_returns_user_notifications(self):
        self._create_notification()
        response = self.client.get(reverse("expense:api-notifications"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_is_read_false(self):
        self._create_notification(is_read=False, title="Unread")
        self._create_notification(is_read=True, title="Read")
        response = self.client.get(
            reverse("expense:api-notifications"), {"is_read": "false"}
        )
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Unread")

    def test_mark_notification_as_read(self):
        notif = self._create_notification(is_read=False)
        response = self.client.put(
            reverse("expense:api-notification-read", kwargs={"pk": str(notif.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
        self.assertIsNotNone(notif.read_at)

    def test_mark_already_read_notification_is_idempotent(self):
        notif = self._create_notification(is_read=True)
        response = self.client.put(
            reverse("expense:api-notification-read", kwargs={"pk": str(notif.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_read"])

    def test_overspending_notification_deduplication(self):
        expense1 = Expense.objects.create(
            owner=self.user, account=self.account,
            amount=Decimal("100"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("100"),
            date=localdate(),
        )
        expense2 = Expense.objects.create(
            owner=self.user, account=self.account,
            amount=Decimal("200"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("200"),
            date=localdate(),
        )
        process_expense_notifications(expense1)
        process_expense_notifications(expense2)
        overspending_count = Notification.objects.filter(
            owner=self.user,
            notification_type=Notification.NotificationType.OVERSPENDING,
        ).count()
        self.assertEqual(overspending_count, 1)


class ExportTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="export-user", email="export@example.com", password="pass",
        )
        self.account = Account.objects.create(
            owner=self.user, name="Export Wallet", account_type=Account.AccountType.CASH,
        )
        Expense.objects.create(
            owner=self.user, account=self.account,
            amount=Decimal("500"), currency="INR",
            exchange_rate=Decimal("1"), converted_amount=Decimal("500"),
            date=localdate(), notes="Export test",
        )
        self.client.force_authenticate(self.user)

    def test_csv_export_returns_correct_content_type(self):
        response = self.client.get(
            reverse("expense:api-export-query"), {"type": "csv"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/csv", response["Content-Type"])

    def test_excel_export_returns_correct_content_type(self):
        response = self.client.get(
            reverse("expense:api-export-query"), {"type": "excel"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("application/ms-excel", response["Content-Type"])

    def test_pdf_export_returns_correct_content_type(self):
        response = self.client.get(
            reverse("expense:api-export-query"), {"type": "pdf"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("application/pdf", response["Content-Type"])

    def test_invalid_export_type_returns_400(self):
        response = self.client.get(
            reverse("expense:api-export-query"), {"type": "xml"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReceiptValidationTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="receipt-user",
            email="receipt@example.com",
            password="pass",
            base_currency="INR",
        )
        self.account = Account.objects.create(
            owner=self.user, name="Receipt Wallet", account_type=Account.AccountType.CASH,
        )
        self.client.force_authenticate(self.user)

    def _base_payload(self):
        return {
            "amount": "100.00",
            "currency": "INR",
            "account": str(self.account.id),
            "date": localdate().isoformat(),
            "notes": "receipt test",
        }

    @staticmethod
    def _make_png_bytes():
        buf = io.BytesIO()
        Image.new("RGB", (10, 10), color="white").save(buf, format="PNG")
        return buf.getvalue()

    def test_valid_png_receipt_is_accepted(self):
        file = SimpleUploadedFile("test.png", self._make_png_bytes(), content_type="image/png")
        response = self.client.post(
            reverse("expense:api-expenses"),
            {**self._base_payload(), "receipt": file},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_image_file_is_rejected(self):
        file = SimpleUploadedFile(
            "fake.png", b"this is not an image", content_type="image/png"
        )
        response = self.client.post(
            reverse("expense:api-expenses"),
            {**self._base_payload(), "receipt": file},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_oversized_file_is_rejected(self):
        oversized = b"x" * (5 * 1024 * 1024 + 1)
        file = SimpleUploadedFile("big.png", oversized, content_type="image/png")
        response = self.client.post(
            reverse("expense:api-expenses"),
            {**self._base_payload(), "receipt": file},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
