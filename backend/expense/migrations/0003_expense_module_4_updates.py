from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expense", "0002_alter_category_options_alter_expense_options_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="expense",
            old_name="description",
            new_name="notes",
        ),
        migrations.AddField(
            model_name="expense",
            name="account",
            field=models.CharField(default="Cash", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="expense",
            name="receipt",
            field=models.FileField(blank=True, null=True, upload_to="receipts/"),
        ),
        migrations.AlterField(
            model_name="expense",
            name="notes",
            field=models.TextField(blank=True),
        ),
    ]
