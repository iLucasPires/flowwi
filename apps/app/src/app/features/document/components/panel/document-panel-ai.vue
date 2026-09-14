<script setup lang="ts">
import { DOCUMENT_AI_ACTIONS } from '@/app/features/document/composables/documentAi'

defineProps<{
  aiOutput: string
  aiLabel: string
  aiRunning: boolean
  aiRunningKey: string | null
  aiPrompt: string
}>()

const emit = defineEmits<{
  runAi: [actionKey?: string]
  insertAi: []
  clearAi: []
  'update:aiPrompt': [value: string]
}>()

function getActionIcon(key: string) {
  switch (key) {
    case 'resumir':
      return 'i-lucide-file-text'
    case 'continuar':
      return 'i-lucide-pen-line'
    case 'titulos':
      return 'i-lucide-heading'
    case 'encurtar':
      return 'i-lucide-scissors'
    default:
      return 'i-lucide-sparkles'
  }
}

defineOptions({ name: 'DocumentPanelAi' })
</script>

<template>
  <div class="flex flex-col gap-2.5">
    <div class="flex items-center justify-between px-0.5">
      <div class="flex items-center gap-1.5">
        <UIcon name="i-lucide-sparkles" class="size-3.5 text-primary" />
        <span class="text-xs font-semibold text-highlighted">Assistente de IA</span>
      </div>

      <UBadge
        label="Notion AI"
        size="xs"
        variant="subtle"
        color="primary"
        class="text-[10px] px-1.5 py-0 h-4"
      />
    </div>

    <USeparator class="my-0.5" />

    <div class="grid grid-cols-2 gap-1.5">
      <UButton
        v-for="action in DOCUMENT_AI_ACTIONS"
        :key="action.key"
        :label="action.label"
        :icon="getActionIcon(action.key)"
        size="xs"
        variant="subtle"
        color="neutral"
        block
        class="justify-start text-xs truncate"
        :loading="aiRunningKey === action.key"
        :disabled="aiRunning && aiRunningKey !== action.key"
        @click="emit('runAi', action.key)"
      />
    </div>

    <div
      v-if="aiOutput"
      class="flex flex-col gap-2 p-3 rounded-lg bg-primary/5 border border-primary/20 transition-all"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1.5">
          <UIcon name="i-lucide-sparkles" class="size-3 text-primary animate-pulse" />
          <span class="text-[11px] font-semibold text-primary uppercase tracking-wider">
            {{ aiLabel || 'Resultado' }}
          </span>
        </div>

        <UButton
          icon="i-lucide-x"
          variant="ghost"
          color="neutral"
          size="2xs"
          @click="emit('clearAi')"
        />
      </div>

      <p class="text-xs text-default leading-relaxed whitespace-pre-wrap">
        {{ aiOutput }}
      </p>

      <div class="flex items-center gap-1.5 pt-1">
        <UButton
          label="Inserir no doc"
          icon="i-lucide-corner-down-left"
          size="xs"
          color="primary"
          @click="emit('insertAi')"
        />
        <UButton
          label="Descartar"
          variant="ghost"
          color="neutral"
          size="xs"
          @click="emit('clearAi')"
        />
      </div>
    </div>

    <div class="flex flex-col gap-1.5">
      <UTextarea
        :model-value="aiPrompt"
        :rows="2"
        autoresize
        placeholder="Pergunte à IA ou peça para reescrever..."
        variant="subtle"
        size="xs"
        class="w-full"
        @update:model-value="emit('update:aiPrompt', String($event))"
      />
      <UButton
        label="Perguntar"
        icon="i-lucide-sparkles"
        size="xs"
        color="primary"
        class="self-end"
        :disabled="!aiPrompt.trim() || (aiRunning && aiRunningKey !== 'custom')"
        :loading="aiRunningKey === 'custom'"
        @click="emit('runAi')"
      />
    </div>
  </div>
</template>
