# FlowWi API — Guia para Agentes de IA

## Visão Geral

API REST para plataforma de gestão criativa/marketing (CRM para agências e equipes de design). Gerencia workplaces multi-tenant, formulários dinâmicos, tarefas kanban, mídias com versionamento e feedback, inbox de notificações e sticky notes.

## Stack

- **Linguagem:** Python 3.12+
- **Framework:** Django 6, Django REST Framework, drf-spectacular (OpenAPI)
- **Banco:** PostgreSQL 18 (psycopg3)
- **Cache/Filas:** Redis 7 (django-rq, django-tasks)
- **Storage:** S3 via django-storages (produção), FileSystem (dev)
- **Auth:** django-allauth headless (Google, GitHub OAuth)
- **AI:** pydantic-ai com Google Gemini (gemini-2.5-flash)
- **Gerenciador de pacotes:** `uv`
- **Linter/Formatter:** `ruff`
- **Async:** Django Channels + Daphne (ASGI)
- **Observabilidade:** logfire, django-silk (dev), django-auditlog
- **Admin:** django-unfold
- **Permissões:** django-guardian (object-level permissions)
- **Extras:** django-import-export, django-money, django-environ

## Comandos

```bash
# Instalar dependências
uv sync

# Rodar servidor
uv run python manage.py runserver

# Migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Lint
uv run ruff check .
uv run ruff format .

# Fix imports automático
uv run ruff check --select I --fix .

# Docker (serviços auxiliares)
docker compose up -d
```

## Estrutura de Diretórios

```
apps/api/
├── config/                  # Configuração Django
│   ├── settings.py          # Settings (arquivo único)
│   ├── urls.py              # URLs
│   ├── asgi.py              # ASGI server
│   ├── wsgi.py              # WSGI server
│   ├── celery.py            # Placeholder Celery (vazio)
│   └── __init__.py
├── apps/                    # Código da aplicação
│   ├── domains/             # Apps de domínio de negócio (ex: form, tasks, document, workplace)
│   ├── integrations/        # Um app por integração externa (ex: google, unsplash, notion)
│   └── common/              # Apps de transporte/infra compartilhada (ex: realtime, streaming) — não são
│                             #   domínio nem integração externa; nenhum domínio depende deles diretamente,
│                             #   é o inverso (eles importam de domínios, ex: realtime importa DocumentRealtimeHandler)
├── lib/                     # Código compartilhado
├── compose.yml
├── pyproject.toml
├── docs/                    # Documentação do projeto
│   └── STRUCTURE.md         # Schema completo do banco
└── templates/               # Templates do projeto
    ├── email/               # Templates de emails
    ├── <email>.html         # Template de email (ex: `email/verify.html`)
    └── oauth/               # Templates de OAuth
```

## Padrão de uma App

Cada app (`apps/domains/<nome>` ou `apps/integrations/<nome>`) segue esta estrutura. Os apps em
`apps/common/` (transporte — `realtime`, `streaming`) são mais enxutos e não seguem esse padrão
completo, já que não têm entidades de negócio próprias.

```
apps/<grupo>/<nome>/
├── __init__.py
├── apps.py                  # AppConfig obrigatório
├── admin.py
├── urls.py                  # DefaultRouter do DRF
├── tasks.py                 # Background tasks (django-tasks)
├── signals.py
├── permissions.py           # (quando necessário)
├── models/
│   ├── __init__.py          # Re-exporta modelos
│   └── <entidade>.py
├── services/
│   ├── __init__.py          # Re-exporta services
│   └── <entidade>.py        # Só para lógica com side effects
├── selectors/
│   ├── __init__.py
│   └── <entidade>.py        # Queries puras (leitura), @staticmethod
├── serializers/
│   ├── __init__.py
│   └── <entidade>.py
├── views/
│   ├── __init__.py
│   └── <entidade>.py
├── schemas/                 # (opcional) Pydantic schemas para AI (ex: form)
├── agents/                  # (opcional) Agentes pydantic-ai
├── consumers/               # (opcional) handlers do protocolo realtime do domínio (ex: document) — não são
│                             #   Channels Consumer; o único Consumer do projeto é
│                             #   `apps.common.realtime.consumers.GlobalConsumer`
├── validators/              # (opcional) Validações custom
├── mixins/                  # (opcional) Models específicos da app (ex: workplace)
├── exceptions/              # (opcional)
├── utils/                   # (opcional)
└── migrations/
```

## Convenções de Código

### Imports

Regras de import (enforced via `ruff --select I`):
- **Entre apps:** caminho absoluto completo, incluindo o grupo — `from apps.domains.workplace.models import Workplace`, `from apps.domains.form.models import Form`, `from apps.integrations.google.services import GoogleDriveService`
- **Da lib:** caminho absoluto `from lib.models import UUIDModel`
- **Dentro da mesma app:** relativo `from ..models import Task`

### Models

- Herdam mixins de `lib.models`: `UUIDModel`, `CreatedModel`, `UpdatedModel`, `TimeStampedModel`, `SoftDeleteModel`, `TimeStampedSoftDeleteModel`, `FileCleanupModel`
- Import: `from lib.models import TimeStampedModel, UUIDModel`
- Usam `gettext_lazy` para verbose_name/help_text
- TextChoices para enums dentro do próprio arquivo do model
- FK para Workplace com `on_delete=CASCADE, null=True, blank=True`

### Services

- Herdam `ServiceBase` de `lib.bases`
- Import: `from lib.bases import ServiceBase`
- Construtor: `super().__init__(Model)`
- **Só criar service quando há lógica de negócio real** (side effects)
- Para CRUD simples, o ViewSet pode usar o queryset diretamente
- Métodos que são queries puras devem ir em selectors

### Selectors

- Classes com `@staticmethod` que retornam `QuerySet`
- Import: `from ..selectors import FormSelector`
- Convenção: `class <Entidade>Selector`
- Para queries complexas, agregações, ou filtros reutilizáveis

### Serializers (Expandable Fields)

- Serializers que suportam expand herdam `ExpandableSerializerModel` de `lib.serializers`
- Definem `expandable_fields` — dict onde key é o nome do campo e value é um callable (lambda) que retorna o serializer expandido
- O frontend solicita expansão via query param `?expand=field1,field2`
- Sem `?expand`, o campo retorna IDs (comportamento padrão do DRF)
- Com `?expand=assignees`, o campo retorna os objetos serializados completos

```python
from lib.serializers import ExpandableSerializerModel


class TaskSerializer(ExpandableSerializerModel, serializers.ModelSerializer):
    expandable_fields = {
        "subs": lambda: SubTaskSerializer(many=True, read_only=True),
        "tags": lambda: TaskTagSerializer(many=True, read_only=True),
        "assignees": lambda: WorkplaceMemberSerializer(many=True, read_only=True),
    }
```

### Views

- Herdam `WorkplaceViewSetMixin` (de `apps.domains.workplace.mixins`) + `ModelViewSet` do DRF
- Para recursos aninhados com `parent_lookup_field`/`parent_filter_field`, herdar também `ViewSetBase` de `lib.bases`
- Atributos obrigatórios: `queryset`, `serializer_class`
- Actions custom via `@action(detail=True/False, ...)`
- `permission_classes = [IsAuthenticated]` é o default

### URLs

- Usar `DefaultRouter` do DRF
- Registrar viewsets com prefixo kebab-case: `router.register(r"form-blocks", FormBlockViewSet)`
- Exportar `urlpatterns = router.urls`

### Multi-tenancy

- Todo recurso pertence a um Workplace
- O frontend envia header `x-workplace-id` em todas as requests
- `WorkplaceViewSetMixin` (de `apps.domains.workplace.mixins`) extrai o header, valida membership e filtra o queryset
- Se o user não for membro do workplace → 403 PermissionDenied
- Se o header não for enviado → queryset vazio (`.none()`)
- Ao criar recursos, o mixin injeta `workplace` no `serializer.save()`

## Autenticação

- Session-based auth (cookie) via django-allauth headless
- Providers: Google OAuth, GitHub OAuth
- Endpoints sob `/allauth/` (allauth URLs) e `/api/` (headless URLs)
- `SessionAuthentication` + `BasicAuthentication` no DRF

## Permissões por objeto (django-guardian)

Hoje só o `Document` usa isso — modelo de referência para levar a outros recursos que
precisem de sharing granular (ao contrário do multi-tenancy por Workplace, que é sempre
tudo-ou-nada via `WorkplaceViewSetMixin`).

- **`DocumentAccess`** (`apps.domains.document.permissions`) é a única fonte das regras
  — `is_workplace_admin`/`can_view`/`can_edit`. Usada por composição, nunca como função
  solta: os `BasePermission` (`DocumentObjectPermission`/`DocumentRelatedObjectPermission`,
  via `BaseDocumentPermission.access`), as views (`access = DocumentAccess()` como
  atributo de classe), o serializer, e o `DocumentRealtimeService` (WebSocket) todos
  seguram sua própria instância — não existe request/view em todos esses lugares, então
  a lógica não podia morar só dentro de uma `BasePermission`.
- **Papel de admin sempre vence**: owner/manager do workplace (`Workplace.is_owner`/
  `is_manager`) enxergam e editam todo documento, ignorando `visibility`/`allow_member_edit`
  — `DocumentAccess.is_workplace_admin`, checado em Python, não via guardian, porque é
  uma regra de papel, não uma concessão por objeto.
- **Autor**: sempre tem `view_document`/`change_document` no próprio documento — concedido
  via guardian (`assign_perm`) no `post_save` (`apps.domains.document.signals.sync_document_permissions`).
- **"Todo o workplace"**: em vez de uma linha de permissão por membro, cada Workplace tem um
  `django.contrib.auth.models.Group` próprio (`apps.domains.workplace.utils.get_workplace_members_group`),
  mantido em sincronia com `WorkplaceMember` via signals (`apps.domains.workplace.signals`). Guardian
  concede `view_document`/`change_document` a esse Group quando `Document.visibility ==
  WORKPLACE` / `allow_member_edit=True`.
- **Alterar quem pode ver/editar** (`visibility`, `allow_member_edit`) é restrito ao autor ou
  admin do workplace — checado no `perform_update` do `DocumentViewSet`, não pelo guardian.
- **`get_queryset`**: admins veem tudo (queryset com `.prefetch_related`, montada na
  própria view — o `DocumentSelector` não sabe de prefetch); o resto passa por
  `DocumentSelector.viewable_for(workplace, user)` (`apps.domains.document.selectors`,
  mesmo padrão do `StickySelector`: classe com `@staticmethod`), que por baixo usa
  `guardian.shortcuts.get_objects_for_user` — um documento sem permissão retorna 404,
  não 403 (não vaza a existência de documentos privados).
- **Recursos filhos** (`DocumentVersion`, `DocumentComment`, `DocumentFeedback`) resolvem a
  permissão contra `obj.document`, não contra si mesmos — sem isso, dava pra ler/editar
  conteúdo de um documento privado direto por essas rotas, ignorando o Document em si.
  Comentar/dar feedback só exige `view_document` (é um mecanismo de feedback do cliente,
  não uma ação de edição); ler/escrever o conteúdo da versão exige `change_document`.

## Realtime (Django Channels / WebSocket)

**Um único consumer pra tudo**: `config.consumer.GlobalConsumer`, uma conexão por aba,
uma rota (`ws/`, `config/routing.py`). Nada de um consumer/rota por feature — eventos são
multiplexados por um campo `type` namespaced por domínio (`document.subscribe`,
`document.acquire_lock`, etc.). Três camadas, cada uma só fazendo sua parte:

1. **`GlobalConsumer`** — só ciclo de vida da conexão. Literalmente só `connect`/
   `disconnect` (mais `receive`/`dispatch`, que existem porque o Channels exige esses
   nomes de entrada, mas contêm zero lógica — só acham o handler pelo prefixo antes do
   primeiro `.` em `type` e repassam). Nenhum `handle_*` de domínio mora aqui.
2. **Handler por conexão** (ex.: `apps.domains.document.consumers.DocumentRealtimeHandler`)
   — instanciado do zero a cada `connect()`, um por classe listada em
   `GlobalConsumer.HANDLER_CLASSES`, então `subscribed_documents`/`held_lock_document_id`
   são privados daquela conexão, não compartilhados entre abas. Fala o protocolo
   `document.*` (parseia mensagens, manda/broadcasta frames), mas não decide sozinho quem
   pode o quê.
3. **`DocumentRealtimeService`** — a lógica de negócio de verdade (quem pode se
   inscrever, quem pode travar). **Nunca em `lib`**, que é só código sem lógica de
   negócio (client Redis, mixins, etc.), nem direto no consumer ou no handler.

Pra adicionar uma feature realtime de outro domínio: uma classe handler nova (mesmo
formato — `prefix`, `receive`/`dispatch`/`on_connect`/`on_disconnect`), adicionada em
`GlobalConsumer.HANDLER_CLASSES`. Nunca uma classe de consumer nova nem uma segunda rota.

Pegadinha do Channels que já causou regressão aqui: `dispatch()` também processa a
mensagem interna `"websocket.connect"` — ou seja, roda **antes** de `connect()`. Qualquer
estado que `_handler_for`/`dispatch` leia (o dict `self.handlers`) precisa existir desde a
construção do objeto (`__init__`), não só depois que a conexão é aceita — um `getattr`
defensivo ali não é "código sujo", é a defesa contra esse ordering.

Único uso hoje: `document.*` — trava de edição + "algo mudou, refaça o fetch". Não é um
editor colaborativo (sem OT/CRDT), só o suficiente pra duas pessoas não sobrescreverem o
rascunho uma da outra em silêncio.

- **Infra**: `CHANNEL_LAYERS` usa `channels_redis` (mesmo `REDIS_URL` do cache/RQ) — sem
  isso as mensagens de grupo (`channel_layer.group_send`) não atravessam processos.
  `config/asgi.py` monta o `URLRouter` a partir de `config/routing.py`
  (`websocket_urlpatterns`). Nomes de grupo do Channels só aceitam `[A-Za-z0-9-_.]` —
  **nunca `:`** (ver `DocumentRealtimeService.group_name`, única fonte do nome —
  usada tanto pelo handler quanto por `notify_document_changed`).
- **Protocolo `document.*`**: a conexão não é presa a um documento na URL — o cliente manda
  `{"type": "document.subscribe", "document_id": <id>}` pra entrar no grupo daquele
  documento (e `document.unsubscribe` pra sair), o que deixa trocar de documento sem
  reconectar o socket inteiro. Sem `view_document` no documento, só aquela inscrição é
  negada (`document.subscribe_denied`) — o resto da conexão continua de pé, ao contrário de
  fechar o socket todo. `document.acquire_lock`/`heartbeat`/`release_lock` seguem o mesmo
  padrão, sempre com `document_id` no payload.
- **Trava de edição** (`DocumentRealtimeService` por cima de
  `apps.domains.document.services.lock.DocumentLockService`): lock pessimista por
  documento em Redis (`doc:lock:<id>`, TTL curto), renovado por heartbeat do cliente.
  Quem tem acesso de edição faz acquire ao entrar em modo editável (rascunho + `can_edit`);
  todo mundo mais no grupo vira read-only até ser liberado (unsubscribe, disconnect, ou o
  heartbeat parar de chegar e o TTL vencer). O handler só guarda **uma** trava por conexão
  (`held_lock_document_id`) — reflete a realidade do frontend (uma aba só edita um
  documento por vez); múltiplas *inscrições* simultâneas são suportadas
  (`subscribed_documents: set`), a trava não.
- **`notify_document_changed(document_id)`** (`apps.domains.document.realtime`): chamado de
  código síncrono (views) após qualquer save que muda o que outro viewer vê — sharing,
  título, capa, status da versão. Propositalmente **não** carrega o documento atualizado no
  payload (isso exigiria duplicar a lógica de `can_edit`/`can_manage_sharing` — que depende
  de quem está olhando — no lado do WS); cada cliente só recebe o sinal e refaz o
  `GET /api/documents/<id>` sozinho. Autosave de conteúdo (PATCH só com `content`) **não**
  dispara isso — aconteceria a cada ~900ms de digitação; só mudança de `status` notifica, e
  a liberação da trava dispara um último aviso pra quem ficou de fora pegar o conteúdo novo.
- **De dentro do handler** (contexto async), nunca chame `notify_document_changed`/
  `async_to_sync` — usa `self.consumer.channel_layer.group_send(...)` direto, já que
  `async_to_sync` explode se chamado de dentro de um event loop já rodando.
- Todo mundo autenticado também entra num grupo `user-<id>` no connect (isso sim direto em
  `GlobalConsumer`, não é lógica de domínio) — ainda sem uso, é base pra futuro push por
  usuário (ex.: "você foi removido deste workplace") independente de qual documento/feature
  a aba está olhando.

## API

- Versionamento por namespace (`NamespaceVersioning`, versão `api`)
- Throttle: 100/h anon, 2000/h user (dev) — 5000/h anon, 50000/h user (prod)
- Paginação: `PageNumberPagination`, 10 por página
- Erros padronizados: `drf-standardized-errors`
- Schema OpenAPI: `/schema/`, Swagger: `/docs/`, Redoc: `/redoc/`
- Filtros: `SearchFilter`, `OrderingFilter` globais
- Default permission: `DjangoModelPermissionsOrAnonReadOnly` (nível global)
- BaseViewSet override: `IsAuthenticated`

## AI (pydantic-ai)

- Agentes ficam em `apps/domains/<nome>/agents/`
- Schemas Pydantic para input/output ficam em `apps/domains/<nome>/schemas/`
- Usam `pydantic_ai.Agent` com `GoogleModel` (gemini-2.5-flash)
- Output tipado com Pydantic BaseModel
- Chamada síncrona via `agent.run_sync(prompt, deps=...)`
- API key em `settings.GOOGLE_AI_API_KEY`

## Banco de Dados (Schema)

Consultar `STRUCTURE.md` para o schema completo. Resumo das entidades:

- **Workplace** → WorkplaceMember (roles: owner, manager, designer)
- **Profile** — dados do usuário (photo, cover)
- **Form** → FormPage → FormBlock → FormResponse → FormAnswer → FormAnswerFile
- **Task** → SubTask, TaskTag (M:N), Assignees (M:N)
- **Media** → MediaVersion, MediaFeedback, MediaComment, GoogleDrive
- **Inbox** — notificações por usuário
- **Sticky** — sticky notes com soft delete

Apps sem entidades próprias no `STRUCTURE.md`:
- **integration** — conexões OAuth com storages externos (Google Drive, Dropbox, OneDrive, Notion), usado para importar mídia direto de fontes do cliente
- **plan** — scaffold vazio (models/views/serializers sem implementação), reservado para planos de assinatura
- **unsplash** — proxy read-only da API do Unsplash (sem models). `UnsplashService` cacheia toda resposta
  no Redis em duas chaves (payload + marcador de frescor), então a cota de 50 req/h só é consumida quando o
  cache expira — e, se o Unsplash cair, o payload velho ainda é servido. Endpoints:
  `GET /api/unsplash/photos` (busca ou feed popular) e `POST /api/unsplash/download` (ping obrigatório
  pelas guidelines quando o usuário escolhe uma foto)

### Capas (cover)

`CoverStyleModel` (em `lib.models`) adiciona `cover_style` + `cover_credit` a quem já tem um
`ImageField` de capa — hoje `Document.cover`, `Profile.cover`, `Form.cover_image` e `Workplace.photo`.
O arquivo enviado tem precedência; `cover_style` guarda a alternativa (cor/gradiente CSS, URL de link
ou URL de foto do Unsplash) e `cover_credit` guarda a atribuição que o Unsplash exige exibir.

## Docker / Infraestrutura

```bash
# Subir serviços auxiliares
docker compose up -d

# Serviços incluídos:
# - postgres:18.3-alpine (porta 5432)
# - redis:7-alpine (porta 6379)
# - pgadmin4 (porta 8080)
# - mailpit (SMTP: 1025, UI: 8025)
```

Produção usa Dockerfile multi-stage (builder → prod) com Daphne como ASGI server —
necessário para o WebSocket de documentos (ver "Realtime" acima) funcionar; rodando via
WSGI/gunicorn, `ws/documents/<id>/` não responde. O reverse proxy na frente também precisa
de uma rota `/ws/` com upgrade de conexão (`proxy_set_header Upgrade`/`Connection`), igual
já deve existir pra `/api`.

## Variáveis de Ambiente

Definidas em `.env` (não commitada). Gerenciadas via `django-environ`. Principais:

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CSRF_TRUSTED_ORIGINS`
- `FRONTEND_URL`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `REDIS_URL`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET_KEY`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET_KEY`
- `GOOGLE_AI_API_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- `API_THROTTLE_ANON`, `API_THROTTLE_USER`, `API_VIEW_CACHE_TIMEOUT`
- `UNSPLASH_ACCESS_KEY`, `UNSPLASH_SECRET_KEY`, `UNSPLASH_ID`, `UNSPLASH_APP_NAME`
- `UNSPLASH_CACHE_TTL` (padrão 6h), `UNSPLASH_CACHE_STALE_TTL` (padrão 7d), `API_THROTTLE_UNSPLASH`
