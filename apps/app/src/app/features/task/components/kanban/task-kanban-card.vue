<script setup lang="ts">
import { useTask } from '@/app/features/task/composables/task'
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import { cTaskPriorityItems } from '@/app/features/task/constants'
import type { iTask } from '@/app/features/task/types'
import { getTaskStatusMeta } from '@/app/features/task/utils'
const props = defineProps<{ task: iTask }>()

const emit = defineEmits<{
  open: [task: iTask]
}>()

const { deleteTask } = useTask()
const { statuses } = useTaskStatus()

const priorityMeta = computed(() => cTaskPriorityItems.find((p) => p.value === props.task.priority))
const statusMeta = computed(() => getTaskStatusMeta(statuses.value, props.task.status))

const createdAtLabel = computed(() =>
  new Date(props.task.created_at).toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' }),
)

const contextMenuItems = computed(() => [
  [
    {
      label: 'Arquivar',
      icon: 'i-lucide-archive',
      color: 'neutral' as const,
      onSelect: () => {},
    },
    {
      label: 'Apagar',
      icon: 'i-lucide-trash-2',
      color: 'error' as const,
      onSelect: () => deleteTask(props.task.public_id),
    },
  ],
])

const handleClick = () => {
  emit('open', props.task)
}
</script>

<template>
  <UContextMenu :items="contextMenuItems" size="sm">
    <UCard variant="subtle" class="group" @click="handleClick">
      <div class="flex flex-col gap-3">
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-center gap-1.5 min-w-0">
            <CIconOrEmoji
              :value="statusMeta?.icon || 'i-lucide-circle'"
              class="size-3.5 shrink-0 text-sm"
              :style="{ color: statusMeta?.color ?? '#a3a3a3' }"
            />
            <span class="min-w-0 text-[13px] font-medium leading-snug text-default truncate">
              {{ task.title }}
            </span>
          </div>

          <CMemberAvatar
            v-if="task.assignees?.[0]"
            :member="task.assignees[0]"
            size="2xs"
            class="shrink-0"
          />
        </div>

        <div class="flex items-center gap-1.5 flex-wrap min-w-0">
          <UIcon
            class="size-2.5 shrink-0 text-muted"
            :class="priorityMeta?.color"
            :name="priorityMeta?.icon ?? 'i-lucide-minus'"
          />

          <CTaskTypeBadge :type="task.type" />
          <CTaskSubtaskCountChip :subs="task.subs" />
          <CTaskDeadlineChip :deadline="task.deadline" class="ml-auto" />
        </div>

        <div class="flex items-center justify-between gap-2">
          <span class="text-[10.5px] text-dimmed">Criado em {{ createdAtLabel }}</span>

          <UDropdownMenu :items="contextMenuItems" :content="{ align: 'end' }">
            <UButton
              icon="i-lucide-ellipsis"
              size="2xs"
              variant="ghost"
              color="neutral"
              class="opacity-0 group-hover:opacity-100 transition-opacity"
              @click.stop
            />
          </UDropdownMenu>
        </div>
      </div>
    </UCard>
  </UContextMenu>
</template>
