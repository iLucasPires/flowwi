<script setup lang="ts">
import type { iSub } from '@/app/features/task/types'
import { useSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  sub: iSub
  index: number
}>()

const emit = defineEmits<{
  toggle: [id: number, value: boolean]
  delete: [id: number]
}>()

const elementRef = useTemplateRef<HTMLElement>('elementRef')

const { isDragSource } = useSortable({
  id: computed(() => props.sub.id),
  index: computed(() => props.index),
  group: 'subtasks',
  element: elementRef,
})
</script>

<template>
  <div
    ref="elementRef"
    class="flex items-center gap-3 px-2 py-1.5 rounded-md group cursor-grab active:cursor-grabbing hover:bg-neutral-100 dark:hover:bg-neutral-800/60 transition-colors"
    :class="{ 'opacity-40': isDragSource }"
  >
    <button
      class="size-4 shrink-0 rounded-full border transition-colors flex items-center justify-center"
      :class="
        sub.is_done
          ? 'border-primary-500 bg-primary-500 text-white'
          : 'border-neutral-400 dark:border-neutral-600 hover:border-primary-400'
      "
      @click.stop="emit('toggle', sub.id, !sub.is_done)"
    >
      <UIcon v-if="sub.is_done" name="i-lucide-check" class="size-2.5" />
    </button>

    <span
      class="flex-1 text-sm truncate"
      :class="
        sub.is_done ? 'line-through text-neutral-400' : 'text-neutral-800 dark:text-neutral-200'
      "
    >
      {{ sub.title }}
    </span>

    <UButton
      class="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
      color="neutral"
      size="2xs"
      variant="ghost"
      icon="i-lucide-x"
      @click.stop="emit('delete', sub.id)"
    />
  </div>
</template>
