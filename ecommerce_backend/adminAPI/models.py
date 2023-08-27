from django.db import models

# from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.conf import settings


class Moderator(models.Model):
    moderator = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moderator"
    )
    phone_number = models.BigIntegerField(blank=True)
    admin_roles = ArrayField(models.CharField(max_length=100), default=list)

    def __str__(self) -> str:
        return self.admin.email


class Notice(models.Model):
    notice = models.TextField()
    notice_date = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField()


class rewards(models.Model):
    points = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
