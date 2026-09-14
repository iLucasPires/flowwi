<script setup lang="ts">
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import type { iTaskStatus } from '@/app/features/task/types'
import { calcReorderPosition } from '@/app/shared/utils/ordering'
import type { DragEndEvent } from '@dnd-kit/vue'
import { DragDropProvider } from '@dnd-kit/vue'
import { isSortable } from '@dnd-kit/vue/sortable'

const overlay = useOverlay()
const { statuses, deleteStatus, reorderStatus } = useTaskStatus()

function openCreate() {
  const component = resolveComponent('CTaskStatusEditDialog')
  if (typeof component === 'object') {
    const modal = overlay.create(component)
    modal.open()
  }
}

function openEdit(status: iTaskStatus) {
  const component = resolveComponent('CTaskStatusEditDialog')
  if (typeof component === 'object') {
    const modal = overlay.create(component, { props: { status } })
    modal.open()
  }
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

      <UButton label="Novo status" icon="i-lucide-plus" size="sm" @click="openCreate" />
    </div>

    <DragDropProvider @drag-end="onDragEnd">
      <ul class="flex flex-col gap-1">
        <CSettingsStatusSortableRow
          v-for="(status, index) in statuses"
          :key="status.id"
          :status="status"
          :index="index"
          @edit="openEdit"
          @delete="onDelete"
        />
      </ul>
    </DragDropProvider>
  </div>
</template>
