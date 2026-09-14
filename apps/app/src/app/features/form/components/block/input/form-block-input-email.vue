<script setup lang="ts">
defineOptions({ name: 'BlockInputEmail' })

defineProps<{
  config: { max_length?: number }
  editor?: boolean
  size?: 'sm' | 'md' | 'lg'
}>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <input
    v-model="model"
    type="email"
    placeholder="nome@exemplo.com"
    :maxlength="config.max_length"
    :disabled="editor"
    class="ft-input w-full"
  />
</template>
