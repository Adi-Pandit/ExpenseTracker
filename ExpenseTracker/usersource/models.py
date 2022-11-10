from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserSource(models.Model):
    usersource=models.CharField(max_length=255,primary_key=True)
    owner=models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural="User sources"

    def __str__(self):
        return self.usersource