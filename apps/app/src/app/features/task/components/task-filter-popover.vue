<script setup lang="ts">
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import { useTaskType } from '@/app/features/task/composables/taskType'
import { cTaskPriorityItems } from '@/app/features/task/constants'
import { useWorkplaceMember } from '@/app/features/workplace/composables/workplaceMember'
import type { DropdownMenuItem } from '@nuxt/ui'

const status = defineModel<number[]>('status', { default: () => [] })
const priority = defineModel<string[]>('priority', { default: () => [] })
const type = defineModel<number[]>('type', { default: () => [] })
const assignee = defineModel<number[]>('assignee', { default: () => [] })

const { statuses } = useTaskStatus()
const { types } = useTaskType()
const { members } = useWorkplaceMember()

function toggleInArray(model: Ref<(string | number)[]>, value: string | number) {
  model.value = model.value.includes(value)
    ? model.value.filter((v) => v !== value)
    : [...model.value, value]
}

function createCheckboxItems(
  options: Array<{
    label: string
    value: string | number
    icon?: string
    avatar?: {
      src: string
      alt: string
    }
  }>,
  model: Ref<(string | number)[]>,
): DropdownMenuItem[] {
  return options.map((option) => ({
    label: option.label,
    icon: option.icon,
    avatar: option.avatar,
    type: 'checkbox',
    checked: model.value.includes(option.value),
    onUpdateChecked: () => toggleInArray(model, option.value),
    onSelect: (e) => e.preventDefault(),
  }))
}

const filters = computed(() => [
  {
    label: 'Status',
    icon: 'i-lucide-circle-dashed',
    model: status as unknown as Ref<(string | number)[]>,
    options: statuses.value.map((s) => ({
      label: s.name,
      value: s.id,
      icon: s.icon,
    })),
  },
  {
    label: 'Tipo',
    icon: 'i-lucide-tag',
    model: type as unknown as Ref<(string | number)[]>,
    options: types.value.map((t) => ({
      label: t.name,
      value: t.id,
      icon: t.icon,
    })),
  },
  {
    label: 'Prioridade',
    icon: 'i-lucide-signal-medium',
    model: priority as unknown as Ref<(string | number)[]>,
    options: cTaskPriorityItems,
  },
  {
    label: 'Responsável',
    icon: 'i-lucide-user',
    model: assignee as unknown as Ref<(string | number)[]>,
    options: members.value.map((m) => ({
      label: m.profile?.full_name ?? '',
      value: m.id,
      avatar: {
        src: m.profile?.photo ?? '',
        alt: m.profile?.full_name ?? '',
      },
    })),
  },
])

function clearFilters() {
  filters.value.forEach((filter) => {
    filter.model.value = []
  })
}

const items = computed<DropdownMenuItem[][]>(() => [
  filters.value.map((filter) => ({
    label: filter.label,
    icon: filter.icon,
    children: createCheckboxItems(filter.options, filter.model),
  })),
  [
    {
      label: 'Limpar filtros',
      icon: 'i-lucide-x',
      onSelect: clearFilters,
    },
  ],
])

const activeCount = computed(() =>
  filters.value.reduce((total, filter) => total + filter.model.value.length, 0),
)
</script>

<template>
  <UDropdownMenu :items="items" :content="{ align: 'end', sideOffset: 8 }" size="sm">
    <UButton label="Filtros" icon="i-lucide-filter" variant="subtle" color="neutral" size="xs">
      <template v-if="activeCount > 0" #trailing>
        <UBadge :label="activeCount" size="xs" color="primary" variant="subtle" />
      </template>
    </UButton>
  </UDropdownMenu>
</template>
