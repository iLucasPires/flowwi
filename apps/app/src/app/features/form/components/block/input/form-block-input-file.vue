<script setup lang="ts">
defineOptions({ name: 'BlockInputFile' })

const props = defineProps<{
  config: { multiple?: boolean; accept?: string[]; max_size?: number }
  editor?: boolean
}>()

const model = defineModel<File | File[] | null>({ default: null })

const fileName = computed(() => {
  if (!model.value) return ''
  if (Array.isArray(model.value)) return model.value.map((f) => f.name).join(', ')
  return model.value.name
})

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  model.value = props.config.multiple ? Array.from(input.files) : input.files[0]!
}
</script>

<template>
  <label
    class="flex flex-col items-center gap-3 w-full px-6 py-8 rounded-xl border-2 border-dashed transition-colors"
    :class="[
      editor ? 'pointer-events-none opacity-60' : 'cursor-pointer',
      model ? 'border-primary bg-primary/5' : 'border-default hover:border-accented',
    ]"
  >
    <UIcon name="i-lucide-upload" class="size-6 text-muted" />
    <span v-if="fileName" class="text-sm font-medium text-highlighted truncate max-w-full">
      {{ fileName }}
    </span>
    <span v-else class="text-sm text-muted">Clique para selecionar arquivo</span>
    <input
      type="file"
      class="sr-only"
      :disabled="editor"
      :multiple="config.multiple"
      :accept="config.accept?.join(',')"
      @change="onFileChange"
    />
  </label>
</template>
