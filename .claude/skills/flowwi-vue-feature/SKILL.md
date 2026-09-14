---
name: flowwi-vue-feature
description: Scaffold a new feature (vertical slice) in the FlowWi Vue 3 frontend (apps/app), or add a component/composable to an existing one, following the feature-based folder structure, routing, auto-import and Nuxt UI conventions. Use when adding a new page/section to the dashboard, a new Vue component, or a new composable.
---

# FlowWi — Nova feature Vue (`apps/app`)

Checklist para adicionar uma feature nova ou estender uma existente em `src/app/`. Detalhe completo em
`apps/app/AGENTS.md` — esta skill é o passo a passo + as duas regras que mais geram retrabalho se
ignoradas (Nuxt UI e auto-imports).

## 0. Regra dura: antes de escrever UI custom, olhe o Nuxt UI

**Nunca** escreva `<button>`, `<select>`, dropdown, popover, árvore, tabs, painéis redimensionáveis ou
paleta de comando na mão sem checar primeiro se o Nuxt UI já tem o componente. Isso já causou retrabalho
real neste projeto (árvore de pastas, busca, tabs e splitters reescritos e depois jogados fora).

| Preciso de... | Use |
|---|---|
| Botão | `UButton` |
| Card / painel arredondado | `UCard` (nunca `border` cru — ver preferência de separação de painéis abaixo) |
| Painéis lado a lado redimensionáveis | `USplitter` |
| Árvore (expand/collapse, seleção) | `UTree` |
| Busca com fuzzy match / ⌘K | `UCommandPalette` (ou `UDashboardSearch*` se for a busca padrão do dashboard) |
| Abas | `UTabs` |
| Dropdown de ações | `UDropdownMenu` (não `UPopover` + botões na mão) |
| Popover de conteúdo livre | `UPopover` |
| Menu de contexto | `UContextMenu` |
| Modal / Slideover | `UModal` / `USlideover` (abrir via `useOverlay()`, nunca `v-model:open` direto na página) |
| Select | `USelect` (simples) / `USelectMenu` (busca/multi/async) |
| Input / Textarea | `UInput` / `UTextarea` |
| Checkbox / Radio / Switch | `UCheckbox(Group)` / `URadioGroup` / `USwitch` |
| Tabela / Paginação | `UTable` / `UPagination` |
| Badge / Avatar / Tooltip / Ícone / Kbd | `UBadge` / `UAvatar` / `UTooltip` / `UIcon` / `UKbd` |
| Toast | `useToast()` + `UToast`/`UToaster` |
| Empty state / Skeleton / Progress | `UEmpty` / `USkeleton` / `UProgress` |
| Editor rico (Tiptap) | `UEditor` + `UEditorToolbar` |
| Upload | `UFileUpload` |
| Date/time picker | `UInputDate` / `UInputTime` / `UCalendar` |
| Stepper / Accordion / Breadcrumb / Chip | `UStepper` / `UAccordion` / `UBreadcrumb` / `UChip` |

Exceções legítimas para HTML cru: `<input>` dentro de uma linha de lista em edição inline (controle fino
de foco/timing), e overlays ancorados em coordenadas livres (não em um elemento trigger).

Se um componente necessário só existe em versão mais nova do `@nuxt/ui`, rode
`pnpm update @nuxt/ui` — não reescreva na mão por estar desatualizado. Fonte de verdade quando a tabela
não bastar: `node_modules/.pnpm/@nuxt+ui@*/node_modules/@nuxt/ui/dist/runtime/components/*.vue`.

**Separação visual entre painéis**: usar `UCard` com cantos arredondados, nunca uma borda/divider reto —
preferência de design consistente no app inteiro.

## 1. Decidir: `features/<nome>` ou `shared/`

- Corresponde a um domínio do backend (`apps/api/apps/domains/*`) ou é uma área autocontida do próprio
  frontend (ex.: `settings`) → **`app/features/<nome>/`**.
- Usado por 2+ features e não pertence a nenhuma (cover picker, busca, primitivos de UI) → **`app/shared/`**.
- Integração externa (equivalente a `apps/api/apps/integrations/*`, ex.: `drive`, `unsplash`) →
  **`app/shared/composables/<nome>/`**, não em `features/`.

## 2. Esqueleto de uma feature nova

```
app/features/<nome>/
├── components/          # subpastas quando há muitos arquivos (ver critério abaixo)
├── composables/
│   └── <nome>.ts
├── pages/
│   └── <nome>-list.vue
├── routes.ts            # array de RouteRecordRaw, path relativo ao layout pai
├── types.ts
├── constants.ts
├── schemas.ts           # (opcional) validação Zod
├── utils.ts             # (opcional)
├── guards/              # (opcional) navigation guards da própria feature
└── index.ts             # barrel — reexporta o que existir
```

`index.ts` (barrel — só o que existir):
```ts
export * from './composables'
export * from './types'
export * from './schemas'
export * from './constants'
export * from './utils'
```

`routes.ts`:
```ts
export const taskRoutes: RouteRecordRaw[] = [
  { path: 'tasks', component: () => import('./pages/task-list.vue') },
  { path: 'tasks/:id', component: () => import('./pages/task-detail.vue') },
]
```

Registrar em `app/core/routes.ts`: importar o array e adicionar em `children` do layout certo
(`AccountLayout`, `PublicLayout` ou `DashboardLayout`). **Nunca** monte rotas dentro da própria feature.

## 3. Guards

Guard mora na feature dona do que verifica (ex.: `userGuard`/`profileGuard` em
`app/features/user/guards/`, `workplaceGuard` em `app/features/workplace/guard.ts`), mas só é
importado/registrado (`router.beforeEach`) em `app/core/routes.ts`. Ordem atual: `userGuard` →
`workplaceGuard` → `profileGuard`.

## 4. Onde colocar componentes

| Local | Critério |
|---|---|
| `app/shared/components/*.vue` | Primitivo reutilizável sem lógica de negócio |
| `app/shared/components/<algo>/` | Usado por 2+ features (ex.: `cover/`, `dashboard/`, `search/`) |
| `app/features/<nome>/components/` | Específico da feature |
| `app/features/<nome>/components/<subpasta>/` | Só quando há muitos arquivos (ex.: `task/kanban/`, `form/editor/block/`) |

## 5. Onde colocar composables

| Local | Critério |
|---|---|
| `app/shared/composables/*.ts` | Genérico, sem domínio (`accentColor.ts`, `shake.ts`) |
| `app/shared/composables/<algo>/` | Usado por 2+ features ou é integração externa (`drive/`, `unsplash/`) |
| `app/features/<nome>/composables/` | Específico da feature — reexportado no `index.ts` da feature |

## 6. Imports — o que é auto e o que não é

Auto-import (via `@nuxt/ui/vite`) cobre **só**:
- `vue`, `vue-router`, `@vueuse/core` (`ref`, `computed`, `useRoute`, `useDebounceFn`, ...)
- Componentes de `app/features/**` e `app/shared/components/**`, prefixados `C` pelo nome do arquivo
  (`sticky-card.vue` → `<CStickyCard>`)

**Tudo o resto é import explícito** — composables, types, constants, schemas, utils do projeto:
```ts
import { useTask } from '@/app/features/task/composables/task'
import type { iTask } from '@/app/features/task/types'
```
Isso é deliberado (o scan automático antigo era raso e causava "cannot find name" silenciosos) — não
tente reativar auto-import para essas categorias.

## 7. Convenções gerais

- Alias `@` → `src/`
- Componentes Nuxt UI prefixados `C`
- Modais/Slideovers via `useOverlay()`, nunca `v-model:open` direto na página
- Variáveis sempre descritivas, nunca nomes de uma letra
- Paginação: `iPaginationNumber<T>` de `app/shared/types/pagination.ts`
- `useRoute().params.id` não vem mais tipado (sem typed-router) — use `String(route.params.id)` ao
  repassar para algo que espera `string`

## 8. Antes de terminar

```bash
pnpm lint         # oxlint + eslint --fix
pnpm format       # oxfmt
pnpm test:unit    # se a feature tiver lógica testável
pnpm build        # type-check + vite build
```
