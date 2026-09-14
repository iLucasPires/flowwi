import { API_DOCUMENT_URLS, apiFetch } from '@/app/core/clients/api'
import type { iDocument, iDocumentVisibility } from '@/app/features/document/types'
import type { iCoverUpdate } from '@/app/shared/types/cover'
import { useDocument } from './document'
import { useDocumentType } from './documentType'

const WIKILINK_RE = /\[\[([^\]]+)\]\]/g

function linksOf(doc: iDocument): string[] {
  const content = doc.versions[0]?.content ?? ''
  const set: string[] = []
  WIKILINK_RE.lastIndex = 0
  let m: RegExpExecArray | null
  while ((m = WIKILINK_RE.exec(content))) {
    const title = m[1]
    if (title && !set.includes(title)) set.push(title)
  }
  return set
}

export type iDocSortOrder = 'newest' | 'oldest' | 'title'

export const DOC_SORT_ITEMS: { label: string; value: iDocSortOrder }[] = [
  { label: 'Mais recentes', value: 'newest' },
  { label: 'Mais antigos', value: 'oldest' },
  { label: 'Alfabética', value: 'title' },
]

export interface iDocTreeItem {
  label: string
  icon?: string
  color?: string
  value: string
  docId: number | null
  type: number | null
  badge: string
  defaultExpanded?: boolean
  children?: iDocTreeItem[]
  onSelect?: () => void
}

export function useDocumentVault() {
  const toast = useToast()
  const { documents, isLoading, createDocument, deleteDocument } = useDocument()
  const { types: documentTypes } = useDocumentType()

  const docs = ref<iDocument[]>([])
  const activeId = ref<number | null>(null)

  const sortOrder = ref<iDocSortOrder>('newest')
  /** Type ids to show; `null` stands for the "Sem tipo" group. Empty = show all. */
  const typeFilter = ref<(number | null)[]>([])

  function sortDocs(list: iDocument[]): iDocument[] {
    const sorted = [...list]
    if (sortOrder.value === 'title') {
      sorted.sort((a, b) => (a.title || 'Sem título').localeCompare(b.title || 'Sem título'))
    } else {
      sorted.sort((a, b) => {
        const diff = new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        return sortOrder.value === 'newest' ? diff : -diff
      })
    }
    return sorted
  }

  // Reconciles on every fresh fetch, not just the first — a remote sync (see
  // `useWorkplaceSync`) invalidates the underlying query whenever someone else
  // creates/renames/deletes a document, and this is what makes that show up in the
  // tree. The doc currently open is the one exception: its entry is kept exactly as
  // it is locally (own in-flight edits use raw PATCHes below, not this query, so a
  // wholesale replace would flash it back to whatever was last saved).
  watch(
    documents,
    (list) => {
      if (isLoading.value) return

      const activeIdValue = activeId.value
      docs.value = list.map(
        (d) => (d.id === activeIdValue ? (docs.value.find((x) => x.id === d.id) ?? d) : d),
      )

      if (activeIdValue == null) {
        if (docs.value.length) activeId.value = docs.value[0]!.id
      } else if (!docs.value.some((d) => d.id === activeIdValue)) {
        activeId.value = docs.value[0]?.id ?? null
      }
    },
    { immediate: true },
  )

  const activeDoc = computed(() => docs.value.find((d) => d.id === activeId.value))

  function openDoc(id: number) {
    activeId.value = id
  }

  function openByTitle(title: string) {
    const hit = docs.value.find((d) => d.title === title)
    if (hit) openDoc(hit.id)
  }

  function docItem(d: iDocument): iDocTreeItem {
    return {
      label: d.title || 'Sem título',
      icon: d.icon || 'i-lucide-file-edit',
      value: `doc:${d.id}`,
      docId: d.id,
      type: d.type,
      badge: d.comments.length ? String(d.comments.length) : '',
      onSelect: () => openDoc(d.id),
    }
  }

  // Grouping is by document type (tag), not by folder — each type with at least
  // one document becomes a top-level group, ordered the same as in Settings;
  // documents without a type land in a trailing "Sem tipo" group.
  const treeItems = computed<iDocTreeItem[]>(() => {
    const byType = new Map<number, iDocument[]>()
    const untyped: iDocument[] = []

    for (const d of docs.value) {
      if (d.type == null) {
        untyped.push(d)
        continue
      }
      const list = byType.get(d.type) ?? []
      list.push(d)
      byType.set(d.type, list)
    }

    const showAll = typeFilter.value.length === 0
    const groups: iDocTreeItem[] = []

    for (const t of documentTypes.value) {
      if (!showAll && !typeFilter.value.includes(t.id)) continue
      const list = byType.get(t.id)
      if (!list?.length) continue
      groups.push({
        label: t.name,
        icon: t.icon || 'i-lucide-tag',
        color: t.color,
        value: `type:${t.id}`,
        docId: null,
        type: t.id,
        badge: '',
        defaultExpanded: true,
        children: sortDocs(list).map(docItem),
      })
    }

    if ((showAll || typeFilter.value.includes(null)) && untyped.length) {
      groups.push({
        label: 'Sem tipo',
        icon: 'i-lucide-file-question',
        value: 'type:none',
        docId: null,
        type: null,
        badge: '',
        defaultExpanded: true,
        children: sortDocs(untyped).map(docItem),
      })
    }

    return groups
  })

  const outline = computed(() => {
    const version = activeDoc.value?.versions[0]
    if (!version) return []
    return version.content
      .split('\n')
      .filter((raw) => /^#{1,3} /.test(raw))
      .map((raw) => {
        const lvl = raw.match(/^#+/)![0].length
        return {
          text: raw.replace(/^#+ /, ''),
          pad: `${8 + (lvl - 1) * 12}px`,
          weight: lvl === 1 ? 600 : lvl === 2 ? 500 : 400,
          color:
            lvl === 1
              ? 'var(--ui-text-highlighted)'
              : lvl === 2
                ? 'var(--ui-text-toned)'
                : 'var(--ui-text-dimmed)',
        }
      })
  })

  const outlinks = computed(() => {
    const doc = activeDoc.value
    if (!doc) return []
    return linksOf(doc).map((title) => {
      const exists = docs.value.some((d) => d.title === title)
      return {
        title: exists ? title : `${title} · não existe`,
        exists,
        onOpen: () => openByTitle(title),
      }
    })
  })

  const backlinks = computed(() => {
    const doc = activeDoc.value
    if (!doc) return []
    return docs.value
      .filter((d) => d.id !== doc.id && linksOf(d).includes(doc.title))
      .map((d) => {
        const version = d.versions[0]
        const hit = version?.content.split('\n').find((l) => l.includes(`[[${doc.title}]]`)) || ''
        return {
          id: d.id,
          title: d.title || 'Sem título',
          excerpt: hit
            .replace(/^[#>\-\d.\s[\]x]*/, '')
            .replace(/\[\[|\]\]|\*\*|`/g, '')
            .trim()
            .slice(0, 110),
          onOpen: () => openDoc(d.id),
        }
      })
  })

  const graph = computed(() => {
    const list = docs.value
    const pos: Record<string, { x: number; y: number }> = {}
    list.forEach((d, i) => {
      const a = (i / list.length) * Math.PI * 2 - Math.PI / 2
      pos[d.title] = { x: 410 + Math.cos(a) * 290, y: 250 + Math.sin(a) * 175 }
    })

    const edges: { x1: number; y1: number; x2: number; y2: number; stroke: string; w: number }[] =
      []
    for (const d of list) {
      for (const title of linksOf(d)) {
        const target = pos[title]
        const source = pos[d.title]
        if (!target || !source) continue
        const isActive = d.id === activeDoc.value?.id || title === activeDoc.value?.title
        edges.push({
          x1: source.x,
          y1: source.y,
          x2: target.x,
          y2: target.y,
          stroke: isActive ? 'var(--ui-text-muted)' : 'var(--ui-border)',
          w: isActive ? 1.4 : 1,
        })
      }
    }

    const degree: Record<string, number> = {}
    for (const d of list) degree[d.title] = 0
    for (const d of list) {
      for (const title of linksOf(d)) {
        if (pos[title] == null) continue
        degree[title] = (degree[title] ?? 0) + 1
        degree[d.title] = (degree[d.title] ?? 0) + 1
      }
    }

    const nodes = list.map((d) => {
      const on = d.id === activeDoc.value?.id
      const size = 10 + Math.min(degree[d.title] ?? 0, 5) * 3
      const p = pos[d.title]!
      return {
        id: d.id,
        left: `${p.x}px`,
        top: `${p.y}px`,
        size: `${size}px`,
        fill: on ? 'var(--ui-text-highlighted)' : 'var(--ui-border-accented)',
        ring: on ? 'var(--ui-text-highlighted)' : 'var(--ui-border-accented)',
        color: on ? 'var(--ui-text-highlighted)' : 'var(--ui-text-dimmed)',
        title: (d.title || 'Sem título').replace(/^(Roteiro|Briefing|Escaleta|Template) — /, ''),
        onOpen: () => openDoc(d.id),
      }
    })

    return { nodes, edges }
  })

  /**
   * `typeId: null` creates a blank document. Otherwise the new document is seeded from
   * that document type's own `default_content` — configured per type in Settings, so
   * there's no separate hardcoded template list to keep in sync with the real types.
   */
  async function createFromTemplate(typeId: number | null) {
    const type = typeId != null ? documentTypes.value.find((t) => t.id === typeId) : undefined
    try {
      const created = await createDocument({
        title: type ? `Novo — ${type.name}` : '',
        type: type?.id ?? null,
        content: type?.default_content ?? '',
      })
      docs.value.push(created)
      activeId.value = created.id
    } catch {
      toast.add({ title: 'Erro ao criar documento', color: 'error' })
    }
  }

  async function removeDoc(id: number) {
    await deleteDocument(id)
    docs.value = docs.value.filter((d) => d.id !== id)
    if (activeId.value === id) activeId.value = docs.value[0]?.id ?? null
  }

  async function updateDocTitle(id: number, title: string) {
    const doc = docs.value.find((d) => d.id === id)
    if (!doc) return
    const previous = doc.title
    doc.title = title
    try {
      await apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: 'PATCH', body: { title } })
    } catch {
      doc.title = previous
      toast.add({ title: 'Erro ao renomear documento', color: 'error' })
    }
  }

  async function duplicateDoc(id: number) {
    const doc = docs.value.find((d) => d.id === id)
    if (!doc) return
    try {
      const created = await createDocument({
        title: doc.title ? `${doc.title} (cópia)` : '',
        folder: doc.folder,
        type: doc.type,
        content: doc.versions[0]?.content ?? '',
      })
      docs.value.push(created)
      activeId.value = created.id
    } catch {
      toast.add({ title: 'Erro ao duplicar documento', color: 'error' })
    }
  }

  async function updateDocType(id: number, type: number | null) {
    const doc = docs.value.find((d) => d.id === id)
    if (!doc) return
    const previous = doc.type
    doc.type = type
    try {
      await apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: 'PATCH', body: { type } })
    } catch {
      doc.type = previous
      toast.add({ title: 'Erro ao atualizar tipo', color: 'error' })
    }
  }

  async function updateDocIcon(id: number, icon: string) {
    const doc = docs.value.find((d) => d.id === id)
    if (!doc) return
    const previous = doc.icon
    doc.icon = icon
    try {
      await apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: 'PATCH', body: { icon } })
    } catch {
      doc.icon = previous
      toast.add({ title: 'Erro ao atualizar ícone', color: 'error' })
    }
  }

  async function updateDocCover(id: number, update: iCoverUpdate) {
    const doc = docs.value.find((d) => d.id === id)
    if (!doc) return
    const previousCover = doc.cover
    const previousStyle = doc.cover_style
    const previousCredit = doc.cover_credit
    try {
      let body: FormData | Record<string, unknown>
      if (update && 'file' in update) {
        body = new FormData()
        body.append('cover', update.file)
        body.append('cover_style', '')
      } else if (update && 'style' in update) {
        body = { cover: null, cover_style: update.style, cover_credit: update.credit }
      } else {
        body = { cover: null, cover_style: '', cover_credit: null }
      }
      const updated = await apiFetch<iDocument>(`${API_DOCUMENT_URLS.LIST}/${id}`, {
        method: 'PATCH',
        body,
      })
      doc.cover = updated.cover
      doc.cover_style = updated.cover_style
      doc.cover_credit = updated.cover_credit
    } catch {
      doc.cover = previousCover
      doc.cover_style = previousStyle
      doc.cover_credit = previousCredit
      toast.add({ title: 'Erro ao atualizar capa', color: 'error' })
    }
  }

  /** Sharing settings — backend rejects this for anyone but the author/workplace admins. */
  async function updateDocSharing(
    id: number,
    update: { visibility?: iDocumentVisibility; allow_member_edit?: boolean },
  ) {
    const doc = docs.value.find((d) => d.id === id)
    if (!doc) return
    const previousVisibility = doc.visibility
    const previousAllowMemberEdit = doc.allow_member_edit
    Object.assign(doc, update)
    try {
      const updated = await apiFetch<iDocument>(`${API_DOCUMENT_URLS.LIST}/${id}`, {
        method: 'PATCH',
        body: update,
      })
      doc.visibility = updated.visibility
      doc.allow_member_edit = updated.allow_member_edit
    } catch {
      doc.visibility = previousVisibility
      doc.allow_member_edit = previousAllowMemberEdit
      toast.add({ title: 'Erro ao atualizar compartilhamento', color: 'error' })
    }
  }

  return {
    docs,
    isLoading,
    activeId,
    activeDoc,
    openDoc,
    openByTitle,
    treeItems,
    documentTypes,
    sortOrder,
    typeFilter,
    outline,
    outlinks,
    backlinks,
    graph,
    createFromTemplate,
    removeDoc,
    updateDocType,
    updateDocTitle,
    updateDocIcon,
    updateDocCover,
    updateDocSharing,
    duplicateDoc,
  }
}
