<script setup lang="ts">
import { cStickyVisibilityItems } from '@/app/features/sticky/constants'
import type { DropdownMenuItem } from '@nuxt/ui'

const visibility = defineModel<string | undefined>('visibility')

function buildCheckboxChildren(
  items: { label: string; value: string; icon: string }[],
  model: Ref<string | undefined>,
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
      label: 'Visibilidade',
      icon: 'i-lucide-eye',
      children: buildCheckboxChildren(cStickyVisibilityItems, visibility),
    },
  ],
])
</script>

<template>
  <UDropdownMenu :items="items" :content="{ align: 'end', sideOffset: 8 }" size="xs">
    <UButton icon="i-lucide-filter" color="neutral" variant="subtle" size="sm" />
  </UDropdownMenu>
</template>
