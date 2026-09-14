<script setup lang="ts">
import type { iDocumentSelectionAnchor } from '@/app/features/document/types'
import type { Editor, EditorEvents } from '@tiptap/vue-3'
import { Emoji } from '@tiptap/extension-emoji'
import { TextAlign } from '@tiptap/extension-text-align'
import { CodeBlockShiki } from 'tiptap-extension-code-block-shiki'
import { createImageUploadExtension } from '@/app/features/document/composables/documentEditorImageUpload'

/**
 * Read-only rendering of a document's title + content — no editing chrome, no
 * comments/composables wiring. Takes only the data it needs to render, so it can be
 * dropped as-is onto a future public/client-facing screen (e.g. a shared preview link).
 */
defineOptions({ name: 'DocumentPreview' })

const props = defineProps<{
  title: string
  icon?: string
  hasCover?: boolean
  content: string
}>()

const emit = defineEmits<{
  /** Fires on every text-selection change inside the content, or `null` once it clears. */
  selectionChange: [selection: iDocumentSelectionAnchor | null]
}>()

const editorRef = useTemplateRef<{ editor?: Editor }>('editorRef')

function onSelectionUpdate({ editor }: EditorEvents['selectionUpdate']) {
  const { from, to, empty } = editor.state.selection
  if (empty) {
    emit('selectionChange', null)
    return
  }

  const text = editor.state.doc.textBetween(from, to, ' ').trim()
  if (!text) {
    emit('selectionChange', null)
    return
  }

  // The native selection's bounding box (rather than a single coordsAtPos point)
  // covers multi-line selections and both drag directions correctly, so the
  // toolbar always lands centered over what's actually highlighted.
  const domSelection = window.getSelection()
  const range = domSelection && domSelection.rangeCount > 0 ? domSelection.getRangeAt(0) : null
  const rect = range?.getBoundingClientRect()

  if (!rect || (rect.width === 0 && rect.height === 0)) {
    emit('selectionChange', null)
    return
  }

  emit('selectionChange', {
    text,
    top: rect.top,
    bottom: rect.bottom,
    centerX: rect.left + rect.width / 2,
  })
}

watch(
  () => editorRef.value?.editor,
  (editor, prevEditor) => {
    prevEditor?.off('selectionUpdate', onSelectionUpdate)
    editor?.on('selectionUpdate', onSelectionUpdate)
  },
)
</script>

<template>
  <div class="flex flex-col gap-3.5">
    <div
      v-if="icon"
      :class="hasCover ? '-mt-14 mb-1 relative z-10 inline-block' : 'inline-block mb-1'"
    >
      <div
        class="flex items-center justify-center overflow-hidden"
        :class="hasCover ? 'size-20 rounded-2xl' : 'size-18 rounded-2xl'"
      >
        <CIconOrEmoji :value="icon" class="size-14 text-6xl shrink-0" />
      </div>
    </div>

    <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-highlighted break-words">
      {{ title || 'Sem título' }}
    </h1>

    <UEditor
      ref="editorRef"
      :model-value="props.content"
      :editable="false"
      content-type="markdown"
      :starter-kit="{ codeBlock: false }"
      :extensions="[
        TextAlign.configure({ types: ['heading', 'paragraph'] }),
        Emoji,
        createImageUploadExtension(),
        CodeBlockShiki.configure({
          defaultTheme: 'material-theme',
          themes: { light: 'material-theme-lighter', dark: 'material-theme-palenight' },
        }),
      ]"
      :ui="{
        base: [
          'p-0!',
          '[&_h1]:text-3xl [&_h1]:font-bold [&_h1]:tracking-tight [&_h1]:text-highlighted [&_h1]:mt-6 [&_h1]:mb-2',
          '[&_h2]:text-2xl [&_h2]:font-semibold [&_h2]:tracking-tight [&_h2]:text-highlighted [&_h2]:mt-5 [&_h2]:mb-1.5',
          '[&_h3]:text-xl [&_h3]:font-semibold [&_h3]:tracking-tight [&_h3]:text-highlighted [&_h3]:mt-4 [&_h3]:mb-1',
          '[&_p]:text-[15px] [&_p]:leading-7 [&_p]:text-default [&_p]:my-1',
          '[&_blockquote]:border-s-3 [&_blockquote]:border-default [&_blockquote]:ps-4 [&_blockquote]:my-2 [&_blockquote]:text-toned [&_blockquote]:italic',
          '[&_ul]:list-disc [&_ul]:ps-5 [&_ul]:my-1.5 [&_ul]:leading-relaxed',
          '[&_ol]:list-decimal [&_ol]:ps-5 [&_ol]:my-1.5 [&_ol]:leading-relaxed',
          '[&_hr]:border-default [&_hr]:my-4',
        ],
      }"
    />
  </div>
</template>
