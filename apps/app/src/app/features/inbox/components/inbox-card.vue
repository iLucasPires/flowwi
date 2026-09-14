<script setup lang="ts">
import { getInboxTypeMeta } from '@/app/features/inbox/constants'
import type { iInbox } from '@/app/features/inbox/types'
import { formatTimeAgo } from '@vueuse/core'

const props = defineProps<{
  item: iInbox
  selected?: boolean
}>()

const typeMeta = computed(() => getInboxTypeMeta(props.item.type))
</script>

<template>
  <li
    class="flex items-start gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors"
    :class="[selected ? 'bg-elevated' : 'hover:bg-elevated/50', item.is_read ? 'opacity-60' : '']"
  >
    <div class="relative shrink-0">
      <CMemberAvatar :member="item.sender" />
      <UIcon
        :name="typeMeta.icon"
        :class="typeMeta.color"
        class="absolute -bottom-0.5 -right-0.5 size-3.5 rounded-full bg-default ring-2 ring-default p-0.5"
      />
    </div>

    <div class="min-w-0 flex-1">
      <div class="flex items-center gap-2">
        <span v-if="!item.is_read" class="size-1.5 rounded-full bg-primary shrink-0" />
        <CTextBlock size="sm" weight="medium" :text="item.title" class="truncate" />
      </div>
      <CTextBlock size="xs" :text="item.message" class="truncate" />
    </div>

    <CTextBlock size="xs" class="shrink-0 pl-2" :text="formatTimeAgo(new Date(item.created_at))" />
  </li>
</template>
