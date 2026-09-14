<script setup lang="ts">
import type { iTask } from '@/app/features/task/types'
import { useSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  task: iTask
  index: number
  group: number | null
}>()

const emit = defineEmits<{
  open: [task: iTask]
}>()

const elementRef = useTemplateRef<HTMLElement>('elementRef')

const { isDragSource } = useSortable({
  id: computed(() => props.task.public_id),
  index: computed(() => props.index),
  group: computed(() => props.group ?? undefined),
  element: elementRef,
})
</script>

<template>
  <li ref="elementRef" class="p-1" :class="{ 'opacity-50': isDragSource }">
    <CTaskKanbanCard :task="task" @open="emit('open', task)" />
  </li>
</template>
