from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0010_remove_legacy_budget_tables"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="opening_balance",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14),
        ),
        migrations.AlterField(
            model_name="expense",
            name="amount",
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name="expense",
            name="exchange_rate",
            field=models.DecimalField(decimal_places=8, default=1, max_digits=18),
        ),
        migrations.AlterField(
            model_name="expense",
            name="converted_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14),
        ),
        migrations.AlterField(
            model_name="recurringexpense",
            name="amount",
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
    ]
