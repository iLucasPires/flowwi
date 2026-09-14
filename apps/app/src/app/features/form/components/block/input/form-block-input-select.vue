<script setup lang="ts">
defineOptions({ name: 'BlockInputSelect' })

const props = defineProps<{
  config: { options?: { label: string; value: string | number }[]; multiple?: boolean }
  editor?: boolean
  size?: 'sm' | 'md' | 'lg'
}>()

const model = defineModel<string | string[]>()

const items = computed(() =>
  (props.config.options ?? []).map((opt, index) => ({
    label: opt.label || `Opção ${index + 1}`,
    value: opt.value ? String(opt.value) : `__opt_${index}`,
  })),
)
</script>

<template>
  <select
    v-model="model"
    :multiple="config.multiple"
    :disabled="editor"
    class="ft-input w-full"
  >
    <option value="" disabled selected hidden>Selecione uma opção...</option>
    <option v-for="item in items" :key="item.value" :value="item.value">
      {{ item.label }}
    </option>
  </select>
</template>
