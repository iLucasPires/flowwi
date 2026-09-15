<script setup lang="ts">
import type { iDocumentType } from '@/app/features/document/types'
import type { DropdownMenuItem } from '@nuxt/ui'
import type { iDocSortOrder, iDocTreeItem } from '@/app/features/document/composables/documentVault'

const props = defineProps<{
  treeItems: iDocTreeItem[]
  activeId: number | null
  documentTypes: iDocumentType[]
}>()

const emit = defineEmits<{
  openPalette: []
  openGraph: []
  createFromTemplate: [typeId: number | null]
  deleteDoc: [id: number]
  renameDoc: [id: number, title: string]
  duplicateDoc: [id: number]
  updateType: [id: number, type: number | null]
}>()

const toast = useToast()
const route = useRoute()

const sortOrder = defineModel<iDocSortOrder>('sortOrder', { required: true })
const typeFilter = defineModel<(number | null)[]>('typeFilter', { default: () => [] })

// -----------------------------------------------------------------------------
// Context menu (right-click)
// -----------------------------------------------------------------------------

const contextMenuItem = ref<iDocTreeItem | null>(null)

function findItemByDocId(items: iDocTreeItem[], docId: number): iDocTreeItem | null {
  for (const item of items) {
    if (item.docId === docId) return item
    if (item.children) {
      const found = findItemByDocId(item.children, docId)
      if (found) return found
    }
  }
  return null
}

function onTreeContextMenu(event: MouseEvent) {
  // Sobe até o <li> do item de árvore, depois encontra o marcador data-doc-id dentro dele
  const listItemEl = (event.target as HTMLElement).closest('li[role="presentation"]')
  if (!listItemEl) return
  const markerEl = listItemEl.querySelector('[data-doc-id]')
  if (!markerEl) {
    // Clicou em grupo sem docId — bloqueia abertura do menu
    event.preventDefault()
    event.stopPropagation()
    return
  }
  const docId = Number(markerEl.getAttribute('data-doc-id'))
  const item = findItemByDocId(props.treeItems, docId)
  if (!item) return
  contextMenuItem.value = item
}

const contextMenuItems = computed(() =>
  contextMenuItem.value ? pageMenuItems(contextMenuItem.value) : [],
)

// -----------------------------------------------------------------------------
// Tree
// -----------------------------------------------------------------------------

const collapsedGroups = ref(new Set<string>())

function getGroupKeys(items: iDocTreeItem[]): string[] {
  return items.flatMap((item) =>
    item.children ? [item.value, ...getGroupKeys(item.children)] : [],
  )
}

const expandedKeys = computed(() =>
  getGroupKeys(props.treeItems).filter((key) => !collapsedGroups.value.has(key)),
)

function updateExpanded(keys: string[]) {
  const groups = getGroupKeys(props.treeItems)

  collapsedGroups.value = new Set(groups.filter((group) => !keys.includes(group)))
}

// -----------------------------------------------------------------------------
// Delete (with confirmation)
// -----------------------------------------------------------------------------

const overlay = useOverlay()

async function requestDelete(item: iDocTreeItem) {
  if (item.docId == null) return

  const component = resolveComponent('CDocumentDeleteDialog')
  if (typeof component !== 'object') return

  const modal = overlay.create(component, { props: { title: item.label } })
  const confirmed = await modal.open()
  if (confirmed) emit('deleteDoc', item.docId)
}

// -----------------------------------------------------------------------------
// Rename (dialog)
// -----------------------------------------------------------------------------

async function requestRename(item: iDocTreeItem) {
  if (item.docId == null) return

  const component = resolveComponent('CDocumentRenameDialog')
  if (typeof component !== 'object') return

  const modal = overlay.create(component, { props: { title: item.label } })
  const title = await modal.open()
  if (title != null) emit('renameDoc', item.docId, title)
}

// -----------------------------------------------------------------------------
// Copy link / open in new tab
// -----------------------------------------------------------------------------

function docUrl(item: iDocTreeItem) {
  return `${location.origin}${route.path}?doc=${item.docId}`
}

async function copyLink(item: iDocTreeItem) {
  await navigator.clipboard.writeText(docUrl(item))
  toast.add({ title: 'Link copiado', icon: 'i-lucide-check' })
}

function openInNewTab(item: iDocTreeItem) {
  window.open(docUrl(item), '_blank')
}

// -----------------------------------------------------------------------------
// Page menu (Notion-style)
// -----------------------------------------------------------------------------

function pageMenuItems(item: iDocTreeItem): DropdownMenuItem[][] {
  if (item.docId == null) return []
  const docId = item.docId

  const typeItems: DropdownMenuItem[] = [
    {
      label: 'Sem tipo',
      icon: 'i-lucide-file-question',
      checked: item.type == null,
      type: 'checkbox' as const,
      onSelect: () => emit('updateType', docId, null),
    },
    ...props.documentTypes.map((t) => ({
      label: t.name,
      icon: t.icon || 'i-lucide-tag',
      color: t.color,
      checked: item.type === t.id,
      type: 'checkbox' as const,
      onSelect: () => emit('updateType', docId, t.id),
    })),
  ]

  return [
    [
      { label: 'Copiar link', icon: 'i-lucide-link', onSelect: () => copyLink(item) },
      { label: 'Duplicar', icon: 'i-lucide-copy', onSelect: () => emit('duplicateDoc', docId) },
      { label: 'Renomear', icon: 'i-lucide-pencil', onSelect: () => requestRename(item) },
      { label: 'Mudar tipo', icon: 'i-lucide-tag', children: typeItems },
    ],
    [
      {
        label: 'Mover para lixeira',
        icon: 'i-lucide-trash-2',
        color: 'error',
        onSelect: () => requestDelete(item),
      },
    ],
    [
      {
        label: 'Abrir em nova aba',
        icon: 'i-lucide-external-link',
        onSelect: () => openInNewTab(item),
      },
    ],
  ]
}

defineOptions({
  name: 'DocumentTree',
})
</script>

<template>
  <div class="flex size-full min-h-0 flex-col">
    <CDocumentTreeHeader
      v-model:sort-order="sortOrder"
      v-model:type-filter="typeFilter"
      :document-types="documentTypes"
      @open-palette="emit('openPalette')"
      @open-graph="emit('openGraph')"
      @create-from-template="emit('createFromTemplate', $event)"
    />

    <!-- Tree -->
    <!-- Single UContextMenu driven by @contextmenu event on the container -->
    <UContextMenu :items="contextMenuItems" size="xs" class="min-h-0 flex-1 overflow-hidden">
      <main class="min-h-0 flex-1 overflow-y-auto px-3 py-3" @contextmenu="onTreeContextMenu">
        <UTree
          :items="treeItems"
          :expanded="expandedKeys"
          :get-key="(item: iDocTreeItem) => item.value"
          size="xs"
          color="neutral"
          @update:expanded="updateExpanded"
        >
          <!-- Leading icon + data-doc-id marker for context menu hit-testing -->
          <template #item-leading="{ item }">
            <span v-if="item.docId != null" class="contents" :data-doc-id="item.docId" />
            <CIconOrEmoji
              v-if="item.icon"
              :value="item.icon"
              class="size-4 shrink-0 text-sm"
              :style="item.color ? { color: item.color } : undefined"
            />
          </template>

          <!-- Trailing: group chevron, or a hover-reveal page menu on doc rows -->
          <template #item-trailing="{ item, expanded }">
            <UIcon
              v-if="item.children?.length"
              name="i-lucide-chevron-down"
              class="size-4 shrink-0 transition-transform"
              :class="expanded ? 'rotate-180' : ''"
            />
            <UDropdownMenu
              v-else-if="item.docId != null"
              :items="pageMenuItems(item)"
              size="xs"
              :content="{ align: 'start' }"
            >
              <UButton
                icon="i-lucide-ellipsis-vertical"
                variant="ghost"
                color="neutral"
                size="xs"
                class="opacity-0 group-hover:opacity-100 data-[state=open]:opacity-100"
                @click.stop
              />
            </UDropdownMenu>
          </template>
        </UTree>
      </main>
    </UContextMenu>
  </div>
</template>
