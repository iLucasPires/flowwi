<script setup lang="ts">
import type { NodeViewProps } from '@tiptap/vue-3'
import { NodeViewContent, NodeViewWrapper } from '@tiptap/vue-3'

defineOptions({ name: 'FormEditorColumnsNode' })

const props = defineProps<NodeViewProps>()

const columns = computed(() => (props.node.attrs.columns as number) || 2)
</script>

<template>
  <NodeViewWrapper
    class="group/columns relative grid gap-x-3 my-1 [&_[data-node-view-content-vue]]:contents"
    :style="{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }"
  >
    <!-- Remove the whole row — distinct from a single field's own delete (drag-handle) -->
    <div
      contenteditable="false"
      class="hidden group-hover/columns:flex absolute -top-2 -right-1 z-10 items-center bg-default border border-default rounded-full shadow-sm"
    >
      <UTooltip text="Remover colunas">
        <UButton icon="i-lucide-trash-2" size="2xs" variant="ghost" color="error" @click="deleteNode" />
      </UTooltip>
    </div>

    <NodeViewContent class="contents" />
  </NodeViewWrapper>
</template>
