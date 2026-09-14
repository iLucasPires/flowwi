<script setup lang="ts">
defineProps<{
  isSaving: boolean
  hasError: boolean
  lastSavedAt: Date | null
}>()
</script>

<template>
  <div class="flex items-center justify-center gap-3 pb-2 z-50">
    <span v-if="hasError" class="flex items-center gap-1 text-xs text-red-500">
      <UIcon name="i-lucide-alert-circle" class="size-3" />
      Erro ao salvar
    </span>
    <span v-else-if="isSaving" class="flex items-center gap-1 text-xs text-muted">
      <UIcon name="i-lucide-loader" class="size-3 animate-spin" />
      Salvando...
    </span>
    <span v-else-if="lastSavedAt" class="flex items-center gap-1 text-xs text-muted">
      <UIcon name="i-lucide-check" class="size-3 text-green-500" />
      Salvo
    </span>
  </div>
</template>
