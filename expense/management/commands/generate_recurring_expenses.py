from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from expense.services import generate_due_recurring_expenses


class Command(BaseCommand):
    help = "Generate due expenses from active recurring expense rules."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Optional run date in YYYY-MM-DD format. Defaults to today.",
        )

    def handle(self, *args, **options):
        run_date = None
        if options["date"]:
            run_date = parse_date(options["date"])
            if run_date is None:
                self.stderr.write(self.style.ERROR("Invalid date format. Use YYYY-MM-DD."))
                return

        created_count = generate_due_recurring_expenses(run_date=run_date)
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {created_count} expense(s) from recurring expense rules."
            )
        )
