<script setup lang="ts">
import type { iMediaVersion } from '@/app/features/media/types'
defineProps<{
  versions: iMediaVersion[]
  carouselKey: number
  activeIndex: number
  uploading: boolean
}>()

const emit = defineEmits<{
  prev: []
  next: []
  select: [index: number]
  selectThumb: [index: number]
  delete: [version: iMediaVersion]
  upload: [file: File]
}>()

const carousel = useTemplateRef('carousel')

function scrollTo(index: number) {
  carousel.value?.emblaApi?.scrollTo(index)
}

defineExpose({ scrollTo })

const fileInput = useTemplateRef<HTMLInputElement>('fileInput')

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) emit('upload', file)
}
</script>

<template>
  <UCard
    :ui="{
      body: 'p-2! gap-4 flex flex-col items-center justify-center relative',
    }"
  >
    <!-- Empty state -->
    <div
      v-if="!versions.length"
      class="flex flex-col items-center justify-center h-[50vh] w-full gap-3"
    >
      <UEmpty
        icon="i-lucide-image-off"
        title="Nenhuma versão"
        description="Envie a primeira imagem."
        size="sm"
        variant="subtle"
      />
      <UButton
        icon="i-lucide-upload"
        label="Upload"
        :loading="uploading"
        color="neutral"
        variant="subtle"
        size="sm"
        @click="fileInput?.click()"
      />
    </div>

    <!-- Carousel -->
    <UCarousel
      v-else
      :key="carouselKey"
      ref="carousel"
      v-slot="{ item }"
      arrows
      :items="versions"
      :ui="{
        prev: 'start-2 sm:start-2 bg-[var(--ui-bg)]/80 shadow',
        next: 'end-2 sm:end-2 bg-[var(--ui-bg)]/80 shadow',
      }"
      @select="(i: number) => emit('select', i)"
    >
      <div class="relative flex items-center justify-center h-[50vh] w-full">
        <img v-if="item.file" :src="item.file" class="max-h-full max-w-full object-contain" />
        <UEmpty v-else icon="i-lucide-image-off" title="Sem arquivo" size="sm" variant="subtle" />
      </div>
    </UCarousel>

    <!-- Badge de versão + botão excluir -->
    <div
      v-if="versions[activeIndex]"
      class="absolute top-3 right-3 tabular-nums flex items-center gap-2"
    >
      <UBadge
        :label="`v${versions[activeIndex]?.number || 0}`"
        variant="subtle"
        color="neutral"
        icon="i-lucide-git-branch"
        size="sm"
      />
      <UButton
        icon="i-lucide-upload"
        size="xs"
        color="neutral"
        variant="subtle"
        title="Upload"
        :loading="uploading"
        @click.stop="fileInput?.click()"
      />
      <UButton
        icon="i-lucide-trash-2"
        size="xs"
        color="error"
        variant="subtle"
        label="Excluir"
        @click.stop="emit('delete', versions[activeIndex]!)"
      />
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/*,.pdf,.psd,.ai,.svg"
      class="hidden"
      @change="onFileChange"
    />

    <!-- Thumbnails -->
    <div class="flex gap-2">
      <div
        v-for="(item, index) in versions"
        :key="item.id"
        :class="{ 'opacity-100': activeIndex === index }"
        class="size-11 overflow-hidden opacity-25 hover:opacity-100 transition-opacity cursor-pointer"
        @click="emit('selectThumb', index)"
      >
        <img
          :src="item.file"
          width="44"
          height="44"
          class="rounded-lg size-full object-cover"
          loading="lazy"
        />
      </div>
    </div>
  </UCard>
</template>
