from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from expense.services import (
    generate_inactivity_notifications,
    generate_recurring_reminder_notifications,
)


class Command(BaseCommand):
    help = "Generate recurring reminder and inactivity notifications."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Optional run date in YYYY-MM-DD format. Defaults to today.",
        )
        parser.add_argument(
            "--inactivity-days",
            type=int,
            default=7,
            help="Number of days without expenses before raising inactivity alerts.",
        )

    def handle(self, *args, **options):
        run_date = None
        if options["date"]:
            run_date = parse_date(options["date"])
            if run_date is None:
                self.stderr.write(self.style.ERROR("Invalid date format. Use YYYY-MM-DD."))
                return

        recurring_count = generate_recurring_reminder_notifications(run_date=run_date)
        inactivity_count = generate_inactivity_notifications(
            run_date=run_date, inactivity_days=options["inactivity_days"]
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Generated "
                f"{recurring_count} recurring reminder notification(s) and "
                f"{inactivity_count} inactivity notification(s)."
            )
        )
