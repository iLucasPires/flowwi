<script setup lang="ts">
import { cInboxTypeItems } from '@/app/features/inbox/constants'
import type { DropdownMenuItem } from '@nuxt/ui'

const type = defineModel<number[]>('type', { default: () => [] })

function toggleInArray<T>(model: Ref<T[]>, value: T) {
  model.value = model.value.includes(value)
    ? model.value.filter((v) => v !== value)
    : [...model.value, value]
}

const typeItems = computed<DropdownMenuItem[]>(() =>
  Object.entries(cInboxTypeItems).map(([value, meta]) => ({
    label: meta.label,
    icon: meta.icon,
    type: 'checkbox',
    checked: type.value.includes(Number(value)),
    onUpdateChecked: () => toggleInArray(type, Number(value)),
    onSelect: (e) => e.preventDefault(),
  })),
)

function clearFilters() {
  type.value = []
}

const items = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: 'Tipo',
      icon: 'i-lucide-tag',
      children: typeItems.value,
    },
  ],
  [
    {
      label: 'Limpar filtros',
      icon: 'i-lucide-x',
      onSelect: clearFilters,
    },
  ],
])

const activeCount = computed(() => type.value.length)
</script>

<template>
  <UDropdownMenu
    size="xs"
    :items="items"
    :content="{
      align: 'end',
      sideOffset: 8,
    }"
  >
    <UButton icon="i-lucide-filter" variant="ghost" color="neutral" size="xs">
      <template v-if="activeCount > 0" #trailing>
        <UBadge :label="activeCount" size="xs" color="primary" variant="subtle" />
      </template>
    </UButton>
  </UDropdownMenu>
</template>
