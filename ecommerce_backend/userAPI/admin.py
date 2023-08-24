from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "phone_number",
        "user_type",
    )
