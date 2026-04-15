from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer
from .services import (
    export_expenses_to_csv,
    export_expenses_to_excel,
    export_expenses_to_pdf,
    get_user_expense_stats,
)


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(
        summary="List expenses or create a new expense",
        parameters=[
            OpenApiParameter(name="category", type=str, location=OpenApiParameter.QUERY, description="Filter by category UUID"),
            OpenApiParameter(name="account", type=str, location=OpenApiParameter.QUERY, description="Filter by account name"),
            OpenApiParameter(name="date_from", type=str, location=OpenApiParameter.QUERY, description="Filter expenses from this date (YYYY-MM-DD)"),
            OpenApiParameter(name="date_to", type=str, location=OpenApiParameter.QUERY, description="Filter expenses up to this date (YYYY-MM-DD)"),
            OpenApiParameter(name="min_amount", type=float, location=OpenApiParameter.QUERY, description="Minimum amount"),
            OpenApiParameter(name="max_amount", type=float, location=OpenApiParameter.QUERY, description="Maximum amount"),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Expense.objects.filter(owner=self.request.user).select_related("category")
        params = self.request.query_params

        category = params.get("category")
        account = params.get("account")
        date_from = params.get("date_from")
        date_to = params.get("date_to")
        min_amount = params.get("min_amount")
        max_amount = params.get("max_amount")

        if category:
            queryset = queryset.filter(category_id=category)
        if account:
            queryset = queryset.filter(account__icontains=account.strip())
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return Expense.objects.filter(owner=self.request.user).select_related("category")


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(Q(owner=None) | Q(owner=self.request.user))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)


class ExpenseStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get expense statistics",
        responses={200: OpenApiResponse(description="Aggregated expense statistics")},
    )
    def get(self, request):
        return Response(get_user_expense_stats(request.user))


class ExpenseExportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Export expenses",
        parameters=[
            OpenApiParameter(
                name="format_type",
                type=str,
                location=OpenApiParameter.PATH,
                enum=["csv", "excel", "pdf"],
                description="Export format",
            )
        ],
        responses={
            200: OpenApiResponse(description="Exported expense file"),
            400: OpenApiResponse(description="Invalid export format"),
        },
    )
    def get(self, request, format_type):
        expenses = Expense.objects.filter(owner=request.user).select_related("category")

        if format_type == "csv":
            return export_expenses_to_csv(expenses)
        if format_type == "excel":
            return export_expenses_to_excel(expenses)
        if format_type == "pdf":
            return export_expenses_to_pdf(expenses)
        return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)
