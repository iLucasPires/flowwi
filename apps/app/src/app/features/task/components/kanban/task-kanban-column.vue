<script setup lang="ts">
import type { iTask } from '@/app/features/task/types'
import { useDroppable } from '@dnd-kit/vue'

const props = defineProps<{
  columnKey: string
  status: number | null
  label: string
  dot: string
  tasks: iTask[]
}>()

const emit = defineEmits<{
  open: [task: iTask]
}>()

const columnRef = useTemplateRef<HTMLElement>('columnRef')
const dotIsHex = computed(() => props.dot?.startsWith('#'))

useDroppable({
  id: computed(() => `column-${props.columnKey}`),
  element: columnRef,
  data: computed(() => ({ status: props.status })),
})
</script>

<template>
  <div ref="columnRef" class="w-[320px] shrink-0 flex flex-col overflow-hidden">
    <header class="flex items-center justify-between gap-2 px-1 pb-3 border-b border-default">
      <div class="flex items-center gap-2">
        <span
          class="size-2 rounded-full shrink-0"
          :class="!dotIsHex ? dot : undefined"
          :style="dotIsHex ? { backgroundColor: dot } : undefined"
        />
        <span class="text-xs font-medium text-default">{{ label }}</span>
      </div>
      <span class="text-xs text-muted tabular-nums">{{ tasks.length }}</span>
    </header>

    <main class="flex-1 overflow-y-auto pt-2.5 scrollbar-hide">
      <ul class="space-y-2">
        <CTaskKanbanSortableCard
          v-for="(task, index) in tasks"
          :key="task.public_id"
          :task="task"
          :index="index"
          :group="status"
          @open="emit('open', $event)"
        />
      </ul>
    </main>
  </div>
</template>
