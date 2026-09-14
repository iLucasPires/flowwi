<script setup lang="ts">
import type { TaskStatusCategory, iTaskStatus } from '@/app/features/task/types'
import { useSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  status: iTaskStatus
  index: number
}>()

const emit = defineEmits<{
  edit: [status: iTaskStatus]
  delete: [status: iTaskStatus]
}>()

const categoryLabels: Record<TaskStatusCategory, string> = {
  todo: 'A fazer',
  in_progress: 'Em progresso',
  done: 'Concluído',
  cancelled: 'Cancelado',
}

const elementRef = useTemplateRef<HTMLElement>('elementRef')
const handleRef = useTemplateRef<HTMLElement>('handleRef')

const { isDragSource } = useSortable({
  id: computed(() => props.status.id),
  index: computed(() => props.index),
  element: elementRef,
  handle: handleRef,
})
</script>

<template>
  <li
    ref="elementRef"
    class="flex items-center gap-2 rounded-lg px-2 py-2 hover:bg-accented/40"
    :class="{ 'opacity-50': isDragSource }"
  >
    <span ref="handleRef" class="cursor-grab active:cursor-grabbing text-dimmed">
      <UIcon name="i-lucide-grip-vertical" class="size-4" />
    </span>

    <CIconOrEmoji
      :value="status.icon"
      fallback="i-lucide-circle"
      class="size-4 shrink-0 text-sm"
      :style="{ color: status.color }"
    />

    <span class="flex-1 text-sm font-medium">{{ status.name }}</span>

    <UBadge :label="categoryLabels[status.category]" size="sm" variant="subtle" color="neutral" />

    <UButton
      icon="i-lucide-pencil"
      size="xs"
      variant="ghost"
      color="neutral"
      @click="emit('edit', status)"
    />
    <UButton
      icon="i-lucide-trash-2"
      size="xs"
      variant="ghost"
      color="error"
      @click="emit('delete', status)"
    />
  </li>
</template>
