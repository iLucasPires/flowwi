from rest_framework import serializers

from ..models import GoogleDriveConnection


class GoogleDriveConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleDriveConnection
        fields = ["id", "workplace", "connected_by", "folder_id", "is_active", "created_at"]
        read_only_fields = ["connected_by", "created_at", "workplace"]
