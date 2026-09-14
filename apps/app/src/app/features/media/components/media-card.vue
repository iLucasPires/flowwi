<script setup lang="ts">
import type { iMedia } from '@/app/features/media/types'
import { formatTimeAgo } from '@vueuse/core'

/**
 * Component to display a summary of an Media piece in a card format.
 */
defineOptions({ name: 'MediaCard' })

const props = defineProps<{
  /** The media data to display */
  media: iMedia
}>()

const emit = defineEmits<{
  /** Triggered when the card is clicked */
  click: []
  /** Triggered when the delete action is selected */
  delete: []
  /** Triggered when the download action is selected */
  download: []
  /** Triggered when the edit action is selected */
  edit: []
  /** Triggered when the share action is selected */
  share: []
}>()

/**
 * The most recent version of the media.
 */
const latestVersion = computed(() => props.media.versions?.[0])

/**
 * Total number of versions for this media piece.
 */
const versionCount = computed(() => props.media.versions?.length ?? 0)

const PREVIEW_META: Record<number, { icon: string; label: string }> = {
  1: { icon: 'i-lucide-image', label: 'Imagem' },
  2: { icon: 'i-lucide-film', label: 'Vídeo' },
  3: { icon: 'i-lucide-file', label: 'Arquivo' },
  4: { icon: 'i-lucide-link', label: 'Link' },
  5: { icon: 'i-lucide-file-text', label: 'Texto' },
  6: { icon: 'i-lucide-file-type', label: 'Documento' },
}

/**
 * Icon + label shown on the card's preview area when there's no real image to render.
 */
const previewMeta = computed(
  () =>
    PREVIEW_META[latestVersion.value?.type ?? -1] ?? {
      icon: 'i-lucide-file-question',
      label: 'Sem versão',
    },
)

const showImagePreview = computed(
  () => latestVersion.value?.type === 1 && !!latestVersion.value?.file,
)

/**
 * Menu actions for the dropdown.
 */
const actions = computed(() => [
  [
    {
      label: 'Editar',
      icon: 'i-lucide-pencil',
      onSelect: () => emit('edit'),
    },
    {
      label: 'Compartilhar',
      icon: 'i-lucide-share-2',
      onSelect: () => emit('share'),
    },
  ],
  [
    {
      label: 'Excluir',
      icon: 'i-lucide-trash-2',
      color: 'error' as const,
      onSelect: () => emit('delete'),
    },
  ],
])
</script>

<template>
  <UCard
    variant="subtle"
    class="cursor-pointer"
    :ui="{
      body: 'flex flex-col gap-4',
      header: 'flex justify-between',
      footer: 'flex justify-between',
    }"
    @click="emit('click')"
  >
    <div class="h-44 bg-elevated/60 rounded-md flex items-center justify-center overflow-hidden">
      <img
        v-if="showImagePreview"
        :src="latestVersion?.file"
        :alt="media.title"
        class="size-full object-cover object-center"
      />
      <div v-else class="flex flex-col items-center gap-1.5 text-dimmed">
        <UIcon :name="previewMeta.icon" class="size-6" />
        <span class="text-[11px] font-mono">{{ previewMeta.label }}</span>
      </div>
    </div>

    <div class="flex justify-between w-full">
      <div>
        <CTextBlock weight="medium" size="sm" :text="media.title" />
        <CTextBlock weight="normal" size="xs" class="truncate" :text="media.notes.slice(0, 90)" />
      </div>

      <UDropdownMenu :items="actions" size="sm">
        <UButton
          icon="i-lucide-ellipsis-vertical"
          variant="ghost"
          color="neutral"
          size="sm"
          @click.stop
        />
      </UDropdownMenu>
    </div>

    <template #footer>
      <div class="flex gap-2">
        <UBadge
          :label="`versão: ${versionCount}`"
          icon="i-lucide-history"
          variant="subtle"
          color="neutral"
          size="sm"
        />
        <UBadge
          :label="`tarefa: ${media.task ?? 'nenhum'}`"
          icon="i-lucide-kanban"
          variant="subtle"
          color="neutral"
          size="sm"
        />
      </div>

      <div class="flex justify-between">
        <CTextBlock weight="normal" size="xs" :text="formatTimeAgo(new Date(media.created_at))" />
      </div>
    </template>
  </UCard>
</template>
