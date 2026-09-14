<script setup lang="ts">
import type { iDocument } from '@/app/features/document/types'
const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  docs: iDocument[]
}>()

const emit = defineEmits<{
  close: [id?: number]
}>()

function pick(id: number) {
  emit('close', id)
}

const groups = computed(() => [
  {
    id: 'docs',
    items: props.docs.map((d) => ({
      id: d.id,
      label: d.title || 'Sem título',
      suffix: d.folder || 'Raiz',
      icon: 'i-lucide-file-edit',
      searchText: d.versions[0]?.content ?? '',
      onSelect: () => pick(d.id),
    })),
  },
])

defineOptions({ name: 'DocumentCommandPalette' })
</script>

<template>
  <UModal
    v-model:open="open"
    :ui="{ content: 'sm:max-w-lg' }"
    :title="'Buscar'"
    :description="'Buscar documentos por título ou conteúdo'"
  >
    <template #content>
      <UCommandPalette
        :groups="groups"
        :fuse="{ fuseOptions: { keys: ['label', 'searchText'] } }"
        placeholder="Buscar documentos, títulos e conteúdo..."
        close
        @update:open="open = $event"
      >
        <template #empty>
          <UEmpty title="Nada encontrado" icon="i-lucide-search-x" variant="naked" size="xs" />
        </template>
      </UCommandPalette>
    </template>
  </UModal>
</template>
