<script setup lang="ts">
import { useUser } from '@/app/features/user/composables/user'
import { useWorkplaceMember } from '@/app/features/workplace/composables/workplaceMember'
const props = defineProps<{
  userId: number | null
  /** Avatar/badge only, no name — for tight spaces like a sticky card footer. */
  compact?: boolean
}>()

const { user } = useUser()
const { members } = useWorkplaceMember()

const isMe = computed(() => props.userId != null && props.userId === user.value?.id)

const owner = computed(() => members.value.find((m) => m.user === props.userId))

const displayName = computed(() => {
  const profile = owner.value?.profile
  return profile?.full_name || profile?.username || 'Desconhecido'
})

const tooltipText = computed(() =>
  isMe.value ? 'Criado por você' : `Criado por ${displayName.value}`,
)

defineOptions({ name: 'MemberOwnerIndicator' })
</script>

<template>
  <UTooltip :text="tooltipText">
    <div class="flex items-center gap-1.5 shrink-0">
      <UAvatar :src="owner?.profile?.photo || ''" :alt="displayName" size="3xs" />
      <span
        v-if="!compact"
        class="text-xs text-dimmed truncate max-w-24"
        v-text="isMe ? 'Você' : displayName"
      />
    </div>
  </UTooltip>
</template>
