import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from uuid_extensions import uuid7


def migrate_expense_accounts(apps, schema_editor):
    Account = apps.get_model("expense", "Account")
    Expense = apps.get_model("expense", "Expense")

    for expense in Expense.objects.exclude(legacy_account_name="").iterator():
        account_name = (expense.legacy_account_name or "").strip() or "Cash"
        normalized_name = account_name.lower()
        if "credit" in normalized_name:
            account_type = "credit_card"
        elif "bank" in normalized_name:
            account_type = "bank"
        else:
            account_type = "cash"

        account, _ = Account.objects.get_or_create(
            owner_id=expense.owner_id,
            name=account_name,
            defaults={
                "account_type": account_type,
                "opening_balance": 0,
            },
        )
        expense.account_id = account.id
        expense.save(update_fields=["account"])


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0003_expense_module_4_updates"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid7,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "account_type",
                    models.CharField(
                        choices=[
                            ("cash", "Cash"),
                            ("bank", "Bank"),
                            ("credit_card", "Credit Card"),
                        ],
                        max_length=20,
                    ),
                ),
                ("opening_balance", models.FloatField(default=0)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accounts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddConstraint(
            model_name="account",
            constraint=models.UniqueConstraint(
                fields=("owner", "name"),
                name="unique_account_name_per_owner",
            ),
        ),
        migrations.RenameField(
            model_name="expense",
            old_name="account",
            new_name="legacy_account_name",
        ),
        migrations.AddField(
            model_name="expense",
            name="account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="expenses",
                to="expense.account",
            ),
        ),
        migrations.RunPython(migrate_expense_accounts, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="expense",
            name="account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="expenses",
                to="expense.account",
            ),
        ),
        migrations.RemoveField(
            model_name="expense",
            name="legacy_account_name",
        ),
    ]
