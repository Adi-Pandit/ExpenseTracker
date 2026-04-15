from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid_extensions import uuid7


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
