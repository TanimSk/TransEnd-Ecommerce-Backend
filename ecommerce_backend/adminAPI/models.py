from django.db import models

# from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.conf import settings


class Moderator(models.Model):
    moderator = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moderator"
    )
    phone_number = models.CharField(max_length=100, blank=True)
    admin_roles = ArrayField(models.CharField(max_length=100), default=list)

    def __str__(self) -> str:
        return self.admin.email


class BookedCalls(models.Model):
    phone_number = models.CharField(max_length=100)
    book_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.phone_number


class Notice(models.Model):
    notice = models.TextField()
    notice_date = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField()


class CouponCode(models.Model):
    code = models.CharField(max_length=50)
    discount = models.IntegerField()
    validity = models.IntegerField()
    max_discount = models.IntegerField(blank=True, null=True)
    coupon_added = models.DateField(auto_now=True)


class Reward(models.Model):
    points = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    max_amount = models.IntegerField(default=0)


class ExtraPayment(models.Model):
    inside_dhaka = models.IntegerField(default=0)
    outside_dhaka = models.IntegerField(default=0)
