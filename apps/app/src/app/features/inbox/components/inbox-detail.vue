<script setup lang="ts">
import { getInboxTypeMeta } from '@/app/features/inbox/constants'
import type { iInbox } from '@/app/features/inbox/types'
import { formatTimeAgo } from '@vueuse/core'

const props = defineProps<{
  item: iInbox
}>()

const emit = defineEmits<{
  delete: [item: iInbox]
}>()

const typeMeta = computed(() => getInboxTypeMeta(props.item.type))

const senderName = computed(() => {
  const sender = props.item.sender
  if (typeof sender !== 'object' || !sender) return null
  return sender.profile?.full_name || null
})
</script>

<template>
  <div class="size-full flex flex-col overflow-hidden">
    <header class="flex items-start justify-between gap-4 px-6 py-4 shrink-0">
      <div class="min-w-0">
        <div class="flex items-center gap-1.5 mb-1">
          <UIcon :name="typeMeta.icon" :class="typeMeta.color" class="size-3.5 shrink-0" />
          <CTextBlock size="xs" weight="medium" :class="typeMeta.color" :text="typeMeta.label" />
          <template v-if="senderName">
            <span class="text-dimmed text-xs">·</span>
            <CTextBlock size="xs" weight="medium" :text="senderName" />
          </template>
        </div>
        <CTextBlock weight="bold" size="xl" :text="item.title" class="truncate" />
        <CTextBlock weight="normal" size="xs" :text="formatTimeAgo(new Date(item.created_at))" />
      </div>

      <UButton
        icon="i-lucide-trash-2"
        color="neutral"
        variant="ghost"
        size="sm"
        class="shrink-0"
        @click="emit('delete', item)"
      />
    </header>

    <div class="flex-1 min-h-0 overflow-y-auto px-6 py-4">
      <CTextBlock weight="normal" size="sm" :text="item.message" />
    </div>
  </div>
</template>
