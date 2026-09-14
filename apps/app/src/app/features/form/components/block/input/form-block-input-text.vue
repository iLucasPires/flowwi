<script setup lang="ts">
defineOptions({ name: 'BlockInputText' })

defineProps<{
  config: { long?: boolean; max_length?: number }
  editor?: boolean
  size?: 'sm' | 'md' | 'lg'
}>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <textarea
    v-if="config.long"
    v-model="model"
    placeholder="Digite sua resposta..."
    :maxlength="config.max_length"
    :disabled="editor"
    rows="4"
    class="ft-input w-full resize-none"
  />
  <input
    v-else
    v-model="model"
    type="text"
    placeholder="Digite sua resposta..."
    :maxlength="config.max_length"
    :disabled="editor"
    class="ft-input w-full"
  />
</template>
