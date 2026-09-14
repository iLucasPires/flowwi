<script setup lang="ts">
import type { iDocument, iDocumentLock, iDocumentSelectionAnchor, iDocumentVersion } from '@/app/features/document/types'
import { getDocumentTypeMeta } from '@/app/features/document/utils'
import type { iCoverCredit } from '@/app/shared/types/cover'
import type { BreadcrumbItem } from '@nuxt/ui'
import { useDocumentType } from '@/app/features/document/composables/documentType'

defineOptions({ name: 'DocumentCenterSplitter' })

const props = defineProps<{
  doc: iDocument
  currentVersion: iDocumentVersion | undefined
  activeIndex: number
  isReadonly: boolean
  lockedBy: iDocumentLock | null
  isLockedByOther: boolean
  saving: boolean
  splitOpen: boolean
  canComment: boolean
  submittingAnchored: boolean
}>()

const emit = defineEmits<{
  titleInput: [value: string]
  updateIcon: [icon: string]
  selectCoverFile: [file: File]
  selectCoverStyle: [style: string, credit: iCoverCredit]
  removeCover: []
  contentChange: [value: string]
  toggleSplit: []
  submitComment: [payload: { quote: string; content: string }]
}>()

const { types: documentTypes } = useDocumentType()

// Why the doc is read-only, in priority order — most specific/actionable first. Only
// shown when `isReadonly` is true; explains a state that used to look like a silent bug
// (e.g. "I gave them edit access but it still won't let them type").
const readonlyReason = computed(() => {
  if (props.isLockedByOther && props.lockedBy) {
    return {
      icon: 'i-lucide-lock',
      text: `${props.lockedBy.username} está editando este documento agora.`,
    }
  }
  if (props.currentVersion?.status === 'published') {
    return {
      icon: 'i-lucide-file-check-2',
      text: 'Esta versão foi publicada — crie uma nova revisão para editar.',
    }
  }
  if (!props.doc.can_edit) {
    return { icon: 'i-lucide-eye', text: 'Você só tem acesso de visualização a este documento.' }
  }
  return null
})

const breadcrumb = computed<BreadcrumbItem[]>(() => {
  const doc = props.doc
  const typeLabel = getDocumentTypeMeta(documentTypes.value, doc.type)?.name ?? 'Sem tipo'
  return [{ label: typeLabel }, { label: doc.title || 'Sem título', icon: doc.icon || undefined }]
})

// ── Select-text-to-comment ──────────────────────────────────────────────────
// Only the read-only preview (published versions) can ever be commented on — the
// draft editor doesn't track selection at all, since `canComment` is false there.

/** Live position/text of the current non-empty selection, while previewing. */
const selection = ref<iDocumentSelectionAnchor | null>(null)
/** Whether the comment composer popover is open — pauses selection tracking while composing. */
const composing = ref(false)

function onPreviewSelectionChange(next: iDocumentSelectionAnchor | null) {
  // Once the composer is open, its textarea takes focus and the browser collapses the
  // visible text selection — which fires a `selectionUpdate` with an empty selection.
  // Reacting to it here would null the anchor and, through `v-if="selection"` below,
  // instantly unmount the popover we just opened. Freeze the anchor while composing;
  // it's cleared explicitly once the composer actually closes.
  if (composing.value) return

  selection.value = props.canComment ? next : null
}

/** Closing the composer (cancel, submit, click outside) always drops the stale anchor. */
function onComposingChange(value: boolean) {
  composing.value = value
  if (!value) selection.value = null
}

function submitComment(payload: { quote: string; content: string }) {
  emit('submitComment', payload)
}

/** Scrolling moves the text away from a `fixed` toolbar anchored to old viewport coords. */
function onContentScroll() {
  if (!composing.value) selection.value = null
}

watch(
  () => props.doc.id,
  () => {
    selection.value = null
    composing.value = false
  },
)
</script>

<template>
  <div class="size-full flex flex-col min-h-0">
    <div class="flex items-center gap-3 px-4.5 py-2.5 border-b border-default shrink-0">
      <UBreadcrumb
        class="min-w-0 flex-1"
        :items="breadcrumb"
        :ui="{
          list: 'flex-nowrap overflow-hidden',
          item: 'min-w-0 last:min-w-fit',
          link: 'text-[11.5px] gap-1 text-dimmed hover:text-toned aria-[current=page]:text-toned aria-[current=page]:font-medium',
          linkLabel: 'truncate',
          separatorIcon: 'size-3.5',
        }"
      >
        <template #item-leading="{ item }">
          <CIconOrEmoji v-if="item.icon" :value="item.icon" class="size-3.5 shrink-0 text-xs" />
        </template>
      </UBreadcrumb>

      <CMemberOwnerIndicator :user-id="doc.author" />

      <div class="w-px h-4 bg-border shrink-0" />

      <slot name="side-panel" />
    </div>

    <UBanner
      v-if="isReadonly && readonlyReason"
      icon="i-lucide-info"
      color="neutral"
      :title="readonlyReason.text"
    />

    <div class="flex-1 overflow-y-auto min-h-0" @scroll="onContentScroll">
      <CDocumentCover
        v-if="doc.cover || doc.cover_style"
        :src="doc.cover"
        :style="doc.cover_style"
        :credit="doc.cover_credit"
        :editable="!isReadonly"
        @select-file="emit('selectCoverFile', $event)"
        @select-style="(style, credit) => emit('selectCoverStyle', style, credit)"
        @remove="emit('removeCover')"
      />

      <div
        class="max-w-5xl w-full mx-auto px-8 pb-12"
        :class="doc.cover || doc.cover_style ? 'pt-0' : 'pt-8'"
      >
        <CDocumentPreview
          v-if="isReadonly"
          :title="doc.title"
          :icon="doc.icon"
          :has-cover="!!doc.cover || !!doc.cover_style"
          :content="currentVersion?.content ?? ''"
          @selection-change="onPreviewSelectionChange"
        />

        <template v-else>
          <div class="relative group/header mb-4">
            <div
              v-if="doc.icon"
              :class="
                doc.cover || doc.cover_style
                  ? '-mt-14 relative z-10 inline-block'
                  : 'inline-block mb-1'
              "
            >
              <CIconPicker
                :model-value="doc.icon"
                fallback="i-lucide-file-text"
                icon-class="size-14 text-6xl"
                @update:model-value="emit('updateIcon', $event)"
              />
            </div>

            <div
              class="flex items-center gap-1 transition-opacity duration-200"
              :class="[
                doc.icon ? 'mt-1' : doc.cover || doc.cover_style ? 'pt-3' : 'mb-1',
                !doc.icon || (!doc.cover && !doc.cover_style)
                  ? 'opacity-0 group-hover/header:opacity-100 focus-within:opacity-100'
                  : 'hidden',
              ]"
            >
              <CIconPicker
                v-if="!doc.icon"
                empty-label="Adicionar ícone"
                @update:model-value="emit('updateIcon', $event)"
              />

              <CDocumentCover
                v-if="!doc.cover && !doc.cover_style"
                @select-file="emit('selectCoverFile', $event)"
                @select-style="(style, credit) => emit('selectCoverStyle', style, credit)"
                @remove="emit('removeCover')"
              />
            </div>
          </div>

          <UInput
            :model-value="doc.title"
            :highlight="false"
            placeholder="Sem título"
            variant="none"
            :ui="{
              base: 'p-0! mb-4 text-3xl sm:text-4xl! font-bold tracking-tight text-highlighted placeholder:text-dimmed/40',
            }"
            @update:model-value="emit('titleInput', $event as string)"
          />

          <CDocumentEditor
            :current-version="currentVersion"
            @content-change="emit('contentChange', $event)"
          />
        </template>
      </div>
    </div>

    <CDocumentCommentComposer
      v-if="selection"
      :selection="selection"
      :submitting="submittingAnchored"
      @update:open="onComposingChange"
      @submit="submitComment"
    />
  </div>
</template>
