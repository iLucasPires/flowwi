from django.contrib import admin

from .models import QuickLink


@admin.register(QuickLink)
class QuickLinkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "url",
        "workplace",
        "created_by",
        "created_at",
    )
    list_filter = (
        "workplace",
        "created_at",
    )
    search_fields = ("title", "url")
