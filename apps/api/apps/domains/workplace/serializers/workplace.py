from django.db import transaction
from django.utils.text import slugify
from rest_framework import serializers

from ..exceptions import WorkplaceNameAlreadyExists
from ..models import Workplace, WorkplaceMember, WorkplaceMemberRole
from ..services import WorkplaceService


class WorkplaceSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.workplace_service = WorkplaceService()

    class Meta:
        model = Workplace
        fields = [
            "id",
            "public_id",
            "name",
            "slug",
            "photo",
            "cover_style",
            "cover_credit",
            "is_active",
            "invite_key",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "slug",
            "invite_key",
        ]

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]

        user = request.user
        slug = slugify(validated_data["name"])

        if self.workplace_service.exists(slug=slug, deleted_at__isnull=True):
            raise WorkplaceNameAlreadyExists()

        validated_data["slug"] = slug
        workplace = super().create(validated_data)

        WorkplaceMember.objects.create(
            user=user,
            workplace=workplace,
            role=WorkplaceMemberRole.OWNER,
        )

        return workplace
