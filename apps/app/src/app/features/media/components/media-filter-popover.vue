<script setup lang="ts">
import { cMediaTypeItems } from '@/app/features/media/constants'
defineOptions({ name: 'MediaFilterPopover' })

const type = defineModel<number[]>('type', { default: () => [] })
const groupBy = defineModel<'none' | 'day' | 'hour'>('groupBy', { default: 'none' })
const sortOrder = defineModel<'recent' | 'oldest'>('sortOrder', { default: 'recent' })

const open = ref(false)

const groupByItems = [
  { label: 'Sem agrupamento', value: 'none' as const },
  { label: 'Por dia', value: 'day' as const },
  { label: 'Por hora', value: 'hour' as const },
]

const sortOrderItems = [
  { label: 'Mais recentes', value: 'recent' as const },
  { label: 'Mais antigos', value: 'oldest' as const },
]

const typeItems = cMediaTypeItems

function toggleType(value: number) {
  type.value = type.value.includes(value)
    ? type.value.filter((v) => v !== value)
    : [...type.value, value]
}

function clearFilters() {
  type.value = []
  groupBy.value = 'none'
  sortOrder.value = 'recent'
}

const activeCount = computed(
  () =>
    type.value.length + (groupBy.value !== 'none' ? 1 : 0) + (sortOrder.value !== 'recent' ? 1 : 0),
)
</script>

<template>
  <UPopover v-model:open="open" trigger="click" :content="{ align: 'end', sideOffset: 8 }">
    <UButton icon="i-lucide-filter" variant="subtle" color="neutral" size="xs">
      <template v-if="activeCount > 0" #trailing>
        <UBadge :label="activeCount" size="xs" color="primary" variant="subtle" />
      </template>
    </UButton>

    <template #content>
      <div class="w-72 flex flex-col gap-4 p-3">
        <div class="flex flex-col gap-2.5">
          <div class="flex items-center justify-between gap-3">
            <span class="text-xs text-muted">Agrupamento</span>
            <USelect
              v-model="groupBy"
              :items="groupByItems"
              value-key="value"
              size="xs"
              variant="subtle"
              class="w-36"
            />
          </div>

          <div class="flex items-center justify-between gap-3">
            <span class="text-xs text-muted">Ordenação</span>
            <USelect
              v-model="sortOrder"
              :items="sortOrderItems"
              value-key="value"
              size="xs"
              variant="subtle"
              class="w-36"
            />
          </div>
        </div>

        <USeparator />

        <div class="flex flex-col gap-2">
          <span class="text-xs font-semibold text-highlighted">Tipo</span>

          <div class="flex flex-wrap gap-1.5">
            <UButton
              v-for="item in typeItems"
              :key="item.value"
              :label="item.label"
              :icon="item.icon"
              size="xs"
              :variant="type.includes(item.value) ? 'subtle' : 'ghost'"
              :color="type.includes(item.value) ? 'primary' : 'neutral'"
              :ui="{ base: 'rounded-full' }"
              @click="toggleType(item.value)"
            />
          </div>
        </div>

        <USeparator />

        <UButton
          label="Limpar filtros"
          icon="i-lucide-x"
          variant="ghost"
          color="neutral"
          size="xs"
          block
          @click="clearFilters"
        />
      </div>
    </template>
  </UPopover>
</template>
