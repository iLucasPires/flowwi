<script setup lang="ts">
import { useTask } from '@/app/features/task/composables/task'
import { cTaskPriorityItems } from '@/app/features/task/constants'
import type { iTask } from '@/app/features/task/types'
const props = defineProps<{ task: iTask }>()

const emit = defineEmits<{
  open: [task: iTask]
}>()

const { deleteTask } = useTask()

const priorityMeta = computed(() => cTaskPriorityItems.find((p) => p.value === props.task.priority))

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
    <UCard
      variant="subtle"
      @click="handleClick"
      :ui="{
        header: 'flex justify-betwee',
      }"
    >
      <template #header>
        <span class="flex-1 min-w-0 text-[13px] font-medium leading-snug text-default">
          {{ task.title }}
        </span>

        <UAvatar
          v-if="task.assignees?.[0]"
          size="2xs"
          :src="task.assignees[0].profile?.photo || ''"
          :alt="task.assignees[0].profile?.full_name"
          icon="i-lucide-user"
        />
      </template>

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
    </UCard>
  </UContextMenu>
</template>
