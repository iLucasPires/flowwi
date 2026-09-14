<script setup lang="ts">
import { cMediaVersionItems } from '@/app/features/media/constants'
const model = defineModel<string | undefined>()

const props = defineProps<{
  placeholder?: string
  size?: string
  color?: string
  clearable?: boolean
}>()

const active = computed(() => props.clearable && !!model.value)
const versionItems = cMediaVersionItems
const currentItem = computed(() => versionItems.find((i) => i.value === model.value))
const icon = computed(() => currentItem.value?.icon ?? 'i-lucide-layers')
const iconColor = computed(() => currentItem.value?.color ?? 'text-neutral-400')
</script>

<template>
  <USelectMenu
    v-model="model"
    value-key="value"
    variant="subtle"
    :items="versionItems"
    :placeholder="placeholder"
    :size="size as any"
    :color="(color as any) ?? 'neutral'"
  >
    <template #leading>
      <UIcon :name="icon" :class="['size-4', iconColor]" />
    </template>
    <template v-if="active" #trailing>
      <UIcon
        name="i-lucide-x"
        class="size-3.5 cursor-pointer opacity-50 hover:opacity-100"
        @click.stop.prevent="model = undefined"
      />
    </template>
    <template #item="{ item }">
      <UIcon :name="item.icon" :class="['size-4', item.color]" />
      <span>{{ item.label }}</span>
    </template>
  </USelectMenu>
</template>
