from django.contrib import admin

from .models import SubTask, Task, TaskStatus, TaskTag, TaskType


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workplace",
        "title",
        "type",
        "status",
        "priority",
        "position",
        "origin",
        "deadline",
        "completed_at",
        "created_by",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "type",
        "status",
        "priority",
        "origin",
        "deadline",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "title",
        "description",
    )


@admin.register(TaskTag)
class TaskTagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "color",
        "workplace",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "workplace",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "color",
        "position",
        "workplace",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "category",
        "workplace",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "color",
        "position",
        "workplace",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "workplace",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "title",
        "is_done",
        "assignee",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_done",
        "created_at",
        "updated_at",
    )
    search_fields = ("title",)
