import { API_FORM_URLS, apiFetch } from '@/app/core/clients/api'
import type { tFormBlockOut, tFormOut, tFormPageOut } from '@/app/features/form/schemas'
import type { iFormBlockCondition, iFormBlockDraft, iFormPageDraft, tFormBlockType } from '@/app/features/form/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import type { iCoverUpdate } from '@/app/shared/types/cover'

export function useFormEditor(formId: string | number) {
  const toast = useToast()
  const formData = ref<tFormOut | null>(null)
  const loading = ref(true)
  const isSaving = ref(false)
  const hasError = ref(false)
  const selectedPage = ref(0)
  const pages = ref<iFormPageDraft[]>([
    { key: crypto.randomUUID(), title: '', description: '', order: 0, blocks: [] },
  ])

  const initialHasPagination = ref(false)
  const initialPageIds = ref<number[]>([])

  // --- Derived state ---
  const allBlocks = computed(() => pages.value.flatMap((p) => p.blocks))
  const currentPage = computed(() => pages.value[selectedPage.value] ?? pages.value[0])

  // --- Load ---
  async function load() {
    loading.value = true
    try {
      const id = String(formId)
      const [form, pagesRes, blocksRes] = await Promise.all([
        apiFetch<tFormOut>(`${API_FORM_URLS.LIST}/${id}`),
        apiFetch<iPaginationNumber<tFormPageOut>>(API_FORM_URLS.PAGES, { params: { form: id } }),
        apiFetch<{ results: tFormBlockOut[] }>(API_FORM_URLS.BLOCKS, { params: { form: id } }),
      ])

      formData.value = form

      const apiPages = (Array.isArray(pagesRes) ? pagesRes : pagesRes.results) as tFormPageOut[]
      const apiBlocks = (
        Array.isArray(blocksRes) ? blocksRes : blocksRes.results
      ) as tFormBlockOut[]

      const toBlockDraft = (b: tFormBlockOut): iFormBlockDraft => ({
        key: b.client_id || String(b.id),
        title: b.title,
        type: b.type as tFormBlockType,
        required: b.required,
        config: b.config ?? {},
        col_span: b.col_span ?? 0,
        col_start: b.col_start ?? 0,
        condition: (b.condition && Object.keys(b.condition).length > 0
          ? b.condition
          : {}) as unknown as iFormBlockCondition,
      })

      const orderedPages = [...apiPages].sort((a, b) => a.order - b.order)
      initialHasPagination.value = orderedPages.length > 0
      initialPageIds.value = orderedPages.map((p) => p.id)

      if (orderedPages.length) {
        const blocksByPage = new Map<number, tFormBlockOut[]>()
        const noPageBlocks: tFormBlockOut[] = []
        for (const b of apiBlocks) {
          if (typeof b.page === 'number') {
            const list = blocksByPage.get(b.page) ?? []
            list.push(b)
            blocksByPage.set(b.page, list)
          } else {
            noPageBlocks.push(b)
          }
        }

        pages.value = orderedPages.map((p, i) => {
          const list = [...(blocksByPage.get(p.id) ?? [])].sort((a, b) => a.order - b.order)
          return {
            key: String(p.id),
            title: p.title ?? '',
            description: p.description ?? '',
            order: i,
            blocks: list.map(toBlockDraft),
          }
        })

        if (noPageBlocks.length && pages.value[0]) {
          pages.value[0].blocks.push(
            ...noPageBlocks.sort((a, b) => a.order - b.order).map(toBlockDraft),
          )
        }
      } else {
        pages.value = [
          {
            key: crypto.randomUUID(),
            title: '',
            description: '',
            order: 0,
            blocks: apiBlocks.sort((a, b) => a.order - b.order).map(toBlockDraft),
          },
        ]
      }

      selectedPage.value = 0
    } finally {
      loading.value = false
    }
  }

  // --- Save ---
  async function save(): Promise<boolean> {
    if (isSaving.value) return false
    isSaving.value = true
    try {
      const id = String(formId)
      const numericId = Number(id)
      const isNumericKey = (key: string) =>
        Number.isFinite(Number(key)) && String(Number(key)) === key

      const hasPageMeta = pages.value.some((p) => Boolean(p.title?.trim() || p.description?.trim()))
      const shouldUsePagination =
        initialHasPagination.value || pages.value.length > 1 || hasPageMeta

      if (shouldUsePagination) {
        // Sync pages
        for (let i = 0; i < pages.value.length; i++) {
          const p = pages.value[i]!
          p.order = i
          if (!isNumericKey(p.key)) {
            const created = await apiFetch<tFormPageOut>(API_FORM_URLS.PAGES, {
              method: 'POST',
              body: { form: numericId, title: p.title, description: p.description, order: i },
            })
            p.key = String(created.id)
          } else {
            await apiFetch(`${API_FORM_URLS.PAGES}/${Number(p.key)}`, {
              method: 'PATCH',
              body: { title: p.title, description: p.description, order: i },
            })
          }
        }

        // Delete removed pages
        if (initialHasPagination.value) {
          const currentIds = new Set(
            pages.value.filter((p) => isNumericKey(p.key)).map((p) => Number(p.key)),
          )
          const removed = initialPageIds.value.filter((pid) => !currentIds.has(pid))
          await Promise.all(
            removed.map((pid) =>
              apiFetch(`${API_FORM_URLS.PAGES}/${pid}`, { method: 'DELETE' }).catch(() => null),
            ),
          )
        }

        // Bulk sync blocks
        const payload = pages.value.flatMap((p) => {
          const pageId = Number(p.key)
          return p.blocks.map((b, bi) => {
            const blockId = Number(b.key)
            const base: Record<string, unknown> = {
              form: numericId,
              page: pageId,
              title: b.title,
              type: b.type,
              required: b.required,
              order: bi,
              config: b.config,
              col_span: b.col_span,
              col_start: b.col_start,
              condition: b.condition,
              client_id: b.key,
            }
            if (Number.isFinite(blockId) && String(blockId) === b.key) base.id = blockId
            return base
          })
        })

        if (payload.length) {
          await apiFetch(`${API_FORM_URLS.BLOCKS}/bulk`, { method: 'POST', body: payload })
        }
      } else {
        const flat = (pages.value[0]?.blocks ?? []).map((b, i) => {
          const blockId = Number(b.key)
          const base: Record<string, unknown> = {
            form: numericId,
            page: null,
            title: b.title,
            type: b.type,
            required: b.required,
            order: i,
            config: b.config,
            col_span: b.col_span,
            col_start: b.col_start,
            condition: b.condition,
            client_id: b.key,
          }
          if (Number.isFinite(blockId) && String(blockId) === b.key) base.id = blockId
          return base
        })
        if (flat.length) {
          await apiFetch(`${API_FORM_URLS.BLOCKS}/bulk`, { method: 'POST', body: flat })
        }
      }

      return true
    } catch {
      hasError.value = true
      setTimeout(() => {
        hasError.value = false
      }, 600)
      return false
    } finally {
      isSaving.value = false
    }
  }

  // --- Page management ---
  function addPage() {
    pages.value.push({
      key: crypto.randomUUID(),
      title: '',
      description: '',
      order: pages.value.length,
      blocks: [],
    })
    selectedPage.value = pages.value.length - 1
  }

  function removePage(index: number) {
    if (pages.value.length <= 1) {
      pages.value[0]!.blocks = []
      return
    }
    const orphans = pages.value[index]?.blocks ?? []
    pages.value.splice(index, 1)
    pages.value.forEach((p, i) => {
      p.order = i
    })
    // Move orphan blocks to previous page
    const target = pages.value[Math.max(0, index - 1)]
    if (target) target.blocks.push(...orphans)
    selectedPage.value = Math.min(selectedPage.value, pages.value.length - 1)
  }

  function movePage(from: number, to: number) {
    const selectedKey = pages.value[selectedPage.value]?.key
    const [item] = pages.value.splice(from, 1)
    pages.value.splice(to, 0, item!)
    pages.value.forEach((p, i) => {
      p.order = i
    })
    if (selectedKey) {
      const idx = pages.value.findIndex((p) => p.key === selectedKey)
      if (idx >= 0) selectedPage.value = idx
    }
  }

  // --- Title, icon, cover (mirrors documentEditing.ts / documentVault.ts) ---
  function onTitleInput(title: string) {
    if (!formData.value) return
    formData.value.title = title
    updateTitleDebounced(title)
  }

  const updateTitleDebounced = useDebounceFn(async (title: string) => {
    if (!formData.value) return
    try {
      await apiFetch(`${API_FORM_URLS.LIST}/${formData.value.id}`, { method: 'PATCH', body: { title } })
    } catch {
      toast.add({ title: 'Erro ao salvar título', color: 'error' })
    }
  }, 900)

  async function updateIcon(icon: string) {
    if (!formData.value) return
    const previous = formData.value.icon
    formData.value.icon = icon
    try {
      await apiFetch(`${API_FORM_URLS.LIST}/${formData.value.id}`, { method: 'PATCH', body: { icon } })
    } catch {
      formData.value.icon = previous
      toast.add({ title: 'Erro ao atualizar ícone', color: 'error' })
    }
  }

  async function updateCover(update: iCoverUpdate) {
    if (!formData.value) return
    const previousCoverImage = formData.value.cover_image
    const previousStyle = formData.value.cover_style
    const previousCredit = formData.value.cover_credit
    try {
      let body: FormData | Record<string, unknown>
      if (update && 'file' in update) {
        body = new FormData()
        body.append('cover_image', update.file)
        body.append('cover_style', '')
      } else if (update && 'style' in update) {
        body = { cover_image: null, cover_style: update.style, cover_credit: update.credit }
      } else {
        body = { cover_image: null, cover_style: '', cover_credit: null }
      }
      const updated = await apiFetch<tFormOut>(`${API_FORM_URLS.LIST}/${formData.value.id}`, {
        method: 'PATCH',
        body,
      })
      formData.value.cover_image = updated.cover_image
      formData.value.cover_style = updated.cover_style
      formData.value.cover_credit = updated.cover_credit
    } catch {
      formData.value.cover_image = previousCoverImage
      formData.value.cover_style = previousStyle
      formData.value.cover_credit = previousCredit
      toast.add({ title: 'Erro ao atualizar capa', color: 'error' })
    }
  }

  async function updateTheme(themeId: number | null) {
    if (!formData.value) return
    const previous = formData.value.theme
    formData.value.theme = themeId
    try {
      const updated = await apiFetch<tFormOut>(`${API_FORM_URLS.LIST}/${formData.value.id}`, {
        method: 'PATCH',
        body: { theme: themeId },
        params: { expand: 'theme' },
      })
      formData.value.theme = updated.theme
    } catch {
      formData.value.theme = previous
      toast.add({ title: 'Erro ao aplicar tema', color: 'error' })
    }
  }

  // --- Autosave with debounce ---
  const lastSavedAt = ref<Date | null>(null)
  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  function scheduleSave() {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(async () => {
      const ok = await save()
      if (ok) lastSavedAt.value = new Date()
    }, 1500)
  }

  watch(
    pages,
    () => {
      if (!loading.value) scheduleSave()
    },
    { deep: true },
  )

  return {
    formData,
    loading,
    isSaving,
    hasError,
    lastSavedAt,
    selectedPage,
    pages,
    allBlocks,
    currentPage,
    load,
    save,
    addPage,
    removePage,
    movePage,
    onTitleInput,
    updateIcon,
    updateCover,
    updateTheme,
  }
}
