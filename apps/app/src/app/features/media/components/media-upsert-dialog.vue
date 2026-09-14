<script setup lang="ts">
import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia } from '@/app/features/media/types'
const props = defineProps<{ media: iMedia }>()
const emit = defineEmits<{ close: [result?: { changed?: true }] }>()

const toast = useToast()
const saving = ref(false)
const form = reactive({
  title: props.media.title || '',
  notes: props.media.notes || '',
})

async function save() {
  saving.value = true
  try {
    await apiFetch(`${API_MEDIA_URLS.LIST}/${props.media.id}`, {
      method: 'PATCH',
      body: { title: form.title, notes: form.notes },
    })
    toast.add({ title: 'Media atualizada', color: 'success' })
    emit('close', { changed: true })
  } catch {
    toast.add({ title: 'Erro ao salvar', color: 'error' })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <UModal
    title="Editar Media"
    :open="true"
    :dismissible="false"
    :ui="{
      content: 'sm:max-w-lg',
      body: 'flex flex-col gap-4',
      footer: 'flex items-center justify-end gap-2',
    }"
    @close="emit('close')"
  >
    <template #body>
      <UFormField label="Título" size="xs">
        <UInput
          v-model="form.title"
          size="xs"
          placeholder="Título da media..."
          variant="subtle"
          class="w-full"
        />
      </UFormField>
      <UFormField label="Notas" size="xs">
        <UTextarea
          v-model="form.notes"
          size="xs"
          placeholder="Observações..."
          variant="subtle"
          class="w-full"
          :rows="10"
          autoresize
        />
      </UFormField>
    </template>
    <template #footer>
      <UButton label="Cancelar" variant="ghost" color="neutral" size="xs" @click="emit('close')" />
      <UButton label="Salvar" size="xs" :loading="saving" @click="save" />
    </template>
  </UModal>
</template>
