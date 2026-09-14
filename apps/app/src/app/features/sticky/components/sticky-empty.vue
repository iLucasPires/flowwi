<script setup lang="ts">
const emit = defineEmits(['create'])
</script>

<template>
  <UEmpty
    title="Nenhuma sticky encontrada"
    description="Faça uma nova sticky para começar."
    icon="i-lucide-sticky-note"
    variant="subtle"
    size="sm"
    class="h-full"
  >
    <template #actions>
      <UButton
        label="Criar sticky"
        icon="i-lucide-plus"
        color="primary"
        size="sm"
        @click="emit('create')"
      />
    </template>
  </UEmpty>
</template>
