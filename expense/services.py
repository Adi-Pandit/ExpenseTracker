import csv
import datetime

import xlwt
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from .models import Expense


def get_user_expense_stats(user):
    today = datetime.date.today()

    today_expenses = (
        Expense.objects.filter(owner=user, date=today).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )

    week_start = today - datetime.timedelta(days=today.weekday())
    week_expenses = (
        Expense.objects.filter(owner=user, date__gte=week_start).aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )

    month_start = today.replace(day=1)
    month_expenses = (
        Expense.objects.filter(owner=user, date__gte=month_start).aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0
    )

    year_start = today.replace(month=1, day=1)
    year_expenses = (
        Expense.objects.filter(owner=user, date__gte=year_start).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )

    current_month = today.replace(day=1)
    next_month = current_month + relativedelta(months=1)
    monthly_expenses = Expense.objects.filter(
        owner=user, date__gte=current_month, date__lt=next_month
    ).select_related("category")

    category_data = {}
    total_monthly = monthly_expenses.aggregate(Sum("amount"))["amount__sum"] or 0

    if total_monthly > 0:
        for expense in monthly_expenses:
            category_name = expense.category.name if expense.category else "Uncategorized"
            category_data[category_name] = category_data.get(category_name, 0) + expense.amount

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
    writer.writerow(["Amount", "Account", "Notes", "Category", "Date"])
    for expense in expenses:
        writer.writerow(
            [
                expense.amount,
                expense.account,
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

    columns = ["Amount", "Account", "Notes", "Category", "Date"]
    for col_num, column_name in enumerate(columns):
        sheet.write(0, col_num, column_name, header_style)

    row_style = xlwt.XFStyle()
    rows = expenses.values_list("amount", "account", "notes", "category__name", "date")
    for row_num, row in enumerate(rows, start=1):
        for col_num, value in enumerate(row):
            sheet.write(row_num, col_num, str(value or ""), row_style)

    workbook.save(response)
    return response


def export_expenses_to_pdf(expenses):
    total = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
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

    data = [["No", "Amount", "Account", "Category", "Notes", "Date"]]
    for index, expense in enumerate(expenses, start=1):
        data.append(
            [
                str(index),
                f"Rs. {expense.amount}",
                expense.account,
                expense.category.name if expense.category else "",
                expense.notes,
                expense.date.strftime("%Y-%m-%d"),
            ]
        )

    data.append(["", f"Total: Rs. {total}", "", "", "", ""])

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
