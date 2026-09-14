<script setup lang="ts">
import { useMediaDetail } from '@/app/features/media/composables/mediaDetail'
import { useMediaFeedback } from '@/app/features/media/composables/mediaFeedback'
import { formatMediaTime, useMediaVideoComments } from '@/app/features/media/composables/mediaVideo'
import type { iMedia } from '@/app/features/media/types'
const props = defineProps<{ media: iMedia }>()

defineOptions({ name: 'MediaVideoDetailView' })

const router = useRouter()

const PIN_COLORS = ['bg-primary', 'bg-secondary', 'bg-warning', 'bg-error', 'bg-success']

const { mediaData, versions, activeIndex, currentVersion, selectIndex } = useMediaDetail(
  props.media,
)

const feedbackTab = ref('media')
const { likeCount, dislikeCount, toggleFeedback, myFeedback } = useMediaFeedback(
  mediaData,
  feedbackTab,
  currentVersion,
)

const { draftTime, draftText, selectTime, cancelDraft, submitDraft, generalDraft, submitGeneral } =
  useMediaVideoComments(mediaData, currentVersion)

const videoEl = useTemplateRef<HTMLVideoElement>('videoEl')
const duration = ref(0)
const played = ref(0)

watch(currentVersion, () => {
  duration.value = 0
  played.value = 0
})

function onLoadedMetadata() {
  duration.value = videoEl.value?.duration ?? 0
}

function onTimeUpdate() {
  played.value = videoEl.value?.currentTime ?? 0
}

const playedPct = computed(() => (duration.value ? (played.value / duration.value) * 100 : 0))
const durationLabel = computed(() => formatMediaTime(duration.value))
const draftTimeLabel = computed(() =>
  draftTime.value != null ? formatMediaTime(draftTime.value) : '',
)

const pinsAtVersion = computed(() => {
  if (!currentVersion.value) return []
  return mediaData.value.comments
    .filter((c) => c.version === currentVersion.value!.id && c.block_index != null)
    .sort((a, b) => (a.block_index ?? 0) - (b.block_index ?? 0))
    .map((c, i) => ({
      ...c,
      color: PIN_COLORS[i % PIN_COLORS.length],
      pct: duration.value ? ((c.block_index ?? 0) / duration.value) * 100 : 0,
      label: formatMediaTime(c.block_index ?? 0),
    }))
})

const generalComments = computed(() =>
  mediaData.value.comments.filter((c) => c.block_index == null),
)

const taskModalComments = computed(() => [
  ...pinsAtVersion.value.map((c) => ({ ...c, kindTag: c.label })),
  ...generalComments.value.map((c) => ({ ...c, kindTag: 'Geral' })),
])

const draftPct = computed(() =>
  draftTime.value != null && duration.value ? (draftTime.value / duration.value) * 100 : null,
)

const taskModalOpen = ref(false)

function onScrubberClick(e: MouseEvent) {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const pct = Math.min(99, Math.max(1, ((e.clientX - rect.left) / rect.width) * 100))
  if (!duration.value) return
  selectTime((pct / 100) * duration.value)
}

function backToList() {
  router.push('/dashboard/media')
}
</script>

<template>
  <div class="size-full flex overflow-hidden bg-elevated/30 p-1.5 gap-1.5">
    <UCard
      :ui="{
        root: 'flex-1 flex flex-col min-w-0',
        body: 'flex-1 flex flex-col min-h-0 p-0 sm:p-0',
      }"
    >
      <!-- Top bar -->
      <div class="flex items-center justify-between px-5 py-3.5 shrink-0">
        <div class="flex items-center gap-2.5 min-w-0">
          <UButton
            icon="i-lucide-arrow-left"
            variant="ghost"
            color="neutral"
            size="xs"
            @click="backToList"
          />
          <span class="text-xs text-dimmed">Media /</span>
          <span class="text-xs font-medium text-highlighted truncate">{{ mediaData.title }}</span>
          <UBadge icon="i-lucide-film" size="sm" variant="subtle" color="neutral">Vídeo</UBadge>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <UButton
            :label="String(likeCount)"
            icon="i-lucide-thumbs-up"
            size="xs"
            variant="subtle"
            :color="myFeedback?.decision === 1 ? 'primary' : 'neutral'"
            @click="toggleFeedback(1)"
          />
          <UButton
            :label="String(dislikeCount)"
            icon="i-lucide-thumbs-down"
            size="xs"
            variant="subtle"
            :color="myFeedback?.decision === 2 ? 'error' : 'neutral'"
            @click="toggleFeedback(2)"
          />
        </div>
      </div>

      <div class="flex-1 flex overflow-hidden min-h-0">
        <!-- Left: player -->
        <div class="flex-1 flex flex-col gap-3.5 p-5 min-w-0">
          <div class="flex items-center justify-between shrink-0">
            <span class="text-sm font-medium text-highlighted">{{
              currentVersion?.number ? `v${currentVersion.number}` : ''
            }}</span>
            <div class="flex items-center gap-1.5">
              <UButton
                icon="i-lucide-chevron-left"
                size="xs"
                variant="subtle"
                color="neutral"
                :disabled="activeIndex >= versions.length - 1"
                @click="selectIndex(activeIndex + 1)"
              />
              <span class="text-xs text-dimmed px-1"
                >{{ versions.length - activeIndex }} de {{ versions.length }}</span
              >
              <UButton
                icon="i-lucide-chevron-right"
                size="xs"
                variant="subtle"
                color="neutral"
                :disabled="activeIndex <= 0"
                @click="selectIndex(activeIndex - 1)"
              />
            </div>
          </div>

          <div
            class="flex-1 rounded-xl overflow-hidden border border-default bg-elevated/40 min-h-0 flex items-center justify-center"
          >
            <video
              v-if="currentVersion?.file"
              ref="videoEl"
              :src="currentVersion.file"
              controls
              class="max-w-full max-h-full"
              @loadedmetadata="onLoadedMetadata"
              @timeupdate="onTimeUpdate"
            />
            <div v-else class="flex flex-col items-center gap-2 text-dimmed">
              <UIcon name="i-lucide-play-circle" class="size-14" />
              <span class="text-xs">Sem arquivo de vídeo nesta versão</span>
            </div>
          </div>

          <div class="flex flex-col gap-1.5 shrink-0">
            <span class="text-[11px] text-dimmed"
              >Clique na barra para comentar em um instante específico</span
            >
            <div class="relative h-10 flex items-center cursor-pointer" @click="onScrubberClick">
              <div class="w-full h-1.5 rounded-full bg-accented">
                <div class="h-full rounded-full bg-dimmed" :style="{ width: `${playedPct}%` }" />
              </div>

              <div
                v-for="p in pinsAtVersion"
                :key="p.id"
                class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 size-4 rounded-full border-2 border-default cursor-pointer z-[2]"
                :class="p.color"
                :style="{ left: `${p.pct}%` }"
                :title="p.content"
              />

              <div
                v-if="draftPct != null"
                class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 size-4 rounded-full bg-primary border-2 border-primary/40 z-[3]"
                :style="{ left: `${draftPct}%` }"
              />
            </div>
            <div class="flex justify-between text-[10.5px] text-dimmed font-mono">
              <span>0:00</span>
              <span>{{ durationLabel }}</span>
            </div>

            <div
              v-if="draftTime != null"
              class="rounded-lg border border-default bg-elevated/60 p-2.5 flex flex-col gap-2"
            >
              <span class="text-[11px] text-primary font-mono">em {{ draftTimeLabel }}</span>
              <UTextarea
                v-model="draftText"
                :rows="2"
                autoresize
                placeholder="O que precisa ajustar nesse momento?"
                variant="subtle"
                size="xs"
                class="w-full"
              />
              <div class="flex justify-end gap-1.5">
                <UButton
                  label="Cancelar"
                  variant="ghost"
                  color="neutral"
                  size="xs"
                  @click="cancelDraft"
                />
                <UButton
                  label="Comentar"
                  size="xs"
                  :disabled="!draftText.trim()"
                  @click="submitDraft()"
                />
              </div>
            </div>
          </div>

          <div v-if="versions.length > 1" class="flex gap-1.5 shrink-0 overflow-x-auto pb-0.5">
            <button
              v-for="(v, i) in versions"
              :key="v.id"
              class="px-2.5 py-1.5 rounded-md text-xs shrink-0 border cursor-pointer"
              :class="
                i === activeIndex
                  ? 'border-primary text-primary bg-primary/10'
                  : 'border-default text-dimmed hover:bg-elevated/60'
              "
              @click="selectIndex(i)"
            >
              v{{ v.number }}
            </button>
          </div>
        </div>
      </div>
    </UCard>

    <UCard
      :ui="{
        root: 'w-[340px] shrink-0 flex flex-col',
        body: 'flex-1 flex flex-col min-h-0 p-0 sm:p-0',
      }"
    >
      <!-- Comments -->
      <div class="flex flex-col overflow-hidden size-full">
        <div class="flex items-center justify-between px-4 pt-4">
          <span class="text-xs font-semibold text-highlighted">Comentários</span>
          <UButton
            label="Criar task"
            icon="i-lucide-plus"
            size="xs"
            variant="subtle"
            color="neutral"
            @click="taskModalOpen = true"
          />
        </div>

        <div class="flex-1 overflow-y-auto flex flex-col gap-1 px-4 pt-3 pb-4">
          <span class="text-[11px] font-semibold text-dimmed uppercase tracking-wide mb-0.5"
            >No tempo</span
          >

          <span v-if="pinsAtVersion.length === 0" class="text-xs text-dimmed pb-3.5">
            Clique na barra de progresso para marcar um instante.
          </span>

          <div v-for="p in pinsAtVersion" :key="p.id" class="flex gap-2 py-2">
            <span
              class="font-mono text-[10.5px] font-semibold text-inverted rounded px-1.5 py-0.5 shrink-0 self-start"
              :class="p.color"
            >
              {{ p.label }}
            </span>
            <span class="text-xs text-toned leading-snug">{{ p.content }}</span>
          </div>

          <div class="h-px bg-default my-3" />

          <span class="text-[11px] font-semibold text-dimmed uppercase tracking-wide mb-0.5"
            >Geral</span
          >
          <div v-for="g in generalComments" :key="g.id" class="flex gap-2 py-2">
            <UAvatar size="2xs" icon="i-lucide-user" class="shrink-0" />
            <span class="text-xs text-toned leading-snug">{{ g.content }}</span>
          </div>
        </div>

        <div class="p-4 shrink-0 flex flex-col gap-2">
          <UTextarea
            v-model="generalDraft"
            :rows="2"
            autoresize
            placeholder="Deixe um comentário geral sobre esse arquivo..."
            variant="subtle"
            size="xs"
            class="w-full"
          />
          <UButton
            label="Comentar"
            size="xs"
            class="self-end"
            :disabled="!generalDraft.trim()"
            @click="submitGeneral()"
          />
        </div>
      </div>
    </UCard>

    <CMediaCommentTaskModal
      v-model:open="taskModalOpen"
      :media="mediaData"
      :comments="taskModalComments"
    />
  </div>
</template>
