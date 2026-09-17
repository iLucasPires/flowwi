<script setup lang="ts">
import { usePendingWorkplaceMembers } from '@/app/features/workplace/composables/workplaceMember'

const { pendingMembers, isLoading, approveMember, approveStatus, rejectMember, rejectStatus } =
  usePendingWorkplaceMembers()

defineOptions({ name: 'MemberPendingList' })
</script>

<template>
  <UCard
    v-if="isLoading || pendingMembers.length"
    :ui="{ body: 'flex flex-col gap-1 p-2 sm:p-2' }"
  >
    <template #header>
      <div class="flex items-center gap-2">
        <UIcon name="i-lucide-user-round-plus" class="size-4 text-dimmed" />
        <h3 class="text-sm font-semibold">Pedidos de entrada</h3>
        <UBadge :label="String(pendingMembers.length)" variant="subtle" color="neutral" size="sm" />
      </div>
    </template>

    <div
      v-for="member in pendingMembers"
      :key="member.public_id"
      class="flex items-center gap-3 rounded-lg px-2 py-1.5 hover:bg-accented/40"
    >
      <CMemberAvatar :member="member" size="sm" />
      <div class="flex-1 min-w-0">
        <p class="font-medium text-default text-sm truncate">
          {{ member.profile?.full_name ?? '—' }}
        </p>
        <p class="text-xs text-dimmed truncate">{{ member.profile?.email ?? '' }}</p>
      </div>

      <UButton
        label="Recusar"
        variant="ghost"
        color="neutral"
        size="xs"
        :loading="rejectStatus === 'pending'"
        @click="rejectMember(member.public_id)"
      />
      <UButton
        label="Aprovar"
        icon="i-lucide-check"
        color="primary"
        size="xs"
        :loading="approveStatus === 'pending'"
        @click="approveMember(member.public_id)"
      />
    </div>
  </UCard>
</template>
