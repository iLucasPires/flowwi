<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  as?: keyof HTMLElementTagNameMap
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'
  weight?: 'normal' | 'medium' | 'semibold' | 'bold'
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  as: 'p',
  size: 'base',
  weight: 'normal',
})

const sizeClasses = {
  xs: 'text-xs',
  sm: 'text-sm',
  base: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl',
  '2xl': 'text-2xl',
  '3xl': 'text-3xl',
  '4xl': 'text-4xl',
}

const weightClasses = {
  normal: 'font-normal',
  medium: 'font-medium',
  semibold: 'font-semibold',
  bold: 'font-bold',
}

const defaultColor = computed(() => {
  if (props.color) return props.color

  switch (props.size) {
    case '3xl':
    case '4xl':
      return 'text-neutral-800 dark:text-neutral-100'

    case '2xl':
    case 'xl':
      return 'text-neutral-700 dark:text-neutral-200'

    case 'lg':
    case 'base':
      return 'text-neutral-600 dark:text-neutral-300'

    case 'sm':
    case 'xs':
      return 'text-neutral-500 dark:text-neutral-400'

    default:
      return 'text-neutral-600 dark:text-neutral-300'
  }
})

const classes = computed(() => [
  sizeClasses[props.size],
  weightClasses[props.weight],
  defaultColor.value,
])
</script>

<template>
  <component :is="as" :class="classes">
    <slot>{{ text }}</slot>
  </component>
</template>
