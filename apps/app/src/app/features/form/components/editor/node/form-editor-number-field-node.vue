<script setup lang="ts">
import type { NodeViewProps } from '@tiptap/vue-3'
import { NodeViewWrapper } from '@tiptap/vue-3'
import type { iFieldAttrs } from '@/app/features/form/composables/formEditorFieldNode'
import type { iFormBlockDraft, tFormBlockTypesMap } from '@/app/features/form/types'

defineOptions({ name: 'FormEditorNumberFieldNode' })

const props = defineProps<NodeViewProps>()

const blockTypesMap = inject<Ref<tFormBlockTypesMap>>('formEditorBlockTypes', ref({}))
const allBlocks = inject<Ref<iFormBlockDraft[]>>('formEditorAllBlocks', ref([]))

const attrs = computed(() => props.node.attrs as iFieldAttrs)

const blockDraft = computed<iFormBlockDraft>(() => ({
  key: attrs.value.blockKey,
  title: attrs.value.title,
  type: 'number',
  required: attrs.value.required,
  config: attrs.value.config,
  col_span: 0,
  col_start: 0,
  condition: attrs.value.condition,
}))

function applyBlockUpdate(value: iFormBlockDraft) {
  props.updateAttributes({
    title: value.title,
    required: value.required,
    config: value.config,
    condition: value.condition,
  })
}
</script>

<template>
  <NodeViewWrapper
    class="group/field relative min-w-0 my-1"
    :class="selected ? 'bg-elevated/60' : 'hover:bg-elevated/30 transition-colors'"
  >
    <div contenteditable="false">
      <CFormEditorFieldHeader
        :block="blockDraft"
        :all-blocks="allBlocks"
        :block-types="blockTypesMap"
        @update:block="applyBlockUpdate"
      />
      <CFormBlockInputNumber :config="attrs.config" editor />
    </div>
  </NodeViewWrapper>
</template>
