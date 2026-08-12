import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import localdate

from expense.models import Account, Category, Expense, RecurringExpense

User = get_user_model()

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
    ("Food & Dining",     Decimal("120"),  Decimal("450"),  "Groceries"),
    ("Food & Dining",     Decimal("80"),   Decimal("300"),  "Restaurant"),
    ("Food & Dining",     Decimal("40"),   Decimal("150"),  "Coffee"),
    ("Transportation",    Decimal("50"),   Decimal("500"),  "Fuel"),
    ("Transportation",    Decimal("20"),   Decimal("200"),  "Auto rickshaw"),
    ("Bills & Utilities", Decimal("800"),  Decimal("1200"), "Electricity bill"),
    ("Bills & Utilities", Decimal("300"),  Decimal("600"),  "Internet bill"),
    ("Entertainment",     Decimal("200"),  Decimal("800"),  "Movies"),
    ("Shopping",          Decimal("500"),  Decimal("3000"), "Clothing"),
    ("Healthcare",        Decimal("200"),  Decimal("1500"), "Pharmacy"),
]


class Command(BaseCommand):
    help = "Seed demo data for an existing user. Pass --username to target a specific account."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Username to seed data for (defaults to first non-superuser).",
        )

    def handle(self, *args, **options):
        # ── Resolve user ──────────────────────────────────────────────────────
        username = options.get("username")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f"No user with username '{username}' found.")
        else:
            user = User.objects.filter(is_superuser=False).first()
            if not user:
                raise CommandError("No non-superuser found. Create an account via /register first.")

        self.stdout.write(f"Seeding demo data for user '{user.username}' ({user.email})...")

        # ── Global categories ─────────────────────────────────────────────────
        for name in GLOBAL_CATEGORIES:
            Category.objects.get_or_create(name=name, owner=None)
        self.stdout.write(f"Ensured {len(GLOBAL_CATEGORIES)} global categories.")

        # ── Accounts (skip if already exist) ──────────────────────────────────
        bank, _ = Account.objects.get_or_create(
            owner=user, name="HDFC Savings",
            defaults={"account_type": Account.AccountType.BANK, "opening_balance": Decimal("50000")},
        )
        cash, _ = Account.objects.get_or_create(
            owner=user, name="Cash Wallet",
            defaults={"account_type": Account.AccountType.CASH, "opening_balance": Decimal("5000")},
        )
        card, _ = Account.objects.get_or_create(
            owner=user, name="SBI Credit Card",
            defaults={"account_type": Account.AccountType.CREDIT_CARD, "opening_balance": Decimal("0")},
        )
        accounts = [bank, cash, card]
        self.stdout.write("Ensured 3 accounts.")

        # ── Expenses (last 6 months, ~6–8 per month) ──────────────────────────
        today = localdate()
        categories = {c.name: c for c in Category.objects.filter(owner=None)}
        expense_count = 0

        for months_back in range(6):
            ref_date = today.replace(day=1) - timedelta(days=months_back * 30)
            for _ in range(random.randint(6, 8)):
                cat_name, low, high, notes = random.choice(EXPENSES_TEMPLATE)
                amount = Decimal(str(random.uniform(float(low), float(high)))).quantize(Decimal("0.01"))
                expense_date = ref_date + timedelta(days=random.randint(0, 27))
                Expense.objects.create(
                    owner=user,
                    account=random.choice(accounts),
                    category=categories.get(cat_name),
                    amount=amount,
                    currency=user.base_currency,
                    exchange_rate=Decimal("1"),
                    converted_amount=amount,
                    date=expense_date,
                    notes=notes,
                )
                expense_count += 1

        self.stdout.write(f"Created {expense_count} expenses.")

        # ── Recurring expenses ─────────────────────────────────────────────────
        RecurringExpense.objects.get_or_create(
            owner=user, notes="Monthly rent",
            defaults={
                "account": bank,
                "category": categories.get("Bills & Utilities"),
                "amount": Decimal("15000"),
                "currency": user.base_currency,
                "frequency": RecurringExpense.Frequency.MONTHLY,
                "start_date": today.replace(day=1),
                "next_run_date": today.replace(day=1),
            },
        )
        RecurringExpense.objects.get_or_create(
            owner=user, notes="Netflix subscription",
            defaults={
                "account": card,
                "category": categories.get("Entertainment"),
                "amount": Decimal("649"),
                "currency": user.base_currency,
                "frequency": RecurringExpense.Frequency.MONTHLY,
                "start_date": today.replace(day=1),
                "next_run_date": today.replace(day=1),
            },
        )
        RecurringExpense.objects.get_or_create(
            owner=user, notes="Gym membership",
            defaults={
                "account": bank,
                "category": categories.get("Healthcare"),
                "amount": Decimal("1200"),
                "currency": user.base_currency,
                "frequency": RecurringExpense.Frequency.MONTHLY,
                "start_date": today.replace(day=1),
                "next_run_date": today.replace(day=1),
            },
        )
        self.stdout.write("Ensured 3 recurring expenses.")
        self.stdout.write(self.style.SUCCESS(f"Done — demo data seeded for '{user.username}'."))
