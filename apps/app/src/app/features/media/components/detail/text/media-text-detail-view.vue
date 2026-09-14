<script setup lang="ts">
import { useMediaDetail } from '@/app/features/media/composables/mediaDetail'
import { useMediaFeedback } from '@/app/features/media/composables/mediaFeedback'
import { useMediaTextAutosave, useMediaTextComments } from '@/app/features/media/composables/mediaText'
import type { iMedia } from '@/app/features/media/types'
import type { EditorToolbarItem } from '@nuxt/ui'
import type { EditorEvents, Editor as TiptapEditor } from '@tiptap/vue-3'

const props = defineProps<{ media: iMedia }>()

defineOptions({ name: 'MediaTextDetailView' })

const router = useRouter()

const { mediaData, versions, activeIndex, currentVersion, selectIndex } = useMediaDetail(
  props.media,
)

const feedbackTab = ref('media')
const { likeCount, dislikeCount, toggleFeedback, myFeedback } = useMediaFeedback(
  mediaData,
  feedbackTab,
  currentVersion,
)

const { saving, onContentChange } = useMediaTextAutosave(mediaData, currentVersion)
const { submitAnchored, submittingAnchored, generalDraft, submitGeneral } = useMediaTextComments(
  mediaData,
  currentVersion,
)

const toolbarItems: EditorToolbarItem[][] = [
  [
    {
      icon: 'i-lucide-heading',
      tooltip: { text: 'Headings' },
      content: { align: 'start' },
      items: [
        { kind: 'heading', level: 1, icon: 'i-lucide-heading-1', label: 'Heading 1' },
        { kind: 'heading', level: 2, icon: 'i-lucide-heading-2', label: 'Heading 2' },
        { kind: 'heading', level: 3, icon: 'i-lucide-heading-3', label: 'Heading 3' },
      ],
    },
  ],
  [
    { kind: 'mark', mark: 'bold', icon: 'i-lucide-bold', tooltip: { text: 'Bold' } },
    { kind: 'mark', mark: 'italic', icon: 'i-lucide-italic', tooltip: { text: 'Italic' } },
    { kind: 'mark', mark: 'underline', icon: 'i-lucide-underline', tooltip: { text: 'Underline' } },
    {
      kind: 'mark',
      mark: 'strike',
      icon: 'i-lucide-strikethrough',
      tooltip: { text: 'Strikethrough' },
    },
  ],
]

// ── Select-text-to-comment ──────────────────────────────────────────────────

const editorRef = useTemplateRef<{ editor?: TiptapEditor }>('editorRef')

/** Live position/text of the current non-empty selection, while the user is selecting. */
const selection = ref<{ text: string; top: number; left: number } | null>(null)
/** Frozen quote + open state once the user clicks "Comentar" — decoupled from further selection changes. */
const composer = ref<{ quote: string; top: number; left: number; text: string } | null>(null)

function onSelectionUpdate({ editor }: EditorEvents['selectionUpdate']) {
  if (composer.value) return

  const { from, to, empty } = editor.state.selection
  if (empty) {
    selection.value = null
    return
  }

  const text = editor.state.doc.textBetween(from, to, ' ').trim()
  if (!text) {
    selection.value = null
    return
  }

  const coords = editor.view.coordsAtPos(to)
  selection.value = { text, top: coords.bottom + 6, left: coords.left }
}

function openComposer() {
  if (!selection.value) return
  composer.value = {
    quote: selection.value.text,
    top: selection.value.top,
    left: selection.value.left,
    text: '',
  }
  selection.value = null
}

function closeComposer() {
  composer.value = null
}

async function submitComposer() {
  if (!composer.value || !composer.value.text.trim()) return
  await submitAnchored({ quote: composer.value.quote, content: composer.value.text.trim() })
  composer.value = null
}

watch(
  () => editorRef.value?.editor,
  (editor, prevEditor) => {
    prevEditor?.off('selectionUpdate', onSelectionUpdate)
    editor?.on('selectionUpdate', onSelectionUpdate)
  },
)

watch(currentVersion, () => {
  selection.value = null
  composer.value = null
})

// ── Comments ─────────────────────────────────────────────────────────────

const anchoredComments = computed(() => {
  if (!currentVersion.value) return []
  return mediaData.value.comments.filter((c) => c.version === currentVersion.value!.id && c.quote)
})

const generalComments = computed(() => mediaData.value.comments.filter((c) => !c.quote))

function truncateQuote(quote: string) {
  return quote.length > 28 ? `${quote.slice(0, 28)}…` : quote
}

const taskModalComments = computed(() => [
  ...anchoredComments.value.map((c) => ({ ...c, kindTag: `"${truncateQuote(c.quote)}"` })),
  ...generalComments.value.map((c) => ({ ...c, kindTag: 'Geral' })),
])

const taskModalOpen = ref(false)

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
          <UBadge icon="i-lucide-file-text" size="sm" variant="subtle" color="neutral"
            >Texto</UBadge
          >
          <span v-if="saving" class="text-[11px] text-dimmed">Salvando…</span>
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
        <!-- Continuous writing surface -->
        <div class="flex-1 flex flex-col gap-3 p-5 min-w-0">
          <div v-if="versions.length > 1" class="flex items-center justify-between shrink-0">
            <span class="text-sm font-medium text-highlighted">v{{ currentVersion?.number }}</span>
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
            class="flex-1 min-h-0 overflow-y-auto rounded-xl border border-default bg-elevated/20 px-8 py-6"
          >
            <UEditor
              v-if="currentVersion"
              :key="currentVersion.id"
              ref="editorRef"
              v-slot="{ editor }"
              :model-value="currentVersion.text_content"
              content-type="markdown"
              class="size-full max-w-2xl mx-auto"
              placeholder="Comece a escrever…"
              :ui="{
                base: [
                  'p-0!',
                  '[&_h1]:text-2xl [&_h1]:font-semibold',
                  '[&_h2]:text-xl [&_h2]:font-semibold',
                  '[&_h3]:text-lg [&_h3]:font-semibold',
                  '[&_p]:text-sm [&_p]:leading-relaxed',
                ],
              }"
              @update:model-value="onContentChange($event as string)"
            >
              <UEditorToolbar :editor="editor" :items="toolbarItems" layout="bubble" />
            </UEditor>
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
            >No texto</span
          >

          <span v-if="anchoredComments.length === 0" class="text-xs text-dimmed pb-3.5">
            Selecione um trecho do texto para comentar.
          </span>

          <div v-for="c in anchoredComments" :key="c.id" class="flex flex-col gap-1 py-2">
            <span
              class="text-[11px] text-primary bg-primary/10 rounded px-1.5 py-0.5 self-start max-w-full truncate"
            >
              "{{ c.quote }}"
            </span>
            <span class="text-xs text-toned leading-snug">{{ c.content }}</span>
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

    <!-- Floating "Comentar" button on text selection -->
    <UButton
      v-if="selection"
      label="Comentar"
      icon="i-lucide-message-square-plus"
      size="xs"
      class="fixed z-40 shadow-lg"
      :style="{ top: `${selection.top}px`, left: `${selection.left}px` }"
      @mousedown.prevent="openComposer"
    />

    <!-- Inline comment composer, anchored where the selection ended -->
    <div
      v-if="composer"
      class="fixed z-40 w-72 rounded-lg border border-default bg-default shadow-lg p-2.5 flex flex-col gap-2"
      :style="{ top: `${composer.top}px`, left: `${composer.left}px` }"
    >
      <span
        class="text-[11px] text-primary bg-primary/10 rounded px-1.5 py-0.5 self-start max-w-full truncate"
      >
        "{{ composer.quote }}"
      </span>
      <UTextarea
        v-model="composer.text"
        :rows="2"
        autoresize
        autofocus
        placeholder="O que precisa ajustar aqui?"
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
          @click="closeComposer"
        />
        <UButton
          label="Comentar"
          size="xs"
          :disabled="!composer.text.trim()"
          :loading="submittingAnchored"
          @click="submitComposer"
        />
      </div>
    </div>

    <CMediaCommentTaskModal
      v-model:open="taskModalOpen"
      :media="mediaData"
      :comments="taskModalComments"
    />
  </div>
</template>
