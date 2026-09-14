<script setup lang="ts">
import type { iCoverCredit } from '@/app/shared/types/cover'
import { coverBackgroundStyle } from '@/app/shared/utils/cover'
const props = withDefaults(
  defineProps<{
    /** Uploaded cover file URL — takes precedence over `styleValue`. */
    src?: string | null
    /** CSS color/gradient or external image URL used when there is no uploaded file. */
    styleValue?: string
    credit?: iCoverCredit
    heightClass?: string
    emptyLabel?: string
  }>(),
  {
    src: null,
    styleValue: '',
    credit: null,
    heightClass: 'h-48',
    emptyLabel: 'Adicionar capa',
  },
)

const emit = defineEmits<{
  selectFile: [file: File]
  selectStyle: [style: string, credit: iCoverCredit]
  remove: []
}>()

const open = ref(false)

const hasCover = computed(() => !!props.src || !!props.styleValue)

const styleBackground = computed(() =>
  props.src ? undefined : coverBackgroundStyle(null, props.styleValue),
)

function onSelectFile(file: File) {
  emit('selectFile', file)
  open.value = false
}

function onSelectStyle(style: string, credit: iCoverCredit) {
  emit('selectStyle', style, credit)
  open.value = false
}

defineOptions({ name: 'CoverBanner' })
</script>

<template>
  <div
    class="relative w-full rounded-md overflow-hidden bg-neutral-100 dark:bg-neutral-800 group"
    :class="heightClass"
  >
    <img v-if="src" :src="src" alt="Capa" loading="lazy" class="size-full object-cover" />
    <div v-else-if="styleValue" class="size-full" :style="styleBackground" />

    <CCoverCredit v-if="!src" :credit="credit" class="absolute top-2 left-3 z-10" />

    <div
      class="absolute bottom-2 right-3 flex items-center gap-1.5 transition-opacity duration-200 z-10"
      :class="hasCover ? 'opacity-0 group-hover:opacity-100' : 'opacity-100'"
    >
      <UPopover v-model:open="open">
        <UButton
          :icon="hasCover ? 'i-lucide-image' : 'i-lucide-image-plus'"
          :label="hasCover ? 'Alterar capa' : emptyLabel"
          size="xs"
          variant="subtle"
          color="neutral"
        />
        <template #content>
          <CCoverPicker @select-file="onSelectFile" @select-style="onSelectStyle" />
        </template>
      </UPopover>

      <UButton
        v-if="hasCover"
        icon="i-lucide-x"
        label="Remover"
        size="xs"
        variant="subtle"
        color="neutral"
        @click="emit('remove')"
      />
    </div>
  </div>
</template>
