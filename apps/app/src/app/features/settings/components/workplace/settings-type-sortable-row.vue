<script
  setup
  lang="ts"
  generic="T extends { id: number; name: string; color: string; icon: string }"
>
import { useSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  type: T
  index: number
}>()

const emit = defineEmits<{
  edit: [type: T]
  delete: [type: T]
}>()

const elementRef = useTemplateRef<HTMLElement>('elementRef')
const handleRef = useTemplateRef<HTMLElement>('handleRef')

const { isDragSource } = useSortable({
  id: computed(() => props.type.id),
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
      :value="type.icon"
      fallback="i-lucide-box"
      class="size-4 shrink-0 text-sm"
      :style="{ color: type.color }"
    />

    <span class="flex-1 text-sm font-medium">{{ type.name }}</span>

    <UButton
      icon="i-lucide-pencil"
      size="xs"
      variant="ghost"
      color="neutral"
      @click="emit('edit', type)"
    />
    <UButton
      icon="i-lucide-trash-2"
      size="xs"
      variant="ghost"
      color="error"
      @click="emit('delete', type)"
    />
  </li>
</template>
