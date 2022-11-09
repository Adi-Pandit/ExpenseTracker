from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserCategory(models.Model):
    usercategory=models.CharField(max_length=255,primary_key=True)
    owner=models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural="User categories"

    def __str__(self):
        return self.usercategory