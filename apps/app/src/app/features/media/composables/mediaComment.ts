import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia, iMediaComment, iMediaVersion } from '@/app/features/media/types'
import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { useMutation } from '@tanstack/vue-query'

export function useMediaComment(
  mediaData: Ref<iMedia>,
  feedbackTab: Ref<string>,
  currentVersion: ComputedRef<iMediaVersion | undefined>,
) {
  const toast = useToast()
  const commentBody = ref('')

  const activeComments = computed(() =>
    feedbackTab.value === 'version'
      ? (currentVersion.value?.comments ?? [])
      : mediaData.value.comments,
  )

  const { mutateAsync: addCommentMutation, status: addStatus } = useMutation({
    mutationFn: async () => {
      const body: Record<string, unknown> = {
        media: mediaData.value.id,
        content: commentBody.value,
      }

      if (feedbackTab.value === 'version' && currentVersion.value) {
        body.version = currentVersion.value.id
      }

      return apiFetch<iMediaComment>(API_MEDIA_URLS.COMMENTS, { method: 'POST', body })
    },
    onSuccess: (newComment) => {
      commentBody.value = ''
      if (newComment) activeComments.value.push(newComment)
    },
    onError: () => {
      toast.add({ title: 'Erro ao comentar', color: 'error' })
    },
  })

  async function addComment() {
    if (!commentBody.value.trim()) return
    await addCommentMutation()
  }

  return {
    commentBody,
    activeComments,
    addComment,
    isAdding: computed(() => addStatus.value === 'pending'),
  }
}
