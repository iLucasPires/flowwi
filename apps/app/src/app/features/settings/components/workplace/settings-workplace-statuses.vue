<script setup lang="ts">
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import type { iTaskStatus } from '@/app/features/task/types'
import { calcReorderPosition } from '@/app/shared/utils/ordering'
import type { DragEndEvent } from '@dnd-kit/vue'
import { DragDropProvider } from '@dnd-kit/vue'
import { isSortable } from '@dnd-kit/vue/sortable'

const { statuses, createStatus, updateStatus, deleteStatus, reorderStatus } = useTaskStatus()

/** The status that should open straight into rename mode — set right after creating
 * one, cleared once its row has consumed the signal. Same one-shot pattern as
 * Linear's "new label" row appearing already editable. */
const autoEditId = ref<number | null>(null)

async function addStatus() {
  const created = await createStatus({
    name: 'Novo status',
    color: '#a3a3a3',
    icon: '',
    category: 'todo',
  })
  autoEditId.value = created.id
}

async function onUpdate(status: iTaskStatus, data: Partial<iTaskStatus>) {
  await updateStatus({ id: status.id, data })
}

async function onDelete(status: iTaskStatus) {
  await deleteStatus(status.id)
}

function onDragEnd(event: DragEndEvent) {
  if (event.canceled) return
  const { source } = event.operation
  if (!source || !isSortable(source)) return

  const initialIndex = Number(source.sortable.initialIndex)
  const finalIndex = Number(source.sortable.index)
  if (initialIndex === finalIndex) return

  const item = statuses.value[initialIndex]
  if (!item) return

  const position = calcReorderPosition(statuses.value, initialIndex, finalIndex)
  reorderStatus({ id: item.id, position })
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold">Status</h2>
        <p class="text-sm text-dimmed mt-1">
          Personalize as colunas do fluxo de trabalho das suas tarefas.
        </p>
      </div>

      <UButton label="Novo status" icon="i-lucide-plus" size="sm" @click="addStatus" />
    </div>

    <DragDropProvider @drag-end="onDragEnd">
      <ul class="flex flex-col gap-1">
        <CSettingsStatusSortableRow
          v-for="(status, index) in statuses"
          :key="status.id"
          :status="status"
          :index="index"
          :auto-edit="status.id === autoEditId"
          @update="onUpdate"
          @delete="onDelete"
          @auto-edit-done="autoEditId = null"
        />
      </ul>
    </DragDropProvider>
  </div>
</template>
