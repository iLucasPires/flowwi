<script setup lang="ts">
import { API_WEBHOOK_URLS, apiFetch } from '@/app/core/clients/api'
import type { iWebhook } from '@/app/features/workplace/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import type { TableColumn } from '@nuxt/ui'
import { upperFirst } from 'scule'
import { getPaginationRowModel } from '@tanstack/table-core'
import type { Row } from '@tanstack/table-core'
import { useQuery, useQueryClient } from '@tanstack/vue-query'

const props = defineProps<{
  workplaceId: number
}>()

const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const USwitch = resolveComponent('USwitch')

const toast = useToast()
const queryClient = useQueryClient()
const table = useTemplateRef('table')

const search = defineModel<string>('search')
const isActive = defineModel<boolean | undefined>('isActive')
const columnVisibility = ref()
const pagination = ref({ pageIndex: 0, pageSize: 15 })

const page = computed(() => pagination.value.pageIndex + 1)
const pageSize = computed(() => pagination.value.pageSize)

const { data, isLoading: loading } = useQuery({
  queryKey: computed(() => [
    'webhooks',
    props.workplaceId,
    page.value,
    pageSize.value,
    search.value ?? '',
    isActive.value ?? null,
  ]),
  queryFn: () =>
    apiFetch<iPaginationNumber<iWebhook>>(API_WEBHOOK_URLS.LIST, {
      query: {
        page: page.value,
        page_size: pageSize.value,
        search: (search.value ?? '').trim() || undefined,
        is_active: isActive.value ?? undefined,
      },
    }),
  enabled: computed(() => !!props.workplaceId),
})

const endpoints = computed(() => data.value?.results ?? [])
const total = computed(() => data.value?.count ?? 0)

watch(
  () => [search.value, isActive.value],
  () => {
    pagination.value.pageIndex = 0
  },
)

async function toggleWebhook(ep: iWebhook) {
  await apiFetch(`${API_WEBHOOK_URLS.LIST}/${ep.id}`, {
    method: 'PATCH',
    body: { is_active: !ep.is_active },
  })
  await queryClient.invalidateQueries({ queryKey: ['webhooks', props.workplaceId] })
}

async function removeWebhook(id: number) {
  await apiFetch(`${API_WEBHOOK_URLS.LIST}/${id}`, { method: 'DELETE' })
  toast.add({ title: 'Webhook removido', color: 'success' })
  await queryClient.invalidateQueries({ queryKey: ['webhooks', props.workplaceId] })
}

function getRowItems(row: Row<iWebhook>) {
  return [
    { type: 'label', label: 'Ações' },
    {
      label: 'Remover webhook',
      icon: 'i-lucide-trash',
      color: 'error',
      onSelect() {
        removeWebhook(row.original.id)
      },
    },
  ]
}

const columns: TableColumn<iWebhook>[] = [
  {
    accessorKey: 'url',
    header: 'URL',
    cell: ({ row }) => h('span', { class: 'font-mono text-xs' }, row.original.url),
  },
  {
    accessorKey: 'events',
    header: 'Eventos',
    cell: ({ row }) =>
      h(
        'div',
        { class: 'flex gap-1 flex-wrap' },
        row.original.events.map((e) =>
          h(UBadge, { size: 'xs', variant: 'subtle', color: 'neutral' }, () => e),
        ),
      ),
  },
  {
    accessorKey: 'is_active',
    header: 'Status',
    cell: ({ row }) =>
      h(USwitch, {
        modelValue: row.original.is_active,
        'onUpdate:modelValue': () => toggleWebhook(row.original),
        size: 'sm',
      }),
  },
  {
    accessorKey: 'created_at',
    header: 'Criado em',
    cell: ({ row }) =>
      row.original.created_at
        ? h(
            'span',
            { class: 'text-xs text-dimmed tabular-nums' },
            new Date(row.original.created_at).toLocaleDateString('pt-BR', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
            }),
          )
        : '—',
  },
  {
    id: 'actions',
    cell: ({ row }) =>
      h(
        'div',
        { class: 'flex items-center justify-end' },
        h(UDropdownMenu, { content: { align: 'end' }, items: getRowItems(row) }, () =>
          h(UButton, {
            icon: 'i-lucide-more-horizontal',
            color: 'neutral',
            variant: 'ghost',
          }),
        ),
      ),
  },
]
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-wrap items-center justify-end gap-1.5">
      <UDropdownMenu
        :items="
          table?.tableApi
            ?.getAllColumns()
            ?.filter((column) => column.getCanHide())
            ?.map((column) => ({
              label: upperFirst(column.id),
              type: 'checkbox' as const,
              checked: column.getIsVisible(),
              onUpdateChecked(checked: boolean) {
                table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
              },
              onSelect(e?: Event) {
                e?.preventDefault()
              },
            }))
        "
        :content="{ align: 'end' }"
      >
        <UButton
          label="Colunas"
          color="neutral"
          variant="ghost"
          trailing-icon="i-lucide-filter"
          size="sm"
        />
      </UDropdownMenu>
    </div>

    <div class="rounded-lg overflow-hidden bg-elevated/40">
      <UTable
        ref="table"
        v-model:column-visibility="columnVisibility"
        v-model:pagination="pagination"
        :pagination-options="{
          getPaginationRowModel: getPaginationRowModel(),
          manualPagination: true,
          rowCount: total,
        }"
        :data="endpoints"
        :columns="columns"
        :loading="loading"
        class="w-full"
        :ui="{
          th: 'py-2.5 px-4 font-semibold text-[11px] uppercase tracking-wider text-dimmed bg-accented/30 focus:outline-none',
          td: 'py-3 px-4 text-sm align-middle',
          tr: 'hover:bg-accented/40 transition-colors',
        }"
      />
    </div>

    <div class="flex items-center justify-between gap-3 pt-2">
      <div class="text-xs text-dimmed font-medium">Total de {{ total }} webhooks.</div>
      <UPagination
        v-if="total > pagination.pageSize"
        :default-page="(table?.tableApi?.getState()?.pagination?.pageIndex || 0) + 1"
        :items-per-page="table?.tableApi?.getState()?.pagination?.pageSize || 15"
        :total="total"
        variant="ghost"
        color="neutral"
        size="sm"
        @update:page="(p: number) => table?.tableApi?.setPageIndex(p - 1)"
      />
    </div>
  </div>
</template>
