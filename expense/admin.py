from django.contrib import admin

from .models import Account, Category, Expense, Notification, RecurringExpense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]
    list_filter = ["owner"]
    search_fields = ["name"]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "account_type", "opening_balance", "owner"]
    list_filter = ["account_type", "owner"]
    search_fields = ["name", "owner__username", "owner__email"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["__str__", "amount", "currency", "converted_amount", "date", "category", "account", "owner"]
    list_filter = ["currency", "category", "account", "owner"]
    search_fields = ["notes", "owner__username", "owner__email", "category__name", "account__name"]
    date_hierarchy = "date"
    readonly_fields = ["exchange_rate", "converted_amount"]


@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ["__str__", "amount", "currency", "frequency", "next_run_date", "is_active", "owner"]
    list_filter = ["frequency", "is_active", "owner"]
    search_fields = ["notes", "owner__username", "owner__email", "account__name"]
    readonly_fields = ["last_generated_date"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "notification_type", "owner", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read", "owner"]
    search_fields = ["title", "message", "owner__username", "owner__email"]
    readonly_fields = ["created_at", "read_at", "dedupe_key"]
