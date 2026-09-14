import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia } from '@/app/features/media/types'
import { ref, computed, toRaw } from 'vue'
import { useQuery } from '@tanstack/vue-query'

export function useMediaDetail(initialMedia: iMedia) {
  // `initialMedia` may come from a vue-query cache, whose nested arrays/objects
  // are deeply readonly — a shallow copy would still share those readonly
  // references, silently dropping local mutations (comments/feedback pushes).
  const mediaData = ref<iMedia>(structuredClone(toRaw(initialMedia)))

  const versions = computed(() => mediaData.value.versions)

  const activeIndex = ref(0)
  const carouselKey = ref(0)
  const feedbackTab = ref('version')

  const currentVersion = computed(() => versions.value[activeIndex.value])

  const { refetch, status } = useQuery({
    queryKey: ['media', initialMedia.id],
    queryFn: () => apiFetch<iMedia>(`${API_MEDIA_URLS.LIST}/${initialMedia.id}`),
  })

  async function refetchMedia() {
    try {
      const state = await refetch()
      if (state.data) mediaData.value = structuredClone(toRaw(state.data))
    } catch (err) {
      console.error('Failed to refetch media details:', err)
    }
  }

  function selectIndex(index: number) {
    activeIndex.value = index
  }

  function resetCarousel() {
    carouselKey.value++
    activeIndex.value = 0
  }

  return {
    mediaData,
    versions,
    activeIndex,
    carouselKey,
    feedbackTab,
    currentVersion,
    isLoading: computed(() => status.value === 'pending'),
    refetchMedia,
    selectIndex,
    resetCarousel,
  }
}
