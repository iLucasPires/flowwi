<script setup lang="ts">
import type { iDocumentType } from '@/app/features/document/types'
import type { DropdownMenuItem } from '@nuxt/ui'
import { DOC_SORT_ITEMS, type iDocSortOrder } from '@/app/features/document/composables/documentVault'

const props = defineProps<{
  types: iDocumentType[]
}>()

const sortOrder = defineModel<iDocSortOrder>('sortOrder', { required: true })
const typeFilter = defineModel<(number | null)[]>('typeFilter', { default: () => [] })

function toggleInFilter(value: number | null) {
  typeFilter.value = typeFilter.value.includes(value)
    ? typeFilter.value.filter((v) => v !== value)
    : [...typeFilter.value, value]
}

const sortItems = computed<DropdownMenuItem[]>(() =>
  DOC_SORT_ITEMS.map((s) => ({
    label: s.label,
    type: 'checkbox',
    checked: sortOrder.value === s.value,
    onUpdateChecked: () => (sortOrder.value = s.value),
    onSelect: (e) => e.preventDefault(),
  })),
)

const typeItems = computed<DropdownMenuItem[]>(() => [
  ...props.types.map((t) => ({
    label: t.name,
    icon: t.icon || 'i-lucide-tag',
    type: 'checkbox' as const,
    checked: typeFilter.value.includes(t.id),
    onUpdateChecked: () => toggleInFilter(t.id),
    onSelect: (e: Event) => e.preventDefault(),
  })),
  {
    label: 'Sem tipo',
    icon: 'i-lucide-file-question',
    type: 'checkbox' as const,
    checked: typeFilter.value.includes(null),
    onUpdateChecked: () => toggleInFilter(null),
    onSelect: (e: Event) => e.preventDefault(),
  },
])

function clearFilter() {
  typeFilter.value = []
}

const items = computed<DropdownMenuItem[][]>(() => [
  [{ label: 'Ordenar', type: 'label' }, ...sortItems.value],
  [{ label: 'Tipo', icon: 'i-lucide-tag', children: typeItems.value }],
  [
    {
      label: 'Limpar filtro',
      icon: 'i-lucide-x',
      disabled: typeFilter.value.length === 0,
      onSelect: clearFilter,
    },
  ],
])

const activeCount = computed(() => typeFilter.value.length)

defineOptions({ name: 'DocumentTreeFilterPopover' })
</script>

<template>
  <UDropdownMenu size="xs" :items="items" :content="{ align: 'end', sideOffset: 8 }">
    <UButton icon="i-lucide-list-filter" variant="ghost" color="neutral" size="xs">
      <template v-if="activeCount > 0" #trailing>
        <UBadge :label="activeCount" size="xs" color="primary" variant="subtle" />
      </template>
    </UButton>
  </UDropdownMenu>
</template>
