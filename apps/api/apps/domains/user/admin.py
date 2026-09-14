from django.contrib import admin

from .models import Profile

admin.site.register(Profile)


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "photo",
        "cover",
        "created_at",
        "updated_at",
    )
