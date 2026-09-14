<script setup lang="ts">
import { useSticky } from '@/app/features/sticky/composables/sticky'
import type { iSticky } from '@/app/features/sticky/types'
import { randomPastelColor } from '@/app/shared/utils/color'
import { calcReorderPosition } from '@/app/shared/utils/ordering'
import { isSortable } from '@dnd-kit/vue/sortable'
import { DragDropProvider, type DragEndEvent } from '@dnd-kit/vue'

defineOptions({ name: 'StickiesPage' })

const { stickies, isLoading, deleteSticky, createSticky, reorderSticky } = useSticky()

const removingId = ref<number | null>(null)
const creating = ref(false)
const autofocusId = ref<number | null>(null)

const showInitialLoading = computed(() => isLoading.value && stickies.value.length === 0)

const filterVisibility = ref<string | undefined>(undefined)

const filteredStickies = computed(() => {
  const list = stickies.value
  if (!list.length) return []

  return list
    .filter((s) => {
      if (filterVisibility.value && s.visibility !== filterVisibility.value) return false

      return true
    })
    .sort((a, b) => (a.position < b.position ? -1 : 1))
})

async function addSticky() {
  creating.value = true
  try {
    const sticky = await createSticky({
      text: '',
      color: randomPastelColor(),
      visibility: 'private',
    })
    autofocusId.value = sticky.id
  } finally {
    creating.value = false
  }
}

async function onRemove(sticky: iSticky) {
  removingId.value = sticky.id
  try {
    await deleteSticky(sticky.id)
  } finally {
    removingId.value = null
  }
}

function onDragEnd(event: DragEndEvent) {
  if (event.canceled) return
  const { source } = event.operation
  if (!source || !isSortable(source)) return

  const { initialIndex, index } = source.sortable
  if (initialIndex === index) return

  reorderSticky({
    id: source.id as number,
    position: calcReorderPosition(filteredStickies.value, initialIndex, index),
  })
}
</script>

<template>
  <CDashboardContent title="Stickies" description="Notas rápidas do seu workspace">
    <template #actions>
      <CStickyFilterDropdown v-model:visibility="filterVisibility" />

      <CStickyTrashSlideover />

      <UButton
        label="Nova sticky"
        icon="i-lucide-plus"
        color="primary"
        variant="solid"
        size="sm"
        :loading="creating"
        @click="addSticky"
      />
    </template>

    <CStickySkeleton v-if="showInitialLoading" />
    <CStickyEmpty v-else-if="stickies.length === 0" @create="addSticky" />

    <DragDropProvider v-else @drag-end="onDragEnd">
      <UPageGrid>
        <CStickySortableCard
          v-for="(sticky, index) in filteredStickies"
          :key="sticky.id"
          :sticky="sticky"
          :index="index"
          :autofocus="autofocusId === sticky.id"
          :class="removingId === sticky.id ? 'opacity-50 pointer-events-none' : ''"
          @remove="onRemove(sticky)"
        />
      </UPageGrid>
    </DragDropProvider>
  </CDashboardContent>
</template>
