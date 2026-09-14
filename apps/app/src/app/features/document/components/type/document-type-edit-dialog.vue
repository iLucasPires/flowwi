<script setup lang="ts">
import type { iDocumentType } from '@/app/features/document/types'
import { useDocumentType } from '@/app/features/document/composables/documentType'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  type?: iDocumentType
}>()

const { createType, updateType } = useDocumentType()

const isEditing = computed(() => !!props.type)

const name = ref(props.type?.name ?? '')
const color = ref(props.type?.color ?? '#5CFCD4')
const icon = ref(props.type?.icon ?? '')
const defaultContent = ref(props.type?.default_content ?? '')

const saving = ref(false)

async function save() {
  if (!name.value.trim()) return
  saving.value = true
  try {
    const data = {
      name: name.value,
      color: color.value,
      icon: icon.value,
      default_content: defaultContent.value,
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
    :ui="{ content: 'sm:max-w-3xl' }"
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
            placeholder="Nome do tipo"
            size="md"
            variant="subtle"
            class="flex-1"
            autofocus
          />
        </div>

        <UFormField
          label="Texto base do documento"
          description="Conteúdo inicial de todo documento criado com este tipo — deixe em branco para começar vazio."
          size="xs"
        >
          <div
            class="h-96 overflow-y-auto rounded-md border border-default bg-elevated/30 px-3 py-2"
          >
            <CDocumentTypeTemplateEditor
              v-model="defaultContent"
              placeholder="Escreva a estrutura padrão — pressione '/' para comandos..."
            />
          </div>
        </UFormField>
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
