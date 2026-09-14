<script setup lang="ts">
import { getDocumentTypeMeta } from '@/app/features/document/utils'
import { useDocumentType } from '@/app/features/document/composables/documentType'

const props = defineProps<{
  type: number | null
}>()

const { types } = useDocumentType()

const meta = computed(() => getDocumentTypeMeta(types.value, props.type))
</script>

<template>
  <span
    v-if="meta"
    class="inline-flex items-center gap-1 text-[10.5px] text-muted bg-elevated rounded px-1.5 py-0.5 shrink-0"
  >
    <span class="size-1.5 rounded-full shrink-0" :style="{ backgroundColor: meta.color }" />
    {{ meta.name }}
  </span>
</template>
