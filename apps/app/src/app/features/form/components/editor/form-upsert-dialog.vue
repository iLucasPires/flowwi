<script setup lang="ts">
import { API_FORM_URLS, apiFetch } from '@/app/core/clients/api'
import type { iCoverCredit } from '@/app/shared/types/cover'
import { coverBackgroundStyle, coverImageSrc } from '@/app/shared/utils/cover'
import type { tFormOut } from '@/app/features/form/schemas'

defineOptions({ name: 'FormUpsertDialog' })

const props = defineProps<{ form?: tFormOut }>()
const emit = defineEmits<{
  close: [
    result?: {
      created?: true
      id?: number
      saved?: true
    },
  ]
}>()

const submitting = ref(false)
const pickerOpen = ref(false)

const coverFile = ref<File | null>(null)
const localCoverUrl = ref<string | null>(null)
const uploadedCover = ref<string | null>(props.form?.cover_image ?? null)
const coverStyle = ref(props.form?.cover_style ?? '')
const coverCredit = ref<iCoverCredit>(props.form?.cover_credit ?? null)

const data = reactive({
  title: props.form?.title ?? '',
  description: props.form?.description ?? '',
  is_published: props.form?.is_published ?? true,
  require_auth: props.form?.require_auth ?? false,
  require_identity: props.form?.require_identity ?? false,
})

const isEdit = computed(() => props.form != null)

const coverPreview = computed(
  () => localCoverUrl.value ?? coverImageSrc(uploadedCover.value, coverStyle.value),
)
const coverBackground = computed(() =>
  coverPreview.value ? undefined : coverBackgroundStyle(null, coverStyle.value),
)
const hasCover = computed(() => !!coverPreview.value || !!coverBackground.value)

function releaseLocalCover() {
  if (localCoverUrl.value) {
    URL.revokeObjectURL(localCoverUrl.value)
    localCoverUrl.value = null
  }
}

function onSelectCoverFile(file: File) {
  releaseLocalCover()

  coverFile.value = file
  localCoverUrl.value = URL.createObjectURL(file)
  coverStyle.value = ''
  coverCredit.value = null
  pickerOpen.value = false
}

function onSelectCoverStyle(style: string, credit: iCoverCredit) {
  releaseLocalCover()

  coverFile.value = null
  uploadedCover.value = null
  coverStyle.value = style
  coverCredit.value = credit
  pickerOpen.value = false
}

function removeCover() {
  releaseLocalCover()

  coverFile.value = null
  uploadedCover.value = null
  coverStyle.value = ''
  coverCredit.value = null
}

onBeforeUnmount(releaseLocalCover)

/** The uploaded file goes in its own multipart request, after the form itself exists. */
async function uploadCoverFile(formId: number) {
  if (!coverFile.value) return

  const formData = new FormData()

  formData.append('cover_image', coverFile.value)
  formData.append('cover_style', '')

  await apiFetch(`${API_FORM_URLS.LIST}/${formId}`, {
    method: 'PATCH',
    body: formData,
  })
}

async function onSubmit() {
  if (!data.title.trim() || submitting.value) {
    return
  }

  submitting.value = true

  try {
    const body: Record<string, unknown> = {
      ...data,
      cover_style: coverStyle.value,
      cover_credit: coverCredit.value,
    }

    // Nothing uploaded and nothing pending — make sure a previous file is cleared.
    if (!uploadedCover.value && !coverFile.value) {
      body.cover_image = null
    }

    if (isEdit.value) {
      await apiFetch(`${API_FORM_URLS.LIST}/${props.form!.id}`, {
        method: 'PATCH',
        body,
      })

      await uploadCoverFile(props.form!.id)

      emit('close', { saved: true })

      return
    }

    const created = await apiFetch<{ id: number }>(API_FORM_URLS.LIST, {
      method: 'POST',
      body,
    })

    await uploadCoverFile(created.id)

    emit('close', {
      created: true,
      id: created.id,
    })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UModal
    :open="true"
    :dismissible="false"
    :close="false"
    :ui="{
      content: 'sm:max-w-7xl',
      footer: 'justify-end',
    }"
  >
    <template #body>
      <form id="form-upsert" class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <!-- Cover, kept faint behind the form fields -->
        <div v-if="hasCover" class="size-full overflow-hidden absolute inset-0 opacity-5 -z-10">
          <img v-if="coverPreview" :src="coverPreview" alt="" class="size-full object-cover" />
          <div v-else class="size-full" :style="coverBackground" />
        </div>

        <!-- Title -->
        <UInput
          v-model="data.title"
          placeholder="Título do formulário"
          size="xl"
          variant="none"
          class="w-full"
          :ui="{ base: 'px-0! text-2xl font-semibold' }"
          autofocus
        />

        <!-- Description -->
        <CRichTextEditor
          v-model="data.description"
          placeholder="Descrição opcional..."
          class="h-96"
        />

        <!-- Options row -->
        <div class="flex flex-wrap items-center gap-2">
          <CFormPublishedSelect v-model="data.is_published" size="xs" />

          <UPopover v-model:open="pickerOpen">
            <UButton
              icon="i-lucide-image"
              size="xs"
              variant="ghost"
              color="neutral"
              :label="hasCover ? 'Alterar capa' : 'Capa'"
            />
            <template #content>
              <CCoverPicker @select-file="onSelectCoverFile" @select-style="onSelectCoverStyle" />
            </template>
          </UPopover>

          <UButton
            v-if="hasCover"
            icon="i-lucide-x"
            size="xs"
            variant="ghost"
            color="neutral"
            label="Remover"
            @click="removeCover"
          />

          <USeparator orientation="vertical" class="h-4 mx-1" />

          <USwitch v-model="data.require_auth" label="Login" size="xs" />
          <USwitch v-model="data.require_identity" label="Identificação" size="xs" />
        </div>
      </form>
    </template>

    <template #footer>
      <UButton label="Cancelar" variant="ghost" color="neutral" size="xs" @click="emit('close')" />
      <UButton
        type="submit"
        form="form-upsert"
        :loading="submitting"
        :disabled="!data.title.trim()"
        :label="isEdit ? 'Salvar' : 'Criar formulário'"
        size="xs"
      />
    </template>
  </UModal>
</template>
