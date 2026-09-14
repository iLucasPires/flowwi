<script setup lang="ts">
const props = defineProps<{
  role?: string
}>()

const emit = defineEmits<{
  close: [result?: { role?: string }]
}>()

const role = ref<string | undefined>(props.role)

const roleOptions = [
  { label: 'Owner', value: 'owner' },
  { label: 'Gerente', value: 'manager' },
  { label: 'Designer', value: 'designer' },
]

function clearFilters() {
  role.value = undefined
}

function apply() {
  emit('close', {
    role: role.value,
  })
}
</script>

<template>
  <USlideover
    :open="true"
    title="Filtros"
    description="Refine a lista de membros"
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
      <UFormField label="Papel" class="w-full">
        <USelect
          v-model="role"
          :items="roleOptions"
          placeholder="Todos"
          size="sm"
          variant="subtle"
          icon="i-lucide-shield-half"
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
