from django.contrib import admin
from .models import Consumer, Wishlist, OrderedProduct


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
    pass
