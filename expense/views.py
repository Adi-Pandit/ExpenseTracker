from decimal import Decimal

from django.db.models import F, Q, Sum, Value
from django.db.models.deletion import ProtectedError
from django.db.models.functions import Coalesce
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account, Category, Expense, Notification, RecurringExpense
from .serializers import (
    AccountFilterSerializer,
    AccountSerializer,
    CategorySerializer,
    ExpenseFilterSerializer,
    ExpenseSerializer,
    NotificationFilterSerializer,
    NotificationSerializer,
    RecurringExpenseFilterSerializer,
    RecurringExpenseSerializer,
)
from .services import (
    export_expenses_to_csv,
    export_expenses_to_excel,
    export_expenses_to_pdf,
    get_user_expense_stats,
    mark_notification_as_read,
    process_expense_notifications,
)


def get_filtered_expense_queryset(request):
    queryset = Expense.objects.filter(owner=request.user).select_related(
        "category", "account"
    )
    filters = ExpenseFilterSerializer(data=request.query_params)
    filters.is_valid(raise_exception=True)
    values = filters.validated_data

    if category := values.get("category"):
        queryset = queryset.filter(category_id=category)
    if account := values.get("account"):
        queryset = queryset.filter(account_id=account)
    if start_date := values.get("start_date"):
        queryset = queryset.filter(date__gte=start_date)
    if end_date := values.get("end_date"):
        queryset = queryset.filter(date__lte=end_date)
    if (min_amount := values.get("min_amount")) is not None:
        queryset = queryset.filter(amount__gte=min_amount)
    if (max_amount := values.get("max_amount")) is not None:
        queryset = queryset.filter(amount__lte=max_amount)
    if search := values.get("search"):
        queryset = queryset.filter(
            Q(notes__icontains=search)
            | Q(category__name__icontains=search)
            | Q(account__name__icontains=search)
        )

    return queryset


@extend_schema_view(
    get=extend_schema(tags=["Expenses"]),
    post=extend_schema(tags=["Expenses"]),
)
class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(
        summary="List expenses or create a new expense",
        tags=["Expenses"],
        parameters=[
            OpenApiParameter(name="category", type=str, location=OpenApiParameter.QUERY, description="Filter by category UUID"),
            OpenApiParameter(name="account", type=str, location=OpenApiParameter.QUERY, description="Filter by account UUID"),
            OpenApiParameter(name="start_date", type=str, location=OpenApiParameter.QUERY, description="Filter expenses from this date (YYYY-MM-DD)"),
            OpenApiParameter(name="end_date", type=str, location=OpenApiParameter.QUERY, description="Filter expenses up to this date (YYYY-MM-DD)"),
            OpenApiParameter(name="min_amount", type=float, location=OpenApiParameter.QUERY, description="Minimum amount"),
            OpenApiParameter(name="max_amount", type=float, location=OpenApiParameter.QUERY, description="Maximum amount"),
            OpenApiParameter(name="search", type=str, location=OpenApiParameter.QUERY, description="Search notes, category, or account"),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return get_filtered_expense_queryset(self.request)

    def perform_create(self, serializer):
        expense = serializer.save(owner=self.request.user)
        process_expense_notifications(expense)


@extend_schema_view(
    get=extend_schema(tags=["Expenses"]),
    put=extend_schema(tags=["Expenses"]),
    patch=extend_schema(tags=["Expenses"]),
    delete=extend_schema(tags=["Expenses"]),
)
class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return Expense.objects.filter(owner=self.request.user).select_related(
            "category", "account"
        )


@extend_schema_view(
    get=extend_schema(tags=["Accounts"]),
    post=extend_schema(tags=["Accounts"]),
)
class AccountListCreateView(generics.ListCreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List accounts or create an account",
        tags=["Accounts"],
        parameters=[
            OpenApiParameter(name="account_type", type=str, location=OpenApiParameter.QUERY, description="Filter by account type"),
            OpenApiParameter(name="min_balance", type=float, location=OpenApiParameter.QUERY, description="Minimum current balance"),
            OpenApiParameter(name="max_balance", type=float, location=OpenApiParameter.QUERY, description="Maximum current balance"),
            OpenApiParameter(name="search", type=str, location=OpenApiParameter.QUERY, description="Search account name"),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Account.objects.filter(owner=self.request.user).annotate(
            spent=Coalesce(Sum("expenses__converted_amount"), Value(Decimal("0"))),
            current_balance=F("opening_balance")
            - Coalesce(Sum("expenses__converted_amount"), Value(Decimal("0"))),
        )
        filters = AccountFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        values = filters.validated_data

        if account_type := values.get("account_type"):
            queryset = queryset.filter(account_type=account_type)
        if search := values.get("search"):
            queryset = queryset.filter(name__icontains=search)
        if (min_balance := values.get("min_balance")) is not None:
            queryset = queryset.filter(current_balance__gte=min_balance)
        if (max_balance := values.get("max_balance")) is not None:
            queryset = queryset.filter(current_balance__lte=max_balance)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    get=extend_schema(tags=["Accounts"]),
    put=extend_schema(tags=["Accounts"]),
    patch=extend_schema(tags=["Accounts"]),
    delete=extend_schema(tags=["Accounts"]),
)
class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"error": "This account cannot be deleted because it has existing expenses linked to it."},
                status=status.HTTP_409_CONFLICT,
            )


@extend_schema_view(
    get=extend_schema(tags=["Recurring"]),
    post=extend_schema(tags=["Recurring"]),
)
class RecurringExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = RecurringExpenseSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List recurring expenses or create a recurring expense",
        tags=["Recurring"],
        parameters=[
            OpenApiParameter(name="is_active", type=bool, location=OpenApiParameter.QUERY, description="Filter by active status"),
            OpenApiParameter(name="frequency", type=str, location=OpenApiParameter.QUERY, description="Filter by frequency"),
            OpenApiParameter(name="category", type=str, location=OpenApiParameter.QUERY, description="Filter by category UUID"),
            OpenApiParameter(name="account", type=str, location=OpenApiParameter.QUERY, description="Filter by account UUID"),
            OpenApiParameter(name="start_date", type=str, location=OpenApiParameter.QUERY, description="Filter recurring expenses starting from this date"),
            OpenApiParameter(name="end_date", type=str, location=OpenApiParameter.QUERY, description="Filter recurring expenses up to this date"),
            OpenApiParameter(name="min_amount", type=float, location=OpenApiParameter.QUERY, description="Minimum amount"),
            OpenApiParameter(name="max_amount", type=float, location=OpenApiParameter.QUERY, description="Maximum amount"),
            OpenApiParameter(name="search", type=str, location=OpenApiParameter.QUERY, description="Search notes or category"),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = RecurringExpense.objects.filter(owner=self.request.user).select_related(
            "category", "account"
        )
        filters = RecurringExpenseFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        values = filters.validated_data

        if "is_active" in self.request.query_params and (is_active := values.get("is_active")) is not None:
            queryset = queryset.filter(is_active=is_active)
        if frequency := values.get("frequency"):
            queryset = queryset.filter(frequency=frequency)
        if category := values.get("category"):
            queryset = queryset.filter(category_id=category)
        if account := values.get("account"):
            queryset = queryset.filter(account_id=account)
        if start_date := values.get("start_date"):
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date := values.get("end_date"):
            queryset = queryset.filter(start_date__lte=end_date)
        if (min_amount := values.get("min_amount")) is not None:
            queryset = queryset.filter(amount__gte=min_amount)
        if (max_amount := values.get("max_amount")) is not None:
            queryset = queryset.filter(amount__lte=max_amount)
        if search := values.get("search"):
            queryset = queryset.filter(
                Q(notes__icontains=search)
                | Q(category__name__icontains=search)
                | Q(account__name__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    get=extend_schema(tags=["Recurring"]),
    put=extend_schema(tags=["Recurring"]),
    patch=extend_schema(tags=["Recurring"]),
    delete=extend_schema(tags=["Recurring"]),
)
class RecurringExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecurringExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecurringExpense.objects.filter(owner=self.request.user).select_related(
            "category", "account"
        )


@extend_schema_view(
    get=extend_schema(tags=["Categories"]),
    post=extend_schema(tags=["Categories"]),
)
class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(Q(owner=None) | Q(owner=self.request.user))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    get=extend_schema(tags=["Categories"]),
    put=extend_schema(tags=["Categories"]),
    patch=extend_schema(tags=["Categories"]),
    delete=extend_schema(tags=["Categories"]),
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)


@extend_schema_view(get=extend_schema(tags=["Notifications"]))
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List notifications",
        tags=["Notifications"],
        parameters=[
            OpenApiParameter(name="is_read", type=bool, location=OpenApiParameter.QUERY, description="Filter by read status"),
            OpenApiParameter(name="notification_type", type=str, location=OpenApiParameter.QUERY, description="Filter by notification type"),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Notification.objects.filter(owner=self.request.user)
        filters = NotificationFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        values = filters.validated_data

        if "is_read" in self.request.query_params and (is_read := values.get("is_read")) is not None:
            queryset = queryset.filter(is_read=is_read)
        if notification_type := values.get("notification_type"):
            queryset = queryset.filter(notification_type=notification_type)

        return queryset


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    @extend_schema(
        summary="Mark a notification as read",
        tags=["Notifications"],
        responses={200: NotificationSerializer},
    )
    def put(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, owner=request.user)
        notification = mark_notification_as_read(notification)
        return Response(NotificationSerializer(notification).data)


class ExpenseStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get expense statistics",
        tags=["Expenses"],
        responses={200: OpenApiResponse(description="Aggregated expense statistics")},
    )
    def get(self, request):
        return Response(get_user_expense_stats(request.user))


class ExpenseExportView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Export expenses",
        tags=["Expenses"],
        operation_id="export_expenses",
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                location=OpenApiParameter.QUERY,
                enum=["csv", "excel", "pdf"],
                description="Export format",
            ),
            OpenApiParameter(name="category", type=str, location=OpenApiParameter.QUERY, description="Filter by category UUID or name"),
            OpenApiParameter(name="account", type=str, location=OpenApiParameter.QUERY, description="Filter by account UUID or name"),
            OpenApiParameter(name="start_date", type=str, location=OpenApiParameter.QUERY, description="Filter expenses from this date (YYYY-MM-DD)"),
            OpenApiParameter(name="end_date", type=str, location=OpenApiParameter.QUERY, description="Filter expenses up to this date (YYYY-MM-DD)"),
            OpenApiParameter(name="min_amount", type=float, location=OpenApiParameter.QUERY, description="Minimum amount"),
            OpenApiParameter(name="max_amount", type=float, location=OpenApiParameter.QUERY, description="Maximum amount"),
            OpenApiParameter(name="search", type=str, location=OpenApiParameter.QUERY, description="Search notes, category, or account"),
        ],
        responses={
            200: OpenApiResponse(description="Exported expense file"),
            400: OpenApiResponse(description="Invalid export format"),
        },
    )
    def get(self, request, format_type=None):
        export_type = request.query_params.get("type") or format_type
        expenses = get_filtered_expense_queryset(request)

        if export_type == "csv":
            return export_expenses_to_csv(expenses)
        if export_type == "excel":
            return export_expenses_to_excel(expenses)
        if export_type == "pdf":
            return export_expenses_to_pdf(expenses)
        return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)
