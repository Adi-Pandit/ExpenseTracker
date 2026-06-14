from rest_framework import serializers


class DashboardTopCategorySerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=True)
    amount = serializers.FloatField()


class DashboardMonthSpendSerializer(serializers.Serializer):
    label = serializers.CharField()
    total_spend = serializers.FloatField()


class DashboardExpenseItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    amount = serializers.FloatField()
    currency = serializers.CharField()
    converted_amount = serializers.FloatField()
    base_currency = serializers.CharField()
    date = serializers.DateField()
    notes = serializers.CharField()
    category = serializers.CharField(allow_null=True)
    account = serializers.CharField(allow_null=True)


class DashboardAccountBalanceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    type = serializers.CharField()
    opening_balance = serializers.FloatField()
    current_balance = serializers.FloatField()


class DashboardSummarySerializer(serializers.Serializer):
    current_month = DashboardMonthSpendSerializer()
    last_month = DashboardMonthSpendSerializer()
    percent_change = serializers.FloatField()
    top_category = DashboardTopCategorySerializer()
    top_expenses = DashboardExpenseItemSerializer(many=True)
    account_balances = DashboardAccountBalanceSerializer(many=True)


class DashboardTrendPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    amount = serializers.FloatField()


class DashboardTrendsSerializer(serializers.Serializer):
    period = serializers.CharField()
    daily_expenses = DashboardTrendPointSerializer(many=True)


class DashboardCategoryItemSerializer(serializers.Serializer):
    category = serializers.CharField()
    amount = serializers.FloatField()
    percentage = serializers.FloatField()


class DashboardCategoriesSerializer(serializers.Serializer):
    period = serializers.CharField()
    total_spend = serializers.FloatField()
    breakdown = DashboardCategoryItemSerializer(many=True)


class DashboardRecentSerializer(serializers.Serializer):
    recent_transactions = DashboardExpenseItemSerializer(many=True)


class DashboardInsightItemSerializer(serializers.Serializer):
    rule = serializers.CharField()
    message = serializers.CharField()
    severity = serializers.CharField()


class DashboardInsightsSerializer(serializers.Serializer):
    period = serializers.CharField()
    insights = DashboardInsightItemSerializer(many=True)
