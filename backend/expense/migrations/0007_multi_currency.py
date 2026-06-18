from django.db import migrations, models


def backfill_currency_fields(apps, schema_editor):
    User = apps.get_model("authentication", "User")
    Expense = apps.get_model("expense", "Expense")
    RecurringExpense = apps.get_model("expense", "RecurringExpense")

    base_currency_by_owner = {
        str(user.id): user.base_currency for user in User.objects.all()
    }

    for expense in Expense.objects.all():
        base_currency = base_currency_by_owner.get(str(expense.owner_id), "INR")
        expense.currency = base_currency
        expense.exchange_rate = 1
        expense.converted_amount = expense.amount
        expense.save(update_fields=["currency", "exchange_rate", "converted_amount"])

    for recurring_expense in RecurringExpense.objects.all():
        base_currency = base_currency_by_owner.get(str(recurring_expense.owner_id), "INR")
        recurring_expense.currency = base_currency
        recurring_expense.save(update_fields=["currency"])


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0002_user_base_currency"),
        ("expense", "0006_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="currency",
            field=models.CharField(default="INR", max_length=3),
        ),
        migrations.AddField(
            model_name="expense",
            name="exchange_rate",
            field=models.FloatField(default=1),
        ),
        migrations.AddField(
            model_name="expense",
            name="converted_amount",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="recurringexpense",
            name="currency",
            field=models.CharField(default="INR", max_length=3),
        ),
        migrations.RunPython(backfill_currency_fields, migrations.RunPython.noop),
    ]
