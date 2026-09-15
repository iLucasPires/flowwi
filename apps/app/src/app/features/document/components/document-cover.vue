<script setup lang="ts">
import type { iCoverCredit } from '@/app/shared/types/cover'
import { coverBackgroundStyle } from '@/app/shared/utils/cover'
const props = withDefaults(
  defineProps<{
    src?: string | null
    style?: string
    credit?: iCoverCredit
    /** Whether the viewer may change/remove the cover — false renders it read-only. */
    editable?: boolean
  }>(),
  { editable: true },
)

const emit = defineEmits<{
  selectFile: [file: File]
  selectStyle: [style: string, credit: iCoverCredit]
  remove: []
}>()

const open = ref(false)

const hasCover = computed(() => !!props.src || !!props.style)

const styleBackground = computed(() =>
  props.src ? undefined : coverBackgroundStyle(null, props.style),
)

function onSelectFile(file: File) {
  emit('selectFile', file)
  open.value = false
}

function onSelectStyle(style: string, credit: iCoverCredit) {
  emit('selectStyle', style, credit)
  open.value = false
}

defineOptions({ name: 'DocumentCover' })
</script>

<template>
  <div v-if="hasCover" class="relative w-full h-52 sm:h-60 shrink-0 group overflow-hidden">
    <img v-if="src" :src="src" alt="Capa" class="size-full object-cover" />
    <div v-else class="size-full" :style="styleBackground" />

    <CCoverCredit v-if="!src" :credit="credit" class="absolute bottom-3 left-6 z-10" />

    <div
      v-if="editable"
      class="absolute bottom-3 right-6 flex items-center gap-1.5 opacity-0 transition-opacity duration-200 group-hover:opacity-100 z-10"
    >
      <UPopover v-model:open="open">
        <UButton
          icon="i-lucide-image"
          label="Alterar capa"
          size="xs"
          variant="subtle"
          color="neutral"
        />
        <template #content>
          <CCoverPicker @select-file="onSelectFile" @select-style="onSelectStyle" />
        </template>
      </UPopover>

      <UButton
        icon="i-lucide-x"
        label="Remover"
        size="xs"
        variant="subtle"
        color="neutral"
        @click="emit('remove')"
      />
    </div>
  </div>

  <UPopover v-else-if="editable" v-model:open="open">
    <UButton
      icon="i-lucide-image-plus"
      label="Adicionar capa"
      size="xs"
      variant="ghost"
      color="neutral"
    />
    <template #content>
      <CCoverPicker @select-file="onSelectFile" @select-style="onSelectStyle" />
    </template>
  </UPopover>
</template>
