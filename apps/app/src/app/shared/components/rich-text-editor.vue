<script setup lang="ts">
import type { EditorToolbarItem } from '@nuxt/ui'

defineProps<{
  modelValue?: string
  placeholder?: string
  autofocus?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: []
}>()

const items: EditorToolbarItem[][] = [
  [
    {
      icon: 'i-lucide-heading',
      tooltip: { text: 'Headings' },
      content: {
        align: 'start',
      },
      items: [
        {
          kind: 'heading',
          level: 1,
          icon: 'i-lucide-heading-1',
          label: 'Heading 1',
        },
        {
          kind: 'heading',
          level: 2,
          icon: 'i-lucide-heading-2',
          label: 'Heading 2',
        },
        {
          kind: 'heading',
          level: 3,
          icon: 'i-lucide-heading-3',
          label: 'Heading 3',
        },
        {
          kind: 'heading',
          level: 4,
          icon: 'i-lucide-heading-4',
          label: 'Heading 4',
        },
      ],
    },
  ],
  [
    {
      kind: 'mark',
      mark: 'bold',
      icon: 'i-lucide-bold',
      tooltip: { text: 'Bold' },
    },
    {
      kind: 'mark',
      mark: 'italic',
      icon: 'i-lucide-italic',
      tooltip: { text: 'Italic' },
    },
    {
      kind: 'mark',
      mark: 'underline',
      icon: 'i-lucide-underline',
      tooltip: { text: 'Underline' },
    },
    {
      kind: 'mark',
      mark: 'strike',
      icon: 'i-lucide-strikethrough',
      tooltip: { text: 'Strikethrough' },
    },
    {
      kind: 'mark',
      mark: 'code',
      icon: 'i-lucide-code',
      tooltip: { text: 'Code' },
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
    :autofocus="autofocus"
    :placeholder="placeholder"
    :ui="{
      base: [
        'p-0!',
        '[&_p]:text-xs',
        '[&_h1]:text-lg',
        '[&_h2]:text-md',
        '[&_h3]:text-sm',
        '[&_h4]:text-sm',
      ],
    }"
    @update:model-value="emit('update:modelValue', $event as string)"
    @blur="emit('blur')"
  >
    <UEditorToolbar :editor="editor" :items="items" layout="bubble" />
  </UEditor>
</template>
