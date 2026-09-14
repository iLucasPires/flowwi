<script setup lang="ts">
import { useTaskType } from '@/app/features/task/composables/taskType'
import type { iTaskType } from '@/app/features/task/types'
const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  type?: iTaskType
}>()

const { createType, updateType } = useTaskType()

const isEditing = computed(() => !!props.type)

const name = ref(props.type?.name ?? '')
const color = ref(props.type?.color ?? '#5CFCD4')
const icon = ref(props.type?.icon ?? '')

const saving = ref(false)

async function save() {
  if (!name.value.trim()) return
  saving.value = true
  try {
    const data = {
      name: name.value,
      color: color.value,
      icon: icon.value,
    }

    if (isEditing.value && props.type) {
      await updateType({ id: props.type.id, data })
    } else {
      await createType(data)
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
    :title="isEditing ? 'Editar tipo' : 'Novo tipo'"
    :ui="{ content: 'sm:max-w-md' }"
  >
    <template #body>
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
          placeholder="Nome do tipo"
          size="md"
          variant="subtle"
          class="flex-1"
          autofocus
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
