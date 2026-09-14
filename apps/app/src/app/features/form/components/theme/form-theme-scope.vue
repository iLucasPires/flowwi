<script setup lang="ts">
import {
  FORM_THEME_KEY,
  formThemeScopedCss,
  formThemeStyleVars,
} from '@/app/features/form/composables/formTheme'
import type { tFormThemeOut } from '@/app/features/form/schemas'

defineOptions({ name: 'FormThemeScope' })

const props = defineProps<{
  theme?: tFormThemeOut | null
  /** Only the real public page should claim this id — omit it in previews to avoid duplicates. */
  rootId?: string
}>()

const themeRef = computed(() => props.theme)
provide(FORM_THEME_KEY, themeRef)

const styleVars = computed(() => formThemeStyleVars(props.theme))
const scopedCss = computed(() => formThemeScopedCss(props.theme))
</script>

<template>
  <div :id="rootId" class="ft-root" :style="styleVars">
    <Teleport v-if="scopedCss" to="head">
      <style :textContent="scopedCss" />
    </Teleport>
    <slot />
  </div>
</template>
