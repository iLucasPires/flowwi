<script setup lang="ts">
defineOptions({ name: 'BlockInputDate' })

defineProps<{
  config: { min_date?: string; max_date?: string }
  editor?: boolean
  size?: 'sm' | 'md' | 'lg'
}>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <input
    v-model="model"
    type="date"
    :min="config.min_date"
    :max="config.max_date"
    :disabled="editor"
    class="ft-input"
  />
</template>
