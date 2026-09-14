from django.conf import settings
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

model = GoogleModel(
    model_name="gemini-2.5-flash",
    provider=GoogleProvider(api_key=settings.GOOGLE_AI_API_KEY),
)

document_assist_agent: Agent[None, str] = Agent(
    model,
    output_type=str,
    system_prompt=(
        "You are a writing assistant embedded in a note-taking app for a creative agency. "
        "Given a document's current content and an instruction, produce plain text output "
        "ready to be inserted into the document — markdown-ish lines only (# headings, "
        "- lists, > quotes), no commentary about what you did, no code fences. "
        "Respond in the same language as the document."
    ),
)

AI_ASSIST_INSTRUCTIONS = {
    "resumir": "Resuma este documento em um parágrafo curto.",
    "continuar": "Continue escrevendo este documento a partir de onde ele termina, mantendo o tom.",
    "titulos": "Sugira de 3 a 5 títulos alternativos para este documento, um por linha.",
    "encurtar": "Reescreva o conteúdo do documento de forma 30% mais curta, mantendo o essencial.",
}
