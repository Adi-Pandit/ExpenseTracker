import csv
import datetime

import xlwt
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from .currency import convert_amount
from .models import Expense, Notification, RecurringExpense

User = get_user_model()

LARGE_EXPENSE_THRESHOLD = 1000
INACTIVITY_DAYS_THRESHOLD = 7
RECURRING_REMINDER_DAYS = 1


def get_user_expense_stats(user):
    today = datetime.date.today()

    today_expenses = (
        Expense.objects.filter(owner=user, date=today).aggregate(
            Sum("converted_amount")
        )["converted_amount__sum"]
        or 0
    )

    week_start = today - datetime.timedelta(days=today.weekday())
    week_expenses = (
        Expense.objects.filter(owner=user, date__gte=week_start).aggregate(
            Sum("converted_amount")
        )["converted_amount__sum"]
        or 0
    )

    month_start = today.replace(day=1)
    month_expenses = (
        Expense.objects.filter(owner=user, date__gte=month_start).aggregate(
            Sum("converted_amount")
        )["converted_amount__sum"]
        or 0
    )

    year_start = today.replace(month=1, day=1)
    year_expenses = (
        Expense.objects.filter(owner=user, date__gte=year_start).aggregate(
            Sum("converted_amount")
        )["converted_amount__sum"]
        or 0
    )

    current_month = today.replace(day=1)
    next_month = current_month + relativedelta(months=1)
    monthly_expenses = Expense.objects.filter(
        owner=user, date__gte=current_month, date__lt=next_month
    ).select_related("category")

    category_data = {}
    total_monthly = monthly_expenses.aggregate(Sum("converted_amount"))["converted_amount__sum"] or 0

    if total_monthly > 0:
        for expense in monthly_expenses:
            category_name = expense.category.name if expense.category else "Uncategorized"
            category_data[category_name] = (
                category_data.get(category_name, 0) + expense.converted_amount
            )

        category_data = {
            category_name: round((amount / total_monthly) * 100, 2)
            for category_name, amount in category_data.items()
        }

    return {
        "today": today_expenses,
        "week": week_expenses,
        "month": month_expenses,
        "year": year_expenses,
        "category_breakdown": category_data,
        "total_monthly": total_monthly,
    }


def export_expenses_to_csv(expenses):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="expenses_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(["Amount", "Currency", "Base Amount", "Account", "Notes", "Category", "Date"])
    for expense in expenses:
        writer.writerow(
            [
                expense.amount,
                expense.currency,
                expense.converted_amount,
                expense.account.name if expense.account else "",
                expense.notes,
                expense.category.name if expense.category else "",
                expense.date,
            ]
        )
    return response


def export_expenses_to_excel(expenses):
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        f'attachment; filename="expenses_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xls"'
    )
    workbook = xlwt.Workbook(encoding="utf-8")
    sheet = workbook.add_sheet("Expenses")
    header_style = xlwt.XFStyle()
    header_style.font.bold = True

    columns = ["Amount", "Currency", "Base Amount", "Account", "Notes", "Category", "Date"]
    for col_num, column_name in enumerate(columns):
        sheet.write(0, col_num, column_name, header_style)

    row_style = xlwt.XFStyle()
    rows = expenses.values_list(
        "amount",
        "currency",
        "converted_amount",
        "account__name",
        "notes",
        "category__name",
        "date",
    )
    for row_num, row in enumerate(rows, start=1):
        for col_num, value in enumerate(row):
            sheet.write(row_num, col_num, str(value or ""), row_style)

    workbook.save(response)
    return response


def export_expenses_to_pdf(expenses):
    total = expenses.aggregate(Sum("converted_amount"))["converted_amount__sum"] or 0
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="expenses_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    )

    document = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Expense Report", styles["Heading1"]),
        Paragraph("<br/>", styles["Normal"]),
    ]

    data = [["No", "Amount", "Currency", "Base Amount", "Account", "Category", "Notes", "Date"]]
    for index, expense in enumerate(expenses, start=1):
        data.append(
            [
                str(index),
                str(expense.amount),
                expense.currency,
                str(expense.converted_amount),
                expense.account.name if expense.account else "",
                expense.category.name if expense.category else "",
                expense.notes,
                expense.date.strftime("%Y-%m-%d"),
            ]
        )

    data.append(["", f"Total: {total}", "", "", "", "", "", ""])

    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
            ]
        )
    )

    elements.append(table)
    document.build(elements)
    return response


def get_next_recurring_date(current_date, frequency):
    if frequency == RecurringExpense.Frequency.DAILY:
        return current_date + datetime.timedelta(days=1)
    if frequency == RecurringExpense.Frequency.WEEKLY:
        return current_date + datetime.timedelta(weeks=1)
    return current_date + relativedelta(months=1)


def generate_due_recurring_expenses(run_date=None):
    run_date = run_date or datetime.date.today()
    created_count = 0

    due_ids = list(
        RecurringExpense.objects.filter(is_active=True, next_run_date__lte=run_date)
        .order_by("next_run_date", "id")
        .values_list("id", flat=True)
    )

    for pk in due_ids:
        with transaction.atomic():
            try:
                recurring_expense = (
                    RecurringExpense.objects.select_for_update()
                    .select_related("account", "category", "owner")
                    .get(pk=pk, is_active=True, next_run_date__lte=run_date)
                )
            except RecurringExpense.DoesNotExist:
                continue

            generation_date = recurring_expense.next_run_date

            while generation_date <= run_date:
                exchange_rate, converted_amount = convert_amount(
                    recurring_expense.amount,
                    recurring_expense.currency,
                    recurring_expense.owner.base_currency,
                )
                expense = Expense.objects.create(
                    amount=recurring_expense.amount,
                    currency=recurring_expense.currency,
                    exchange_rate=exchange_rate,
                    converted_amount=converted_amount,
                    date=generation_date,
                    notes=recurring_expense.notes,
                    owner=recurring_expense.owner,
                    category=recurring_expense.category,
                    account=recurring_expense.account,
                )
                process_expense_notifications(expense)
                created_count += 1

                recurring_expense.last_generated_date = generation_date
                generation_date = get_next_recurring_date(
                    generation_date, recurring_expense.frequency
                )

            recurring_expense.next_run_date = generation_date
            recurring_expense.save(update_fields=["last_generated_date", "next_run_date"])

    return created_count


def create_large_expense_notification(expense, threshold=LARGE_EXPENSE_THRESHOLD):
    if expense.converted_amount < threshold:
        return None

    return Notification.objects.create(
        owner=expense.owner,
        notification_type=Notification.NotificationType.LARGE_EXPENSE,
        title="Large expense recorded",
        message=(
            f"A large expense of {round(expense.converted_amount, 2)} "
            f"{expense.owner.base_currency} was added to {expense.account.name}."
        ),
        expense=expense,
    )


def create_overspending_notification(expense):
    expense_date = expense.date
    current_month_start = expense_date.replace(day=1)
    last_month_end = current_month_start - datetime.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    current_total = (
        Expense.objects.filter(
            owner=expense.owner, date__gte=current_month_start, date__lte=expense_date
        ).aggregate(total=Sum("converted_amount"))["total"]
        or 0
    )
    last_total = (
        Expense.objects.filter(
            owner=expense.owner, date__gte=last_month_start, date__lte=last_month_end
        ).aggregate(total=Sum("converted_amount"))["total"]
        or 0
    )

    if current_total <= last_total:
        return None

    dedupe_key = f"overspending:{expense_date.year}:{expense_date.month}"
    notification, created = Notification.objects.get_or_create(
        owner=expense.owner,
        dedupe_key=dedupe_key,
        defaults={
            "notification_type": Notification.NotificationType.OVERSPENDING,
            "title": "Overspending alert",
            "message": (
                f"Your spending this month ({round(current_total, 2)}) is now above "
                f"last month ({round(last_total, 2)}) in {expense.owner.base_currency}."
            ),
            "expense": expense,
        },
    )
    if not created:
        notification.message = (
            f"Your spending this month ({round(current_total, 2)}) is now above "
            f"last month ({round(last_total, 2)}) in {expense.owner.base_currency}."
        )
        notification.expense = expense
        notification.is_read = False
        notification.read_at = None
        notification.save(update_fields=["message", "expense", "is_read", "read_at"])
    return notification


def process_expense_notifications(expense):
    create_large_expense_notification(expense)
    create_overspending_notification(expense)


def generate_recurring_reminder_notifications(run_date=None):
    run_date = run_date or datetime.date.today()
    reminder_date = run_date + datetime.timedelta(days=RECURRING_REMINDER_DAYS)
    created_count = 0

    recurring_expenses = RecurringExpense.objects.filter(
        is_active=True, next_run_date=reminder_date
    ).select_related("account", "owner")

    for recurring_expense in recurring_expenses:
        dedupe_key = (
            f"recurring-reminder:{recurring_expense.id}:{recurring_expense.next_run_date}"
        )
        _, created = Notification.objects.get_or_create(
            owner=recurring_expense.owner,
            dedupe_key=dedupe_key,
            defaults={
                "notification_type": Notification.NotificationType.RECURRING_REMINDER,
                "title": "Recurring expense reminder",
                "message": (
                    f"Recurring expense '{recurring_expense.notes or recurring_expense.account.name}' "
                    f"is due on {recurring_expense.next_run_date}."
                ),
                "recurring_expense": recurring_expense,
            },
        )
        created_count += int(created)

    return created_count


def generate_inactivity_notifications(run_date=None, inactivity_days=INACTIVITY_DAYS_THRESHOLD):
    run_date = run_date or datetime.date.today()
    inactivity_cutoff = run_date - datetime.timedelta(days=inactivity_days)
    created_count = 0

    for user in User.objects.all():
        last_expense = (
            Expense.objects.filter(owner=user).order_by("-date").values_list("date", flat=True).first()
        )
        if last_expense and last_expense > inactivity_cutoff:
            continue

        dedupe_key = f"inactivity:{run_date.isoformat()}:{inactivity_days}"
        _, created = Notification.objects.get_or_create(
            owner=user,
            dedupe_key=dedupe_key,
            defaults={
                "notification_type": Notification.NotificationType.INACTIVITY,
                "title": "Inactivity alert",
                "message": f"No expenses have been added in the last {inactivity_days} days.",
            },
        )
        created_count += int(created)

    return created_count


def mark_notification_as_read(notification):
    if notification.is_read:
        return notification

    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save(update_fields=["is_read", "read_at"])
    return notification


def recalculate_user_expenses_to_base_currency(user):
    expenses_to_update = []
    for expense in Expense.objects.filter(owner=user):
        exchange_rate, converted_amount = convert_amount(
            expense.amount, expense.currency, user.base_currency
        )
        expense.exchange_rate = exchange_rate
        expense.converted_amount = converted_amount
        expenses_to_update.append(expense)

    if expenses_to_update:
        Expense.objects.bulk_update(
            expenses_to_update, ["exchange_rate", "converted_amount"]
        )
