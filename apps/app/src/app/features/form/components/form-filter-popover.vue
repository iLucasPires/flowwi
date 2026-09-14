<script setup lang="ts">
import { cFormPublishedItems } from '@/app/features/form/constants'
import type { DropdownMenuItem } from '@nuxt/ui'

const published = defineModel<boolean | undefined>('published')

function buildCheckboxChildren(
  items: { label: string; value: boolean; icon: string }[],
  model: Ref<boolean | undefined>,
): DropdownMenuItem[] {
  return items.map((item) => ({
    label: item.label,
    icon: item.icon,
    type: 'checkbox' as const,
    checked: model.value === item.value,
    onUpdateChecked(checked: boolean) {
      model.value = checked ? item.value : undefined
    },
    onSelect(e: Event) {
      e.preventDefault()
    },
  }))
}

const items = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: 'Status',
      icon: 'i-lucide-globe',
      children: buildCheckboxChildren(cFormPublishedItems, published),
    },
  ],
])
</script>

<template>
  <UDropdownMenu :items="items" :content="{ align: 'end', sideOffset: 8 }" size="xs">
    <UButton icon="i-lucide-filter" color="neutral" variant="subtle" size="xs" />
  </UDropdownMenu>
</template>
