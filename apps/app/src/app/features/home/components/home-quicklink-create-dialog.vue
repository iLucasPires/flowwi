<script setup lang="ts">
import { useQuicklink } from '@/app/features/home/composables/quicklink'

const open = defineModel<boolean>('open', { required: true })

const { createQuicklink, creating } = useQuicklink()

const title = ref('')
const url = ref('')

watch(open, (isOpen) => {
  if (isOpen) {
    title.value = ''
    url.value = ''
  }
})

async function onSubmit() {
  await createQuicklink({ title: title.value.trim(), url: url.value.trim() })
  open.value = false
}
</script>

<template>
  <UModal v-model:open="open" title="Adicionar link" :ui="{ content: 'sm:max-w-md' }">
    <template #body>
      <form id="quicklink-create-form" class="flex flex-col gap-3" @submit.prevent="onSubmit">
        <UFormField label="Título" name="title">
          <UInput v-model="title" placeholder="Ex: Figma do projeto" class="w-full" autofocus />
        </UFormField>

        <UFormField label="URL" name="url">
          <UInput v-model="url" type="url" placeholder="https://..." class="w-full" />
        </UFormField>
      </form>
    </template>

    <template #footer>
      <UButton label="Cancelar" variant="ghost" color="neutral" size="xs" @click="open = false" />
      <UButton
        type="submit"
        form="quicklink-create-form"
        label="Adicionar"
        size="xs"
        :loading="creating"
        :disabled="!title.trim() || !url.trim()"
      />
    </template>
  </UModal>
</template>
