import calendar
from datetime import timedelta
from decimal import Decimal

from django.db.models import Case, Count, DecimalField, Q, Sum, Value, When
from django.utils.timezone import localdate

from expense.models import Expense


def current_month_range(today):
    start = today.replace(day=1)
    _, last_day = calendar.monthrange(today.year, today.month)
    end = today.replace(day=last_day)
    return start, end


def last_month_range(today):
    current_start = today.replace(day=1)
    last_month_end = current_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    return last_month_start, last_month_end


def add_monthly_comparison_rule(insights, current_total, last_total):
    if current_total == 0 and last_total == 0:
        insights.append(
            {
                "rule": "monthly_comparison",
                "message": "No spending recorded in either this month or last month yet.",
                "severity": "info",
            }
        )
        return

    if last_total:
        change = round(((current_total - last_total) / last_total) * 100, 2)
        if change > 0:
            message = f"You spent {abs(change)}% more than last month."
            severity = "warning" if change >= 20 else "info"
        elif change < 0:
            message = f"You spent {abs(change)}% less than last month."
            severity = "positive"
        else:
            message = "Your spending is unchanged from last month."
            severity = "info"
    else:
        message = "This is your first month with recorded spending."
        severity = "info"

    insights.append(
        {
            "rule": "monthly_comparison",
            "message": message,
            "severity": severity,
        }
    )


def add_category_dominance_rule(insights, current_month_expenses, current_total):
    if not current_total:
        return

    top_category_row = (
        current_month_expenses.values("category__name")
        .annotate(total=Sum("converted_amount"))
        .order_by("-total")
        .first()
    )

    if not top_category_row:
        return

    category_name = top_category_row["category__name"] or "Uncategorized"
    share = round((top_category_row["total"] / current_total) * 100, 2)

    if share >= 40:
        message = f"{category_name} dominates your spending at {share}% of this month total."
        severity = "warning" if share >= 55 else "info"
    else:
        message = f"{category_name} is your top category this month at {share}%."
        severity = "info"

    insights.append(
        {
            "rule": "category_dominance",
            "message": message,
            "severity": severity,
        }
    )


def add_spending_spike_rule(insights, current_month_expenses):
    daily_totals = list(
        current_month_expenses.values("date")
        .annotate(total=Sum("converted_amount"))
        .order_by("date")
    )

    if len(daily_totals) < 3:
        return

    totals = [row["total"] or 0 for row in daily_totals]
    average_daily = sum(totals) / len(totals)
    peak_day = max(daily_totals, key=lambda row: row["total"] or 0)
    peak_amount = peak_day["total"] or 0

    if average_daily > 0 and peak_amount >= average_daily * 2:
        insights.append(
            {
                "rule": "spending_spike",
                "message": (
                    f"Spending spiked on {peak_day['date']} with {round(peak_amount, 2)} "
                    f"spent versus a daily average of {round(average_daily, 2)}."
                ),
                "severity": "warning",
            }
        )


def add_weekend_weekday_rule(insights, current_month_expenses):
    # week_day lookup: 1=Sunday, 2=Monday … 7=Saturday (Django convention)
    WEEKEND = [1, 7]
    WEEKDAY = [2, 3, 4, 5, 6]

    result = current_month_expenses.aggregate(
        weekend_total=Sum(
            Case(
                When(date__week_day__in=WEEKEND, then="converted_amount"),
                default=Value(Decimal("0")),
                output_field=DecimalField(),
            )
        ),
        weekday_total=Sum(
            Case(
                When(date__week_day__in=WEEKDAY, then="converted_amount"),
                default=Value(Decimal("0")),
                output_field=DecimalField(),
            )
        ),
        weekend_days=Count("date", filter=Q(date__week_day__in=WEEKEND), distinct=True),
        weekday_days=Count("date", filter=Q(date__week_day__in=WEEKDAY), distinct=True),
    )

    weekend_total = result["weekend_total"] or Decimal("0")
    weekday_total = result["weekday_total"] or Decimal("0")
    weekend_days = result["weekend_days"] or 0
    weekday_days = result["weekday_days"] or 0

    if weekend_total == 0 and weekday_total == 0:
        return

    weekend_average = weekend_total / weekend_days if weekend_days else Decimal("0")
    weekday_average = weekday_total / weekday_days if weekday_days else Decimal("0")

    if weekend_average > weekday_average * Decimal("1.25") and weekend_days:
        message = (
            f"You spend more on weekends: average {round(weekend_average, 2)} "
            f"per active weekend day versus {round(weekday_average, 2)} on weekdays."
        )
    elif weekday_average > weekend_average * Decimal("1.25") and weekday_days:
        message = (
            f"You spend more on weekdays: average {round(weekday_average, 2)} "
            f"per active weekday versus {round(weekend_average, 2)} on weekends."
        )
    else:
        message = "Your weekend and weekday spending patterns are fairly balanced."

    insights.append(
        {
            "rule": "weekend_vs_weekday",
            "message": message,
            "severity": "info",
        }
    )


def build_smart_insights(user):
    today = localdate()
    current_start, current_end = current_month_range(today)
    last_start, last_end = last_month_range(today)

    current_qs = Expense.objects.filter(
        owner=user, date__gte=current_start, date__lte=current_end
    )
    last_qs = Expense.objects.filter(
        owner=user, date__gte=last_start, date__lte=last_end
    )

    current_total = round(
        current_qs.aggregate(total=Sum("converted_amount"))["total"] or 0, 2
    )
    last_total = round(
        last_qs.aggregate(total=Sum("converted_amount"))["total"] or 0, 2
    )

    insights = []
    add_monthly_comparison_rule(insights, current_total, last_total)
    add_category_dominance_rule(insights, current_qs, current_total)
    add_spending_spike_rule(insights, current_qs)
    add_weekend_weekday_rule(insights, current_qs)

    if not insights:
        insights.append(
            {
                "rule": "baseline",
                "message": "Not enough spending data yet to generate smart insights.",
                "severity": "info",
            }
        )

    return {
        "period": current_start.strftime("%B %Y"),
        "insights": insights,
    }
