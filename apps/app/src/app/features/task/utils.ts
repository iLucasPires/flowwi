import { cTaskPriorityItems } from '@/app/features/task/constants'
import type { TaskStatusCategory, iTask, iTaskStatus, iTaskType } from '@/app/features/task/types'
export function getTaskPriorityMeta(value: string) {
  return cTaskPriorityItems.find((p) => p.value === value)
}

export function getTaskTypeMeta(types: iTaskType[], id: number | null) {
  return types.find((t) => t.id === id)
}

export function getTaskStatusMeta(statuses: iTaskStatus[], id: number | null) {
  return statuses.find((s) => s.id === id)
}

export function isDoneOrCancelledCategory(category: TaskStatusCategory | undefined) {
  return category === 'done' || category === 'cancelled'
}

export function formatDeadline(d: string | null): string | null {
  if (!d) return null
  const date = new Date(d + 'T00:00:00')
  if (isNaN(date.getTime())) return null
  return date.toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' })
}

export function isTaskOverdue(d: string | null): boolean {
  if (!d) return false
  const date = new Date(d + 'T00:00:00')
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date < today
}

export function sortTasksByDeadline(tasks: iTask[], ascending: boolean) {
  return [...tasks].sort((left, right) => {
    const leftDeadline = left.deadline ?? ''
    const rightDeadline = right.deadline ?? ''

    if (!leftDeadline && !rightDeadline) return left.position < right.position ? -1 : 1
    if (!leftDeadline) return 1
    if (!rightDeadline) return -1

    const deadlineCompare = ascending
      ? leftDeadline.localeCompare(rightDeadline)
      : rightDeadline.localeCompare(leftDeadline)

    if (deadlineCompare !== 0) return deadlineCompare
    return left.position < right.position ? -1 : 1
  })
}

const PRIORITY_ORDER = { urgent: 0, high: 1, medium: 2, low: 3 } as const

export function sortTasksByPriority(tasks: iTask[]) {
  return [...tasks].sort((left, right) => {
    const priorityCompare = PRIORITY_ORDER[left.priority] - PRIORITY_ORDER[right.priority]
    if (priorityCompare !== 0) return priorityCompare
    return left.position < right.position ? -1 : 1
  })
}
