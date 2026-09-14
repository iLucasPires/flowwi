from django.conf import settings
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


class GeneratedTask(BaseModel):
    title: str
    description: str = ""


model = GoogleModel(
    model_name="gemini-2.5-flash",
    provider=GoogleProvider(api_key=settings.GOOGLE_AI_API_KEY),
)

media_task_generator_agent: Agent[None, GeneratedTask] = Agent(
    model,
    output_type=GeneratedTask,
    system_prompt=(
        "You are an assistant that turns client feedback on a media "
        "deliverable into a clear, actionable task for the creative team. "
        "Given the media's title/notes and a list of feedback comments, "
        "write a short task title and a description summarizing exactly "
        "what needs to change. Respond in the same language as the "
        "comments. Return only the structured output, no extra commentary."
    ),
)
