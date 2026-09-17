import random
from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from .models.sticky import Sticky, StickyVisibility

# Realistic PT-BR quick-note texts, so factory-built stickies read like real
# workspace notes instead of generic Faker lorem-ipsum. A blank text is included
# on purpose, matching the "(sem texto)" empty state stickies can have in the UI.
TEXTS = [
    "Ligar para o cliente sobre o orçamento",
    "Revisar contrato antes de assinar",
    "Comprar café para a reunião de amanhã",
    "Ideia: newsletter quinzenal",
    "Lembrar de exportar o relatório em PDF",
    "Enviar briefing atualizado pro time",
    "Testar nova paleta de cores no site",
    "Backup dos arquivos do projeto",
    "Ideia pra post: bastidores da produção",
    "Confirmar presença na call de sexta",
    "Separar referências pro moodboard",
    "Atualizar senha do Wi-Fi do escritório",
    "Pedir feedback do cliente sobre a proposta",
    "Organizar a mesa antes da visita",
    "Anotar ideias do brainstorm de hoje",
    "Revisar orçamento do mês",
    "Pesquisar fornecedor de brindes",
    "Rever apresentação antes da reunião",
    "Marcar horário no dentista",
    "Renovar assinatura das ferramentas",
    "",
]

VISIBILITY_WEIGHTS = [
    (StickyVisibility.PRIVATE, 7),
    (StickyVisibility.WORKFLOW, 3),
]


def weighted_choice(weights):
    population, weights_ = zip(*weights, strict=True)
    return random.choices(population, weights=weights_, k=1)[0]


def random_pastel_color() -> str:
    """Port of the frontend's randomPastelColor() (color.ts), so seeded stickies
    look like ones a person actually created through the UI."""
    hue = random.randint(0, 359)
    saturation = (60 + random.randint(0, 19)) / 100
    lightness = (75 + random.randint(0, 14)) / 100

    a = saturation * min(lightness, 1 - lightness)

    def channel(n: int) -> str:
        k = (n + hue / 30) % 12
        color = lightness - a * max(min(k - 3, 9 - k, 1), -1)
        return format(round(255 * color), "02x")

    return f"#{channel(0)}{channel(8)}{channel(4)}"


class StickyFactory(DjangoModelFactory):
    """Builds a Sticky with realistic PT-BR content. Relations (workplace,
    created_by), position and trash state are scenario-specific and always
    passed in explicitly by the caller.
    """

    class Meta:
        model = Sticky

    class Params:
        trashed = factory.Trait(
            deleted_at=factory.LazyFunction(lambda: timezone.now() - timedelta(days=random.randint(0, 10))),
        )

    text = factory.LazyFunction(lambda: random.choice(TEXTS))
    color = factory.LazyFunction(random_pastel_color)
    visibility = factory.LazyFunction(lambda: weighted_choice(VISIBILITY_WEIGHTS))
