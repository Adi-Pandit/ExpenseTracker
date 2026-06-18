import os
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.timezone import localdate

from expense.models import Account, Category, Expense, RecurringExpense

User = get_user_model()

USERNAME = "adityapandit"
EMAIL = "adityapandit2304@outlook.com"
FIRST_NAME = "Aditya"
LAST_NAME = "Pandit"

GLOBAL_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Personal Care",
    "Gifts & Donations",
    "Business",
    "Other",
]

EXPENSES_TEMPLATE = [
    ("Food & Dining",    Decimal("120"),  Decimal("450"),  "Groceries"),
    ("Food & Dining",    Decimal("80"),   Decimal("300"),  "Restaurant"),
    ("Food & Dining",    Decimal("40"),   Decimal("150"),  "Coffee"),
    ("Transportation",   Decimal("50"),   Decimal("500"),  "Fuel"),
    ("Transportation",   Decimal("20"),   Decimal("200"),  "Auto rickshaw"),
    ("Bills & Utilities", Decimal("800"), Decimal("1200"), "Electricity bill"),
    ("Bills & Utilities", Decimal("300"), Decimal("600"),  "Internet bill"),
    ("Entertainment",    Decimal("200"),  Decimal("800"),  "Movies"),
    ("Shopping",         Decimal("500"),  Decimal("3000"), "Clothing"),
    ("Healthcare",       Decimal("200"),  Decimal("1500"), "Pharmacy"),
]


class Command(BaseCommand):
    help = "Seed demo data for the expense tracker."

    def handle(self, *args, **options):
        password = os.environ.get("SEED_USER_PASSWORD")
        if not password:
            self.stderr.write("SEED_USER_PASSWORD env var not set — aborting.")
            return

        # ── User ──────────────────────────────────────────────────────────────
        user, created = User.objects.get_or_create(
            username=USERNAME,
            defaults={
                "email": EMAIL,
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "base_currency": "INR",
            },
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"Created user '{USERNAME}'.")
        else:
            self.stdout.write(f"User '{USERNAME}' already exists — skipping user creation.")
            return

        # ── Global categories ─────────────────────────────────────────────────
        for name in GLOBAL_CATEGORIES:
            Category.objects.get_or_create(name=name, owner=None)
        self.stdout.write(f"Ensured {len(GLOBAL_CATEGORIES)} global categories.")

        # ── Accounts ──────────────────────────────────────────────────────────
        bank = Account.objects.create(
            owner=user,
            name="HDFC Savings",
            account_type=Account.AccountType.BANK,
            opening_balance=Decimal("50000"),
        )
        cash = Account.objects.create(
            owner=user,
            name="Cash Wallet",
            account_type=Account.AccountType.CASH,
            opening_balance=Decimal("5000"),
        )
        card = Account.objects.create(
            owner=user,
            name="SBI Credit Card",
            account_type=Account.AccountType.CREDIT_CARD,
            opening_balance=Decimal("0"),
        )
        accounts = [bank, cash, card]
        self.stdout.write("Created 3 accounts.")

        # ── Expenses (last 6 months, ~6–8 per month) ──────────────────────────
        today = localdate()
        categories = {c.name: c for c in Category.objects.filter(owner=None)}
        expense_count = 0

        for months_back in range(6):
            # Approximate first day of that month
            ref_date = today.replace(day=1) - timedelta(days=months_back * 30)
            for _ in range(random.randint(6, 8)):
                template = random.choice(EXPENSES_TEMPLATE)
                cat_name, low, high, notes = template
                amount = Decimal(str(random.uniform(float(low), float(high)))).quantize(
                    Decimal("0.01")
                )
                expense_date = ref_date + timedelta(days=random.randint(0, 27))
                Expense.objects.create(
                    owner=user,
                    account=random.choice(accounts),
                    category=categories.get(cat_name),
                    amount=amount,
                    currency="INR",
                    exchange_rate=Decimal("1"),
                    converted_amount=amount,
                    date=expense_date,
                    notes=notes,
                )
                expense_count += 1

        self.stdout.write(f"Created {expense_count} expenses.")

        # ── Recurring expenses ─────────────────────────────────────────────────
        RecurringExpense.objects.create(
            owner=user,
            account=bank,
            category=categories.get("Bills & Utilities"),
            amount=Decimal("15000"),
            currency="INR",
            frequency=RecurringExpense.Frequency.MONTHLY,
            notes="Monthly rent",
            start_date=today.replace(day=1),
            next_run_date=today.replace(day=1),
        )
        RecurringExpense.objects.create(
            owner=user,
            account=card,
            category=categories.get("Entertainment"),
            amount=Decimal("649"),
            currency="INR",
            frequency=RecurringExpense.Frequency.MONTHLY,
            notes="Netflix subscription",
            start_date=today.replace(day=1),
            next_run_date=today.replace(day=1),
        )
        RecurringExpense.objects.create(
            owner=user,
            account=bank,
            category=categories.get("Healthcare"),
            amount=Decimal("1200"),
            currency="INR",
            frequency=RecurringExpense.Frequency.MONTHLY,
            notes="Gym membership",
            start_date=today.replace(day=1),
            next_run_date=today.replace(day=1),
        )
        self.stdout.write("Created 3 recurring expenses.")
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
