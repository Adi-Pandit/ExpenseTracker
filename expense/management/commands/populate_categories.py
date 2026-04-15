from django.core.management.base import BaseCommand
from expense.models import Category


class Command(BaseCommand):
    help = "Populate database with default global categories"

    def handle(self, *args, **options):
        default_categories = [
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

        created_count = 0
        for category_name in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_name, owner=None, defaults={}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created category: {category_name}")
                )
            else:
                self.stdout.write(f"Category already exists: {category_name}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} new categories")
        )
