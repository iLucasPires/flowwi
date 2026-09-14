<script setup lang="ts">
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import type { TaskStatusCategory, iTaskStatus } from '@/app/features/task/types'
const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  status?: iTaskStatus
}>()

const { createStatus, updateStatus } = useTaskStatus()

const categoryOptions = [
  { label: 'A fazer', value: 'todo' },
  { label: 'Em progresso', value: 'in_progress' },
  { label: 'Concluído', value: 'done' },
  { label: 'Cancelado', value: 'cancelled' },
]

const isEditing = computed(() => !!props.status)

const name = ref(props.status?.name ?? '')
const color = ref(props.status?.color ?? '#5CFCD4')
const icon = ref(props.status?.icon ?? '')
const category = ref<TaskStatusCategory>(props.status?.category ?? 'todo')

const saving = ref(false)

async function save() {
  if (!name.value.trim()) return
  saving.value = true
  try {
    const data = {
      name: name.value,
      color: color.value,
      icon: icon.value,
      category: category.value,
    }

    if (isEditing.value && props.status) {
      await updateStatus({ id: props.status.id, data })
    } else {
      await createStatus(data)
    }

    open.value = false
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <UModal
    v-model:open="open"
    :title="isEditing ? 'Editar status' : 'Novo status'"
    :ui="{ content: 'sm:max-w-md' }"
  >
    <template #body>
      <div class="flex flex-col gap-4">
        <div class="flex items-center gap-2">
          <UPopover>
            <UButton size="md" variant="subtle" :style="{ color }">
              <span class="size-3 rounded-full" :style="{ backgroundColor: color }" />
            </UButton>
            <template #content>
              <UColorPicker v-model="color" class="p-2" />
            </template>
          </UPopover>

          <CIconPicker v-model="icon" :color="color" />

          <UInput
            v-model="name"
            placeholder="Nome do status"
            size="md"
            variant="subtle"
            class="flex-1"
            autofocus
          />
        </div>

        <USelectMenu
          v-model="category"
          :items="categoryOptions"
          value-key="value"
          placeholder="Categoria"
          size="md"
          variant="subtle"
        />
      </div>
    </template>
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton label="Cancelar" variant="ghost" color="neutral" size="md" @click="open = false" />
        <UButton
          label="Salvar"
          color="primary"
          size="md"
          :disabled="!name.trim()"
          :loading="saving"
          @click="save"
        />
      </div>
    </template>
  </UModal>
</template>
