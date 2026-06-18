from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="base_currency",
            field=models.CharField(default="INR", max_length=3),
        ),
    ]
