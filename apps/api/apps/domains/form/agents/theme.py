from __future__ import annotations

import dataclasses

from django.conf import settings
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from ..schemas import GeneratedTheme


@dataclasses.dataclass
class ThemeGeneratorDeps:
    pass


model = GoogleModel(
    model_name="gemini-2.5-flash",
    provider=GoogleProvider(api_key=settings.GOOGLE_AI_API_KEY),
)

theme_generator_agent: Agent[ThemeGeneratorDeps, GeneratedTheme] = Agent(
    model,
    deps_type=ThemeGeneratorDeps,
    output_type=GeneratedTheme,
    system_prompt=(
        "You are a visual design assistant for public-facing forms. "
        "Given a description of the desired look and feel, generate a theme with: "
        "name (a short label for the theme), "
        "accent_color (one of: neutral, red, orange, amber, green, emerald, cyan, blue, "
        "indigo, violet, pink — pick the closest match, never invent a new value), "
        "radius (one of: none, sm, md, lg, xl), "
        "input_size (one of: sm, md, lg), "
        "font (one of: sans, serif, mono), "
        "background_style (a CSS color or gradient value, e.g. '#f5f5f4' or "
        "'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' — leave empty if no "
        "background was requested), "
        "and custom_css (optional advanced CSS rules; every selector MUST be scoped under "
        "a '.ft-root' ancestor, e.g. '.ft-root .ft-page-title { letter-spacing: -0.02em; }'). "
        "Only these hooks exist in the markup, never invent others: #ft-form (root), "
        ".ft-root (scope), .ft-progress/.ft-progress-bar, .ft-page-title/.ft-page-description, "
        ".ft-question/.ft-question-label/.ft-question-required, .ft-field, .ft-content, "
        ".ft-nav/.ft-btn-prev/.ft-btn-next, .ft-welcome/.ft-welcome-title/"
        ".ft-welcome-description/.ft-welcome-start, .ft-complete. Leave custom_css empty "
        "unless something was requested that the other fields can't express. "
        "Never use @import, <script>, or url() pointing to a remote host in custom_css. "
        "Respond in the same language as the input. "
        "Return only the structured output, no extra commentary."
    ),
)
