from django.contrib import admin
from .models import Moderator, Notice


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
