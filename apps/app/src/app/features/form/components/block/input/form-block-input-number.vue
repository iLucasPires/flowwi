<script setup lang="ts">
defineOptions({ name: 'BlockInputNumber' })

defineProps<{
  config: { min?: number; max?: number; step?: number }
  editor?: boolean
  size?: 'sm' | 'md' | 'lg'
}>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <input
    v-model="model"
    type="number"
    placeholder="0"
    :min="config.min"
    :max="config.max"
    :step="config.step"
    :disabled="editor"
    class="ft-input w-full"
  />
</template>
