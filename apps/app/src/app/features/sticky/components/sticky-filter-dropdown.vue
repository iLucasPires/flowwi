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

function clearFilters() {
  visibility.value = undefined
}

const items = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: 'Visibilidade',
      icon: 'i-lucide-eye',
      children: buildCheckboxChildren(cStickyVisibilityItems, visibility),
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

const activeCount = computed(() => (visibility.value ? 1 : 0))
</script>

<template>
  <UDropdownMenu :items="items" :content="{ align: 'end', sideOffset: 8 }" size="xs">
    <UButton label="Filtros" icon="i-lucide-filter" variant="subtle" color="neutral" size="xs">
      <template v-if="activeCount > 0" #trailing>
        <UBadge :label="activeCount" size="xs" color="primary" variant="subtle" />
      </template>
    </UButton>
  </UDropdownMenu>
</template>
