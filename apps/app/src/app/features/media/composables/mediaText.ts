import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia, iMediaComment, iMediaVersion } from '@/app/features/media/types'
import { useMutation } from '@tanstack/vue-query'

/** Debounced autosave of a text version's content back to the backend. */
export function useMediaTextAutosave(
  mediaData: Ref<iMedia>,
  currentVersion: ComputedRef<iMediaVersion | undefined>,
) {
  const toast = useToast()
  const saving = ref(false)

  async function persist(content: string) {
    const version = currentVersion.value
    if (!version) return

    saving.value = true
    try {
      await apiFetch(`${API_MEDIA_URLS.VERSIONS}/${version.id}`, {
        method: 'PATCH',
        body: { text_content: content },
      })
    } catch {
      toast.add({ title: 'Erro ao salvar', color: 'error' })
    } finally {
      saving.value = false
    }
  }

  const debouncedPersist = useDebounceFn(persist, 900)

  function onContentChange(content: string) {
    const version = currentVersion.value
    if (!version) return

    const idx = mediaData.value.versions.findIndex((v) => v.id === version.id)
    const existing = mediaData.value.versions[idx]
    if (idx > -1 && existing) mediaData.value.versions[idx] = { ...existing, text_content: content }

    debouncedPersist(content)
  }

  return { saving, onContentChange }
}

/** Comments for a text version — either anchored to a selected quote, or general. */
export function useMediaTextComments(
  mediaData: Ref<iMedia>,
  currentVersion: ComputedRef<iMediaVersion | undefined>,
) {
  const toast = useToast()
  const generalDraft = ref('')

  const { mutateAsync: submitAnchored, isPending: submittingAnchored } = useMutation({
    mutationFn: async (payload: { quote: string; content: string }) => {
      if (!currentVersion.value) return null

      return apiFetch<iMediaComment>(API_MEDIA_URLS.COMMENTS, {
        method: 'POST',
        body: {
          media: mediaData.value.id,
          version: currentVersion.value.id,
          quote: payload.quote,
          content: payload.content,
        },
      })
    },
    onSuccess: (comment) => {
      if (comment) mediaData.value.comments.push(comment)
    },
    onError: () => toast.add({ title: 'Erro ao comentar', color: 'error' }),
  })

  const { mutateAsync: submitGeneral, isPending: submittingGeneral } = useMutation({
    mutationFn: async () => {
      const content = generalDraft.value.trim()
      if (!content) return null

      return apiFetch<iMediaComment>(API_MEDIA_URLS.COMMENTS, {
        method: 'POST',
        body: { media: mediaData.value.id, content },
      })
    },
    onSuccess: (comment) => {
      if (!comment) return
      mediaData.value.comments.push(comment)
      generalDraft.value = ''
    },
    onError: () => toast.add({ title: 'Erro ao comentar', color: 'error' }),
  })

  return {
    submitAnchored,
    submittingAnchored,
    generalDraft,
    submitGeneral,
    submittingGeneral,
  }
}
