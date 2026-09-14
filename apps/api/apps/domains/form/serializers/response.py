from rest_framework import serializers

from ..models import FormAnswer, FormResponse


class FormAnswerInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAnswer
        fields = [
            "id",
            "block",
            "value",
        ]
        read_only_fields = ["id"]


class FormResponseSerializer(serializers.ModelSerializer):
    answers = FormAnswerInlineSerializer(many=True)

    class Meta:
        model = FormResponse
        fields = [
            "id",
            "form",
            "created_at",
            "answers",
            "respondent_email",
            "respondent_phone",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        response = FormResponse.objects.create(**validated_data)

        FormAnswer.objects.bulk_create(
            [
                FormAnswer(
                    response=response,
                    **data,
                )
                for data in answers_data
            ]
        )

        return response
