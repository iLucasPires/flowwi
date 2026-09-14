<script setup lang="ts">
import type { StickyVisibility } from '@/app/features/sticky/types'
const props = defineProps<{
  visibility: StickyVisibility
  canEditVisibility: boolean
}>()

const emit = defineEmits<{
  'update:visibility': [StickyVisibility]
}>()

const VISIBILITY_ITEMS: {
  value: StickyVisibility
  label: string
  icon: string
  description: string
}[] = [
  {
    value: 'private',
    label: 'Privado',
    icon: 'i-lucide-lock',
    description: 'Só você pode ver este sticky.',
  },
  {
    value: 'workplace',
    label: 'Workplace',
    icon: 'i-lucide-users',
    description: 'Todo mundo no workplace pode ver.',
  },
]

function selectVisibility(value: StickyVisibility) {
  if (!props.canEditVisibility || value === props.visibility) return
  emit('update:visibility', value)
}

defineOptions({ name: 'StickyPanelShare' })
</script>

<template>
  <div class="flex flex-col gap-2.5 w-64">
    <div class="flex items-center gap-1.5 px-0.5">
      <UIcon name="i-lucide-share-2" class="size-3.5 text-muted" />
      <span class="text-xs font-semibold text-highlighted">Visibilidade</span>
    </div>

    <USeparator class="my-0.5" />

    <div class="flex flex-col gap-1">
      <UButton
        v-for="item in VISIBILITY_ITEMS"
        :key="item.value"
        variant="ghost"
        color="neutral"
        block
        :disabled="!canEditVisibility"
        class="justify-start px-2.5 py-2 h-auto rounded-md"
        :class="visibility === item.value ? 'bg-elevated' : ''"
        @click="selectVisibility(item.value)"
      >
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <UIcon
            :name="item.icon"
            class="size-3.5 shrink-0"
            :class="visibility === item.value ? 'text-primary' : 'text-dimmed'"
          />
          <div class="flex flex-col items-start min-w-0">
            <span class="text-xs font-medium text-default">{{ item.label }}</span>
            <span class="text-[10.5px] text-dimmed leading-tight text-start">
              {{ item.description }}
            </span>
          </div>
        </div>
        <UIcon
          v-if="visibility === item.value"
          name="i-lucide-check"
          class="size-3.5 shrink-0 text-primary"
        />
      </UButton>
    </div>

    <p v-if="!canEditVisibility" class="text-[10.5px] text-dimmed leading-tight px-0.5">
      Só quem criou este sticky pode alterar a visibilidade.
    </p>
  </div>
</template>
