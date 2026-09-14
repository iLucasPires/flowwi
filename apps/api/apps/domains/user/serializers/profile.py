from rest_framework import serializers

from ..models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
    )

    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "photo",
            "cover",
            "cover_style",
            "cover_credit",
            "username",
            "email",
            "full_name",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        instance = super().update(instance, validated_data)

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)

            instance.user.save(update_fields=list(user_data.keys()))

        return instance
