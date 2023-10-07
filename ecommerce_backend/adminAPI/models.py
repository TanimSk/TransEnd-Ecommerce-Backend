from django.db import models

# from django.contrib.auth.models import User
from django.conf import settings


class Moderator(models.Model):
    moderator = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moderator"
    )
    phone_number = models.CharField(max_length=100, blank=True)
    admin_roles = models.TextField(default="[]")

    def __str__(self) -> str:
        return self.moderator.email


class BookedCall(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    book_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.phone_number


class Notice(models.Model):
    notice = models.TextField()
    notice_date = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField()


class CouponCode(models.Model):
    code = models.CharField(max_length=50)
    discount_bdt = models.IntegerField()
    validity = models.IntegerField()
    min_price = models.IntegerField(blank=True, null=True)
    coupon_added = models.DateField(auto_now=True)


class Reward(models.Model):
    points = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    max_amount = models.IntegerField(default=0)


class ExtraPayment(models.Model):
    inside_dhaka = models.IntegerField(default=0)
    outside_dhaka = models.IntegerField(default=0)
