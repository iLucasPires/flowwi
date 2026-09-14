<script setup lang="ts">
import { cTaskPriorityItems } from '@/app/features/task/constants'
const model = defineModel<string | undefined>()

const props = defineProps<{
  placeholder?: string
  size?: string
  variant?: string
  activeVariant?: string
  color?: string
  clearable?: boolean
}>()

const active = computed(() => props.clearable && !!model.value)
const items = computed(() => cTaskPriorityItems)
const currentItem = computed(() => cTaskPriorityItems.find((i) => i.value === model.value))
const icon = computed(() => currentItem.value?.icon ?? 'i-lucide-signal-low')
const iconColor = computed(() => currentItem.value?.color ?? 'text-neutral-400')
</script>

<template>
  <USelectMenu
    v-model="model"
    value-key="value"
    variant="ghost"
    :items="items"
    :placeholder="placeholder"
    :size="size"
    :ui="{
      content: 'w-56',
      itemLabel: 'whitespace-nowrap truncate',
    }"
  >
    <template #leading>
      <UIcon :name="icon" :class="['size-4 shrink-0', iconColor]" />
    </template>
    <template v-if="active" #trailing>
      <UIcon
        name="i-lucide-x"
        class="size-3.5 cursor-pointer opacity-50 hover:opacity-100"
        @click.stop.prevent="model = undefined"
      />
    </template>
    <template #item="{ item }">
      <UIcon :name="item.icon" :class="['size-4 shrink-0', item.color]" />
      <span v-text="item.label" class="truncate whitespace-nowrap" />
    </template>
  </USelectMenu>
</template>
