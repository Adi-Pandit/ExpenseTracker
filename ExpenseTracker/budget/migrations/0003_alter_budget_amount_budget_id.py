# Generated by Django 4.1.2 on 2022-11-20 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_budget_amount_delete_source_alter_budget_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget_amount',
            name='budget_id',
            field=models.IntegerField(),
        ),
    ]
