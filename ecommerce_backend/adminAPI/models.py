from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Admin(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_admin"
    )
    phone_number = models.IntegerField(blank=True)
    admin_roles = ArrayField(models.CharField(max_length=100), default=list)
    TYPES = (("user", "user"), ("admin", "admin"))
    user_type = models.CharField(max_length=20, choices=TYPES)


class Notice(models.Model):
    notice = models.TextField()
    notice_date = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField()


class rewards(models.Model):
    points = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
