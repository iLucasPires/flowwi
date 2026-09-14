<script setup lang="ts">
import type { iSub } from '@/app/features/task/types'
const props = defineProps<{
  subs?: iSub[]
}>()

const doneCount = computed(() => (props.subs ?? []).filter((sub) => sub.is_done).length)
</script>

<template>
  <span v-if="subs?.length" class="text-[10.5px] text-muted shrink-0">
    {{ doneCount }}/{{ subs.length }}
  </span>
</template>
