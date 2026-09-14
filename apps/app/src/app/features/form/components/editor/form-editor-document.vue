<script setup lang="ts">
import { cFormBlockTypeItems } from '@/app/features/form/constants'
import type { DropdownMenuItem, EditorCustomHandlers, EditorSuggestionMenuItem } from '@nuxt/ui'
import { mapEditorItems } from '@nuxt/ui/utils/editor'
import type { Editor, JSONContent } from '@tiptap/vue-3'
import type { Component } from 'vue'
import { createFieldExtension, FIELD_NODE_NAMES, insertFieldNode } from '@/app/features/form/composables/formEditorFieldNode'
import { createFormColumnExtension, createFormColumnsExtension } from '@/app/features/form/composables/formEditorColumnsNode'
import { blocksToDoc, docToBlocks } from '@/app/features/form/composables/formDocConverter'
import ChoiceFieldNode from '@/app/features/form/components/editor/node/form-editor-choice-field-node.vue'
import DateFieldNode from '@/app/features/form/components/editor/node/form-editor-date-field-node.vue'
import EmailFieldNode from '@/app/features/form/components/editor/node/form-editor-email-field-node.vue'
import FileFieldNode from '@/app/features/form/components/editor/node/form-editor-file-field-node.vue'
import NumberFieldNode from '@/app/features/form/components/editor/node/form-editor-number-field-node.vue'
import SelectFieldNode from '@/app/features/form/components/editor/node/form-editor-select-field-node.vue'
import TextFieldNode from '@/app/features/form/components/editor/node/form-editor-text-field-node.vue'
import TimeFieldNode from '@/app/features/form/components/editor/node/form-editor-time-field-node.vue'
import type { iFormBlockDraft, iFormPageDraft, tFormBlockType } from '@/app/features/form/types'

const FIELD_COMPONENTS: Record<Exclude<tFormBlockType, 'content'>, Component> = {
  text: TextFieldNode,
  email: EmailFieldNode,
  number: NumberFieldNode,
  date: DateFieldNode,
  time: TimeFieldNode,
  select: SelectFieldNode,
  choice: ChoiceFieldNode,
  file: FileFieldNode,
}

const fieldExtensions = Object.entries(FIELD_NODE_NAMES).map(([type, name]) =>
  createFieldExtension(name, FIELD_COMPONENTS[type as Exclude<tFormBlockType, 'content'>]),
)

defineOptions({ name: 'FormEditorDocument' })

const props = defineProps<{
  page: iFormPageDraft
}>()

const emit = defineEmits<{
  'update:blocks': [value: iFormBlockDraft[]]
}>()

const blockTypesMap = computed(() =>
  cFormBlockTypeItems.reduce(
    (acc, item) => ({ ...acc, [item.value]: { label: item.label, icon: item.icon, color: item.color } }),
    {} as Record<string, { label: string; icon: string; color: string }>,
  ),
)
provide('formEditorBlockTypes', blockTypesMap)

const doc = computed(() => blocksToDoc(props.page.blocks))

function onDocUpdate(value: unknown) {
  emit('update:blocks', docToBlocks(value as Parameters<typeof docToBlocks>[0]))
}

interface FieldDockItem {
  label: string
  description: string
  icon: string
  fieldType: Exclude<tFormBlockType, 'content'>
  configOverride?: Record<string, unknown>
}

const fieldItems: FieldDockItem[] = [
  { label: 'Pergunta curta', description: 'Resposta de texto curto.', icon: 'i-lucide-type', fieldType: 'text' },
  {
    label: 'Texto longo',
    description: 'Resposta de texto em parágrafo.',
    icon: 'i-lucide-text',
    fieldType: 'text',
    configOverride: { long: true },
  },
  { label: 'Número', description: 'Resposta numérica.', icon: 'i-lucide-hash', fieldType: 'number' },
  { label: 'Email', description: 'Endereço de email.', icon: 'i-lucide-mail', fieldType: 'email' },
  { label: 'Data', description: 'Seletor de data.', icon: 'i-lucide-calendar', fieldType: 'date' },
  { label: 'Hora', description: 'Seletor de hora.', icon: 'i-lucide-clock', fieldType: 'time' },
  { label: 'Seleção única', description: 'Escolher uma opção de uma lista.', icon: 'i-lucide-list', fieldType: 'select' },
  {
    label: 'Múltipla escolha',
    description: 'Escolher uma ou mais opções.',
    icon: 'i-lucide-check-circle',
    fieldType: 'choice',
  },
  { label: 'Upload', description: 'Envio de arquivo.', icon: 'i-lucide-paperclip', fieldType: 'file' },
]

interface ColumnsDockItem {
  label: string
  description: string
  icon: string
  columns: number
}

const columnsItems: ColumnsDockItem[] = [
  { label: '2 colunas', description: 'Duas perguntas lado a lado.', icon: 'i-lucide-columns-2', columns: 2 },
  { label: '3 colunas', description: 'Três perguntas lado a lado.', icon: 'i-lucide-columns-3', columns: 3 },
  { label: '4 colunas', description: 'Quatro perguntas lado a lado.', icon: 'i-lucide-columns-4', columns: 4 },
]

const customHandlers = {
  field: {
    canExecute: () => true,
    execute: (editor: Editor, cmd?: FieldDockItem) =>
      cmd
        ? insertFieldNode(editor, FIELD_NODE_NAMES[cmd.fieldType], cmd.fieldType, cmd.configOverride)
        : editor.chain(),
    isActive: (editor: Editor, cmd?: FieldDockItem) =>
      cmd ? editor.isActive(FIELD_NODE_NAMES[cmd.fieldType]) : false,
    isDisabled: undefined,
  },
  formColumns: {
    canExecute: (editor: Editor) => editor.can().insertFormColumns(2),
    execute: (editor: Editor, cmd?: ColumnsDockItem) =>
      editor.chain().focus().insertFormColumns(cmd?.columns ?? 2),
    isActive: () => false,
    isDisabled: undefined,
  },
} satisfies EditorCustomHandlers

const selectedNode = ref<{ node: JSONContent; pos: number }>()

function handleItems(editor: Editor): DropdownMenuItem[][] {
  if (!selectedNode.value?.node?.type) return []

  return mapEditorItems(
    editor,
    [
      [
        {
          kind: 'duplicate',
          pos: selectedNode.value?.pos,
          label: 'Duplicar',
          icon: 'i-lucide-copy',
        },
      ],
      [
        {
          kind: 'moveUp',
          pos: selectedNode.value?.pos,
          label: 'Mover para cima',
          icon: 'i-lucide-arrow-up',
        },
        {
          kind: 'moveDown',
          pos: selectedNode.value?.pos,
          label: 'Mover para baixo',
          icon: 'i-lucide-arrow-down',
        },
      ],
      [
        {
          kind: 'delete',
          pos: selectedNode.value?.pos,
          label: 'Excluir',
          icon: 'i-lucide-trash-2',
        },
      ],
    ],
    customHandlers,
  ) as DropdownMenuItem[][]
}

const suggestionItems = [
  [
    { type: 'label', label: 'Texto' },
    { kind: 'paragraph', label: 'Texto', description: 'Um parágrafo livre.', icon: 'i-lucide-pilcrow' },
    { kind: 'heading', level: 1, label: 'Título 1', description: 'Título de seção grande.', icon: 'i-lucide-heading-1' },
    { kind: 'heading', level: 2, label: 'Título 2', description: 'Título médio.', icon: 'i-lucide-heading-2' },
    { kind: 'heading', level: 3, label: 'Título 3', description: 'Título pequeno.', icon: 'i-lucide-heading-3' },
  ],
  [{ type: 'label', label: 'Perguntas' }, ...fieldItems.map((item) => ({ kind: 'field' as const, ...item }))],
  [
    { type: 'label', label: 'Layout' },
    ...columnsItems.map((item) => ({ kind: 'formColumns' as const, ...item })),
  ],
] satisfies EditorSuggestionMenuItem<typeof customHandlers>[][]
</script>

<template>
  <UEditor
    v-slot="{ editor, handlers }"
    :model-value="doc"
    content-type="json"
    :starter-kit="{ horizontalRule: false, codeBlock: false, blockquote: false }"
    :extensions="[...fieldExtensions, createFormColumnsExtension(), createFormColumnExtension()]"
    :handlers="customHandlers"
    placeholder="Pressione '/' para adicionar uma pergunta..."
    :ui="{
      base: [
        'pl-0! pr-0! pt-0! pb-0!',
        'sm:pl-10! sm:-ml-10!',
        '[&_[data-type=form-column]]:min-w-0 [&_[data-type=form-column]]:min-h-12',
        '[&_[data-type=form-column]]:rounded-lg [&_[data-type=form-column]]:border [&_[data-type=form-column]]:border-dashed [&_[data-type=form-column]]:border-muted/60 [&_[data-type=form-column]]:px-2 [&_[data-type=form-column]]:py-2',
        '[&_h1]:text-2xl [&_h1]:font-bold [&_h1]:tracking-tight [&_h1]:text-highlighted [&_h1]:mt-6 [&_h1]:mb-2',
        '[&_h2]:text-xl [&_h2]:font-semibold [&_h2]:tracking-tight [&_h2]:text-highlighted [&_h2]:mt-5 [&_h2]:mb-1.5',
        '[&_h3]:text-base [&_h3]:font-semibold [&_h3]:tracking-tight [&_h3]:text-highlighted [&_h3]:mt-4 [&_h3]:mb-1',
        '[&_p]:text-[15px] [&_p]:leading-7 [&_p]:text-toned [&_p]:my-1',
      ],
    }"
    @update:model-value="onDocUpdate"
  >
    <UEditorSuggestionMenu :editor="editor" :items="suggestionItems" />

    <UEditorDragHandle
      v-slot="{ ui, onClick }"
      :editor="editor"
      @node-change="selectedNode = $event"
    >
      <UButton
        icon="i-lucide-trash-2"
        color="neutral"
        variant="ghost"
        size="sm"
        :class="typeof ui?.handle === 'function' ? ui.handle() : ''"
        @click="
          (event) => {
            event.stopPropagation()
            const selected = onClick?.()
            if (selected) editor.chain().focus().deleteRange({ from: selected.pos, to: selected.pos + selected.node.nodeSize }).run()
          }
        "
      />

      <UButton
        icon="i-lucide-plus"
        color="neutral"
        variant="ghost"
        size="sm"
        :class="typeof ui?.handle === 'function' ? ui.handle() : ''"
        @click="
          (event) => {
            event.stopPropagation()
            const selected = onClick?.()
            handlers.suggestion?.execute(editor, { pos: selected?.pos }).run()
          }
        "
      />

      <UDropdownMenu
        v-slot="{ open }"
        :modal="false"
        :items="handleItems(editor)"
        :content="{ side: 'left' }"
        :ui="{ content: 'w-44' }"
        @update:open="editor.chain().setMeta('lockDragHandle', $event).run()"
      >
        <UButton
          color="neutral"
          variant="ghost"
          active-variant="soft"
          size="sm"
          icon="i-lucide-grip-vertical"
          :active="open"
          :class="typeof ui?.handle === 'function' ? ui.handle() : ''"
        />
      </UDropdownMenu>
    </UEditorDragHandle>
  </UEditor>
</template>
