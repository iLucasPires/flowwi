import { API_DOCUMENT_URLS, apiFetch } from '@/app/core/clients/api'
import type { iDocument, iDocumentComment, iDocumentVersion } from '@/app/features/document/types'
import { useMutation } from '@tanstack/vue-query'

/** Comments for a document's latest version — either anchored to a selected quote, or general. */
export function useDocumentComments(
  activeDoc: ComputedRef<iDocument | undefined>,
  currentVersion: ComputedRef<iDocumentVersion | undefined>,
) {
  const toast = useToast()
  const generalDraft = ref('')

  // The version being drafted hasn't settled yet — comments only open up once it's published.
  const canComment = computed(() => currentVersion.value?.status === 'published')

  const { mutateAsync: submitAnchored, isPending: submittingAnchored } = useMutation({
    mutationFn: async (payload: { quote: string; content: string }) => {
      const doc = activeDoc.value
      const version = currentVersion.value
      if (!doc || !version || !canComment.value) return null

      return apiFetch<iDocumentComment>(API_DOCUMENT_URLS.COMMENTS, {
        method: 'POST',
        body: {
          document: doc.id,
          version: version.id,
          quote: payload.quote,
          content: payload.content,
        },
      })
    },
    onSuccess: (comment) => {
      if (!comment || !activeDoc.value) return
      activeDoc.value.comments.push(comment)
    },
    onError: () => toast.add({ title: 'Erro ao comentar', color: 'error' }),
  })

  const { mutateAsync: submitGeneral, isPending: submittingGeneral } = useMutation({
    mutationFn: async () => {
      const content = generalDraft.value.trim()
      const doc = activeDoc.value
      const version = currentVersion.value
      if (!content || !doc || !version || !canComment.value) return null

      return apiFetch<iDocumentComment>(API_DOCUMENT_URLS.COMMENTS, {
        method: 'POST',
        body: { document: doc.id, version: version.id, content },
      })
    },
    onSuccess: (comment) => {
      if (!comment || !activeDoc.value) return
      activeDoc.value.comments.push(comment)
      generalDraft.value = ''
    },
    onError: () => toast.add({ title: 'Erro ao comentar', color: 'error' }),
  })

  return {
    canComment,
    submitAnchored,
    submittingAnchored,
    generalDraft,
    submitGeneral,
    submittingGeneral,
  }
}
