<script setup lang="ts">
import { useTaskType } from '@/app/features/task/composables/taskType'
import { getTaskTypeMeta } from '@/app/features/task/utils'
const props = defineProps<{
  type: number | null
}>()

const { types } = useTaskType()

const meta = computed(() => getTaskTypeMeta(types.value, props.type))
</script>

<template>
  <span
    v-if="meta"
    class="inline-flex items-center gap-1 text-[10.5px] text-muted bg-elevated rounded px-1.5 py-0.5 shrink-0"
  >
    <span class="size-1.5 rounded-full shrink-0" :style="{ backgroundColor: meta.color }" />
    {{ meta.name }}
  </span>
</template>
