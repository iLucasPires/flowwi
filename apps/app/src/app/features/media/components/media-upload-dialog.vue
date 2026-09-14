<script setup lang="ts">
import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import { MEDIA_TYPE_ART, MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_IMAGE, MEDIA_TYPE_VIDEO } from '@/app/features/media/types'
import type { iMedia, iMediaVersion } from '@/app/features/media/types'
import { useTask } from '@/app/features/task/composables/task'
const emit = defineEmits<{
  close: [result?: { uploaded?: true }]
}>()

const toast = useToast()
const { tasks } = useTask()

const uploading = ref(false)
const file = ref<File | null>(null)
const mode = ref<'file' | 'text'>('file')
const textContent = ref('')

const form = reactive({
  task: undefined as number | undefined,
  title: '',
  notes: '',
})

const modeItems = [
  { label: 'Arquivo', value: 'file' as const, icon: 'i-lucide-upload' },
  { label: 'Texto', value: 'text' as const, icon: 'i-lucide-file-text' },
]

const artTasks = computed(() => (tasks.value ?? []).map((t) => ({ label: t.title, value: t.id })))

const canSubmit = computed(() =>
  mode.value === 'file' ? !!file.value : !!textContent.value.trim(),
)

function inferMediaType(): number {
  const name = file.value?.name.toLowerCase() ?? ''
  const mime = file.value?.type ?? ''

  if (name.endsWith('.psd') || name.endsWith('.ai')) return MEDIA_TYPE_ART
  if (mime.startsWith('image/')) return MEDIA_TYPE_IMAGE
  if (mime.startsWith('video/')) return MEDIA_TYPE_VIDEO
  if (mime === 'application/pdf' || name.endsWith('.pdf')) return MEDIA_TYPE_DOCUMENT

  return MEDIA_TYPE_ART
}

async function submit() {
  if (!canSubmit.value) return
  uploading.value = true

  try {
    const media = await apiFetch<iMedia>(API_MEDIA_URLS.LIST, {
      method: 'POST',
      body: {
        ...(form.task ? { task: form.task } : {}),
        title: form.title,
        notes: form.notes,
        type: mode.value === 'text' ? MEDIA_TYPE_DOCUMENT : inferMediaType(),
      },
    })

    if (mode.value === 'text') {
      await apiFetch<iMediaVersion>(API_MEDIA_URLS.VERSIONS, {
        method: 'POST',
        body: { media: media.id, text_content: textContent.value },
      })
    } else if (file.value) {
      const formData = new FormData()
      formData.append('media', String(media.id))
      formData.append('file', file.value)

      await apiFetch<iMediaVersion>(API_MEDIA_URLS.VERSIONS, {
        method: 'POST',
        body: formData,
      })
    }

    emit('close', { uploaded: true })
  } catch {
    toast.add({
      title: 'Erro ao enviar media',
      color: 'error',
    })
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <UModal
    title="Upload de media"
    :open="true"
    @close="emit('close')"
    :dismissible="false"
    :close="false"
    :ui="{
      content: 'sm:max-w-2xl',
      footer: 'items-start gap-2 flex-col',
    }"
  >
    <template #body>
      <UForm class="flex flex-col gap-4" id="media-upload-form" @submit.prevent="submit">
        <UFormField size="xs" label="Titulo">
          <UInput
            v-model="form.title"
            size="xs"
            placeholder="Titulo da media"
            variant="subtle"
            class="w-full"
          />
        </UFormField>

        <UFormField size="xs" label="Notas">
          <UTextarea
            size="xs"
            autoresize
            v-model="form.notes"
            placeholder="Observações..."
            variant="subtle"
            class="w-full"
            :rows="5"
          />
        </UFormField>

        <UFormField size="xs" label="Tarefa">
          <USelectMenu
            v-model="form.task"
            :items="artTasks"
            size="xs"
            value-key="value"
            placeholder="Selecione uma tarefa"
            icon="i-lucide-brush"
            variant="subtle"
            class="w-full"
          />
        </UFormField>

        <UFormField size="xs" label="Conteúdo" required>
          <UTabs v-model="mode" :items="modeItems" size="xs" :content="false" class="mb-3" />

          <UFileUpload
            v-if="mode === 'file'"
            v-model="file"
            size="xs"
            label="Drop your image here"
            description="SVG, PNG, JPG or GIF (max. 2MB)"
            accept="image/*,.pdf,.psd,.ai,.svg"
          />
          <UTextarea
            v-else
            v-model="textContent"
            size="xs"
            variant="subtle"
            autoresize
            :rows="8"
            class="w-full"
            placeholder="Escreva ou cole o texto..."
          />
        </UFormField>
      </UForm>
    </template>
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton
          label="Cancelar"
          variant="ghost"
          color="neutral"
          size="sm"
          @click="emit('close')"
        />
        <UButton
          form="media-upload-form"
          type="submit"
          label="Enviar"
          size="sm"
          :loading="uploading"
          :disabled="!canSubmit"
        />
      </div>
    </template>
  </UModal>
</template>
