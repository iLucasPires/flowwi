<script setup lang="ts">
import { cFormChoiceKeys } from '@/app/features/form/constants'
import type { NodeViewProps } from '@tiptap/vue-3'
import { NodeViewWrapper } from '@tiptap/vue-3'
import type { iFieldAttrs } from '@/app/features/form/composables/formEditorFieldNode'
import { useFieldOptions } from '@/app/features/form/composables/useFieldOptions'
import type { iFormBlockDraft, tFormBlockTypesMap } from '@/app/features/form/types'

defineOptions({ name: 'FormEditorSelectFieldNode' })

const props = defineProps<NodeViewProps>()

const blockTypesMap = inject<Ref<tFormBlockTypesMap>>('formEditorBlockTypes', ref({}))
const allBlocks = inject<Ref<iFormBlockDraft[]>>('formEditorAllBlocks', ref([]))

const attrs = computed(() => props.node.attrs as iFieldAttrs)

const blockDraft = computed<iFormBlockDraft>(() => ({
  key: attrs.value.blockKey,
  title: attrs.value.title,
  type: 'select',
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

const config = computed(() => attrs.value.config)
function updateConfig(config: Record<string, unknown>) {
  props.updateAttributes({ config })
}

const { currentOptions, newOptionLabel, addOption, removeOption, updateOptionLabel } = useFieldOptions(
  config,
  updateConfig,
)

const optionKeys = cFormChoiceKeys
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
      <CFormBlockInputSelect :config="attrs.config" editor />

      <div class="mt-3 flex flex-col gap-0">
        <div
          v-for="(opt, optIndex) in currentOptions"
          :key="optIndex"
          class="flex items-center gap-2.5 py-1.5 group/opt"
        >
          <span
            class="flex items-center justify-center size-5 shrink-0 rounded border border-default text-[10px] font-mono text-muted select-none"
          >
            {{ optionKeys[optIndex] }}
          </span>
          <input
            :value="opt.label"
            type="text"
            :placeholder="`Opção ${optIndex + 1}`"
            class="flex-1 bg-transparent text-sm text-toned border-0 p-0 focus:outline-none focus:ring-0 placeholder:text-dimmed/50"
            @input="updateOptionLabel(optIndex, ($event.target as HTMLInputElement).value)"
          />
          <button
            type="button"
            class="opacity-0 group-hover/opt:opacity-100 shrink-0 text-muted hover:text-error transition-all"
            @click="removeOption(optIndex)"
          >
            <UIcon name="i-lucide-x" class="size-3.5" />
          </button>
        </div>

        <div class="flex items-center gap-2.5 py-1.5">
          <span class="flex items-center justify-center size-5 shrink-0">
            <UIcon name="i-lucide-plus" class="size-3.5 text-muted" />
          </span>
          <input
            v-model.trim="newOptionLabel"
            type="text"
            placeholder="Adicionar opção..."
            class="flex-1 bg-transparent text-sm text-muted border-0 p-0 focus:outline-none focus:ring-0 placeholder:text-dimmed/50 focus:text-highlighted"
            @keydown.enter="addOption"
          />
        </div>
      </div>
    </div>
  </NodeViewWrapper>
</template>
