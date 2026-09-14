# FlowWi — Guia para Agentes de IA

Projeto pessoal. Monorepo (`apps/api` + `apps/app`) com o backend e o frontend do FlowWi.

## O que é o FlowWi

Uma mistura de **Notion + Formtype/Typeform**, pensada como fluxo de trabalho completo para empresas
criativas (produção de vídeo, fotografia, marketing, design). A ideia central:

1. **Formulários dinâmicos** captam pedidos/briefings de clientes (`Form → FormPage → FormBlock → FormResponse → FormAnswer`).
2. Essas respostas alimentam a organização de **tarefas** em kanban/lista/calendário (`Task`, `SubTask`, tags, assignees).
3. Cada tarefa produz **mídia** (imagem, vídeo, PDF, link/site, texto) versionada (`Media → MediaVersion`).
4. O cliente dá **feedback** direto na mídia (like/dislike, comentários por versão) — esse feedback também
   pode gerar novas tarefas, fechando o loop briefing → produção → revisão → aprovação.
5. Tudo é organizado por **Workplace** (multi-tenant, com roles owner/manager/designer), com inbox de
   notificações, sticky notes, trash (lixeira) e webhooks para integrações externas.

Não é um produto para os clientes finais "editarem documentos" como no Notion — o Notion-like aqui é a
flexibilidade de estrutura (formulários customizáveis, blocos, workplaces); o Formtype-like é a captura de
dados via formulário público e o fluxo que nasce dele.

## Estrutura do repositório

```
flowwi/
├── apps/
│   ├── api/     # Backend — Django + DRF (API REST)
│   ├── app/     # Frontend — Vue 3 SPA
│   └── proxy/   # Nginx — reverse proxy (topologia de produção)
├── docker-compose.yml
└── AGENTS.md    # este arquivo
```

Cada pasta em `apps/` tem seu próprio `AGENTS.md` detalhado — **consulte-os antes de mexer no código**, eles
têm convenções específicas de cada stack:

- [`apps/api/AGENTS.md`](apps/api/AGENTS.md) — apps Django, padrões de service/selector/serializer/view, multi-tenancy, AI agents
- [`apps/app/AGENTS.md`](apps/app/AGENTS.md) — componentes Vue, composables, auto-imports, roteamento

`apps/api/docs/STRUCTURE.md` tem o schema completo do banco de dados (todas as entidades e relações).

## Skills

`.claude/skills/` tem skills do Claude Code com o passo a passo das convenções deste projeto (checadas
contra o código, não só a doc):

- `flowwi-django-domain` — criar um app de domínio/integração novo no backend (`apps/api`)
- `flowwi-vue-feature` — criar uma feature/componente novo no frontend (`apps/app`), incluindo o mapa de
  componentes do Nuxt UI

Já os `.agents/skills` dentro de `apps/app/` são skills de bibliotecas de terceiros (Vue, Pinia, Nuxt UI,
TanStack) sincronizadas via `skills-lock.json` — não confundir com as skills do projeto acima.

## Stack resumida

| Camada    | Stack                                                                              |
|-----------|-------------------------------------------------------------------------------------|
| Frontend  | Vue 3, Vue Router 5, Pinia/Pinia Colada, Nuxt UI 4, Vite, TypeScript, Zod, pnpm     |
| Backend   | Django 6 + DRF, PostgreSQL 18, Redis (django-rq/django-tasks), Channels (WS), `uv` |
| Auth      | django-allauth headless (Google/GitHub OAuth), sessão via cookie                   |
| AI        | pydantic-ai + Google Gemini (geração/organização assistida a partir de formulários) |
| Storage   | S3 (produção) / filesystem (dev); integrações OAuth com Google Drive, Dropbox, OneDrive, Notion (`apps/integration`, WIP) |

## Domínios principais (backend `apps/`)

| App           | Responsabilidade                                                             |
|---------------|--------------------------------------------------------------------------------|
| `workplace`   | Tenant raiz — Workplace, membros, roles, permissões object-level              |
| `profile`     | Dados de perfil do usuário (foto, capa)                                       |
| `form`        | Formulários dinâmicos, páginas, blocos, respostas — inclui agente de AI       |
| `tasks`       | Tarefas (kanban), subtasks, tags, assignees                                   |
| `media`       | Mídia versionada, feedback (like/dislike), comentários, WS consumers          |
| `inbox`       | Notificações por usuário                                                      |
| `sticky`      | Sticky notes (privadas ou de workplace)                                       |
| `trash`       | Lixeira genérica (soft-delete cross-model, purge automático)                  |
| `integration` | Conexões OAuth com storages externos (Google Drive, Dropbox, OneDrive, Notion) — em desenvolvimento |
| `plan`        | Placeholder/scaffold para planos de assinatura — ainda sem implementação      |
| `unsplash`    | Proxy cacheado da API do Unsplash — alimenta o seletor de capas do frontend    |

Webhooks (`Webhook`/`WebhookSubscription`, eventos como `form.response.created`, `task.created`,
`Media.created`) permitem integração externa por workplace.

## Rodando localmente

Stack completa via Docker (ver [README.md](README.md) para detalhes):
```bash
cp .env.example .env
docker compose up
```

Ou cada app isoladamente:
```bash
cd apps/api && uv sync && uv run python manage.py migrate && uv run python manage.py runserver
cd apps/app && pnpm install && pnpm dev
```

Detalhes de comandos, lint, convenções de código, etc. estão nos AGENTS.md de cada pasta.
