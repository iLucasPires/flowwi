<script setup lang="ts">
import { useTaskType } from '@/app/features/task/composables/taskType'
import type { iTaskType } from '@/app/features/task/types'
import { calcReorderPosition } from '@/app/shared/utils/ordering'
import type { DragEndEvent } from '@dnd-kit/vue'
import { DragDropProvider } from '@dnd-kit/vue'
import { isSortable } from '@dnd-kit/vue/sortable'

const { types, createType, updateType, deleteType, reorderType } = useTaskType()

/** One-shot: the type that should open straight into rename mode, right after
 * creation — same pattern as the status table. */
const autoEditId = ref<number | null>(null)

async function addType() {
  const created = await createType({ name: 'Novo tipo', color: '#a3a3a3', icon: '' })
  autoEditId.value = created.id
}

async function onUpdate(type: iTaskType, data: Partial<iTaskType>) {
  await updateType({ id: type.id, data })
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

      <UButton label="Novo tipo" icon="i-lucide-plus" size="sm" @click="addType" />
    </div>

    <DragDropProvider @drag-end="onDragEnd">
      <ul class="flex flex-col gap-1">
        <CSettingsTypeSortableRow
          v-for="(type, index) in types"
          :key="type.id"
          :type="type"
          :index="index"
          :auto-edit="type.id === autoEditId"
          @update="onUpdate"
          @delete="onDelete"
          @auto-edit-done="autoEditId = null"
        />
      </ul>
    </DragDropProvider>
  </div>
</template>
