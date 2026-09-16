<script setup lang="ts">
import { useTask } from '@/app/features/task/composables/task'
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import { useTaskType } from '@/app/features/task/composables/taskType'
import type { TaskCreateSchema } from '@/app/features/task/schemas'
const open = defineModel<boolean>('open', { required: true })
const props = defineProps<{
  initialTitle?: string
  initialDescription?: string
}>()
const emit = defineEmits<{ created: [] }>()

const { createTask } = useTask()
const { statuses } = useTaskStatus()
const { types } = useTaskType()
const creating = ref(false)

const initialState: TaskCreateSchema = {
  title: '',
  description: '',
  type: null,
  priority: 'medium',
  status: null,
  assignees: [],
  startDate: null,
  endDate: null,
}

const state = reactive<TaskCreateSchema>({
  ...initialState,
  title: props.initialTitle ?? initialState.title,
  description: props.initialDescription ?? initialState.description,
})

function resetState() {
  Object.assign(state, {
    ...initialState,
    title: props.initialTitle ?? initialState.title,
    description: props.initialDescription ?? initialState.description,
    status: statuses.value.find((s) => s.category === 'todo')?.id ?? statuses.value[0]?.id ?? null,
    type: types.value[0]?.id ?? null,
    assignees: [],
  })
}

watch(open, (isOpen) => {
  if (isOpen) resetState()
})

watch([statuses, types], () => {
  if (!open.value) return
  if (state.status === null && statuses.value.length > 0) {
    state.status = statuses.value.find((s) => s.category === 'todo')?.id ?? statuses.value[0]?.id ?? null
  }
  if (state.type === null && types.value.length > 0) {
    state.type = types.value[0]?.id ?? null
  }
})

async function onSubmit() {
  creating.value = true
  try {
    const { endDate, ...rest } = state
    await createTask({
      ...rest,
      deadline: endDate ? endDate.toString() : null,
    })
    open.value = false
    resetState()
    emit('created')
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <UModal
    v-model:open="open"
    :dismissible="false"
    :close="false"
    :ui="{
      content: 'sm:max-w-7xl',
      footer: 'justify-end',
    }"
  >
    <template #body>
      <form @submit.prevent="onSubmit" class="flex flex-col gap-4" id="task-create-form">
        <UFormField name="title">
          <UInput
            v-model="state.title"
            placeholder="Título"
            size="xl"
            variant="none"
            class="w-full"
            :ui="{ base: 'px-0! text-2xl font-semibold' }"
            autofocus
          />
        </UFormField>

        <CRichTextEditor
          v-model="state.description"
          class="h-96"
          placeholder="Descreva a tarefa..."
        />

        <div class="flex gap-2 me-auto">
          <CTaskStatusSelect v-model="state.status" size="xs" placeholder="Status" />
          <CTaskPrioritySelect v-model="state.priority" size="xs" placeholder="Prioridade" />
          <CTaskTypeSelect v-model="state.type" size="xs" placeholder="Tipo" />
          <CTaskMemberSelect v-model="state.assignees" size="xs" />
          <CTaskDeadlineSelect v-model="state.endDate" size="xs" />
        </div>
      </form>
    </template>

    <template #footer>
      <UButton label="Cancelar" variant="ghost" color="neutral" size="xs" @click="open = false" />
      <UButton
        type="submit"
        form="task-create-form"
        :loading="creating"
        :disabled="!state.title.trim()"
        label="Criar tarefa"
        size="xs"
      />
    </template>
  </UModal>
</template>
