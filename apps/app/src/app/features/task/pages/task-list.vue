<script setup lang="ts">
import { useTask } from '@/app/features/task/composables/task'
import type { iTask } from '@/app/features/task/types'
defineOptions({ name: 'TaskPage' })

const { tasks, isLoading, reorderTask, invalidate: refresh } = useTask()
const router = useRouter()
const overlay = useOverlay()

const groupTab = ref<'default' | 'date' | 'priority'>('default')
const viewTab = ref<'board' | 'list'>('board')
const sortAsc = ref(true)

const groupItems = [
  { label: 'Padrão', value: 'default', icon: 'i-lucide-wallet-cards' },
  { label: 'Data', value: 'date', icon: 'i-lucide-calendar-days' },
  { label: 'Prioridade', value: 'priority', icon: 'i-lucide-circle-dot-dashed' },
]

const viewItems = [
  { label: 'board', value: 'board', icon: 'i-lucide-kanban' },
  { label: 'list', value: 'list', icon: 'i-lucide-list-chevrons-up-down' },
]

const search = ref('')
const filterStatus = ref<number[]>([])
const filterPriority = ref<string[]>([])
const filterType = ref<number[]>([])
const filterAssignee = ref<number[]>([])

const filteredTasks = computed(() => {
  let list = tasks.value ?? []

  if (search.value) {
    const query = search.value.toLowerCase()
    list = list.filter((task) => task.title.toLowerCase().includes(query))
  }

  if (filterStatus.value.length) {
    list = list.filter((task) => task.status !== null && filterStatus.value.includes(task.status))
  }

  if (filterPriority.value.length) {
    list = list.filter((task) => filterPriority.value.includes(task.priority))
  }

  if (filterType.value.length) {
    list = list.filter((task) => task.type !== null && filterType.value.includes(task.type))
  }

  if (filterAssignee.value.length) {
    list = list.filter((task) =>
      task.assignees?.some((assignee) => filterAssignee.value.includes(assignee.id)),
    )
  }

  return list
})

async function onReorder(taskId: string, newPosition: string, status: number) {
  await reorderTask({ public_id: taskId, position: newPosition, status })
}

async function openCreate() {
  const component = resolveComponent('CTaskCreateDialog')

  if (typeof component == 'object') {
    const modal = overlay.create(component)

    const result = await modal.open()
    if (result) refresh()
  }
}

function openTask(task: iTask | { public_id: string }) {
  router.push(`/dashboard/tasks/${task.public_id}`)
}
</script>

<template>
  <CDashboardContent title="Tarefas" description="Gerenciamento de tarefas">
    <template #actions>
      <UInput
        v-model="search"
        placeholder="Buscar..."
        icon="i-lucide-search"
        size="xs"
        variant="subtle"
      />

      <CTaskFilterPopover
        v-model:status="filterStatus"
        v-model:priority="filterPriority"
        v-model:type="filterType"
        v-model:assignee="filterAssignee"
      />

      <UTabs v-model="groupTab" :items="groupItems" size="xs" :content="false" />
      <UTabs v-model="viewTab" :items="viewItems" size="xs" :content="false" />

      <CTaskTrashSlideover />

      <UButton label="Nova tarefa" icon="i-lucide-plus" size="xs" @click="openCreate" />
    </template>

    <div class="size-full flex flex-col overflow-hidden">
      <CTaskViewKanban
        v-if="viewTab == 'board'"
        :tasks="filteredTasks"
        :loading="isLoading"
        :group-by="groupTab"
        :sort-asc="sortAsc"
        @open="openTask"
        @reorder="onReorder"
        @create="openCreate"
      />

      <CTaskViewList
        v-else-if="viewTab == 'list'"
        :tasks="filteredTasks"
        :loading="isLoading"
        :group-by="groupTab"
        :sort-asc="sortAsc"
        @open="openTask"
        @reorder="onReorder"
      />
    </div>
  </CDashboardContent>
</template>
