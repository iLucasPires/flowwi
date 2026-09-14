<script setup lang="ts">
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
const model = defineModel<number | null | undefined>()

const props = defineProps<{
  placeholder?: string
  size?: string
  variant?: string
  activeVariant?: string
  color?: string
  clearable?: boolean
}>()

const { statuses } = useTaskStatus()

const active = computed(() => props.clearable && !!model.value)
const items = computed(() =>
  statuses.value.map((status) => ({
    value: status.id,
    label: status.name,
    icon: status.icon || 'i-lucide-circle',
    color: status.color,
  })),
)
const currentItem = computed(() => items.value.find((i) => i.value === model.value))
const icon = computed(() => currentItem.value?.icon ?? 'i-lucide-circle')
const iconColor = computed(() => currentItem.value?.color ?? '#a3a3a3')

const selectValue = computed({
  get: () => model.value ?? undefined,
  set: (value: number | undefined) => {
    model.value = value ?? null
  },
})
</script>

<template>
  <USelectMenu
    v-model="selectValue"
    value-key="value"
    :items="items"
    :placeholder="placeholder"
    :size="size"
    variant="ghost"
    :ui="{
      content: 'w-56',
      itemLabel: 'whitespace-nowrap truncate',
    }"
  >
    <template #leading>
      <CIconOrEmoji :value="icon" class="size-4 shrink-0 text-sm" :style="{ color: iconColor }" />
    </template>
    <template v-if="active" #trailing>
      <UIcon
        name="i-lucide-x"
        class="size-3.5 cursor-pointer opacity-50 hover:opacity-100"
        @click.stop.prevent="model = null"
      />
    </template>
    <template #item="{ item }">
      <CIconOrEmoji
        :value="item.icon"
        class="size-4 shrink-0 text-sm"
        :style="{ color: item.color }"
      />
      <span v-text="item.label" class="truncate whitespace-nowrap" />
    </template>
  </USelectMenu>
</template>
