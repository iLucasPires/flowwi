<script setup lang="ts">
import type { EditorSuggestionMenuItem, EditorToolbarItem } from '@nuxt/ui'
import { TextAlign } from '@tiptap/extension-text-align'
import { CodeBlockShiki } from 'tiptap-extension-code-block-shiki'

/**
 * Full-size markdown editor for a document type's starter template — same visual
 * language as the real document editor (bubble toolbar on selection, slash commands,
 * heading sizes), minus the pieces that only make sense against a real document
 * (mentions, image upload, AI). No persistent toolbar/header sits above the writing
 * area — same as `CDocumentEditor`/`CRichTextEditor`, formatting shows up only when
 * you select text or type "/". Its own component rather than a mode of
 * `CRichTextEditor`, which is tuned small/compact for inline descriptions elsewhere.
 */
defineOptions({ name: 'DocumentTypeTemplateEditor' })

defineProps<{
  modelValue?: string
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const headingItems = [
  { kind: 'heading', level: 1, icon: 'i-lucide-heading-1', label: 'Título 1' },
  { kind: 'heading', level: 2, icon: 'i-lucide-heading-2', label: 'Título 2' },
  { kind: 'heading', level: 3, icon: 'i-lucide-heading-3', label: 'Título 3' },
] as const

const listItems = [
  { kind: 'bulletList', icon: 'i-lucide-list', label: 'Lista com marcadores' },
  { kind: 'orderedList', icon: 'i-lucide-list-ordered', label: 'Lista numerada' },
] as const

const bubbleToolbarItems: EditorToolbarItem[][] = [
  [
    {
      label: 'Título',
      trailingIcon: 'i-lucide-chevron-down',
      // Without these the button inherits the toolbar's default active styling
      // (primary/soft), which paints a loud highlight since this button is always
      // "active" for whatever block type the cursor is in.
      activeColor: 'neutral',
      activeVariant: 'ghost',
      tooltip: { text: 'Título' },
      content: { align: 'start' },
      items: [{ kind: 'paragraph', label: 'Texto', icon: 'i-lucide-type' }, ...headingItems],
    },
  ],
  [
    { kind: 'mark', mark: 'bold', icon: 'i-lucide-bold', tooltip: { text: 'Negrito' } },
    { kind: 'mark', mark: 'italic', icon: 'i-lucide-italic', tooltip: { text: 'Itálico' } },
    {
      kind: 'mark',
      mark: 'underline',
      icon: 'i-lucide-underline',
      tooltip: { text: 'Sublinhado' },
    },
    {
      kind: 'mark',
      mark: 'strike',
      icon: 'i-lucide-strikethrough',
      tooltip: { text: 'Riscado' },
    },
    { kind: 'mark', mark: 'code', icon: 'i-lucide-code', tooltip: { text: 'Código' } },
  ],
  [
    ...listItems,
    { kind: 'blockquote', icon: 'i-lucide-text-quote', tooltip: { text: 'Citação' } },
    { kind: 'codeBlock', icon: 'i-lucide-square-code', tooltip: { text: 'Bloco de código' } },
  ],
  [
    { slot: 'link' as const, icon: 'i-lucide-link', tooltip: { text: 'Link' } },
    {
      kind: 'horizontalRule',
      icon: 'i-lucide-minus',
      tooltip: { text: 'Divisor' },
    },
  ],
]

const suggestionItems: EditorSuggestionMenuItem[][] = [
  [
    { type: 'label', label: 'Blocos básicos' },
    {
      kind: 'paragraph',
      label: 'Texto',
      description: 'Comece a escrever texto comum.',
      icon: 'i-lucide-type',
    },
    {
      kind: 'heading',
      level: 1,
      label: 'Título 1',
      description: 'Título de seção grande.',
      icon: 'i-lucide-heading-1',
    },
    {
      kind: 'heading',
      level: 2,
      label: 'Título 2',
      description: 'Título de subseção médio.',
      icon: 'i-lucide-heading-2',
    },
    {
      kind: 'heading',
      level: 3,
      label: 'Título 3',
      description: 'Título pequeno de subseção.',
      icon: 'i-lucide-heading-3',
    },
    {
      kind: 'bulletList',
      label: 'Lista com marcadores',
      description: 'Crie uma lista simples com marcadores.',
      icon: 'i-lucide-list',
    },
    {
      kind: 'orderedList',
      label: 'Lista numerada',
      description: 'Crie uma lista numerada ordenada.',
      icon: 'i-lucide-list-ordered',
    },
    {
      kind: 'blockquote',
      label: 'Citação',
      description: 'Destaque uma citação ou reflexão.',
      icon: 'i-lucide-text-quote',
    },
    {
      kind: 'codeBlock',
      label: 'Bloco de código',
      description: 'Trecho de código com destaque de sintaxe.',
      icon: 'i-lucide-square-code',
    },
    {
      kind: 'horizontalRule',
      label: 'Divisor',
      description: 'Divida blocos visualmente com uma linha.',
      icon: 'i-lucide-minus',
    },
  ],
]
</script>

<template>
  <UEditor
    v-slot="{ editor }"
    :model-value="modelValue"
    content-type="markdown"
    class="size-full"
    :starter-kit="{ codeBlock: false }"
    :extensions="[
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      CodeBlockShiki.configure({
        defaultTheme: 'material-theme',
        themes: { light: 'material-theme-lighter', dark: 'material-theme-palenight' },
      }),
    ]"
    :placeholder="placeholder"
    :ui="{
      base: [
        'p-0!',
        '[&_h1]:text-2xl [&_h1]:font-bold [&_h1]:tracking-tight [&_h1]:text-highlighted [&_h1]:mt-4 [&_h1]:mb-1.5',
        '[&_h2]:text-xl [&_h2]:font-semibold [&_h2]:tracking-tight [&_h2]:text-highlighted [&_h2]:mt-3.5 [&_h2]:mb-1',
        '[&_h3]:text-lg [&_h3]:font-semibold [&_h3]:tracking-tight [&_h3]:text-highlighted [&_h3]:mt-3 [&_h3]:mb-0.5',
        '[&_p]:text-sm [&_p]:leading-6 [&_p]:text-default [&_p]:my-1',
        '[&_blockquote]:border-s-3 [&_blockquote]:border-default [&_blockquote]:ps-3 [&_blockquote]:my-1.5 [&_blockquote]:text-toned [&_blockquote]:italic',
        '[&_ul]:list-disc [&_ul]:ps-5 [&_ul]:my-1 [&_ul]:leading-relaxed',
        '[&_ol]:list-decimal [&_ol]:ps-5 [&_ol]:my-1 [&_ol]:leading-relaxed',
        '[&_hr]:border-default [&_hr]:my-3',
      ],
    }"
    @update:model-value="emit('update:modelValue', $event as string)"
  >
    <!-- No fixed header — formatting surfaces only on selection (bubble) or via "/". -->
    <UEditorToolbar
      :editor="editor"
      :items="bubbleToolbarItems"
      layout="bubble"
      size="xs"
      :should-show="
        ({ view, state }) => {
          const { selection } = state
          return view.hasFocus() && !selection.empty
        }
      "
    >
      <template #link>
        <CDocumentEditorLinkPopover :editor="editor" />
      </template>
    </UEditorToolbar>

    <UEditorSuggestionMenu :editor="editor" :items="suggestionItems" />
  </UEditor>
</template>
