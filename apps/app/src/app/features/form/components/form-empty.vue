<script setup lang="ts">
const emit = defineEmits(['create'])
</script>

<template>
  <UEmpty
    title="Nenhum formulário"
    description="Crie seu primeiro modelo."
    icon="i-lucide-file-text"
    variant="subtle"
    size="sm"
    class="h-full"
  >
    <template #actions>
      <UButton
        label="Criar template"
        icon="i-lucide-plus"
        variant="solid"
        size="sm"
        @click="emit('create')"
      />
    </template>
  </UEmpty>
</template>
