import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia, iMediaVersion } from '@/app/features/media/types'
import { useMutation } from '@tanstack/vue-query'

export function useMediaVersion(
  mediaData: Ref<iMedia>,
  versions: ComputedRef<iMediaVersion[]>,
  activeIndex: Ref<number>,
  resetCarousel: () => void,
) {
  const toast = useToast()
  const newFile = ref<File | null>(null)

  const { mutateAsync: uploadVersion, status: uploadStatus } = useMutation({
    mutationFn: async (file: File) => {
      const body = new FormData()
      body.append('media', String(mediaData.value.id))
      body.append('file', file)
      return apiFetch<iMediaVersion>(API_MEDIA_URLS.VERSIONS, { method: 'POST', body })
    },
    onSuccess: (newVersion) => {
      newFile.value = null
      if (newVersion) {
        mediaData.value.versions.unshift(newVersion)
        activeIndex.value = 0
      }
      resetCarousel()
      toast.add({ title: 'Versão enviada', color: 'success' })
    },
    onError: () => {
      toast.add({ title: 'Erro ao enviar', color: 'error' })
    },
  })

  const uploading = computed(() => uploadStatus.value === 'pending')

  watch(newFile, async (file) => {
    if (!file) return
    await uploadVersion(file)
  })

  const { mutateAsync: deleteVersionMutation } = useMutation({
    mutationFn: async (v: iMediaVersion) => {
      await apiFetch(`${API_MEDIA_URLS.VERSIONS}/${v.id}`, { method: 'DELETE' })
      return v.id
    },
    onSuccess: (deletedId) => {
      const idx = mediaData.value.versions.findIndex((ver) => ver.id === deletedId)
      if (idx > -1) mediaData.value.versions.splice(idx, 1)
      if (activeIndex.value >= mediaData.value.versions.length) {
        activeIndex.value = Math.max(0, mediaData.value.versions.length - 1)
      }
      resetCarousel()
      toast.add({ title: 'Versão removida', color: 'success' })
    },
    onError: () => {
      toast.add({ title: 'Erro ao remover', color: 'error' })
    },
  })

  async function deleteVersion(v: iMediaVersion) {
    await deleteVersionMutation(v)
  }

  return { uploading, newFile, deleteVersion }
}
