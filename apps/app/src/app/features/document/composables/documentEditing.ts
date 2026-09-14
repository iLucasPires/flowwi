import { API_DOCUMENT_URLS, apiFetch } from '@/app/core/clients/api'
import { useDocumentRealtime } from '@/app/features/document/composables/documentRealtime'
import type { iDocument, iDocumentVersion, iDocumentVersionStatus } from '@/app/features/document/types'
/** Continuous-content autosave and version navigation for the active document. */
export function useDocumentEditing(activeDoc: ComputedRef<iDocument | undefined>) {
  const toast = useToast()
  const saving = ref(false)

  // Versions are returned latest-first, so index 0 is the latest. `activeIndex` is which
  // one is currently open — like flipping between script drafts, not a "restore" pointer.
  const activeIndex = ref(0)
  const versions = computed(() => activeDoc.value?.versions ?? [])
  const currentVersion = computed(() => versions.value[activeIndex.value])

  // Read-only for any of three reasons: the version was published (a workflow lock —
  // branch a new revision to keep writing), the user simply doesn't have edit access to
  // this document at all (view-only sharing), or someone else currently holds the
  // realtime edit lock. `can_edit` defaults to false while the document hasn't loaded
  // yet, so nothing looks editable before permissions are actually known.
  const canEdit = computed(() => activeDoc.value?.can_edit ?? false)

  /** True while this document is a draft the user is allowed to edit — the condition
   * under which we should be holding the realtime lock (see below). */
  const structurallyEditable = computed(
    () => currentVersion.value?.status !== 'published' && canEdit.value,
  )

  async function refetchActiveDoc() {
    const doc = activeDoc.value
    if (!doc) return
    try {
      const fresh = await apiFetch<iDocument>(`${API_DOCUMENT_URLS.LIST}/${doc.id}`)
      Object.assign(doc, fresh)
    } catch {
      // Best-effort — a failed refetch just leaves this tab stale until the next signal.
    }
  }

  const documentId = computed(() => activeDoc.value?.id ?? null)
  const { lockedBy, isLockedByOther, acquireLock, releaseLock } = useDocumentRealtime(documentId, {
    onDocumentChanged: refetchActiveDoc,
  })

  // Hold the lock for as long as we're actually in editable mode, and only then —
  // browsing an old/published version, or losing edit access mid-session, releases it.
  watch(
    structurallyEditable,
    (editable) => {
      if (editable) acquireLock()
      else releaseLock()
    },
    { immediate: true },
  )

  const isReadonly = computed(() => !structurallyEditable.value || isLockedByOther.value)

  watch(
    () => activeDoc.value?.id,
    () => {
      activeIndex.value = 0
    },
  )

  function selectVersion(index: number) {
    if (index < 0 || index >= versions.value.length) return
    activeIndex.value = index
  }

  async function persist(versionId: number, content: string) {
    saving.value = true
    try {
      await apiFetch(`${API_DOCUMENT_URLS.VERSIONS}/${versionId}`, {
        method: 'PATCH',
        body: { content },
      })
    } catch {
      toast.add({ title: 'Erro ao salvar', color: 'error' })
    } finally {
      saving.value = false
    }
  }

  const debouncedPersist = useDebounceFn(
    (versionId: number, content: string) => persist(versionId, content),
    900,
  )

  function onContentChange(content: string) {
    const version = currentVersion.value
    if (!version || version.status === 'published' || isLockedByOther.value) return
    version.content = content
    debouncedPersist(version.id, content)
  }

  async function setVersionStatus(status: iDocumentVersionStatus) {
    const version = currentVersion.value
    if (!version || version.status === status || !canEdit.value || isLockedByOther.value) return
    const prev = version.status
    version.status = status
    try {
      await apiFetch(`${API_DOCUMENT_URLS.VERSIONS}/${version.id}`, {
        method: 'PATCH',
        body: { status },
      })
    } catch {
      version.status = prev
      toast.add({
        title: status === 'published' ? 'Erro ao publicar' : 'Erro ao voltar para rascunho',
        color: 'error',
      })
    }
  }

  /** Branches a new editable draft off whichever version is currently open, and switches to it. */
  async function newRevision() {
    const version = currentVersion.value
    const doc = activeDoc.value
    if (!version || !doc || !canEdit.value || isLockedByOther.value) return
    const newVersion = await apiFetch<iDocumentVersion>(
      API_DOCUMENT_URLS.NEW_REVISION(version.id),
      { method: 'POST' },
    )
    doc.versions.unshift(newVersion)
    activeIndex.value = 0
  }

  function onTitleInput(title: string) {
    const doc = activeDoc.value
    if (!doc || isLockedByOther.value) return
    doc.title = title
    updateTitleDebounced(doc.id, title)
  }

  const updateTitleDebounced = useDebounceFn(async (id: number, title: string) => {
    try {
      await apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: 'PATCH', body: { title } })
    } catch {
      toast.add({ title: 'Erro ao salvar título', color: 'error' })
    }
  }, 900)

  return {
    saving,
    versions,
    activeIndex,
    selectVersion,
    currentVersion,
    isReadonly,
    lockedBy,
    isLockedByOther,
    onContentChange,
    setVersionStatus,
    newRevision,
    onTitleInput,
  }
}
