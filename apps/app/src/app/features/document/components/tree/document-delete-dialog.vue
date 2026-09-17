<script setup lang="ts">
const open = defineModel<boolean>('open', { required: true })

defineProps<{
  title: string
}>()

const emit = defineEmits<{
  close: [confirmed: boolean]
}>()

defineOptions({ name: 'DocumentDeleteDialog' })
</script>

<template>
  <UModal
    v-model:open="open"
    title="Excluir documento?"
    :description="`“${title}” será movido para a lixeira e pode ser restaurado depois.`"
    :ui="{ content: 'sm:max-w-sm' }"
  >
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton
          label="Cancelar"
          variant="ghost"
          color="neutral"
          size="md"
          @click="emit('close', false)"
        />
        <UButton label="Excluir" color="error" size="md" @click="emit('close', true)" />
      </div>
    </template>
  </UModal>
</template>
