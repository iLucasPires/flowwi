<script setup lang="ts">
const props = defineProps<{
  isActive?: boolean
}>()

const emit = defineEmits<{
  close: [result?: { isActive?: boolean }]
}>()

const status = ref<'active' | 'inactive' | undefined>(
  props.isActive === true ? 'active' : props.isActive === false ? 'inactive' : undefined,
)

const statusOptions = [
  { label: 'Ativos', value: 'active' as const },
  { label: 'Inativos', value: 'inactive' as const },
]

function clearFilters() {
  status.value = undefined
}

function apply() {
  emit('close', {
    isActive: status.value === 'active' ? true : status.value === 'inactive' ? false : undefined,
  })
}
</script>

<template>
  <USlideover
    :open="true"
    title="Filtros"
    description="Refine a lista de webhooks"
    side="right"
    :dismissible="true"
    @close="emit('close')"
    :ui="{
      content: 'sm:max-w-md',
      header: 'border-none pb-0',
      body: 'flex flex-col gap-4',
      footer: 'flex justify-end gap-2',
    }"
  >
    <template #body>
      <UFormField label="Status" class="w-full">
        <USelect
          v-model="status"
          :items="statusOptions"
          placeholder="Todos"
          size="sm"
          variant="subtle"
          icon="i-lucide-toggle-left"
          class="w-full"
        />
      </UFormField>
    </template>
    <template #footer>
      <UButton
        label="Limpar"
        icon="i-lucide-x"
        size="xs"
        variant="ghost"
        color="neutral"
        @click="clearFilters"
      />
      <UButton label="Aplicar" size="xs" color="primary" variant="solid" @click="apply" />
    </template>
  </USlideover>
</template>
