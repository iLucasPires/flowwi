<script setup lang="ts">
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
const { workplace } = useWorkplace()
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-lg font-semibold">Workspace</h2>
      <p class="text-sm text-dimmed mt-1">Configurações gerais do workspace.</p>
    </div>

    <CWorkplaceGeneralForm v-if="workplace" :workplace="workplace" />

    <UEmpty
      v-else
      title="Nenhum workspace selecionado"
      description="Selecione um workspace para ver as configurações."
      icon="i-lucide-building-2"
      variant="subtle"
      size="sm"
    />
  </div>
</template>
