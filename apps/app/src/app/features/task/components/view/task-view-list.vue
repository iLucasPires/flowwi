<script setup lang="ts">
import { useTaskDrag } from '@/app/features/task/composables/taskDrag'
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import type { iTask } from '@/app/features/task/types'
import { sortTasksByDeadline, sortTasksByPriority } from '@/app/features/task/utils'
import { DragDropProvider } from '@dnd-kit/vue'

defineOptions({ name: 'TaskListView' })

const props = defineProps<{
  tasks: iTask[]
  loading?: boolean
  groupBy?: 'default' | 'date' | 'priority'
  sortAsc?: boolean
}>()

const emit = defineEmits<{
  open: [task: iTask]
  reorder: [taskId: string, newPosition: string, status: number]
}>()

const { statuses } = useTaskStatus()

const { tasksByStatus, onDragEnd } = useTaskDrag(
  computed(() => props.tasks),
  (taskId, newPosition, status) => emit('reorder', taskId, newPosition, status),
)

function sortGroupTasks(tasks: iTask[]) {
  const groupBy = props.groupBy ?? 'default'

  if (groupBy === 'date') return sortTasksByDeadline(tasks, true)
  if (groupBy === 'priority') return sortTasksByPriority(tasks)
  if (props.sortAsc === false) return sortTasksByDeadline(tasks, true)

  return tasks
}

const columns = computed(() =>
  statuses.value
    .map((status) => ({
      key: status.id,
      label: status.name,
      dot: status.color,
      tasks: sortGroupTasks(tasksByStatus(status.id)),
    }))
    .filter((column) => column.tasks.length > 0),
)
</script>

<template>
  <div class="flex-1 overflow-y-auto min-w-0">
    <DragDropProvider @drag-end="onDragEnd">
      <template v-if="tasks.length">
        <div v-for="column in columns" :key="column.key" class="mb-1.5">
          <div class="flex items-center gap-2 px-1 pt-3.5 pb-1.5">
            <span class="size-2 rounded-full shrink-0" :style="{ background: column.dot }" />
            <span class="text-xs font-medium text-default">{{ column.label }}</span>
            <span class="text-xs text-muted">{{ column.tasks.length }}</span>
          </div>

          <CTaskListDropGroup
            :status="column.key"
            :tasks="column.tasks"
            @open="emit('open', $event)"
          />
        </div>
      </template>

      <div v-else class="flex items-center justify-center py-20">
        <UEmpty
          icon="i-lucide-list-checks"
          title="Nenhuma tarefa encontrada"
          variant="subtle"
          size="sm"
        />
      </div>
    </DragDropProvider>
  </div>
</template>
