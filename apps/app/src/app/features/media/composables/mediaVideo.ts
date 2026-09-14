import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia, iMediaComment, iMediaVersion } from '@/app/features/media/types'
import { useMutation } from '@tanstack/vue-query'

/** Formats seconds as `m:ss`. */
export function formatMediaTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

/** Draft-comment state for pinning a comment to a specific video timestamp, plus the general composer. */
export function useMediaVideoComments(
  mediaData: Ref<iMedia>,
  currentVersion: ComputedRef<iMediaVersion | undefined>,
) {
  const toast = useToast()

  const draftTime = ref<number | null>(null)
  const draftText = ref('')
  const generalDraft = ref('')

  function selectTime(seconds: number) {
    draftTime.value = Math.round(seconds)
    draftText.value = ''
  }

  function cancelDraft() {
    draftTime.value = null
    draftText.value = ''
  }

  const { mutateAsync: submitDraft, isPending: submittingDraft } = useMutation({
    mutationFn: async () => {
      const time = draftTime.value
      const content = draftText.value.trim()
      if (time == null || !content || !currentVersion.value) return null

      return apiFetch<iMediaComment>(API_MEDIA_URLS.COMMENTS, {
        method: 'POST',
        body: {
          media: mediaData.value.id,
          version: currentVersion.value.id,
          block_index: time,
          content,
        },
      })
    },
    onSuccess: (comment) => {
      if (!comment) return
      mediaData.value.comments.push(comment)
      draftTime.value = null
      draftText.value = ''
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
    draftTime,
    draftText,
    selectTime,
    cancelDraft,
    submitDraft,
    submittingDraft,
    generalDraft,
    submitGeneral,
    submittingGeneral,
  }
}
