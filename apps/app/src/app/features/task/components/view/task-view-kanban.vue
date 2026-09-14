<script setup lang="ts">
import { useTaskDrag } from '@/app/features/task/composables/taskDrag'
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import type { iTask } from '@/app/features/task/types'
import { sortTasksByDeadline, sortTasksByPriority } from '@/app/features/task/utils'
import { DragDropProvider } from '@dnd-kit/vue'

defineOptions({ name: 'TaskKanbanView' })

const props = defineProps<{
  tasks: iTask[]
  loading?: boolean
  groupBy?: 'default' | 'date' | 'priority'
  sortAsc?: boolean
}>()

const emit = defineEmits<{
  open: [task: iTask]
  reorder: [taskId: string, newPosition: string, status: number]
  create: []
}>()

const { statuses } = useTaskStatus()

const statusColumns = computed(() =>
  statuses.value.map((status) => ({
    label: status.name,
    value: status.id,
    icon: status.icon,
    dot: status.color,
  })),
)

const { tasksByStatus, onDragEnd } = useTaskDrag(
  computed(() => props.tasks),
  (taskId, newPosition, status) => emit('reorder', taskId, newPosition, status),
)

function sortColumnTasks(tasks: iTask[]) {
  const groupBy = props.groupBy ?? 'default'

  if (groupBy === 'date') return sortTasksByDeadline(tasks, true)
  if (groupBy === 'priority') return sortTasksByPriority(tasks)
  if (props.sortAsc === false) return sortTasksByDeadline(tasks, true)

  return [...tasks].sort((left, right) => (left.position < right.position ? -1 : 1))
}

const columns = computed(() =>
  statusColumns.value.map((column) => ({
    key: column.value,
    label: column.label,
    dot: column.dot,
    status: column.value,
    tasks: sortColumnTasks(tasksByStatus(column.value)),
  })),
)
</script>

<template>
  <DragDropProvider @drag-end="onDragEnd">
    <div class="flex-1 flex gap-5 overflow-x-auto overflow-y-hidden pb-1">
      <CTaskKanbanColumn
        v-for="column in columns"
        :key="column.key"
        :column-key="String(column.key)"
        :status="column.status"
        :label="column.label"
        :dot="column.dot"
        :tasks="column.tasks"
        @open="(task) => emit('open', task)"
      />
    </div>
  </DragDropProvider>
</template>
