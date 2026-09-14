import type { iTask } from '@/app/features/task/types'
import { calcInsertPosition, calcReorderPosition } from '@/app/shared/utils/ordering'
import type { DragEndEvent } from '@dnd-kit/vue'
import { isSortable } from '@dnd-kit/vue/sortable'

/**
 * Composable que abstrai a lógica de drag and drop para tarefas.
 * Encapsula o cálculo de reordenação fracionária e cruzamento de status.
 */
export function useTaskDrag(
  tasks: Ref<iTask[]>,
  onReorder: (taskId: string, newPosition: string, status: number) => void,
) {
  function tasksByStatus(status: number) {
    return tasks.value
      .filter((task) => task.status === status)
      .sort((a, b) => (a.position < b.position ? -1 : 1))
  }

  function onDragEnd(event: DragEndEvent) {
    if (event.canceled) return

    const { source, target } = event.operation
    if (!source || !target) return

    // Empty column drop (target is a droppable container, not sortable)
    if (!isSortable(target) && isSortable(source)) {
      const dropStatus = target.data?.status as number | undefined
      const sourceStatus = Number(source.sortable.initialGroup ?? source.sortable.group)
      if (!dropStatus || dropStatus === sourceStatus) return
      const targetTasks = tasksByStatus(dropStatus)

      onReorder(String(source.id), calcInsertPosition(targetTasks, targetTasks.length), dropStatus)
      return
    }

    if (!isSortable(source)) return

    const taskId = String(source.id)
    const initialIndex = Number(source.sortable.initialIndex)
    const finalIndex = Number(source.sortable.index)
    const sourceStatus = Number(source.sortable.initialGroup ?? source.sortable.group)
    const targetStatus = Number(source.sortable.group)

    if (initialIndex === finalIndex && sourceStatus === targetStatus) return

    const targetTasks = tasksByStatus(targetStatus)

    if (sourceStatus === targetStatus) {
      onReorder(taskId, calcReorderPosition(targetTasks, initialIndex, finalIndex), targetStatus)
    } else {
      onReorder(taskId, calcInsertPosition(targetTasks, finalIndex), targetStatus)
    }
  }

  return {
    tasksByStatus,
    onDragEnd,
  }
}
