from django.contrib import admin
from .models import Consumer, Wishlist, OrderedProduct, OrderPackageTrack


@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = (
        "consumer",
        "name",
        "phone_number",
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "consumer",
        "product",
        "wishlisted_date",
    )


@admin.register(OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    list_display = (
        "consumer",
        "product",
        "total_price",
    )


@admin.register(OrderPackageTrack)
class OrderPackageTrackAdmin(admin.ModelAdmin):
    list_display = ("tracking_id",)
