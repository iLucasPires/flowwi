<script setup lang="ts">
import type { NodeViewProps } from '@tiptap/vue-3'
import { NodeViewWrapper } from '@tiptap/vue-3'

defineOptions({ name: 'DocumentEditorImageUploadNode' })

const props = defineProps<NodeViewProps>()

const MAX_SIZE = 2 * 1024 * 1024

const toast = useToast()
const file = ref<File | null>(null)
const loading = ref(false)

watch(file, async (newFile) => {
  if (!newFile) return

  if (newFile.size > MAX_SIZE) {
    toast.add({ title: 'Imagem muito grande (máx. 2MB)', color: 'error' })
    file.value = null
    return
  }

  loading.value = true

  const reader = new FileReader()
  reader.onload = () => {
    const dataUrl = reader.result as string
    loading.value = false

    if (!dataUrl) return

    const pos = props.getPos()
    if (typeof pos !== 'number') return

    props.editor
      .chain()
      .focus()
      .deleteRange({ from: pos, to: pos + 1 })
      .setImage({ src: dataUrl })
      .run()
  }
  reader.onerror = () => {
    loading.value = false
    toast.add({ title: 'Erro ao ler a imagem', color: 'error' })
    file.value = null
  }
  reader.readAsDataURL(newFile)
})
</script>

<template>
  <NodeViewWrapper>
    <UFileUpload
      v-model="file"
      accept="image/*"
      label="Enviar uma imagem"
      description="SVG, PNG, JPG ou GIF (máx. 2MB)"
      :preview="false"
      class="min-h-48"
    >
      <template #leading>
        <UAvatar
          :icon="loading ? 'i-lucide-loader-circle' : 'i-lucide-image'"
          size="xl"
          :ui="{ icon: [loading && 'animate-spin'] }"
        />
      </template>
    </UFileUpload>
  </NodeViewWrapper>
</template>
