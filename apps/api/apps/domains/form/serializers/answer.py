from rest_framework import serializers

from ..models import FormAnswer


class FormAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAnswer
        fields = [
            "id",
            "block",
            "value",
        ]
