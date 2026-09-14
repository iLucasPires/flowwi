<script setup lang="ts">
import type { tFormOut } from '@/app/features/form/schemas'
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  forms: tFormOut[]
  actions: (form: tFormOut) => DropdownMenuItem[][]
}>()

const emit = defineEmits<{
  open: [form: tFormOut]
  answers: [form: tFormOut]
  'copy-link': [form: tFormOut]
}>()

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('pt-BR')
}
</script>

<template>
  <UTable
    :data="forms"
    :columns="[
      { accessorKey: 'title', header: 'Título' },
      { accessorKey: 'is_published', header: 'Status' },
      { accessorKey: 'created_at', header: 'Criado em' },
      { accessorKey: 'actions', header: '' },
    ]"
    class="w-full"
  >
    <template #title-cell="{ row }">
      <button class="text-left font-medium hover:underline" @click="emit('open', row.original)">
        {{ row.original.title }}
      </button>
    </template>

    <template #is_published-cell="{ row }">
      <UBadge
        :color="row.original.is_published ? 'success' : 'neutral'"
        :label="row.original.is_published ? 'Publicado' : 'Rascunho'"
        size="xs"
        variant="subtle"
      />
    </template>

    <template #created_at-cell="{ row }">
      <CTextBlock size="sm" :text="formatDate(row.original.created_at)" class="text-muted" />
    </template>

    <template #actions-cell="{ row }">
      <UDropdownMenu :items="actions(row.original)" size="xs">
        <UButton icon="i-lucide-more-horizontal" variant="ghost" color="neutral" size="xs" square />
      </UDropdownMenu>
    </template>
  </UTable>
</template>
