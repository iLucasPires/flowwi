<script setup lang="ts">
import type { iInbox } from '@/app/features/inbox/types'
import { usePendingWorkplaceMembers } from '@/app/features/workplace/composables/workplaceMember'

const props = defineProps<{
  item: iInbox
}>()

const { approveMember, approveStatus, rejectMember, rejectStatus } = usePendingWorkplaceMembers()

const pendingRequest = computed(() => {
  const related = props.item.related_member
  if (!related || related.status !== 'pending') return null
  return related
})

defineOptions({ name: 'InboxBodyJoinRequest' })
</script>

<template>
  <div class="flex flex-col gap-4">
    <CTextBlock weight="normal" size="sm" :text="item.message" />

    <div v-if="pendingRequest" class="flex items-center gap-2">
      <UButton
        label="Recusar"
        variant="ghost"
        color="neutral"
        size="xs"
        :loading="rejectStatus === 'pending'"
        @click="rejectMember(pendingRequest.public_id)"
      />
      <UButton
        label="Aprovar"
        icon="i-lucide-check"
        color="primary"
        size="xs"
        :loading="approveStatus === 'pending'"
        @click="approveMember(pendingRequest.public_id)"
      />
    </div>

    <p v-else-if="item.related_member" class="text-xs text-dimmed">Este pedido já foi respondido.</p>
  </div>
</template>
