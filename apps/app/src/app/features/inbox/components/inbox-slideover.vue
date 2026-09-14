<script setup lang="ts">
import { useInbox } from '@/app/features/inbox/composables/inbox'
import { getInboxTypeMeta } from '@/app/features/inbox/constants'
const open = ref(false)

const { items, unreadCount, markAsRead, markAllAsRead, deleteAll } = useInbox()

const decoratedItems = computed(() =>
  items.value.map((item) => ({ ...item, typeIcon: getInboxTypeMeta(item.type).icon })),
)

function handleMarkAllAsRead(event: MouseEvent) {
  void event
  void markAllAsRead()
}

function handleDeleteAll(event: MouseEvent) {
  void event
  void deleteAll()
}
</script>

<template>
  <USlideover v-model:open="open" title="Inbox" side="right">
    <UButton icon="i-lucide-inbox" variant="ghost" color="neutral" @click="open = true">
      <template v-if="unreadCount > 0" #trailing>
        <UBadge :label="unreadCount" size="xs" />
      </template>
    </UButton>

    <template #close>
      <div class="flex gap-1 justify-end w-full">
        <UTooltip text="Marcar todas como lidas">
          <UButton
            size="sm"
            variant="ghost"
            color="neutral"
            icon="i-lucide-check-check"
            @click="handleMarkAllAsRead"
          />
        </UTooltip>
        <UTooltip text="Limpar tudo">
          <UButton
            size="sm"
            variant="ghost"
            color="neutral"
            icon="i-lucide-trash-2"
            @click="handleDeleteAll"
          />
        </UTooltip>
        <UButton
          size="sm"
          variant="ghost"
          color="neutral"
          icon="i-lucide-x"
          @click="open = false"
        />
      </div>
    </template>

    <template #body>
      <UEmpty
        v-if="items.length === 0"
        title="Nenhuma notificação por aqui"
        icon="i-lucide-inbox"
        variant="subtle"
        size="sm"
      />

      <div v-else class="flex flex-col gap-0.5">
        <div
          v-for="item in decoratedItems"
          :key="item.id"
          class="group flex items-start gap-3 rounded-lg px-3 py-2.5 cursor-pointer transition-colors hover:bg-elevated/50"
          :class="{ 'opacity-50': item.is_read }"
          @click="!item.is_read && markAsRead(item.id)"
        >
          <UAvatar :icon="item.typeIcon" :alt="item.title" size="sm" />

          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <span v-if="!item.is_read" class="size-1.5 rounded-full bg-primary shrink-0" />
              <span class="text-sm font-medium truncate">{{ item.title }}</span>
            </div>
            <p class="text-xs text-dimmed mt-0.5 line-clamp-2">
              {{ item.message }}
            </p>
            <span class="text-[11px] text-dimmed/60 mt-1 block">
              {{
                new Date(item.created_at).toLocaleString('pt-BR', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              }}
            </span>
          </div>
        </div>
      </div>
    </template>
  </USlideover>
</template>
