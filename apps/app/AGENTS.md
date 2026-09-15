# AGENTS.md — Frontend (`app/`)

## Stack

- Vue 3 + Vue Router 5 (rotas escritas à mão, sem file-based routing — ver "Roteamento") + Pinia 3 + Pinia Colada
- Nuxt UI 4 (via `@nuxt/ui/vite` — sem Nuxt, apenas o design system)
- Vite
- Zod, VueUse, TypeScript
- Linting: oxlint + ESLint
- Formatting: oxfmt
- Package manager: pnpm
- Porta: 8080 (produção via Nginx)

## Estrutura: `app/core` / `app/features` / `app/shared`

`src/app/` é organizado por **feature** (vertical slice), não por tipo de arquivo. Cada feature é
dona de tudo que é só dela — componentes, composables, types, rotas, guards. `core/` é o chassi
do app (zero lógica de domínio); `shared/` é o que várias features usam e não pertence a nenhuma.
`src/main.ts` (fora de `app/`) é o único ponto de entrada — importa `app/App.vue` e
`app/core/routes.ts` e monta o app; `src/styles/` (também fora de `app/`) guarda o CSS global.

```
app/
├── src/
│   ├── main.ts                   # Entry point — importa App.vue e o router de app/
│   ├── styles/                   # CSS global (main.css, themes/)
│   ├── app/
│   │   ├── App.vue
│   │   ├── core/                 # Chassi do app — zero lógica de domínio
│   │   │   ├── routes.ts         # Monta o router: importa routes+guards de cada feature
│   │   │   ├── clients/          # api.ts (apiFetch + todas as API_*_URLS) + index.ts
│   │   │   └── layouts/          # account-layout.vue, dashboard-layout.vue, public-layout.vue
│   │   ├── features/
│   │   │   ├── document/
│   │   │   │   ├── components/       # comment/, editor/, layout/, panel/, tree/, type/ + soltos (cover, preview, command-palette, graph-modal)
│   │   │   │   ├── composables/      # document.ts, documentVault.ts, documentEditing.ts...
│   │   │   │   ├── pages/            # documents.vue
│   │   │   │   ├── routes.ts         # documentRoutes
│   │   │   │   ├── types.ts, constants.ts, utils.ts
│   │   │   │   └── index.ts          # barrel (composables + types + constants + utils)
│   │   │   ├── form/                 # + schemas.ts (Zod), components/theme (temas). components/block, editor, public, view
│   │   │   ├── inbox/
│   │   │   ├── media/                 # components/detail, version
│   │   │   ├── settings/               # SÓ components/ (general/, integration/, workplace/) — agrega
│   │   │   │                           # abas de outras features no CSettingsDialog, sem lógica própria
│   │   │   ├── sticky/                 # + schemas.ts
│   │   │   ├── task/                   # + schemas.ts, utils.ts. components/kanban, list, status, subtask, type, view
│   │   │   ├── user/                   # + guards/ (userGuard, profileGuard), profile.ts (iProfile)
│   │   │   └── workplace/              # + schemas.ts, guard.ts (workplaceGuard). components/member, webhook
│   │   └── shared/                     # Cross-feature — usado por 2+ features, não é de nenhuma
│   │       ├── components/
│   │       │   ├── *.vue              # Primitivos (text-block, input-date, input-time, rich-text-editor, full-calendar, icon-picker, icon-or-emoji)
│   │       │   ├── cover/              # CoverPicker/CoverBanner/CoverCredit — usado por document, form, workplace, user
│   │       │   ├── dashboard/          # CDashboardContent (wrapper de página padrão)
│   │       │   └── search/             # SearchPalette (busca cross-domain)
│   │       ├── composables/
│   │       │   ├── accentColor.ts, shake.ts   # genéricos, sem domínio
│   │       │   ├── drive/, unsplash/           # integrações externas (não são "domain" no backend)
│   │       │   └── search/
│   │       ├── types/                   # auth, calendar, cover, notification, pagination, unsplash
│   │       └── utils/                   # avatar, color, cover, emoji, ordering, router, social, time, toast
│   └── __tests__/                   # Testes unitários
├── vite.config.ts
├── package.json
└── Dockerfile
```

**Critério features vs. shared**: se corresponde a um app do backend (`api/apps/domains/*`:
document, form, inbox, media, sticky, task, user, workplace) ou é uma área sólida e autocontida
do próprio frontend (`settings`, mesmo sem domain no backend) → `features/`. Se é usado por 2+
features e não pertence a nenhuma (cover picker, busca, primitivos de UI) → `shared/`. Integrações
externas (`drive`, `unsplash` — equivalentes a `api/apps/integrations/*`) também ficam em
`shared/`, não em `features/`.

**Barrel por feature**: `app/features/<nome>/index.ts` reexporta `./composables`, `./types`,
`./constants`, `./schemas`, `./utils` (o que existir). Serve para import coletivo
(`import { useTask, iTask } from '@/app/features/task'`), mas o padrão é importar do arquivo
específico (`@/app/features/task/composables/task`) — deixa explícito de onde cada coisa vem, ver
"Auto-imports" abaixo.

## Roteamento

Sem file-based routing. Cada feature declara suas próprias rotas em `app/features/<nome>/routes.ts`
(array de `RouteRecordRaw`, path relativo ao layout pai):

```ts
// app/features/task/routes.ts
export const taskRoutes: RouteRecordRaw[] = [
  { path: 'tasks', component: () => import('./pages/task-list.vue') },
  { path: 'tasks/:id', component: () => import('./pages/task-detail.vue') },
]
```

Uma feature pode exportar mais de um array quando suas páginas montam em pontos diferentes da
árvore — ex: `workplace` tem `workplaceRoutes` (`/dashboard/workplaces/*`) e
`workplaceSetupRoutes` (`/account/setup/workplace/*`).

`app/core/routes.ts` importa todos os arrays e monta a árvore final (`/account`, `/dashboard`,
`/public`, cada um usando um layout de `app/core/layouts/`). Guards ficam na feature dona do que
verificam (`userGuard`/`profileGuard` em `app/features/user/guards/`, `workplaceGuard` em
`app/features/workplace/guard.ts`) e só são importados/registrados (`router.beforeEach`) em
`app/core/routes.ts` — nunca dentro da própria feature.

**Perda ao tirar o typed-router**: `useRoute()` não vem mais tipado por rota — `route.params.id`
é `string | string[] | undefined`, não um `string` garantido. Use `String(route.params.id)` ao
repassar para algo que espera `string`.

## ⚠️ Antes de escrever UI custom: olhe o mapa de componentes do Nuxt UI

**Regra dura**: antes de criar um `<button>`/`<div>`/`<select>` cru, um dropdown, um
popover, uma árvore, um layout de painéis redimensionáveis, uma paleta de comando,
tabs, etc. — **procure primeiro se o Nuxt UI já tem o componente** na tabela abaixo.
Errei isso repetidas vezes nesta sessão (reescrevi árvore de pastas, paleta de busca,
tabs e painéis redimensionáveis na mão antes de descobrir que `UTree`, `UCommandPalette`,
`UTabs` e `USplitter` já existiam) — o usuário teve que apontar cada um.

**Por quê importa** (não é só "menos código"): o usuário consegue re-temear a UI
**globalmente** editando o tema do Nuxt UI (`app.config.ts` / `appConfig.ui`) — isso só
funciona se os componentes reais do Nuxt UI forem usados. HTML+Tailwind cru não recebe
esses ajustes globais.

Versão instalada: ver `@nuxt/ui` em `package.json` (atualizar via `pnpm update @nuxt/ui`
quando um componente necessário só existir em versão mais nova — foi preciso ir de 4.9.0
para 4.11.0 para ter `USplitter`). Fonte de verdade sempre que a tabela abaixo não bastar:
`node_modules/.pnpm/@nuxt+ui@*/node_modules/@nuxt/ui/dist/runtime/components/*.vue` (o
`.vue` real da versão instalada, não a doc pública, que pode estar à frente).

### Mapa de componentes (relevantes para este dashboard SPA)

| Preciso de... | Use | Não escreva na mão |
| --- | --- | --- |
| Botão | `UButton` | `<button>` cru |
| Card / painel com cantos arredondados | `UCard` | `<div class="border rounded-lg">` |
| Separar painéis lado a lado/empilhados, redimensionável | `USplitter` | flex com larguras fixas + drag handler manual |
| Árvore de pastas/itens (expand/collapse, seleção) | `UTree` | lista recursiva de `<div>` com estado de collapse na mão |
| Busca com fuzzy match + atalho de teclado | `UCommandPalette` (dentro de `UModal`, ou `UDashboardSearch`/`UDashboardSearchButton` se for o padrão de busca do dashboard) | `<input>` + filtro manual + lista de resultados |
| Abas | `UTabs` | linha de `<button>` com `:class` condicional |
| Menu dropdown (clique) | `UDropdownMenu` | `UPopover` + lista de `<button>` na mão (só use `UPopover` para conteúdo que não é uma lista de ações — texto livre, formulário pequeno, etc.) |
| Popover simples (conteúdo livre) | `UPopover` | — |
| Menu de contexto (botão direito) | `UContextMenu` | — |
| Modal | `UModal` | overlay + div fixo na mão |
| Slideover (painel lateral deslizante) | `USlideover` | — |
| Select simples | `USelect` | `<select>` cru |
| Select com busca/multi/async | `USelectMenu` | — |
| Input de texto | `UInput` | `<input>` cru (exceção: quando precisa de controle fino de foco/timing dentro de um item de lista dinâmica — ver nota abaixo) |
| Textarea | `UTextarea` | `<textarea>` cru |
| Checkbox / grupo | `UCheckbox` / `UCheckboxGroup` | — |
| Radio group | `URadioGroup` | — |
| Switch (toggle) | `USwitch` | — |
| Tabela | `UTable` | `<table>` cru |
| Paginação | `UPagination` | — |
| Badge/tag pequeno | `UBadge` | `<span class="rounded-full px-2">` |
| Avatar | `UAvatar` / `UAvatarGroup` | — |
| Tooltip | `UTooltip` | `title="..."` cru quando precisa de estilo consistente |
| Atalho de teclado visual (⌘K etc.) | `UKbd` | `<span class="font-mono border rounded">` |
| Ícone | `UIcon` | — |
| Toast/notificação | `useToast()` + `UToast`/`UToaster` (já configurado globalmente) | — |
| Estado vazio | `UEmpty` | — |
| Skeleton de loading | `USkeleton` | — |
| Progress bar | `UProgress` | — |
| Editor de texto rico (Tiptap) | `UEditor` + `UEditorToolbar` (ver `content-type="markdown"`, slot `v-slot="{ editor }"` expõe a instância Tiptap real) | — |
| Upload de arquivo | `UFileUpload` | — |
| Date/time picker | `UInputDate` / `UInputTime` / `UCalendar` | — |
| Stepper (wizard multi-etapa) | `UStepper` | — |
| Accordion | `UAccordion` | — |
| Breadcrumb | `UBreadcrumb` | `span`/`/` na mão (já tem em `document-vault-view.vue` um breadcrumb feito na mão — candidato a migrar) |
| Chip (indicador de contagem/status sobre um ícone) | `UChip` | — |

### Componentes que existem mas **não** se aplicam aqui

`Page*`, `Blog*`, `Pricing*`, `ChangelogVersion*`, `Footer*`, `Header`, `Hero`,
`Marquee`, `Chat*` — são para sites de marketing/documentação estilo Nuxt Content
(Nuxt UI Pro templates) ou UI de chat com LLM. Este projeto é um dashboard SPA
autenticado; não fazem sentido aqui.

### Exceções legítimas para HTML cru

- `<input>` dentro de um item de lista dinâmica (linha de árvore sendo renomeada,
  célula de edição inline) onde é preciso controlar foco/timing exatos via
  `ref` callback + `watch(..., {flush:'post'}) + nextTick()` — `UInput` também
  funciona aqui, mas só vale a pena trocar se não estiver brigando com o wrapper.
- Overlays posicionados livremente por coordenadas de seleção de texto (botão
  flutuante "Comentar" ancorado em `editor.view.coordsAtPos()`) — não é o caso de
  uso do `UPopover` (que ancora em um elemento trigger, não em coordenadas livres).

## Auto-imports (via `@nuxt/ui/vite`)

O plugin `ui()` configura auto-import só para o essencial de framework:
- **Módulos:** `vue`, `vue-router`, `@vueuse/core` (`ref`, `computed`, `watch`, `useRoute`,
  `useDebounceFn`, etc. — nunca precisam de import)
- **Componentes:** todo `src/app/features/**` e `src/app/shared/components/**`, com prefixo `C`
  (ex: `sticky-card.vue` → `<CStickyCard>`) — nome vem só do filename, a pasta não importa

**Composables, types, constants, schemas e utils do projeto NÃO são mais auto-importados —
usam import explícito** (`import { useTask } from '@/app/features/task/composables/task'` /
`import type { iTask } from '@/app/features/task/types'`). Essa é uma mudança deliberada: o
mecanismo antigo (`unimport`/`unplugin-auto-import` escaneando `src/composables`, `src/utils`,
`src/types` etc.) tem uma pegadinha real — o scan de cada diretório em `dirs` é **raso**
(`dir/*.ts`, não `dir/**/*.ts`); só resolve arquivos aninhados se algum arquivo direto naquele
dir fizer `export * from` apontando pra eles. Isso já causou uma sessão inteira de debug
(centenas de "cannot find name" silenciosos) quando a estrutura virou `features/`. Import
explícito elimina essa classe de bug e deixa "de onde vem isso" visível sem depender de um
`.d.ts` gerado.

Componentes continuam auto-registrados (`unplugin-vue-components`, que É recursivo de verdade)
— o ganho de "só usar `<CBotão>`" compensa o "de onde vem" ali, já que o nome já é derivável do
filename.

## Estilo de código

- Variáveis sempre descritivas — nunca usar nomes de uma letra (ex: `p`, `e`, `v`, `fd`)
- Foco em código legível: preferir clareza sobre brevidade

## Convenções

- Alias `@` → `src/` (código do app fica sob `@/app/...`; `@/styles/...` é o CSS global)
- Componentes Nuxt UI prefixados com `C` (ex: `<CButton>`)
- Modais/Slideovers: abrir sempre via `useOverlay()` (nunca `v-model:open` direto na página)
- Rotas: um `routes.ts` por feature, montado em `app/core/routes.ts` — ver "Roteamento" acima
- Guards de navegação: `userGuard` → `workplaceGuard` → `profileGuard`
- Proxy dev: `/api` e `/media` → backend (via env `VITE_API_URL`)
- Paginação: usar `iPaginationNumber<T>` de `app/shared/types/pagination.ts`

## Padrão de componentes

| Pasta                                   | Critério                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------------- |
| `app/shared/components/*.vue`           | Primitivo reutilizável sem lógica de negócio                                  |
| `app/shared/components/<algo>/`         | Usado por 2+ features, não pertence a nenhuma (cover, dashboard, search)       |
| `app/features/<nome>/components/`       | Específico da feature — pode ter subpastas quando há muitos arquivos          |
| `app/features/form/components/editor/`  | Exceção: tem arquivos filhos (`block/`) que justificam subpasta               |
| `app/features/task/components/kanban/`  | Subpasta por tipo de visualização                                             |
| `app/features/settings/components/`     | Subpastas `general/`, `integration/` e `workplace/`                           |
| `app/shared/components/cover/`          | Seletor de capa reutilizável — usado por document, form, workplace e user     |
| `app/features/document/components/layout\|panel\|tree/` | Agrupado pelo consumidor real: `layout/` = as 3 estruturas da página (left/center/right-splitter); `panel/` = abas abertas só pelo right-splitter; `tree/` = dialogs/popover abertos só pelo left-splitter. Um arquivo sem irmão de mesmo domínio (`document-cover.vue`, `document-preview.vue`, `document-command-palette.vue`, `document-graph-modal.vue`) fica solto na raiz de `components/` em vez de ganhar uma subpasta de arquivo único |

## Capas (cover)

Toda capa da aplicação usa o mesmo seletor, `CCoverPicker` (Galeria de cores/gradientes, Unsplash,
Upload e Link). Ele emite `select-file` (arquivo) ou `select-style` (`style`, `credit`).

O valor escolhido vai para dois campos no backend: o `ImageField` existente (`cover`, `cover_image`
ou `photo`) quando é upload, e `cover_style` + `cover_credit` quando é cor, gradiente, link ou foto
do Unsplash. Para renderizar use `coverImageSrc()` / `coverBackgroundStyle()` de
`app/shared/utils/cover.ts` — o arquivo enviado sempre tem precedência sobre o `cover_style`.

Fotos do Unsplash exigem exibir a atribuição: renderize `CCoverCredit` junto da capa. A busca passa
pelo proxy do backend (`useUnsplash()`), nunca direto na API do Unsplash.

Onde já está ligado: documento (`CDocumentCover`), perfil e workplace (`CCoverBanner`) e formulário
(`CFormUpsertDialog`).

## Compartilhamento de documento (`can_edit`, sharing)

O backend calcula `can_edit`/`can_manage_sharing`/`is_admin_view` por request (ver
`api/AGENTS.md` → Permissões por objeto) — **nunca reimplemente essa lógica de papel/permissão
no frontend**, sempre confie nesses campos vindos da API.

- `useDocumentEditing`'s `isReadonly` combina três motivos independentes: a versão foi
  publicada (trava de workflow), `doc.can_edit` é `false` (sem permissão de edição), ou
  outra pessoa está com a trava de edição em tempo real (ver abaixo) — qualquer um cai pro
  modo leitura (`CDocumentPreview`), escondendo título, ícone, troca de capa e o editor de
  conteúdo. `CDocumentCenterSplitter` mostra um banner explicando qual dos três é ("fulano
  está editando agora" / "versão publicada" / "só visualização") — antes disso os três casos
  eram visualmente idênticos e pareciam bug de permissão.
- `CDocumentPanelShare` (popover no `CDocumentRightPanel`, ícone de cadeado/pessoas) edita
  `visibility` ('private' | 'workplace') e `allow_member_edit` — desabilitado quando
  `!doc.can_manage_sharing` (só autor/admin do workplace pode mudar).
- `updateDocSharing()` em `documentVault.ts` (`app/features/document/composables/`) faz o PATCH
  otimista, igual ao padrão de `updateDocCover`/`updateDocType`.

## Realtime de documento (WebSocket)

`useDocumentRealtime(documentId, { onDocumentChanged })` (em `documentEditing.ts`, dentro de
`app/features/document/composables/`) mantém uma conexão com `ws/documents/<id>/` (ver
`api/AGENTS.md` → Realtime) — proxied em dev via `vite.config.ts` (`/ws`, com `ws: true`).

- `useDocumentEditing` chama `acquireLock()`/`releaseLock()` sozinho, assistindo
  `structurallyEditable` (rascunho + `can_edit`) — não chame isso na mão em outro lugar.
  Heartbeat a cada 8s enquanto segura a trava; reconecta sozinho (2s) se a conexão cair sem
  ter sido um `disconnect()` intencional (troca de doc, unmount).
- `lockedBy`/`isLockedByOther`, retornados por `useDocumentEditing`, alimentam o banner em
  `CDocumentCenterSplitter` — não construa um segundo indicador de "quem está editando" em
  outro componente, passe esses dois adiante.
- `onDocumentChanged` (evento `document_changed` do servidor) refaz o `GET` do documento e
  faz `Object.assign(doc, fresh)` — mutação direta no objeto que já vive em
  `documentVault.ts`'s `docs`, mesmo padrão das outras mutações em `documentEditing.ts`
  (`onTitleInput`, `onContentChange` etc. também mutam `activeDoc.value` direto).

## Padrão de composables

| Local                                    | Critério                                                          |
| ------------------------------------------ | -------------------------------------------------------------------- |
| `app/shared/composables/*.ts`              | Genérico, sem vínculo de domínio (`accentColor.ts`, `shake.ts`)      |
| `app/shared/composables/<algo>/`           | Usado por 2+ features ou é integração externa (`drive/`, `unsplash/`, `search/`) |
| `app/features/<nome>/composables/`         | Específico da feature, com `index.ts` reexportando o barrel          |

## Comandos

```bash
pnpm install        # Instalar dependências
pnpm dev            # Servidor de desenvolvimento
pnpm build          # Build de produção (type-check + vite build)
pnpm lint           # Lint (oxlint + eslint com --fix)
pnpm format         # Formatar com oxfmt
pnpm test:unit      # Testes via Vitest
```
