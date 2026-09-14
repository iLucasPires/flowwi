<script setup lang="ts">
import type { iSub } from '@/app/features/task/types'
import { calcReorderPosition } from '@/app/shared/utils/ordering'
import { DragDropProvider, type DragEndEvent } from '@dnd-kit/vue'
import { isSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  subs: iSub[]
}>()

const emit = defineEmits<{
  toggle: [id: number, value: boolean]
  delete: [id: number]
  create: [title: string]
  reorder: [id: number, position: string]
}>()

const expanded = ref(true)
const newTitle = ref('')

const sortedSubs = computed(() =>
  [...props.subs].sort((a, b) => (a.position < b.position ? -1 : 1)),
)
const doneCount = computed(() => props.subs.filter((s) => s.is_done).length)

function onDragEnd(event: DragEndEvent) {
  if (event.canceled) return
  const { source } = event.operation
  if (!source || !isSortable(source)) return

  const { initialIndex, index } = source.sortable
  if (initialIndex === index) return

  emit('reorder', source.id as number, calcReorderPosition(sortedSubs.value, initialIndex, index))
}

function onSubmit() {
  if (!newTitle.value.trim()) return
  emit('create', newTitle.value.trim())
  newTitle.value = ''
}
</script>

<template>
  <div class="flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <button
        class="flex items-center gap-2 text-xs font-medium text-neutral-700 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-neutral-100"
        @click="expanded = !expanded"
      >
        <UIcon
          name="i-lucide-chevron-down"
          class="size-3.5 transition-transform"
          :class="{ '-rotate-90': !expanded }"
        />
        <span>Sub-task</span>
        <span v-if="subs.length" class="text-neutral-500"> {{ doneCount }}/{{ subs.length }} </span>
      </button>

      <UButton
        icon="i-lucide-plus"
        size="2xs"
        variant="ghost"
        color="neutral"
        @click="expanded = true"
      />
    </div>

    <!-- Content -->
    <div v-show="expanded" class="mt-2 mx-2">
      <DragDropProvider @drag-end="onDragEnd">
        <div class="flex flex-col">
          <CTaskSubtaskSortableRow
            v-for="(sub, index) in sortedSubs"
            :key="sub.id"
            :sub="sub"
            :index="index"
            @toggle="(id, val) => emit('toggle', id, val)"
            @delete="(id) => emit('delete', id)"
          />
        </div>
      </DragDropProvider>

      <UInput
        v-model.trim="newTitle"
        placeholder="Add sub-issue..."
        variant="ghost"
        size="xs"
        class="w-full"
        @keydown.enter="onSubmit"
      />
    </div>
  </div>
</template>
