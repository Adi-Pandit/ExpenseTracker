from django.conf import settings
from django.db import models
from django.utils.timezone import now
from uuid_extensions import uuid7


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_category_name_per_owner",
            )
        ]

    def __str__(self):
        return self.name


class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    amount = models.FloatField()
    date = models.DateField(default=now)
    notes = models.TextField(blank=True)
    account = models.CharField(max_length=100)
    receipt = models.FileField(upload_to="receipts/", null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )

    def __str__(self):
        return (self.notes or f"{self.amount} expense")[:50]

    class Meta:
        ordering = ["-date", "-id"]
