<script setup lang="ts">
import { useWorkplaceMember } from '@/app/features/workplace/composables/workplaceMember'
const model = defineModel<number[]>({ default: () => [] })

defineProps<{
  size?: 'xs' | 'sm' | 'md' | 'lg'
  variant?: 'subtle' | 'ghost' | 'outline'
  class?: string
}>()

const { members } = useWorkplaceMember()

const memberItems = computed(() =>
  members.value.map((m) => ({
    label: m.profile?.full_name,
    value: m.id,
    member: m,
  })),
)

const selectedMembers = computed(() =>
  model.value.map((id) => members.value.find((m) => m.id === id)).filter((m) => !!m),
)
</script>

<template>
  <USelectMenu
    v-model="model"
    :items="memberItems"
    value-key="value"
    multiple
    :size="size ?? 'sm'"
    variant="ghost"
    color="neutral"
    placeholder="Membro"
    :ui="{
      content: 'w-64',
      itemLabel: 'whitespace-nowrap truncate',
    }"
  >
    <template #leading>
      <UAvatarGroup v-if="selectedMembers.length" size="3xs" :max="3">
        <CMemberAvatar v-for="m in selectedMembers" :key="m.id" :member="m" />
      </UAvatarGroup>
      <UIcon v-else name="i-lucide-user" class="size-4 shrink-0 text-neutral-400" />
    </template>
    <template #item="{ item }">
      <CMemberAvatar :member="item.member" size="3xs" class="shrink-0" />
      <span v-text="item.label" class="truncate whitespace-nowrap" />
    </template>
  </USelectMenu>
</template>
