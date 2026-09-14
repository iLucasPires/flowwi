# FlowWi

Uma mistura de **Notion + Typeform**, pensada como fluxo de trabalho completo para empresas criativas
(produção de vídeo, fotografia, marketing, design): formulários dinâmicos captam briefings de clientes,
essas respostas viram **tarefas** organizadas em kanban/lista/calendário, cada tarefa produz **mídia**
versionada, e o cliente aprova ou pede ajustes com feedback direto na mídia — fechando o loop
*briefing → produção → revisão → aprovação*.

> Projeto pessoal, desenvolvido como portfólio.

## Funcionalidades

- **Formulários dinâmicos** — builder com páginas, blocos condicionais e temas, respostas via link público
- **Tarefas** — kanban, lista e calendário, com subtasks, tags, prioridades e responsáveis
- **Mídia versionada** — imagem, vídeo, PDF, link e texto, com feedback (like/dislike) e comentários por versão
- **Workplaces multi-tenant** — roles (owner/manager/designer) e permissões por objeto
- **Inbox, sticky notes e lixeira** (soft-delete) por workplace
- **Webhooks** para integrar eventos (`form.response.created`, `task.created`, `media.created`, ...) com sistemas externos
- **Login social** (Google/GitHub) via django-allauth headless
- **Agente de IA** (Gemini) para geração e organização assistida de formulários

## Arquitetura

Monorepo com três aplicações em `apps/`:

```
flowwi/
├── apps/
│   ├── api/      # Django + DRF — REST API, WebSockets (Channels), jobs (RQ)
│   ├── app/      # Vue 3 SPA — dashboard e páginas públicas de formulário/mídia
│   └── proxy/    # Nginx — expõe app + api sob uma única origem (topologia de produção)
├── docker-compose.yml
└── .env.example
```

```
                       ┌──────────────┐
   browser  ───────▶   │    proxy     │
                       │   (nginx)    │
                       └──────┬───────┘
                   ┌──────────┴──────────┐
                   ▼                     ▼
             ┌───────────┐        ┌────────────┐
             │  app:5173 │        │  api:8000  │
             │  (Vue 3)  │        │ (Django)   │
             └───────────┘        └─────┬──────┘
                                         │
                              ┌──────────┴──────────┐
                              ▼                      ▼
                        ┌───────────┐         ┌────────────┐
                        │ postgres  │         │   redis    │
                        └───────────┘         └────────────┘
```

Em desenvolvimento, o próprio Vite (`apps/app`) já faz proxy de `/api`, `/media` e `/ws` para a API — o
serviço `proxy` é opcional e existe para reproduzir a topologia de produção (uma única origem/porta).

## Stack

| Camada    | Tecnologias                                                                          |
|-----------|---------------------------------------------------------------------------------------|
| Frontend  | Vue 3, Vue Router 5, Pinia/Pinia Colada, Nuxt UI 4, Vite, TypeScript, Zod, pnpm       |
| Backend   | Django 6 + DRF, PostgreSQL 18, Redis (django-rq/django-tasks), Django Channels, `uv` |
| Auth      | django-allauth headless (Google/GitHub OAuth), sessão via cookie                      |
| IA        | pydantic-ai + Google Gemini                                                           |
| Storage   | S3 (produção) / filesystem (dev)                                                      |
| Proxy     | Nginx                                                                                  |
| Infra     | Docker Compose                                                                        |

## Como rodar

Pré-requisitos: Docker e Docker Compose.

```bash
cp .env.example .env
docker compose up
```

Isso sobe Postgres, Redis, Mailpit, a API (com migrations automáticas) e o frontend. Endpoints:

| Serviço  | URL                                                       |
|----------|------------------------------------------------------------|
| Frontend | http://localhost:5173                                      |
| API      | http://localhost:8000                                      |
| Mailpit  | http://localhost:8025 (captura e-mails enviados em dev)     |
| pgAdmin  | http://localhost:8080 (`docker compose --profile tools up`) |

Para simular a topologia de produção com um único ponto de entrada (Nginx na porta 80):

```bash
docker compose --profile proxy up
```

Login social (Google/GitHub), o agente de IA (Gemini) e o seletor de capas (Unsplash) exigem chaves
próprias — preencha-as no `.env` (veja `.env.example`); sem elas, o restante da aplicação funciona
normalmente.

### Rodando cada app isoladamente

```bash
# Backend
cd apps/api
docker compose up -d   # apenas postgres, redis, pgadmin, mailpit
uv sync
uv run python manage.py migrate
uv run python manage.py runserver

# Frontend
cd apps/app
pnpm install
pnpm dev
```

Convenções de código, estrutura de pastas e padrões específicos de cada stack estão documentados nos
`AGENTS.md` de cada app ([`apps/api/AGENTS.md`](apps/api/AGENTS.md), [`apps/app/AGENTS.md`](apps/app/AGENTS.md))
e o schema completo do banco de dados em [`apps/api/docs/STRUCTURE.md`](apps/api/docs/STRUCTURE.md).

## Licença

[MIT](LICENSE)
