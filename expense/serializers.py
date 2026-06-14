from django.utils.timezone import localdate
from drf_spectacular.utils import extend_schema_field
from django.db.models import Q
from rest_framework import serializers

from .currency import convert_amount, normalize_currency_code
from .models import Account, Expense, Category, Notification, RecurringExpense


class RangeFilterSerializer(serializers.Serializer):
    min_amount = serializers.DecimalField(required=False, min_value=0, max_digits=14, decimal_places=2)
    max_amount = serializers.DecimalField(required=False, min_value=0, max_digits=14, decimal_places=2)

    def validate(self, attrs):
        min_amount = attrs.get("min_amount")
        max_amount = attrs.get("max_amount")
        if (
            min_amount is not None
            and max_amount is not None
            and min_amount > max_amount
        ):
            raise serializers.ValidationError(
                {"max_amount": "Maximum amount must be greater than minimum amount."}
            )
        return attrs


class ExpenseFilterSerializer(RangeFilterSerializer):
    category = serializers.UUIDField(required=False)
    account = serializers.UUIDField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    date_from = serializers.DateField(required=False, write_only=True)
    date_to = serializers.DateField(required=False, write_only=True)
    search = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        start_date = attrs.get("start_date") or attrs.get("date_from")
        end_date = attrs.get("end_date") or attrs.get("date_to")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": "End date must not be earlier than start date."}
            )
        attrs["start_date"] = start_date
        attrs["end_date"] = end_date
        attrs.pop("date_from", None)
        attrs.pop("date_to", None)
        return attrs


class RecurringExpenseFilterSerializer(RangeFilterSerializer):
    is_active = serializers.BooleanField(required=False)
    frequency = serializers.ChoiceField(
        choices=RecurringExpense.Frequency.choices, required=False
    )
    category = serializers.UUIDField(required=False)
    account = serializers.UUIDField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    search = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": "End date must not be earlier than start date."}
            )
        return attrs


class AccountFilterSerializer(serializers.Serializer):
    account_type = serializers.ChoiceField(
        choices=Account.AccountType.choices, required=False
    )
    min_balance = serializers.DecimalField(required=False, max_digits=14, decimal_places=2)
    max_balance = serializers.DecimalField(required=False, max_digits=14, decimal_places=2)
    search = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        min_balance = attrs.get("min_balance")
        max_balance = attrs.get("max_balance")
        if (
            min_balance is not None
            and max_balance is not None
            and min_balance > max_balance
        ):
            raise serializers.ValidationError(
                {"max_balance": "Maximum balance must be greater than minimum balance."}
            )
        return attrs


class NotificationFilterSerializer(serializers.Serializer):
    is_read = serializers.BooleanField(required=False)
    notification_type = serializers.ChoiceField(
        choices=Notification.NotificationType.choices, required=False
    )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "owner"]
        read_only_fields = ["owner"]


class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "account_type",
            "opening_balance",
            "current_balance",
            "owner",
        ]
        read_only_fields = ["owner", "current_balance"]

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Account name is required.")
        return cleaned

    def validate_opening_balance(self, value):
        return value

    def validate(self, attrs):
        owner = self.context["request"].user
        name = attrs.get("name", getattr(self.instance, "name", None))
        if not name:
            return attrs

        queryset = Account.objects.filter(owner=owner, name__iexact=name.strip())
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                {"name": "You already have an account with this name."}
            )
        return attrs


class ExpenseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(), allow_null=True, required=False
    )
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.none())
    category_name = serializers.CharField(source="category.name", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)
    owner_base_currency = serializers.CharField(source="owner.base_currency", read_only=True)
    receipt = serializers.FileField(required=False, allow_null=True)
    receipt_path = serializers.CharField(source="receipt.name", read_only=True)
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id",
            "amount",
            "currency",
            "exchange_rate",
            "converted_amount",
            "owner_base_currency",
            "account",
            "account_name",
            "date",
            "notes",
            "receipt",
            "receipt_path",
            "receipt_url",
            "category",
            "category_name",
            "owner",
        ]
        read_only_fields = [
            "owner",
            "exchange_rate",
            "converted_amount",
            "owner_base_currency",
            "receipt_path",
            "receipt_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        category_queryset = Category.objects.all()
        account_queryset = Account.objects.all()
        if request and request.user and request.user.is_authenticated:
            category_queryset = Category.objects.filter(
                Q(owner=None) | Q(owner=request.user)
            )
            account_queryset = Account.objects.filter(owner=request.user)
        self.fields["category"].queryset = category_queryset
        self.fields["account"].queryset = account_queryset

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_currency(self, value):
        return normalize_currency_code(value)

    def validate_notes(self, value):
        return value.strip()

    def validate_date(self, value):
        if value > localdate():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value

    def validate_receipt(self, value):
        if not value:
            return value

        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Receipt file size must not exceed 5 MB.")
        return value

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_receipt_url(self, obj):
        if not obj.receipt:
            return None
        request = self.context.get("request")
        url = obj.receipt.url
        return request.build_absolute_uri(url) if request else url

    def _apply_currency_conversion(self, validated_data, instance=None):
        request = self.context["request"]
        owner = request.user
        currency = validated_data.get(
            "currency", getattr(instance, "currency", owner.base_currency)
        )
        currency = normalize_currency_code(currency)
        amount = validated_data.get("amount", getattr(instance, "amount", None))
        if amount is None:
            return validated_data

        try:
            exchange_rate, converted_amount = convert_amount(
                amount, currency, owner.base_currency
            )
        except ValueError as exc:
            raise serializers.ValidationError({"currency": str(exc)}) from exc

        validated_data["currency"] = currency
        validated_data["exchange_rate"] = exchange_rate
        validated_data["converted_amount"] = converted_amount
        return validated_data

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        validated_data = self._apply_currency_conversion(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._apply_currency_conversion(validated_data, instance=instance)
        return super().update(instance, validated_data)


class RecurringExpenseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(), allow_null=True, required=False
    )
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.none())
    category_name = serializers.CharField(source="category.name", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)
    owner_base_currency = serializers.CharField(source="owner.base_currency", read_only=True)

    class Meta:
        model = RecurringExpense
        fields = [
            "id",
            "amount",
            "currency",
            "owner_base_currency",
            "account",
            "account_name",
            "category",
            "category_name",
            "notes",
            "frequency",
            "start_date",
            "next_run_date",
            "last_generated_date",
            "is_active",
            "owner",
        ]
        read_only_fields = ["owner", "last_generated_date", "owner_base_currency"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        category_queryset = Category.objects.all()
        account_queryset = Account.objects.all()
        if request and request.user and request.user.is_authenticated:
            category_queryset = Category.objects.filter(
                Q(owner=None) | Q(owner=request.user)
            )
            account_queryset = Account.objects.filter(owner=request.user)
        self.fields["category"].queryset = category_queryset
        self.fields["account"].queryset = account_queryset

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_currency(self, value):
        return normalize_currency_code(value)

    def validate_notes(self, value):
        return value.strip()

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        next_run_date = attrs.get(
            "next_run_date", getattr(self.instance, "next_run_date", None)
        )

        if start_date and next_run_date and next_run_date < start_date:
            raise serializers.ValidationError(
                {"next_run_date": "Next run date cannot be earlier than start date."}
            )

        return attrs

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    expense_id = serializers.UUIDField(source="expense.id", read_only=True)
    recurring_expense_id = serializers.UUIDField(
        source="recurring_expense.id", read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "created_at",
            "read_at",
            "expense_id",
            "recurring_expense_id",
        ]
        read_only_fields = fields
