from unicodedata import category
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# Create your models here.
class Budget(models.Model):
    month=models.CharField(max_length=255)
    year=models.IntegerField(default=0)
    owner=models.ForeignKey(to=User, on_delete=models.CASCADE)

class Budget_amount(models.Model):
    category = models.CharField(max_length=255)
    amount = models.FloatField()
    budget_id = models.IntegerField()

    def __str__(self):
        return self.category