from __future__ import annotations

import dataclasses
from typing import Any

from django.conf import settings
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from ..schemas import BlockType


class FormBlockSchema(BaseModel):
    title: str
    type: BlockType
    required: bool = False
    config: dict[str, Any] = Field(default_factory=dict)


class GeneratedForm(BaseModel):
    title: str
    description: str = ""
    blocks: list[FormBlockSchema]


@dataclasses.dataclass
class FormGeneratorDeps:
    pass


model = GoogleModel(
    model_name="gemini-2.5-flash",
    provider=GoogleProvider(api_key=settings.GOOGLE_AI_API_KEY),
)

form_generator_agent: Agent[FormGeneratorDeps, GeneratedForm] = Agent(
    model,
    deps_type=FormGeneratorDeps,
    output_type=GeneratedForm,
    system_prompt=(
        "You are a form builder assistant. "
        "Given a description, generate a structured form with a title, "
        "optional description, and a list of blocks (fields). "
        "Each block must have: title (the question/label), "
        "type (one of: text, email, number, date, time, select, choice, file), "
        "required (bool), and config (object — for select/choice include "
        "'options': [{label, value}]; for text include 'long': bool). "
        "Only generate answerable fields (never the 'content' type, which is "
        "reserved for free-text blocks added manually in the editor). "
        "Respond in the same language as the input. "
        "Return only the JSON structure, no extra commentary."
    ),
)
