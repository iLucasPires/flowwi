<script setup lang="ts">
import { useTaskType } from '@/app/features/task/composables/taskType'
import type { iTaskType } from '@/app/features/task/types'
import { calcReorderPosition } from '@/app/shared/utils/ordering'
import type { DragEndEvent } from '@dnd-kit/vue'
import { DragDropProvider } from '@dnd-kit/vue'
import { isSortable } from '@dnd-kit/vue/sortable'

const overlay = useOverlay()
const { types, deleteType, reorderType } = useTaskType()

function openCreate() {
  const component = resolveComponent('CTaskTypeEditDialog')
  if (typeof component === 'object') {
    const modal = overlay.create(component)
    modal.open()
  }
}

function openEdit(type: iTaskType) {
  const component = resolveComponent('CTaskTypeEditDialog')
  if (typeof component === 'object') {
    const modal = overlay.create(component, { props: { type } })
    modal.open()
  }
}

async function onDelete(type: iTaskType) {
  await deleteType(type.id)
}

function onDragEnd(event: DragEndEvent) {
  if (event.canceled) return
  const { source } = event.operation
  if (!source || !isSortable(source)) return

  const initialIndex = Number(source.sortable.initialIndex)
  const finalIndex = Number(source.sortable.index)
  if (initialIndex === finalIndex) return

  const item = types.value[initialIndex]
  if (!item) return

  const position = calcReorderPosition(types.value, initialIndex, finalIndex)
  reorderType({ id: item.id, position })
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold">Tipos</h2>
        <p class="text-sm text-dimmed mt-1">Personalize os tipos de tarefa do seu workspace.</p>
      </div>

      <UButton label="Novo tipo" icon="i-lucide-plus" size="sm" @click="openCreate" />
    </div>

    <DragDropProvider @drag-end="onDragEnd">
      <ul class="flex flex-col gap-1">
        <CSettingsTypeSortableRow
          v-for="(type, index) in types"
          :key="type.id"
          :type="type"
          :index="index"
          @edit="openEdit"
          @delete="onDelete"
        />
      </ul>
    </DragDropProvider>
  </div>
</template>
