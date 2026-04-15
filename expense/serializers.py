from django.utils.timezone import localdate
from django.db.models import Q
from rest_framework import serializers

from .models import Expense, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "owner"]
        read_only_fields = ["owner"]


class ExpenseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.none())
    category_name = serializers.CharField(source="category.name", read_only=True)
    receipt = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "amount",
            "account",
            "date",
            "notes",
            "receipt",
            "category",
            "category_name",
            "owner",
        ]
        read_only_fields = ["owner"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        queryset = Category.objects.all()
        if request and request.user and request.user.is_authenticated:
            queryset = Category.objects.filter(Q(owner=None) | Q(owner=request.user))
        self.fields["category"].queryset = queryset

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_account(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Account is required.")
        return cleaned

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

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
