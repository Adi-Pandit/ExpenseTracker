from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now
from uuid_extensions import uuid7


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_category_name_per_owner",
            ),
            models.UniqueConstraint(
                fields=["name"],
                name="unique_global_category_name",
                condition=models.Q(owner__isnull=True),
            )
        ]

    def __str__(self):
        return self.name


class Account(models.Model):
    class AccountType(models.TextChoices):
        CASH = "cash", "Cash"
        BANK = "bank", "Bank"
        CREDIT_CARD = "credit_card", "Credit Card"

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    opening_balance = models.FloatField(default=0)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_account_name_per_owner",
            )
        ]

    def __str__(self):
        return self.name

    @property
    def current_balance(self):
        spent = self.expenses.aggregate(total=Sum("converted_amount"))["total"] or 0
        return self.opening_balance - spent


class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    amount = models.FloatField()
    currency = models.CharField(max_length=3, default="INR")
    exchange_rate = models.FloatField(default=1)
    converted_amount = models.FloatField(default=0)
    date = models.DateField(default=now)
    notes = models.TextField(blank=True)
    receipt = models.FileField(upload_to="receipts/", null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="expenses",
    )

    def __str__(self):
        return (self.notes or f"{self.amount} expense")[:50]

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["owner", "-date"], name="exp_owner_date_idx"),
            models.Index(
                fields=["owner", "category", "-date"],
                name="exp_owner_cat_date_idx",
            ),
            models.Index(
                fields=["owner", "account", "-date"],
                name="exp_owner_acct_date_idx",
            ),
        ]


class RecurringExpense(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    amount = models.FloatField()
    currency = models.CharField(max_length=3, default="INR")
    notes = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    start_date = models.DateField(default=now)
    next_run_date = models.DateField()
    last_generated_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurring_expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recurring_expenses",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="recurring_expenses",
    )

    def __str__(self):
        return (self.notes or f"{self.amount} recurring expense")[:50]

    class Meta:
        ordering = ["next_run_date", "id"]
        indexes = [
            models.Index(
                fields=["is_active", "next_run_date"],
                name="recur_active_run_idx",
            ),
            models.Index(
                fields=["owner", "is_active", "next_run_date"],
                name="recur_owner_active_run_idx",
            ),
        ]


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        OVERSPENDING = "overspending", "Overspending Alert"
        LARGE_EXPENSE = "large_expense", "Large Expense Alert"
        RECURRING_REMINDER = "recurring_reminder", "Recurring Reminder"
        INACTIVITY = "inactivity", "Inactivity Alert"

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=25, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    dedupe_key = models.CharField(max_length=255, null=True, blank=True)
    expense = models.ForeignKey(
        Expense,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    recurring_expense = models.ForeignKey(
        RecurringExpense,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["owner", "is_read", "-created_at"],
                name="notif_owner_read_created_idx",
            ),
            models.Index(
                fields=["owner", "notification_type", "-created_at"],
                name="notif_owner_type_created_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "dedupe_key"],
                name="unique_notification_dedupe_key_per_owner",
                condition=models.Q(dedupe_key__isnull=False),
            )
        ]

    def __str__(self):
        return self.title
