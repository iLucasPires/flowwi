<script setup lang="ts">
import type { iFormBlockDraft, tFormBlockTypesMap } from '@/app/features/form/types'

defineOptions({ name: 'FormEditorFieldHeader' })

const props = defineProps<{
  block: iFormBlockDraft
  allBlocks?: iFormBlockDraft[]
  blockTypes: tFormBlockTypesMap
}>()

const emit = defineEmits<{
  'update:block': [value: iFormBlockDraft]
}>()

const showConfig = ref(false)
const showCondition = ref(false)
const hasCondition = computed(() => Object.keys(props.block.condition ?? {}).length > 0)

function updateTitle(title: string) {
  emit('update:block', { ...props.block, title })
}

/** 1-based index among non-content blocks on this page — used for "1 →" numbering. */
const questionNumber = computed(() => {
  const fields = (props.allBlocks ?? []).filter((b) => b.type !== 'content')
  const idx = fields.findIndex((b) => b.key === props.block.key)
  return idx >= 0 ? idx + 1 : null
})
</script>

<template>
  <div class="flex items-start justify-between gap-2 mb-2" contenteditable="false">
    <!-- Question number badge + editable label -->
    <div class="flex items-baseline gap-2 flex-1 min-w-0">
      <span
        v-if="questionNumber !== null"
        class="shrink-0 text-xs font-mono font-medium text-muted select-none leading-none mt-0.5"
      >
        {{ questionNumber }}<UIcon name="i-lucide-arrow-right" class="size-3 inline-block ml-0.5 align-middle" />
      </span>

      <input
        :value="block.title"
        type="text"
        placeholder="Pergunta sem título"
        class="flex-1 min-w-0 bg-transparent text-sm font-medium text-highlighted border-0 p-0 focus:outline-none focus:ring-0 placeholder:text-dimmed/60"
        @input="updateTitle(($event.target as HTMLInputElement).value)"
      />
    </div>

    <!-- Corner controls: shown on hover -->
    <div class="shrink-0 flex items-center gap-0 opacity-0 group-hover/field:opacity-100 transition-opacity">
      <!-- Required dot — always visible when required -->
      <UTooltip :text="block.required ? 'Obrigatório — clique para tornar opcional' : 'Opcional — clique para tornar obrigatório'">
        <UButton
          icon="i-lucide-asterisk"
          size="2xs"
          variant="ghost"
          :color="block.required ? 'error' : 'neutral'"
          :class="block.required ? 'opacity-100!' : ''"
          @click="emit('update:block', { ...block, required: !block.required })"
        />
      </UTooltip>

      <UTooltip text="Configurações do campo">
        <UButton
          icon="i-lucide-settings-2"
          size="2xs"
          variant="ghost"
          :color="showConfig ? 'primary' : 'neutral'"
          @click="() => { showConfig = !showConfig; showCondition = false }"
        />
      </UTooltip>

      <UTooltip text="Lógica condicional">
        <UButton
          icon="i-lucide-git-branch"
          size="2xs"
          variant="ghost"
          :color="hasCondition || showCondition ? 'primary' : 'neutral'"
          @click="() => { showCondition = !showCondition; showConfig = false }"
        />
      </UTooltip>
    </div>
  </div>

  <CFormBlockConfig v-model:open="showConfig" :block="block" @update:block="(v) => emit('update:block', v)" />
  <CFormBlockCondition
    v-model:open="showCondition"
    :block="block"
    :all-blocks="allBlocks"
    :block-types="blockTypes"
    @update:block="(v) => emit('update:block', v)"
  />
</template>
