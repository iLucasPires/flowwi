import random
from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from .models import Task, TaskOrigin, TaskPriority

# Realistic PT-BR titles/descriptions per default task type (see task/signals.py),
# so factory-built tasks read like a real content/marketing workspace instead of
# generic Faker lorem-ipsum.
CONTENT_BY_TYPE = {
    "Arte": [
        ("Criar arte para post de {topic}", "Peça quadrada e stories, seguindo o guia de marca."),
        ("Banner para campanha de {topic}", "Banner principal do site e redes sociais."),
        ("Ilustração para {topic}", "Ilustração de capa para o material de {topic}."),
        (
            "Ajustar identidade visual de {topic}",
            "Revisar cores e tipografia conforme feedback do cliente.",
        ),
        ("Mockup de embalagem para {topic}", "Apresentação em 3D para aprovação interna."),
    ],
    "Post": [
        ("Agendar post sobre {topic}", "Publicar no feed e compartilhar no stories."),
        ("Carrossel sobre {topic}", "5 slides explicando os principais pontos de {topic}."),
        ("Post de bastidores: {topic}", "Registro do dia a dia da equipe durante {topic}."),
        ("Reels sobre {topic}", "Vídeo curto de até 30s para o Instagram e TikTok."),
        ("Enquete sobre {topic}", "Interação rápida nos stories para engajar a audiência."),
    ],
    "Reunião": [
        ("Reunião de alinhamento: {topic}", "Alinhar prioridades e próximos passos com o time."),
        ("Call com cliente sobre {topic}", "Apresentar status e coletar feedback."),
        ("Retrô da campanha de {topic}", "Levantar aprendizados e pontos de melhoria."),
        ("Kickoff do projeto {topic}", "Alinhar escopo, prazos e responsáveis."),
        ("Reunião de briefing: {topic}", "Entender objetivos e referências do cliente."),
    ],
    "Conteúdo": [
        ("Escrever roteiro sobre {topic}", "Roteiro para vídeo institucional de até 2 minutos."),
        ("Redigir newsletter sobre {topic}", "Newsletter mensal com destaques de {topic}."),
        ("Revisar texto do blog sobre {topic}", "Revisão de gramática e SEO on-page."),
        ("Planejar pauta de {topic}", "Definir temas e formatos para o próximo mês."),
        ("Escrever legenda para {topic}", "Legenda com call-to-action para o post de {topic}."),
    ],
    "Outro": [
        ("Organizar arquivos de {topic}", "Reorganizar pastas no Drive e arquivar materiais antigos."),
        ("Revisar orçamento de {topic}", "Conferir custos previstos x realizados."),
        ("Atualizar planilha de {topic}", "Manter os dados de acompanhamento em dia."),
        ("Pesquisar referências para {topic}", "Levantar referências visuais e de concorrentes."),
        ("Configurar ferramenta para {topic}", "Testar e documentar o novo fluxo de trabalho."),
    ],
}

FALLBACK_CONTENT = [
    ("Tarefa sobre {topic}", "Detalhar e concluir conforme prioridade."),
]

TOPICS = [
    "Dia das Mães",
    "Black Friday",
    "lançamento do produto",
    "campanha de fim de ano",
    "aniversário da marca",
    "novo cliente",
    "rebranding",
    "colaboração com influenciador",
    "webinar",
    "feira do setor",
    "campanha de indicação",
    "site novo",
    "app mobile",
    "relatório trimestral",
    "onboarding de cliente",
    "expansão regional",
    "linha de verão",
    "promoção relâmpago",
    "podcast da marca",
    "case de sucesso",
]

PRIORITY_WEIGHTS = [
    (TaskPriority.LOW, 3),
    (TaskPriority.MEDIUM, 5),
    (TaskPriority.HIGH, 3),
    (TaskPriority.URGENT, 1),
]

ORIGIN_WEIGHTS = [
    (TaskOrigin.INTERNAL, 7),
    (TaskOrigin.EXTERNAL, 3),
]


def weighted_choice(weights):
    population, weights_ = zip(*weights, strict=True)
    return random.choices(population, weights=weights_, k=1)[0]


class TaskFactory(DjangoModelFactory):
    """Builds a Task with realistic PT-BR content. Relations (workplace, type,
    status, created_by), position and deadline are scenario-specific and always
    passed in explicitly by the caller.
    """

    class Meta:
        model = Task

    class Params:
        # Template + topic are resolved together so title/description agree
        # (e.g. both mention "Black Friday"), then trashed just fills deleted_at —
        # the caller still passes deleted_by, since that depends on who did it.
        topic = factory.LazyFunction(lambda: random.choice(TOPICS))
        content = factory.LazyAttribute(
            lambda o: random.choice(CONTENT_BY_TYPE.get(o.type.name if o.type else None, FALLBACK_CONTENT))
        )
        trashed = factory.Trait(
            deleted_at=factory.LazyFunction(lambda: timezone.now() - timedelta(days=random.randint(0, 10))),
        )

    title = factory.LazyAttribute(lambda o: o.content[0].format(topic=o.topic))
    description = factory.LazyAttribute(lambda o: o.content[1].format(topic=o.topic))
    priority = factory.LazyFunction(lambda: weighted_choice(PRIORITY_WEIGHTS))
    origin = factory.LazyFunction(lambda: weighted_choice(ORIGIN_WEIGHTS))

    @factory.post_generation
    def assignees(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.assignees.set(extracted)
