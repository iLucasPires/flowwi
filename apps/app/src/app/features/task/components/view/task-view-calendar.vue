<script setup lang="ts">
import type { TaskPriority, iTask } from '@/app/features/task/types'
import type { iCalendarEvent } from '@/app/shared/types/calendar'

defineOptions({ name: 'TaskCalendarView' })

const props = defineProps<{
  tasks: iTask[]
}>()

const emit = defineEmits<{
  open: [task: { id: number }]
}>()

const priorityColor: Record<TaskPriority, string> = {
  urgent: '#ef4444',
  high: '#f97316',
  medium: '#3b82f6',
  low: '#6b7280',
}

const events = computed<iCalendarEvent[]>(() =>
  props.tasks
    .filter((t) => t.deadline)
    .map((t) => ({
      id: `task-${t.id}`,
      title: t.title,
      date: t.deadline!,
      color: priorityColor[t.priority] ?? '#6b7280',
      type: 'task',
      meta: { id: t.id },
    })),
)

function onSelect(event: iCalendarEvent) {
  const id = event.meta?.id
  if (typeof id === 'number') emit('open', { id })
}
</script>

<template>
  <CCalendar :events="events" embedded @select="onSelect" />
</template>
