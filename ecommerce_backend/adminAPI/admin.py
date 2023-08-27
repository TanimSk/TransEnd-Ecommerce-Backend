from django.contrib import admin
from .models import Moderator


@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):
    list_display = (
        "moderator",
        "phone_number",
        "admin_roles",
    )
