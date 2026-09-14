<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
})

const props = defineProps<{
  value?: string
  fallback?: string
}>()

const isEmoji = computed(() => {
  return !!props.value && !props.value.startsWith('i-')
})

const icon = computed(() => {
  return props.value || props.fallback || 'i-lucide-box'
})
</script>

<template>
  <span
    v-if="isEmoji"
    v-bind="$attrs"
    class="inline-flex items-center justify-center leading-none"
    v-text="props.value"
  />

  <UIcon
    v-else
    :name="icon"
    v-bind="$attrs"
  />
</template>

