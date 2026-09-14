from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm, remove_perm

from apps.common.streaming.publisher import publish_resource_changed
from apps.domains.workplace.models import Workplace
from apps.domains.workplace.utils import get_workplace_members_group
from lib.utils.fractional_indexing import generate_n_keys_between

from .models import Document, DocumentType, DocumentVisibility

DEFAULT_TYPES = [
    (
        "Roteiro",
        "#60a5fa",
        "i-lucide-clapperboard",
        "## Cold open\n\n## Bloco 1\n\n## Bloco 2\n\n## Encerramento e chamada",
    ),
    (
        "Cliente",
        "#c084fc",
        "i-lucide-briefcase",
        "## Objetivo\n\n## Direção de arte\n\n## Entregáveis\n\n## Produção e prazos",
    ),
]


@receiver(post_save, sender=Workplace)
def seed_document_defaults(sender, instance, created, **kwargs):
    if not created:
        return

    positions = generate_n_keys_between(None, None, len(DEFAULT_TYPES))
    DocumentType.objects.bulk_create(
        DocumentType(
            workplace=instance,
            name=name,
            color=color,
            icon=icon,
            default_content=default_content,
            position=position,
        )
        for (name, color, icon, default_content), position in zip(
            DEFAULT_TYPES,
            positions,
            strict=True,
        )
    )


@receiver(post_save, sender=Document)
def sync_document_permissions(sender, instance: Document, **kwargs):
    """
    Keeps django-guardian's per-object permissions in step with `visibility`/
    `allow_member_edit`. The author always keeps direct view/change permissions;
    the workplace's Group (kept in sync by `apps.workplace.signals`) only gets them
    while the document is shared that way — runs on every save, but `assign_perm`/
    `remove_perm` are no-ops when the grant is already in the state it should be.

    Workplace admins (owner/manager) are *not* modeled here — they bypass this
    entirely via `DocumentObjectPermission`, since that's a role-based override, not
    a per-object grant.
    """
    if instance.author_id:
        assign_perm("view_document", instance.author, instance)
        assign_perm("change_document", instance.author, instance)

    if not instance.workplace_id:
        return

    group = get_workplace_members_group(instance.workplace_id)
    is_shared = instance.visibility == DocumentVisibility.WORKPLACE

    (assign_perm if is_shared else remove_perm)("view_document", group, instance)

    grant_member_edit = is_shared and instance.allow_member_edit
    (assign_perm if grant_member_edit else remove_perm)("change_document", group, instance)


@receiver(post_save, sender=Document)
def notify_document_list_changed(sender, instance: Document, created, **kwargs):
    if not instance.workplace_id:
        return
    publish_resource_changed(
        instance.workplace_id,
        "document",
        "created" if created else "updated",
        instance.id,
    )


@receiver(post_delete, sender=Document)
def notify_document_purged(sender, instance: Document, **kwargs):
    if not instance.workplace_id:
        return
    publish_resource_changed(instance.workplace_id, "document", "deleted", instance.id)
