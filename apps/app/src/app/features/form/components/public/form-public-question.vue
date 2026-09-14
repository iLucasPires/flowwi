<script setup lang="ts">
import { generateHTML } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import { useFormThemeSize } from '@/app/features/form/composables/formTheme'
import type { tFormBlockOut } from '@/app/features/form/schemas'

defineOptions({ name: 'FormPublicQuestion' })

const props = defineProps<{
  block: tFormBlockOut
}>()

const model = defineModel<unknown>()

const themeSize = useFormThemeSize()
const blockType = computed(() => props.block.type)
const blockConfig = computed(() => props.block.config ?? {})

const contentHtml = computed(() => {
  if (blockType.value !== 'content') return ''
  const node = blockConfig.value.node as Record<string, unknown> | null | undefined
  if (!node) return ''
  return generateHTML({ type: 'doc', content: [node] }, [StarterKit])
})
</script>

<template>
  <!-- Free-text content block: no input, just rendered text -->
  <div
    v-if="blockType === 'content'"
    class="ft-content prose prose-neutral dark:prose-invert prose-sm max-w-none [&_:first-child]:mt-0 [&_:last-child]:mb-0"
    v-html="contentHtml"
  />

  <!-- Answerable field -->
  <div v-else class="ft-question flex flex-col gap-2">
    <p class="ft-question-label text-[15px] font-medium leading-snug">
      {{ block.title }}
      <span v-if="block.required" class="text-red-500 ml-0.5 select-none">*</span>
    </p>

    <div class="ft-field">
      <CFormBlockInputText
        v-if="blockType === 'text'"
        v-model="model as string"
        :config="blockConfig"
        :size="themeSize"
      />
      <CFormBlockInputEmail
        v-else-if="blockType === 'email'"
        v-model="model as string"
        :config="blockConfig"
        :size="themeSize"
      />
      <CFormBlockInputNumber
        v-else-if="blockType === 'number'"
        v-model="model as string"
        :config="blockConfig"
        :size="themeSize"
      />
      <CFormBlockInputDate
        v-else-if="blockType === 'date'"
        v-model="model as string"
        :config="blockConfig"
        :size="themeSize"
      />
      <CFormBlockInputTime
        v-else-if="blockType === 'time'"
        v-model="model as string"
        :config="blockConfig"
        :size="themeSize"
      />
      <CFormBlockInputSelect
        v-else-if="blockType === 'select'"
        v-model="model as string | string[]"
        :config="blockConfig"
        :size="themeSize"
      />
      <CFormBlockInputChoice
        v-else-if="blockType === 'choice'"
        v-model="model as string | string[]"
        :config="blockConfig"
        :size="themeSize"
      />
      <CFormBlockInputFile
        v-else-if="blockType === 'file'"
        v-model="model as File | File[] | null"
        :config="blockConfig"
      />
    </div>
  </div>
</template>
