<script setup lang="ts">
import type { iTask } from '@/app/features/task/types'
import { useDroppable } from '@dnd-kit/vue'

const props = defineProps<{
  status: number
  tasks: iTask[]
}>()

const emit = defineEmits<{
  open: [task: iTask]
}>()

const groupRef = useTemplateRef<HTMLElement>('groupRef')

useDroppable({
  id: computed(() => `list-${props.status}`),
  element: groupRef,
  data: computed(() => ({ status: props.status })),
})
</script>

<template>
  <div ref="groupRef" class="space-y-px rounded-lg">
    <CTaskListSortableRow
      v-for="(task, index) in tasks"
      :key="task.public_id"
      :task="task"
      :index="index"
      :group="status"
      @select="emit('open', task)"
    />
  </div>
</template>
