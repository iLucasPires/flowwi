<script setup lang="ts">
const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  title: string
}>()

const emit = defineEmits<{
  close: [title: string | null]
}>()

const value = ref(props.title)

function confirm() {
  emit('close', value.value.trim())
}

defineOptions({ name: 'DocumentRenameDialog' })
</script>

<template>
  <UModal v-model:open="open" title="Renomear documento" :ui="{ content: 'sm:max-w-sm' }">
    <template #body>
      <UInput
        v-model="value"
        placeholder="Sem título"
        autofocus
        size="xs"
        class="w-full"
        @keyup.enter="confirm"
      />
    </template>

    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton
          label="Cancelar"
          variant="ghost"
          color="neutral"
          size="xs"
          @click="emit('close', null)"
        />
        <UButton label="Renomear" size="xs" @click="confirm" />
      </div>
    </template>
  </UModal>
</template>
