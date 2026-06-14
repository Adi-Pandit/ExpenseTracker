from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from django.utils.timezone import localdate
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from expense.models import Account, Expense
from .serializers import (
    DashboardCategoriesSerializer,
    DashboardInsightsSerializer,
    DashboardRecentSerializer,
    DashboardSummarySerializer,
    DashboardTrendsSerializer,
)
from .services import build_smart_insights, current_month_range, last_month_range

def _serialize_expense(expense):
    return {
        "id": str(expense.id),
        "amount": expense.amount,
        "currency": expense.currency,
        "converted_amount": expense.converted_amount,
        "base_currency": expense.owner.base_currency,
        "date": expense.date,
        "notes": expense.notes,
        "category": expense.category.name if expense.category else None,
        "account": expense.account.name if expense.account else None,
    }


def _get_summary_payload(user):
    today = localdate()
    current_start, current_end = current_month_range(today)
    last_start, last_end = last_month_range(today)

    current_month_expenses = Expense.objects.filter(
        owner=user, date__gte=current_start, date__lte=current_end
    ).select_related("category", "account")
    last_month_expenses = Expense.objects.filter(
        owner=user, date__gte=last_start, date__lte=last_end
    )

    total_spend = (
        current_month_expenses.aggregate(total=Sum("converted_amount"))["total"] or 0
    )
    last_month_spend = (
        last_month_expenses.aggregate(total=Sum("converted_amount"))["total"] or 0
    )
    if last_month_spend:
        percent_change = round(
            ((total_spend - last_month_spend) / last_month_spend) * 100, 2
        )
    elif total_spend:
        percent_change = 100.0
    else:
        percent_change = 0.0

    top_category_row = (
        current_month_expenses.values("category__name")
        .annotate(total=Sum("converted_amount"))
        .order_by("-total")
        .first()
    )

    top_expenses = [
        _serialize_expense(expense)
        for expense in current_month_expenses.order_by("-converted_amount", "-date")[:5]
    ]

    accounts = Account.objects.filter(owner=user).annotate(
        spent=Coalesce(Sum("expenses__converted_amount"), Value(Decimal("0")))
    )
    account_balances = [
        {
            "id": str(account.id),
            "name": account.name,
            "type": account.account_type,
            "opening_balance": account.opening_balance,
            "current_balance": round(account.opening_balance - account.spent, 2),
        }
        for account in accounts
    ]

    return {
        "current_month": {
            "label": current_start.strftime("%B %Y"),
            "total_spend": round(total_spend, 2),
        },
        "last_month": {
            "label": last_start.strftime("%B %Y"),
            "total_spend": round(last_month_spend, 2),
        },
        "percent_change": percent_change,
        "top_category": {
            "name": top_category_row["category__name"] if top_category_row else None,
            "amount": round(top_category_row["total"], 2) if top_category_row else 0,
        },
        "top_expenses": top_expenses,
        "account_balances": account_balances,
    }


def _get_trends_payload(user):
    today = localdate()
    current_start, current_end = current_month_range(today)

    expenses_by_day = {
        row["day"]: round(row["total"], 2)
        for row in (
            Expense.objects.filter(owner=user, date__gte=current_start, date__lte=current_end)
            .annotate(day=TruncDate("date"))
            .values("day")
            .annotate(total=Sum("converted_amount"))
            .order_by("day")
        )
    }

    trend = []
    current_day = current_start
    while current_day <= current_end:
        trend.append(
            {
                "date": current_day,
                "amount": expenses_by_day.get(current_day, 0),
            }
        )
        current_day += timedelta(days=1)

    return {
        "period": current_start.strftime("%B %Y"),
        "daily_expenses": trend,
    }


def _get_categories_payload(user):
    today = localdate()
    current_start, current_end = current_month_range(today)

    category_rows = list(
        Expense.objects.filter(owner=user, date__gte=current_start, date__lte=current_end)
        .values("category__name")
        .annotate(total=Sum("converted_amount"))
        .order_by("-total")
    )
    total_spend = sum(row["total"] for row in category_rows)

    breakdown = []
    for row in category_rows:
        amount = row["total"] or 0
        breakdown.append(
            {
                "category": row["category__name"] or "Uncategorized",
                "amount": round(amount, 2),
                "percentage": round((amount / total_spend) * 100, 2) if total_spend else 0,
            }
        )

    return {
        "period": current_start.strftime("%B %Y"),
        "total_spend": round(total_spend, 2),
        "breakdown": breakdown,
    }


def _get_recent_payload(user):
    recent_expenses = Expense.objects.filter(owner=user).select_related(
        "category", "account"
    ).order_by("-date", "-id")[:10]

    return {
        "recent_transactions": [_serialize_expense(expense) for expense in recent_expenses]
    }


def _get_insights_payload(user):
    return build_smart_insights(user)


@extend_schema_view(
    get=extend_schema(
        tags=["Dashboard"],
        summary="Get dashboard summary",
        responses=DashboardSummarySerializer,
    )
)
class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_get_summary_payload(request.user))


@extend_schema_view(
    get=extend_schema(
        tags=["Dashboard"],
        summary="Get spending trends",
        responses=DashboardTrendsSerializer,
    )
)
class DashboardTrendsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_get_trends_payload(request.user))


@extend_schema_view(
    get=extend_schema(
        tags=["Dashboard"],
        summary="Get category breakdown",
        responses=DashboardCategoriesSerializer,
    )
)
class DashboardCategoriesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_get_categories_payload(request.user))


@extend_schema_view(
    get=extend_schema(
        tags=["Dashboard"],
        summary="Get recent transactions",
        responses=DashboardRecentSerializer,
    )
)
class DashboardRecentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_get_recent_payload(request.user))


@extend_schema_view(
    get=extend_schema(
        tags=["Dashboard"],
        summary="Get smart insights",
        responses=DashboardInsightsSerializer,
    )
)
class DashboardInsightsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_get_insights_payload(request.user))
