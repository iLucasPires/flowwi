from django.core.exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError

from ..schemas import BLOCK_CONFIG_SCHEMAS, ConditionSchema


def validate_form_config(block_type: str, config: dict):
    schema = BLOCK_CONFIG_SCHEMAS.get(block_type)

    if not schema:
        raise ValidationError(f"Tipo não suportado: {block_type}")

    try:
        schema.model_validate({**config, "type": block_type})
    except PydanticValidationError as e:
        raise ValidationError(e.errors()) from e


def validate_form_condition(condition: dict):
    if not condition:
        return

    # Support legacy `client_id` key
    data = dict(condition)
    if "client_id" in data and "field_id" not in data:
        data["field_id"] = data.pop("client_id")

    try:
        ConditionSchema.model_validate(data)
    except PydanticValidationError as e:
        raise ValidationError(e.errors()) from e
