<script setup lang="ts">
import type { iDocumentVersionStatus } from '@/app/features/document/types'
import { cDocumentVersionStatusItems } from '@/app/features/document/constants'

const model = defineModel<iDocumentVersionStatus | undefined>()

interface iProps {
  size?: string
}

defineProps<iProps>()

const isPublished = computed({
  get: () => model.value === 'published',
  set: (value: boolean) => {
    model.value = value ? 'published' : 'draft'
  },
})

const currentItem = computed(() => cDocumentVersionStatusItems.find((i) => i.value === model.value))

const icon = computed(() => currentItem.value?.icon ?? 'i-lucide-file-edit')
const iconColor = computed(() => currentItem.value?.color ?? 'text-neutral-400')

defineOptions({ name: 'DocumentVersionStatusSelect' })
</script>

<template>
  <label class="flex items-center gap-1.5 cursor-pointer select-none">
    <UIcon :name="icon" :class="['size-4 shrink-0', iconColor]" />
    <span class="text-[11.5px] font-medium text-toned">{{ currentItem?.label ?? 'Rascunho' }}</span>
    <USwitch v-model="isPublished" color="success" :size="size" />
  </label>
</template>
