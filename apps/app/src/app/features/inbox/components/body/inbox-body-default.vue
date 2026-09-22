<script setup lang="ts">
import type { iInbox } from '@/app/features/inbox/types'

defineProps<{
  item: iInbox
}>()

defineOptions({ name: 'InboxBodyDefault' })
</script>

<template>
  <CTextBlock weight="normal" size="sm" :text="item.message" />
</template>
