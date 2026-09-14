<script setup lang="ts">
import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import { useMediaComment } from '@/app/features/media/composables/mediaComment'
import { useMediaDetail } from '@/app/features/media/composables/mediaDetail'
import { useMediaFeedback } from '@/app/features/media/composables/mediaFeedback'
import { useMediaVersion } from '@/app/features/media/composables/mediaVersion'
import type { iMedia } from '@/app/features/media/types'
import { ref, useTemplateRef } from 'vue'

/**
 * Detailed view of an media piece, showing version history, comments, and feedback.
 */
defineOptions({ name: 'MediaDetailModal' })

const props = defineProps<{
  /** The media data to display */
  media: iMedia
}>()

defineEmits<{
  /** Triggered when the modal is closed */
  close: [result?: { changed?: true }]
}>()

const carousel = useTemplateRef<InstanceType<typeof CMediaDetailCarousel>>('carousel')

// Detail composable for general media state
const {
  mediaData,
  versions,
  activeIndex,
  carouselKey,
  feedbackTab,
  currentVersion,
  selectIndex,
  resetCarousel,
} = useMediaDetail(props.media)

// Feedback logic (likes/dislikes)
const { likeCount, dislikeCount, toggleFeedback } = useMediaFeedback(
  mediaData,
  feedbackTab,
  currentVersion,
)

// Commenting logic
const { commentBody, activeComments, addComment } = useMediaComment(
  mediaData,
  feedbackTab,
  currentVersion,
)

// Version management logic
const { uploading, newFile, deleteVersion } = useMediaVersion(
  mediaData,
  versions,
  activeIndex,
  resetCarousel,
)

/**
 * Selects a specific version by index and scrolls the carousel.
 */
function selectThumb(index: number) {
  selectIndex(index)
  carousel.value?.scrollTo(index)
}

const tabItems = [
  { label: 'Versão', value: 'version', icon: 'i-lucide-layers' },
  { label: 'Geral', value: 'media', icon: 'i-lucide-image' },
]

/**
 * AI-generated task logic from comments.
 */
const overlay = useOverlay()
const selectableMode = ref(false)
const selectedComments = ref<number[]>([])
const generating = ref(false)

/**
 * Toggles the selection mode for generating tasks.
 */
function toggleSelectable() {
  selectableMode.value = !selectableMode.value
  if (!selectableMode.value) selectedComments.value = []
}

/**
 * Toggles a comment in the selection list.
 */
function toggleComment(id: number) {
  const idx = selectedComments.value.indexOf(id)
  if (idx === -1) selectedComments.value.push(id)
  else selectedComments.value.splice(idx, 1)
}

/**
 * Triggers AI task generation based on selected comments, then opens the
 * task creation dialog pre-filled with the suggestion for review.
 */
async function generateTask() {
  if (!selectedComments.value.length) return
  const toast = useToast()
  generating.value = true
  let suggestion: { title: string; description: string }
  try {
    suggestion = await apiFetch<{ title: string; description: string }>(
      `${API_MEDIA_URLS.LIST}/${props.media.id}/generate-task`,
      {
        method: 'POST',
        body: {
          comment_ids: selectedComments.value,
        },
      },
    )
  } catch (err) {
    toast.add({
      title: 'Erro ao gerar tarefa',
      description: 'Não foi possível gerar a tarefa via IA no momento.',
      color: 'error',
    })
    console.error('AI Task Generation failed:', err)
    generating.value = false
    return
  }
  generating.value = false

  const component = resolveComponent('CTaskCreateDialog')
  if (typeof component !== 'object') return

  const modal = overlay.create(component, {
    props: {
      initialTitle: suggestion.title,
      initialDescription: suggestion.description,
    },
  })

  const result = await modal.open()
  if (result) {
    toggleSelectable()
    toast.add({ title: 'Tarefa criada a partir do feedback', color: 'success' })
  }
}
</script>

<template>
  <UModal
    title="Detalhes da Media"
    :open="true"
    :dismissible="false"
    :ui="{
      content: 'sm:max-w-7xl top-3/7 max-h-160!',
      body: 'flex gap-6',
      footer: 'items-start gap-2 flex-col',
    }"
  >
    <template #body>
      <!-- Coluna esquerda: Carousel + Thumbnails -->
      <div class="flex-1 min-w-0 min-h-0">
        <CMediaDetailCarousel
          ref="carousel"
          :versions="versions"
          :carousel-key="carouselKey"
          :active-index="activeIndex"
          :uploading="uploading"
          @prev="activeIndex--"
          @next="activeIndex++"
          @select="selectIndex"
          @select-thumb="selectThumb"
          @delete="deleteVersion"
          @upload="(f) => (newFile = f)"
        />
      </div>

      <!-- Coluna direita: Feedback + Comments -->
      <div class="flex flex-col w-80 shrink-0 min-h-0 gap-4">
        <div class="flex items-center justify-between">
          <UTabs class="gap-0" v-model="feedbackTab" :items="tabItems" size="xs" />
          <div class="flex items-center gap-1">
            <UButton
              v-if="activeComments.length"
              icon="i-lucide-sparkles"
              :variant="selectableMode ? 'subtle' : 'ghost'"
              :color="selectableMode ? 'primary' : 'neutral'"
              size="xs"
              @click="toggleSelectable"
            />
            <UBadge class="items-center" size="xs" variant="subtle" color="neutral">
              <UButton
                icon="i-lucide-chevron-up"
                size="xs"
                color="neutral"
                variant="ghost"
                @click="toggleFeedback(1)"
              />
              <span
                class="text-[11px] font-medium tabular-nums min-w-4.5 text-center"
                v-text="likeCount - dislikeCount"
              />
              <UButton
                icon="i-lucide-chevron-down"
                size="xs"
                color="neutral"
                variant="ghost"
                @click="toggleFeedback(2)"
              />
            </UBadge>
          </div>
        </div>

        <div class="flex flex-col flex-1 min-h-0">
          <div v-if="activeComments.length" class="flex flex-col flex-1 overflow-hidden">
            <div v-if="selectableMode" class="flex items-center justify-between mb-2">
              <span class="text-[11px] font-medium text-dimmed pl-1"
                >{{ selectedComments.length }} selecionados</span
              >
              <UButton
                label="Gerar Tarefa"
                icon="i-lucide-sparkles"
                size="xs"
                :loading="generating"
                :disabled="!selectedComments.length"
                @click="generateTask"
              />
            </div>
            <div class="flex flex-col gap-1.5 flex-1 overflow-y-auto pr-1">
              <CMediaVersionCommentCard
                v-for="c in activeComments"
                :key="c.id"
                :comment="c"
                :selectable="selectableMode"
                :selected="selectedComments.includes(c.id)"
                @toggle="toggleComment"
              />
            </div>
          </div>

          <UEmpty
            v-else
            class="flex-1"
            title="Nenhum comentário"
            icon="i-lucide-message-square"
            size="xs"
            variant="naked"
            description="Seja o primeiro a comentar."
          />

          <div class="flex items-center gap-2 mt-3">
            <UTextarea
              v-model="commentBody"
              :rows="1"
              :maxrows="5"
              :ui="{ root: 'w-full' }"
              placeholder="Escreva um comentário..."
              variant="subtle"
              autoresize
              size="sm"
              class="flex-1"
              @keydown.meta.enter="addComment"
              @keydown.ctrl.enter="addComment"
            />
            <UButton
              icon="i-lucide-send"
              label="Enviar"
              size="sm"
              :disabled="!commentBody.trim()"
              @click="addComment"
            />
          </div>
        </div>
      </div>
    </template>
  </UModal>
</template>
