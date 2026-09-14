<script setup lang="ts">
import { formatDeadline, isTaskOverdue } from '@/app/features/task/utils'
const props = defineProps<{
  deadline: string | null
}>()

const deadlineLabel = computed(() => formatDeadline(props.deadline))
const isOverdue = computed(() => isTaskOverdue(props.deadline))
</script>

<template>
  <span
    v-if="deadline"
    class="text-[10.5px] tabular-nums shrink-0"
    :class="isOverdue ? 'text-red-400' : 'text-muted'"
  >
    {{ deadlineLabel }}
  </span>
</template>
