from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from apps.common.streaming.publisher import publish_resource_changed
from apps.domains.inbox.models import InboxType
from apps.domains.inbox.services import InboxService
from apps.domains.workplace.models import Workplace, WorkplaceMember
from lib.utils.fractional_indexing import generate_n_keys_between

from .models import Task, TaskStatus, TaskStatusCategory, TaskType

DEFAULT_STATUSES = [
    ("A fazer", TaskStatusCategory.TODO, "#a3a3a3", "i-lucide-circle-dashed"),
    ("Em progresso", TaskStatusCategory.IN_PROGRESS, "#60a5fa", "i-lucide-circle-stop"),
    ("Em revisão", TaskStatusCategory.IN_PROGRESS, "#eab308", "i-lucide-eye"),
    ("Concluído", TaskStatusCategory.DONE, "#4ade80", "i-lucide-circle-check"),
    ("Cancelado", TaskStatusCategory.CANCELLED, "#f87171", "i-lucide-circle-x"),
]

DEFAULT_TYPES = [
    ("Arte", "#c084fc", "i-lucide-palette"),
    ("Post", "#60a5fa", "i-lucide-send"),
    ("Reunião", "#4ade80", "i-lucide-video"),
    ("Conteúdo", "#eab308", "i-lucide-file-text"),
    ("Outro", "#a3a3a3", "i-lucide-box"),
]


@receiver(post_save, sender=Workplace)
def seed_task_defaults(sender, instance, created, **kwargs):
    if not created:
        return

    status_positions = generate_n_keys_between(None, None, len(DEFAULT_STATUSES))
    TaskStatus.objects.bulk_create(
        TaskStatus(
            workplace=instance,
            name=name,
            category=category,
            color=color,
            icon=icon,
            position=position,
        )
        for (name, category, color, icon), position in zip(DEFAULT_STATUSES, status_positions, strict=True)
    )

    type_positions = generate_n_keys_between(None, None, len(DEFAULT_TYPES))
    TaskType.objects.bulk_create(
        TaskType(
            workplace=instance,
            name=name,
            color=color,
            icon=icon,
            position=position,
        )
        for (name, color, icon), position in zip(DEFAULT_TYPES, type_positions, strict=True)
    )


@receiver(post_save, sender=Task)
def notify_task_changed(sender, instance, created, **kwargs):
    action = "deleted" if instance.deleted_at else ("created" if created else "updated")
    publish_resource_changed(instance.workplace_id, "task", action, instance.public_id)


@receiver(post_delete, sender=Task)
def notify_task_purged(sender, instance, **kwargs):
    publish_resource_changed(instance.workplace_id, "task", "deleted", instance.public_id)


@receiver(m2m_changed, sender=Task.assignees.through)
def notify_task_assigned(sender, instance, action, pk_set, **kwargs):
    if action != "post_add" or not pk_set:
        return

    assignees = WorkplaceMember.objects.filter(pk__in=pk_set)
    for assignee in assignees:
        InboxService().send_inbox(
            member=assignee,
            title=f"Tarefa atribuída: {instance.title}",
            message=instance.description or instance.title,
            type=InboxType.TASK_ASSIGNED,
        )
