<script setup lang="ts">
import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import { MEDIA_VERSION_TYPE_TEXT, MEDIA_VERSION_TYPE_VIDEO } from '@/app/features/media/types'
import type { iMedia } from '@/app/features/media/types'
import { useQuery } from '@tanstack/vue-query'

defineOptions({ name: 'MediaDetailPage' })

const route = useRoute()
const router = useRouter()

const mediaId = computed<string | null>(() => {
  const raw = route.params.id
  const value = Array.isArray(raw) ? raw[0] : raw
  return value || null
})

const { data: media, isLoading } = useQuery({
  queryKey: computed(() => ['media', mediaId.value] as const),
  queryFn: () => apiFetch<iMedia>(API_MEDIA_URLS.DETAIL(mediaId.value!)),
  enabled: () => mediaId.value != null,
})

const versionType = computed(() => media.value?.versions?.[0]?.type)
const isVideoMedia = computed(() => versionType.value === MEDIA_VERSION_TYPE_VIDEO)
const isTextMedia = computed(() => versionType.value === MEDIA_VERSION_TYPE_TEXT)

watch(
  media,
  (m) => {
    if (m && !isVideoMedia.value && !isTextMedia.value) router.replace('/dashboard/media')
  },
  { immediate: true },
)
</script>

<template>
  <div class="size-full flex items-center justify-center" v-if="isLoading">
    <UIcon name="i-lucide-loader-2" class="size-6 animate-spin text-dimmed" />
  </div>

  <CMediaVideoDetailView v-else-if="media && isVideoMedia" :media="media" />
  <CMediaTextDetailView v-else-if="media && isTextMedia" :media="media" />
</template>
