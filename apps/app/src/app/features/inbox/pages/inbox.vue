<script setup lang="ts">
import { useInbox } from '@/app/features/inbox/composables/inbox'
import type { iInbox } from '@/app/features/inbox/types'
defineOptions({ name: 'InboxPage' })

const { items, unreadCount, markAsRead, markAllAsRead, deleteNotification, deleteAll } = useInbox()

const search = ref('')
const selectedItem = ref<iInbox | null>(null)
const filterType = ref<number[]>([])

const filteredItems = computed(() => {
  let list = items.value

  if (search.value) {
    const q = search.value.toLowerCase()

    list = list.filter(
      (i) => i.title.toLowerCase().includes(q) || i.message.toLowerCase().includes(q),
    )
  }

  if (filterType.value.length) {
    list = list.filter((i) => filterType.value.includes(i.type))
  }

  return list
})

async function selectItem(item: iInbox) {
  selectedItem.value = item

  if (!item.is_read) {
    await markAsRead(item.id)
  }
}

async function handleDelete(item: iInbox) {
  await deleteNotification(item.id)

  if (selectedItem.value?.id === item.id) {
    selectedItem.value = null
  }
}

async function handleDeleteAll() {
  await deleteAll()
  selectedItem.value = null
}

async function handleMarkAllAsRead() {
  await markAllAsRead()
}

const splitterItems = [
  {
    id: 'list',
    slot: 'list',
    defaultSize: 32,
    minSize: 22,
    maxSize: 45,
  },
  {
    id: 'detail',
    slot: 'detail',
    minSize: 30,
    maxSize: 100,
  },
]
</script>

<template>
  <div class="flex flex-1 overflow-hidden">
    <USplitter
      id="inbox"
      class="rounded-lg border border-default overflow-hidden bg-elevated/50"
      :items="splitterItems"
    >
      <template #list>
        <CInboxListSplitter
          v-model:search="search"
          v-model:filter-type="filterType"
          :items="filteredItems"
          :all-items="items"
          :selected-id="selectedItem?.id ?? null"
          :unread-count="unreadCount"
          @select="selectItem"
          @mark-all-as-read="handleMarkAllAsRead"
          @delete-all="handleDeleteAll"
        />
      </template>

      <template #detail>
        <CInboxDetailSplitter :item="selectedItem" @delete="handleDelete" />
      </template>
    </USplitter>
  </div>
</template>
