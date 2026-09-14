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
    avatar: {
      src: m.profile?.photo ?? '',
      alt: m.profile?.full_name ?? '',
    },
  })),
)
</script>

<template>
  <USelectMenu
    v-model="model"
    :items="memberItems"
    value-key="value"
    multiple
    icon="i-lucide-user"
    :size="size ?? 'sm'"
    variant="ghost"
    color="neutral"
    placeholder="Membro"
    :ui="{
      content: 'w-64',
      itemLabel: 'whitespace-nowrap truncate',
    }"
  >
    <template #item="{ item }">
      <UAvatar
        v-if="item.avatar?.src"
        :src="item.avatar.src"
        :alt="item.avatar.alt"
        size="3xs"
        class="shrink-0"
      />
      <UIcon v-else name="i-lucide-user" class="size-4 shrink-0 text-neutral-400" />
      <span v-text="item.label" class="truncate whitespace-nowrap" />
    </template>
  </USelectMenu>
</template>
