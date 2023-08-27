from django.contrib import admin
from .models import Consumer


@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = (
        "consumer",
        "name",
        "phone_number",
    )
