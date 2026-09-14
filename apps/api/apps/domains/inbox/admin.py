from django.contrib import admin

from .models import Inbox


@admin.register(Inbox)
class InboxAdmin(admin.ModelAdmin):
    list_display = ["title", "member", "sender", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read"]
