import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia, iMediaFeedback, iMediaVersion } from '@/app/features/media/types'
import { useUser } from '@/app/features/user/composables/user'
import { useMutation } from '@tanstack/vue-query'

export function useMediaFeedback(
  mediaData: Ref<iMedia>,
  feedbackTab: Ref<string>,
  currentVersion: ComputedRef<iMediaVersion | undefined>,
) {
  const toast = useToast()
  const { user } = useUser()

  const activeFeedbacks = computed(() =>
    feedbackTab.value === 'version'
      ? (currentVersion.value?.feedbacks ?? [])
      : mediaData.value.feedbacks,
  )

  const myFeedback = computed(() =>
    activeFeedbacks.value.find((f) => f.given_by === user.value?.id),
  )

  const likeCount = computed(() => activeFeedbacks.value.filter((f) => f.decision === 1).length)
  const dislikeCount = computed(() => activeFeedbacks.value.filter((f) => f.decision === 2).length)

  const { mutateAsync: toggleFeedbackMutation, status: toggleStatus } = useMutation({
    mutationFn: async (decision: 1 | 2) => {
      if (myFeedback.value?.decision === decision) {
        await apiFetch(`${API_MEDIA_URLS.FEEDBACKS}/${myFeedback.value.id}`, { method: 'DELETE' })
        return { action: 'deleted', id: myFeedback.value.id } as const
      }

      const body: Record<string, unknown> = {
        media: mediaData.value.id,
        decision,
      }

      if (feedbackTab.value === 'version' && currentVersion.value) {
        body.version = currentVersion.value.id
      }

      const data = await apiFetch<iMediaFeedback>(API_MEDIA_URLS.FEEDBACKS, {
        method: 'POST',
        body,
      })
      return { action: 'created', data } as const
    },
    onSuccess: (res) => {
      if (!res) return
      if (res.action === 'deleted') {
        const idx = activeFeedbacks.value.findIndex((f) => f.id === res.id)
        if (idx > -1) activeFeedbacks.value.splice(idx, 1)
      } else if (res.action === 'created' && res.data) {
        const existingIdx = activeFeedbacks.value.findIndex((f) => f.given_by === user.value?.id)
        if (existingIdx > -1) activeFeedbacks.value[existingIdx] = res.data
        else activeFeedbacks.value.push(res.data)
      }
    },
    onError: () => {
      toast.add({ title: 'Erro no feedback', color: 'error' })
    },
  })

  async function toggleFeedback(decision: 1 | 2) {
    await toggleFeedbackMutation(decision)
  }

  return {
    activeFeedbacks,
    myFeedback,
    likeCount,
    dislikeCount,
    toggleFeedback,
    isToggling: computed(() => toggleStatus.value === 'pending'),
  }
}
