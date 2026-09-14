<script setup lang="ts">
defineOptions({ name: 'BlockInputTime' })

defineProps<{
  config: Record<string, unknown>
  editor?: boolean
  size?: 'sm' | 'md' | 'lg'
}>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <input
    v-model="model"
    type="time"
    :disabled="editor"
    class="ft-input"
  />
</template>
