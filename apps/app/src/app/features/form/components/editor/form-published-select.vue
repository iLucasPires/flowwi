<script setup lang="ts">
import { cFormPublishedItems } from '@/app/features/form/constants'

const model = defineModel<boolean | undefined>()

interface iProps {
  placeholder?: string
  size?: string
  color?: string
}

defineProps<iProps>()

const currentItem = computed(() => cFormPublishedItems.find((i) => i.value === model.value))

const icon = computed(() => currentItem.value?.icon ?? 'i-lucide-globe')
const iconColor = computed(() => currentItem.value?.color ?? 'text-neutral-400')
</script>

<template>
  <USelectMenu
    v-model="model"
    :items="cFormPublishedItems"
    :placeholder="placeholder"
    :size="size"
    value-key="value"
    variant="ghost"
    :color="(color as any) ?? 'neutral'"
  >
    <template #leading>
      <UIcon :name="icon" :class="['size-4', iconColor]" />
    </template>

    <template #item="{ item }">
      <UIcon :name="item.icon" :class="['size-4', item.color]" />
      <span v-text="item.label" />
    </template>
  </USelectMenu>
</template>
