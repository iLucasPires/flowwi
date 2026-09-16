<script setup lang="ts">
import { useSubtask } from '@/app/features/task/composables/subtask'
import { useTask } from '@/app/features/task/composables/task'
import { useTaskDetail } from '@/app/features/task/composables/taskDetail'
import type { TaskUpdateSchema } from '@/app/features/task/schemas'
import type { iSub } from '@/app/features/task/types'
import { CalendarDate, parseDate } from '@internationalized/date'
import type { BreadcrumbItem } from '@nuxt/ui'

defineOptions({ name: 'TaskDetailPage' })

const route = useRoute()

const taskId = computed<string | null>(() => {
  const raw = route.params.id
  const value = Array.isArray(raw) ? raw[0] : raw
  return value || null
})

function deadlineToStr(deadline: CalendarDate | null): string | null {
  if (!deadline) return null
  return deadline.toString()
}

const { updateTask } = useTask()
const { task, isLoading } = useTaskDetail(taskId)
const { createSubtask, toggleSubtask, deleteSubtask, reorderSubtask } = useSubtask()

const taskData = computed(() =>
  taskId.value != null && task.value?.public_id === taskId.value ? task.value : null,
)

const showSkeleton = computed(() => {
  if (taskId.value == null) return false
  if (isLoading.value) return true
  return taskData.value == null
})

const breadcrumbItems = computed<BreadcrumbItem[]>(() => {
  const items: BreadcrumbItem[] = [
    { label: 'Tarefas', icon: 'i-lucide-kanban', to: '/dashboard/tasks' },
  ]
  if (taskData.value) items.push({ label: taskData.value.title || 'Sem título' })
  return items
})

const state = reactive<TaskUpdateSchema>({
  title: '',
  description: '',
  type: null,
  status: null,
  priority: 'medium',
  assignees: [],
  deadline: null,
})

const syncing = ref(false)

watch(
  () => taskData.value?.public_id,
  () => {
    if (!taskData.value) return
    syncing.value = true
    Object.assign(state, {
      title: taskData.value.title,
      description: taskData.value.description,
      type: taskData.value.type,
      status: taskData.value.status,
      priority: taskData.value.priority,
      assignees: (taskData.value.assignees ?? []).map((a) => a.id),
      deadline: taskData.value.deadline ? parseDate(taskData.value.deadline) : null,
    })
    nextTick(() => (syncing.value = false))
  },
  { immediate: true },
)

const autoSave = useDebounceFn(async () => {
  if (!taskData.value) return
  await updateTask({
    public_id: taskData.value.public_id,
    data: {
      ...state,
      assignees: state.assignees.filter(Boolean),
      deadline: deadlineToStr(state.deadline),
    },
  })
}, 500)

watch(
  state,
  () => {
    if (!syncing.value) autoSave()
  },
  { deep: true },
)

const localSubs = ref<iSub[]>([])

watch(
  () => taskData.value?.subs,
  (subs) => {
    if (subs) localSubs.value = [...subs]
  },
  { immediate: true },
)

async function addSubtask(title: string) {
  if (!taskData.value) return
  const result = await createSubtask({ task: taskData.value.id, title })
  if (result) localSubs.value.push(result)
}

async function onToggleSubtask(id: number, newValue: boolean) {
  if (!taskData.value) return
  const sub = localSubs.value.find((s) => s.id === id)
  if (sub) sub.is_done = newValue
  await toggleSubtask({ public_id: sub!.public_id, is_done: newValue })
}

async function onDeleteSubtask(id: number) {
  if (!taskData.value) return
  const sub = localSubs.value.find((s) => s.id === id)
  localSubs.value = localSubs.value.filter((s) => s.id !== id)
  if (sub) await deleteSubtask({ public_id: sub.public_id })
}

async function onReorderSubtask(id: number, position: string) {
  if (!taskData.value) return
  const sub = localSubs.value.find((s) => s.id === id)
  if (sub) sub.position = position
  if (sub) await reorderSubtask({ public_id: sub.public_id, position })
}
</script>

<template>
  <CDashboardContent title="">
    <template #leading>
      <UBreadcrumb :items="breadcrumbItems" />
    </template>

    <CTaskDetailSkeleton v-if="showSkeleton" />

    <UEmpty
      v-else-if="!taskData"
      title="Tarefa não encontrada"
      description="Não foi possível carregar os detalhes da tarefa."
      icon="i-lucide-circle-alert"
      class="min-h-[40dvh]"
      variant="subtle"
      size="sm"
    />

    <div v-else class="flex flex-col gap-8 w-1/2 mx-auto py-8">
      <!-- Main content -->
      <UInput
        v-model="state.title"
        variant="none"
        size="xl"
        :ui="{ base: 'px-0! text-2xl font-semibold' }"
        placeholder="Sem título"
      />

      <div>
        <CRichTextEditor v-model="state.description" placeholder="Adicione uma descrição..." />
      </div>

      <div class="flex gap-2">
        <CTaskStatusSelect v-model="state.status" size="sm" />
        <CTaskPrioritySelect v-model="state.priority" size="sm" />
        <CTaskTypeSelect v-model="state.type" size="sm" />
        <CTaskMemberSelect v-model="state.assignees" size="sm" />
        <CTaskDeadlineSelect v-model="state.deadline" size="sm" />
      </div>

      <CTaskSubtaskSection
        :subs="localSubs"
        @toggle="onToggleSubtask"
        @delete="onDeleteSubtask"
        @create="addSubtask"
        @reorder="onReorderSubtask"
      />
    </div>
  </CDashboardContent>
</template>
