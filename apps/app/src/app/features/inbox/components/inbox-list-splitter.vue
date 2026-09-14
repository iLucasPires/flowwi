<script setup lang="ts">
import type { iInbox } from '@/app/features/inbox/types'
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  items: iInbox[]
  allItems: iInbox[]
  selectedId: number | null
  unreadCount: number
}>()

const emit = defineEmits<{
  select: [item: iInbox]
  markAllAsRead: []
  deleteAll: []
}>()

const search = defineModel<string>('search', { default: '' })
const filterType = defineModel<number[]>('filterType', { default: () => [] })

const actionItems = computed<DropdownMenuItem[]>(() => [
  {
    label: 'Marcar todas como lidas',
    icon: 'i-lucide-check-check',
    onSelect: () => emit('markAllAsRead'),
  },
  {
    label: 'Limpar tudo',
    icon: 'i-lucide-trash-2',
    color: 'error',
    onSelect: () => emit('deleteAll'),
  },
])

defineOptions({ name: 'InboxListSplitter' })
</script>

<template>
  <div class="flex size-full flex-col">
    <div class="flex items-center gap-1 p-3 border-b border-default">
      <p class="font-semibold text-highlighted">Inbox</p>
      <UBadge
        v-if="unreadCount > 0"
        :label="unreadCount"
        size="sm"
        color="primary"
        variant="subtle"
      />

      <UDropdownMenu :items="actionItems" :content="{ align: 'start', sideOffset: 8 }" size="sm">
        <UButton icon="i-lucide-ellipsis" color="neutral" variant="ghost" size="sm" />
      </UDropdownMenu>

      <div class="flex-1" />

      <CInboxSearchPopover v-model="search" />
      <CInboxFilterPopover v-model:type="filterType" />
    </div>

    <div class="flex-1 min-h-0 overflow-y-auto p-4">
      <ul v-if="items.length" class="flex flex-col gap-0.5">
        <CInboxCard
          v-for="item in items"
          :key="item.id"
          :item="item"
          :selected="selectedId === item.id"
          @click="emit('select', item)"
        />
      </ul>

      <UEmpty
        v-else-if="allItems.length"
        title="Nenhum resultado"
        description="Nenhuma notificação corresponde ao filtro."
        icon="i-lucide-search-x"
        class="size-full"
        size="sm"
        variant="naked"
      />

      <UEmpty
        v-else
        title="Nenhuma notificação"
        description="Você está em dia!"
        icon="i-lucide-inbox"
        class="size-full"
        size="sm"
        variant="naked"
      />
    </div>
  </div>
</template>
