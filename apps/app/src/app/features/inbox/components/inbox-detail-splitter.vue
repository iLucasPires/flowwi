<script setup lang="ts">
import type { iInbox } from '@/app/features/inbox/types'
defineProps<{
  item: iInbox | null
}>()

const emit = defineEmits<{
  delete: [item: iInbox]
}>()

defineOptions({ name: 'InboxDetailSplitter' })
</script>

<template>
  <div class="size-full flex items-center justify-center p-4">
    <CInboxDetail v-if="item" :item="item" @delete="emit('delete', $event)" />

    <UEmpty
      v-else
      class="size-full"
      title="Selecione uma notificação"
      description="Escolha um item da lista para ver os detalhes."
      icon="i-lucide-mail"
      size="sm"
      variant="naked"
    />
  </div>
</template>
