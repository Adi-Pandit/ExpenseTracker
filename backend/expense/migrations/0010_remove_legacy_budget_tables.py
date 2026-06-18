from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0009_category_unique_global_category_name"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "DROP TABLE IF EXISTS budget_budget_amount;"
                "DROP TABLE IF EXISTS budget_budget;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
