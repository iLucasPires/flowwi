<script setup lang="ts">
defineOptions({ name: 'BlockInputChoice' })

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

function isSelected(value: string): boolean {
  if (props.config.multiple) return Array.isArray(model.value) && model.value.includes(value)
  return model.value === value
}

function toggle(value: string) {
  if (props.editor) return
  if (props.config.multiple) {
    const current = Array.isArray(model.value) ? [...model.value] : []
    const idx = current.indexOf(value)
    if (idx >= 0) current.splice(idx, 1)
    else current.push(value)
    model.value = current
  } else {
    model.value = value
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <label
      v-for="item in items"
      :key="item.value"
      class="ft-choice-option"
      :class="{ 'ft-choice-option--selected': isSelected(item.value), 'cursor-not-allowed opacity-60': editor }"
    >
      <input
        v-if="config.multiple"
        type="checkbox"
        :value="item.value"
        :checked="isSelected(item.value)"
        :disabled="editor"
        class="sr-only"
        @change="toggle(item.value)"
      />
      <input
        v-else
        type="radio"
        :value="item.value"
        :checked="isSelected(item.value)"
        :disabled="editor"
        class="sr-only"
        @change="toggle(item.value)"
      />
      <span class="ft-choice-indicator" />
      <span class="text-sm">{{ item.label }}</span>
    </label>
  </div>
</template>
