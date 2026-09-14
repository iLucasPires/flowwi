<script setup lang="ts">
import type { iSticky } from '@/app/features/sticky/types'
import { useSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  sticky: iSticky
  index: number
  autofocus?: boolean
}>()

defineEmits<{ remove: [] }>()

const elementRef = useTemplateRef<HTMLElement>('elementRef')

const { isDragSource } = useSortable({
  id: computed(() => props.sticky.id),
  index: computed(() => props.index),
  group: 'stickies',
  element: elementRef,
})
</script>

<template>
  <div ref="elementRef" :class="{ 'opacity-50': isDragSource }">
    <CStickyCard :sticky="sticky" :autofocus="autofocus" @remove="$emit('remove')" />
  </div>
</template>
