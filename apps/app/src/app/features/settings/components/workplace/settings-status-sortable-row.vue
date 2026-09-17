<script setup lang="ts">
import type { TaskStatusCategory, iTaskStatus } from '@/app/features/task/types'
import { useSortable } from '@dnd-kit/vue/sortable'

const props = defineProps<{
  status: iTaskStatus
  index: number
  /** Set by the parent right after this status is created, so it opens straight
   * into rename mode — same as Linear's "new label" row. */
  autoEdit: boolean
}>()

const emit = defineEmits<{
  update: [status: iTaskStatus, data: Partial<iTaskStatus>]
  delete: [status: iTaskStatus]
  /** Tells the parent this row consumed its one-shot `autoEdit` signal. */
  autoEditDone: []
}>()

const categoryOptions: { label: string; value: TaskStatusCategory }[] = [
  { label: 'A fazer', value: 'todo' },
  { label: 'Em progresso', value: 'in_progress' },
  { label: 'Concluído', value: 'done' },
  { label: 'Cancelado', value: 'cancelled' },
]

const elementRef = useTemplateRef<HTMLElement>('elementRef')
const handleRef = useTemplateRef<HTMLElement>('handleRef')
const nameInputRef = useTemplateRef('nameInputRef')

const { isDragSource } = useSortable({
  id: computed(() => props.status.id),
  index: computed(() => props.index),
  element: elementRef,
  handle: handleRef,
})

// ── Inline name editing — click the name to rename it, like a Linear table cell. ──
const isEditingName = ref(false)
const draftName = ref(props.status.name)

function startEditingName() {
  draftName.value = props.status.name
  isEditingName.value = true
  nextTick(() => {
    const el = nameInputRef.value?.$el?.querySelector('input') as HTMLInputElement | undefined
    el?.focus()
    el?.select()
  })
}

function commitName() {
  isEditingName.value = false
  const trimmed = draftName.value.trim()
  if (!trimmed || trimmed === props.status.name) return
  emit('update', props.status, { name: trimmed })
}

function cancelEditingName() {
  isEditingName.value = false
  draftName.value = props.status.name
}

watch(
  () => props.autoEdit,
  (value) => {
    if (!value) return
    startEditingName()
    emit('autoEditDone')
  },
  { immediate: true },
)

// ── Color + icon — a single popover edits both, committed as soon as either changes. ──
function updateColor(color: string) {
  emit('update', props.status, { color })
}

function updateIcon(icon: string) {
  emit('update', props.status, { icon })
}

function updateCategory(category: TaskStatusCategory) {
  if (category === props.status.category) return
  emit('update', props.status, { category })
}
</script>

<template>
  <li
    ref="elementRef"
    class="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-accented/40"
    :class="{ 'opacity-50': isDragSource }"
  >
    <span ref="handleRef" class="cursor-grab active:cursor-grabbing text-dimmed shrink-0">
      <UIcon name="i-lucide-grip-vertical" class="size-4" />
    </span>

    <UPopover>
      <UButton size="xs" variant="ghost" color="neutral" class="p-1 shrink-0">
        <span class="size-4 rounded-full ring-1 ring-default" :style="{ backgroundColor: status.color }" />
      </UButton>
      <template #content>
        <UColorPicker :model-value="status.color" class="p-2" @update:model-value="updateColor" />
      </template>
    </UPopover>

    <CIconPicker
      :model-value="status.icon"
      :color="status.color"
      fallback="i-lucide-circle"
      icon-class="size-4"
      button-class="p-1 shrink-0"
      @update:model-value="updateIcon"
    />

    <UInput
      v-if="isEditingName"
      ref="nameInputRef"
      v-model="draftName"
      size="sm"
      variant="none"
      class="flex-1"
      :ui="{ base: 'px-1.5' }"
      @keydown.enter="commitName"
      @keydown.escape="cancelEditingName"
      @blur="commitName"
    />
    <button
      v-else
      type="button"
      class="flex-1 text-start text-sm font-medium px-1.5 py-1 rounded-md hover:bg-accented/60 transition-colors truncate"
      @click="startEditingName"
    >
      {{ status.name }}
    </button>

    <USelectMenu
      :model-value="status.category"
      :items="categoryOptions"
      value-key="value"
      size="xs"
      variant="ghost"
      color="neutral"
      class="w-36 shrink-0"
      @update:model-value="updateCategory"
    />

    <UButton
      icon="i-lucide-trash-2"
      size="xs"
      variant="ghost"
      color="error"
      class="shrink-0"
      @click="emit('delete', status)"
    />
  </li>
</template>
