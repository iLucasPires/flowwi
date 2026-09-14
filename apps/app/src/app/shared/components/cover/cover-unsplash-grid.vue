<script setup lang="ts">
import { useUnsplash } from '@/app/shared/composables/unsplash/unsplash'
import type { iUnsplashPhoto } from '@/app/shared/types/unsplash'
const emit = defineEmits<{
  select: [photo: iUnsplashPhoto]
}>()

const {
  searchTerm,
  photos,
  isLoading,
  isFetching,
  isError,
  hasNextPage,
  hasPreviousPage,
  nextPage,
  previousPage,
  trackDownload,
} = useUnsplash()

function selectPhoto(photo: iUnsplashPhoto) {
  // Unsplash asks for a download ping whenever a photo is actually picked.
  trackDownload(photo)
  emit('select', photo)
}

defineOptions({ name: 'CoverUnsplashGrid' })
</script>

<template>
  <div class="pt-2 flex flex-col gap-2">
    <UInput
      v-model="searchTerm"
      placeholder="Buscar no Unsplash..."
      icon="i-lucide-search"
      size="xs"
      variant="subtle"
      :loading="isFetching"
      class="w-full"
    />

    <UAlert
      v-if="isError"
      icon="i-lucide-cloud-off"
      color="neutral"
      variant="subtle"
      title="Unsplash indisponível"
      description="Tente novamente em instantes."
      :ui="{ title: 'text-xs', description: 'text-xs' }"
    />

    <div v-else-if="isLoading" class="grid grid-cols-3 gap-2">
      <USkeleton v-for="placeholder in 9" :key="placeholder" class="h-16 rounded-lg" />
    </div>

    <UEmpty
      v-else-if="!photos.length"
      icon="i-lucide-image-off"
      title="Nenhuma foto encontrada"
      :ui="{ title: 'text-xs' }"
    />

    <div v-else class="grid grid-cols-3 gap-2 max-h-64 overflow-y-auto pr-1">
      <UButton
        v-for="photo in photos"
        :key="photo.id"
        variant="ghost"
        color="neutral"
        class="relative h-16 p-0 rounded-lg overflow-hidden ring-1 ring-default hover:ring-2 hover:ring-primary transition-all group"
        :style="{ backgroundColor: photo.color ?? undefined }"
        :title="photo.description || photo.credit.author_name"
        @click="selectPhoto(photo)"
      >
        <img
          :src="photo.thumb_url"
          :alt="photo.description"
          loading="lazy"
          class="size-full object-cover"
        />
        <span
          class="absolute inset-x-0 bottom-0 px-1.5 py-0.5 text-[10px] leading-tight text-white truncate bg-black/50 opacity-0 transition-opacity group-hover:opacity-100"
        >
          {{ photo.credit.author_name }}
        </span>
      </UButton>
    </div>

    <div class="flex items-center justify-between gap-2">
      <UButton
        icon="i-lucide-chevron-left"
        size="xs"
        variant="ghost"
        color="neutral"
        :disabled="!hasPreviousPage"
        @click="previousPage"
      />

      <span class="text-[10px] text-dimmed">Fotos via Unsplash</span>

      <UButton
        icon="i-lucide-chevron-right"
        size="xs"
        variant="ghost"
        color="neutral"
        :disabled="!hasNextPage"
        @click="nextPage"
      />
    </div>
  </div>
</template>
