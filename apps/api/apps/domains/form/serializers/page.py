from rest_framework import serializers

from ..models import FormPage


class FormPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormPage
        fields = [
            "id",
            "form",
            "title",
            "description",
            "order",
        ]
