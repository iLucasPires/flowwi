---
name: flowwi-django-domain
description: Scaffold a new Django domain/integration app in apps/api following FlowWi's established service/selector/serializer/view pattern and multi-tenancy conventions. Use when adding a new backend resource, a new Django app under apps/domains or apps/integrations, or extending an existing domain with a new model+endpoint.
---

# FlowWi — Novo domínio Django (`apps/api`)

Checklist e padrões verificados contra o código real (não só a documentação) para criar um novo app de
domínio (`apps/domains/<nome>`) ou integração (`apps/integrations/<nome>`) na API. Para o schema de banco
e visão geral, ver `apps/api/AGENTS.md` e `apps/api/docs/STRUCTURE.md` — esta skill foca no *como fazer*.

## 1. Onde entra

- **`apps/domains/<nome>`** — tem entidades de negócio próprias (a maioria dos casos).
- **`apps/integrations/<nome>`** — um app por integração externa (Google, Unsplash, ...).
- **`apps/common/<nome>`** — infra de transporte compartilhada, sem entidades próprias (ex.: `realtime`,
  `streaming`). Nenhum domínio depende de `common/`; é o inverso.

## 2. Esqueleto de diretório

```
apps/<grupo>/<nome>/
├── __init__.py
├── apps.py              # AppConfig — label explícito (ver passo 3)
├── admin.py
├── urls.py              # DefaultRouter
├── tasks.py             # (opcional) background tasks via django-tasks
├── signals.py           # (opcional)
├── permissions.py       # (opcional) permission classes do domínio
├── constants.py         # (opcional) ex.: nome de cookie, choices soltas
├── models/
│   ├── __init__.py      # reexporta
│   └── <entidade>.py
├── services/
│   ├── __init__.py
│   └── <entidade>.py    # só lógica com side effects
├── selectors/
│   ├── __init__.py
│   └── <entidade>.py    # queries puras, @staticmethod
├── serializers/
│   ├── __init__.py
│   └── <entidade>.py
├── views/
│   ├── __init__.py
│   └── <entidade>.py
└── migrations/
```

## 3. `apps.py`

Nome do app tem ponto (`apps.domains.<nome>`) — sempre declare `label` explícito para não colidir e
manter os nomes de tabela/migração previsíveis:

```python
from django.apps import AppConfig


class TaskConfig(AppConfig):
    name = "apps.domains.task"
    label = "task"
    verbose_name = "Task"

    def ready(self):
        from . import signals  # noqa: F401  — só se o app tiver signals.py
```

Registrar em `INSTALLED_APPS` (`config/settings.py`), na seção `apps.domains.*` / `apps.integrations.*`.

## 4. Models

- Herdar mixins de `lib.models` conforme necessidade: `UUIDModel`, `CreatedModel`, `UpdatedModel`,
  `TimeStampedModel`, `SoftDeleteModel`, `TimeStampedSoftDeleteModel`, `FileCleanupModel`.
- FK para `Workplace`: `on_delete=models.CASCADE, null=True, blank=True`.
- Enums como `TextChoices` dentro do próprio arquivo do model.
- `gettext_lazy` para `verbose_name`/`help_text`.
- Depois de criar/alterar: `uv run python manage.py makemigrations && uv run python manage.py migrate`.

## 5. Selectors — queries puras

```python
# selectors/<entidade>.py
from django.db.models import QuerySet

from ..models import Sticky


class StickySelector:
    @staticmethod
    def for_workplace(workplace, *, trashed: bool = False) -> QuerySet[Sticky]:
        return Sticky.objects.filter(workplace=workplace, deleted_at__isnull=not trashed)
```

Use para queries complexas/reutilizáveis chamadas de mais de um lugar (view + WS handler, por exemplo).
Para o `get_queryset()` simples de um ViewSet, filtrar direto ali é suficiente — nem tudo precisa de
selector.

## 6. Services — só quando há side effects reais

```python
# services/<entidade>.py
from django.utils import timezone

from lib.bases import ServiceBase

from ..models import Task


class TaskService(ServiceBase):
    def __init__(self):
        super().__init__(Task)

    def trash(self, task: Task, *, deleted_by=None) -> Task:
        task.deleted_at = timezone.now()
        task.save(update_fields=["deleted_at", "updated_at"])
        return task
```

CRUD simples não precisa de service — o ViewSet usa o queryset/serializer diretamente. Só crie um service
quando há lógica de negócio (soft delete, side effects, orquestração de múltiplos models).

## 7. Serializers (expandable fields)

Campos relacionados retornam só o ID por padrão; o frontend pede expansão via `?expand=campo1,campo2`.

```python
from lib.serializers import ExpandableSerializerModel


class TaskSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    expandable_fields = {
        "subs": lambda: SubTaskSerializer(many=True, read_only=True),
        "assignees": lambda: WorkplaceMemberSerializer(many=True, read_only=True),
    }

    class Meta:
        model = Task
        fields = [...]
```

## 8. Views — multi-tenancy (verificado no código, não confie só no AGENTS.md antigo)

`WorkplaceViewSetMixin` (`apps.domains.workplace.mixins`) **só resolve e valida** o workplace ativo — ele
não filtra o queryset nem injeta `workplace` sozinho. O workplace ativo chega via **cookie `workplace_id`**
ou **query param `?workplace_id=`** (não é header). Cada ViewSet cablagem isso explicitamente:

```python
from apps.domains.workplace.mixins import WorkplaceViewSetMixin


class TaskViewSet(WorkplaceViewSetMixin, ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  # ou + IsDesignerOrReadOnly (apps.domains.workplace.permissions)
    lookup_field = "public_id"  # opcional — pk funciona também

    def get_queryset(self):
        workplace = self.get_workplace()
        if workplace is None:
            return self.queryset.none()
        return self.queryset.filter(workplace=workplace)

    def perform_create(self, serializer):
        serializer.save(workplace=self.get_workplace())
```

**Recurso aninhado** (o FK pro workplace não é direto no model, ex.: `SubTask.task.workplace`):
sobrescreva `workplace_lookup_field` e use no filtro:

```python
class SubTaskViewSet(WorkplaceViewSetMixin, ModelViewSet):
    workplace_lookup_field = "task__workplace"

    def get_queryset(self):
        workplace = self.get_workplace()
        return self.queryset.filter(**{self.workplace_lookup_field: workplace})
```

**Recurso filho de outro recurso na URL** (não de workplace, ex.: `/forms/<form_pk>/pages/`): herde também
`ViewSetBase` de `lib.bases`, que cuida de `parent_lookup_field`/`parent_filter_field` (filtra
`get_queryset()` e injeta no `perform_create()` automaticamente — ao contrário do mixin de workplace).

**Reorder/drag-and-drop**: use `generate_key_between` de `lib.utils.fractional_indexing` para calcular a
nova `position` (fractional indexing) em vez de reindexar tudo.

**Soft delete + restore**: sobrescreva `perform_destroy` para chamar `Service().trash(...)` em vez de
deletar, e exponha uma `@action(detail=True, methods=["post"], url_path="restore")` simétrica.

## 9. URLs

```python
# urls.py
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)

urlpatterns = router.urls
```

Prefixo em kebab-case. Registrar em `config/urls.py`, dentro do bloco `# App Domains` /
`# Apps Integrations`:

```python
path("", include("apps.domains.<nome>.urls"), name="<nome>"),
```

## 10. Extras opcionais (só se o domínio precisar)

- **Permissões por objeto (guardian)**: só use quando o recurso precisa de sharing granular (não
  tudo-ou-nada por workplace) — o `Document` é a referência (`apps.domains.document.permissions`,
  `DocumentAccess`). Ver `apps/api/AGENTS.md` → "Permissões por objeto".
- **Realtime (WebSocket)**: nunca crie um novo Consumer/rota. Adicione uma classe handler
  (`prefix`, `receive`/`dispatch`/`on_connect`/`on_disconnect`) em
  `GlobalConsumer.HANDLER_CLASSES` (`config/consumer.py`) e a lógica de negócio em um `*RealtimeService`
  próprio do domínio (nunca em `lib`, nem direto no consumer/handler). Ver `apps/api/AGENTS.md` →
  "Realtime".
- **AI (pydantic-ai)**: schemas Pydantic em `schemas/`, agentes em `agents/`, chamada síncrona via
  `agent.run_sync(...)`, API key em `settings.GOOGLE_AI_API_KEY`.
- **Webhooks**: se o domínio dispara eventos externos (`<recurso>.created`, etc.), integrar com
  `Webhook`/`WebhookSubscription` do app `workplace`.

## 11. Antes de terminar

```bash
uv run ruff check --select I --fix .   # imports (regra: entre apps = absoluto completo,
                                        # dentro da mesma app = relativo `from ..models import X`)
uv run ruff format .
uv run python manage.py makemigrations
uv run python manage.py migrate
```

Adicione o novo app na tabela de "Domínios principais" do `AGENTS.md` raiz e, se tiver entidades novas,
atualize `apps/api/docs/STRUCTURE.md`.
