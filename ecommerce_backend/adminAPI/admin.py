from django.contrib import admin
from .models import Moderator, Notice, Reward, CouponCode, ExtraPayment


@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):
    list_display = (
        "moderator",
        "phone_number",
        "admin_roles",
    )


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "notice",
        "notice_date",
        "expiry_date",
    )


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = (
        "points",
        "amount",
    )


@admin.register(CouponCode)
class CouponCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount",
        "max_discount",
        "validity",
        "coupon_added",
    )


@admin.register(ExtraPayment)
class ExtraPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "inside_dhaka",
        "outside_dhaka",
    )
