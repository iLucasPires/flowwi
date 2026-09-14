<script setup lang="ts">
import { useTask } from '@/app/features/task/composables/task'
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import { cTaskPriorityItems } from '@/app/features/task/constants'
import type { iTask } from '@/app/features/task/types'
import { getTaskStatusMeta, isDoneOrCancelledCategory } from '@/app/features/task/utils'
import { useSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  task: iTask
  index: number
  group: number
}>()

const { deleteTask } = useTask()
const { statuses } = useTaskStatus()

const elementRef = useTemplateRef<HTMLElement>('elementRef')

const { isDragSource } = useSortable({
  id: computed(() => props.task.public_id),
  index: computed(() => props.index),
  group: computed(() => props.group),
  element: elementRef,
})

const priorityMeta = computed(() => cTaskPriorityItems.find((p) => p.value === props.task.priority))

const isDoneOrCancelled = computed(() => {
  const statusMeta = getTaskStatusMeta(statuses.value, props.task.status)
  return isDoneOrCancelledCategory(statusMeta?.category)
})

const contextMenuItems = computed(() => [
  [
    {
      label: 'Apagar',
      icon: 'i-lucide-trash-2',
      color: 'error' as const,
      onSelect: () => deleteTask(props.task.public_id),
    },
  ],
])
</script>

<template>
  <UContextMenu :items="contextMenuItems" size="sm">
    <div
      ref="elementRef"
      class="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-neutral-200/60 dark:hover:bg-neutral-800/60 cursor-grab active:cursor-grabbing transition-colors"
      :class="{ 'opacity-50': isDragSource }"
    >
      <UIcon
        :name="priorityMeta?.icon ?? 'i-lucide-minus'"
        class="size-3.5 shrink-0"
        :class="priorityMeta?.color"
      />
      <span
        class="flex-1 text-sm text-neutral-800 dark:text-neutral-200 truncate min-w-0"
        :class="isDoneOrCancelled ? 'line-through text-neutral-500' : ''"
      >
        {{ task.title }}
      </span>

      <CTaskTypeBadge :type="task.type" />
      <CTaskSubtaskCountChip :subs="task.subs" />
      <CTaskDeadlineChip :deadline="task.deadline" class="w-20" />

      <UAvatarGroup v-if="task.assignees?.length" size="3xs" :max="1">
        <UAvatar
          v-for="assignee in task.assignees"
          :key="assignee.id"
          :src="assignee.profile?.photo || ''"
          :alt="assignee.profile?.full_name"
          icon="i-lucide-user"
        />
      </UAvatarGroup>
    </div>
  </UContextMenu>
</template>
