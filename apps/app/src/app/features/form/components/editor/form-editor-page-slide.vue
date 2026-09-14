<script setup lang="ts">
import type { iFormBlockDraft, iFormPageDraft } from '@/app/features/form/types'
import type { iCoverCredit, iCoverUpdate } from '@/app/shared/types/cover'
import { coverBackgroundStyle, coverImageSrc } from '@/app/shared/utils/cover'

defineOptions({ name: 'FormEditorPageSlide' })

const props = defineProps<{
  page: iFormPageDraft
  pageIndex: number
  totalPages: number
  formIcon?: string
  formCoverImage?: string | null
  formCoverStyle?: string
  formCoverCredit?: iCoverCredit
}>()

const emit = defineEmits<{
  'update:page': [value: iFormPageDraft]
  'delete-page': []
  'update:icon': [icon: string]
  'update:cover': [update: iCoverUpdate]
}>()

function updateTitle(val: string) {
  emit('update:page', { ...props.page, title: val })
}

function updateBlocks(blocks: iFormBlockDraft[]) {
  emit('update:page', { ...props.page, blocks })
}

const canDelete = computed(() => props.totalPages > 1)
const isFirstPage = computed(() => props.pageIndex === 0)

const iconProxy = computed({
  get: () => props.formIcon ?? '',
  set: (val: string) => emit('update:icon', val),
})

const hasIcon = computed(() => !!props.formIcon)
const hasCover = computed(() => !!props.formCoverImage || !!props.formCoverStyle)
const coverImageUrl = computed(() => coverImageSrc(props.formCoverImage, props.formCoverStyle))
const coverBackground = computed(() =>
  coverImageUrl.value ? undefined : coverBackgroundStyle(null, props.formCoverStyle),
)
const coverPopoverOpen = ref(false)

function onSelectCoverFile(file: File) {
  emit('update:cover', { file })
  coverPopoverOpen.value = false
}

function onSelectCoverStyle(style: string, credit: iCoverCredit) {
  emit('update:cover', { style, credit })
  coverPopoverOpen.value = false
}

function removeCover() {
  emit('update:cover', null)
}
</script>

<template>
  <div class="flex flex-col h-full overflow-y-auto">
    <!-- Full-bleed cover — only on the form's first page, mirrors CDocumentCover's placement -->
    <div
      v-if="isFirstPage && hasCover"
      class="relative w-full h-40 sm:h-52 shrink-0 group/cover overflow-hidden"
    >
      <img v-if="coverImageUrl" :src="coverImageUrl" alt="Capa" class="size-full object-cover" />
      <div v-else class="size-full" :style="coverBackground" />

      <CCoverCredit v-if="!coverImageUrl" :credit="formCoverCredit" class="absolute bottom-3 left-6 z-10" />

      <div
        class="absolute bottom-3 right-6 flex items-center gap-1.5 opacity-0 transition-opacity duration-200 group-hover/cover:opacity-100 z-10"
      >
        <UPopover v-model:open="coverPopoverOpen">
          <UButton icon="i-lucide-image" label="Alterar capa" size="xs" variant="subtle" color="neutral" />
          <template #content>
            <CCoverPicker @select-file="onSelectCoverFile" @select-style="onSelectCoverStyle" />
          </template>
        </UPopover>

        <UButton icon="i-lucide-x" label="Remover" size="xs" variant="subtle" color="neutral" @click="removeCover" />
      </div>
    </div>

    <div
      class="w-full max-w-2xl mx-auto px-6 sm:px-0 pb-14 flex flex-col gap-8"
      :class="isFirstPage && hasCover ? 'pt-0' : 'pt-14'"
    >
      <!-- Logo + add-cover row — only on the form's first page, mirrors document header -->
      <div v-if="isFirstPage" class="relative group/header">
        <div
          v-if="hasIcon"
          :class="hasCover ? '-mt-14 relative z-10 inline-block' : 'inline-block mb-1'"
        >
          <CIconPicker
            v-model="iconProxy"
            fallback="i-lucide-image"
            icon-class="size-6 text-2xl text-white"
            button-class="rounded-full! size-14! p-0! justify-center! bg-neutral-950! hover:bg-neutral-900! ring-4! ring-[var(--ui-bg)]!"
          />
        </div>

        <div
          class="flex items-center gap-1 transition-opacity duration-200"
          :class="[
            hasIcon ? 'mt-1' : hasCover ? 'pt-3' : 'mb-1',
            !hasIcon || !hasCover
              ? 'opacity-0 group-hover/header:opacity-100 focus-within:opacity-100'
              : 'hidden',
          ]"
        >
          <CIconPicker v-if="!hasIcon" v-model="iconProxy" empty-label="Adicionar logo" fallback="i-lucide-image" />

          <UPopover v-if="!hasCover" v-model:open="coverPopoverOpen">
            <UButton icon="i-lucide-image-plus" label="Adicionar capa" size="xs" variant="ghost" color="neutral" />
            <template #content>
              <CCoverPicker @select-file="onSelectCoverFile" @select-style="onSelectCoverStyle" />
            </template>
          </UPopover>
        </div>
      </div>

      <!-- Page header: title + optional delete -->
      <div class="flex items-start gap-3 group/page-header">
        <div class="flex-1 flex flex-col gap-1">
          <!-- Page number chip — only shown when there are multiple pages -->
          <span v-if="totalPages > 1" class="text-[11px] font-medium text-muted tracking-widest uppercase select-none">
            Página {{ pageIndex + 1 }}
          </span>

          <input
            :value="page.title"
            type="text"
            placeholder="Título da página (opcional)"
            class="w-full bg-transparent text-2xl sm:text-3xl font-bold tracking-tight text-highlighted border-0 p-0 focus:outline-none focus:ring-0 placeholder:text-dimmed/50"
            @input="updateTitle(($event.target as HTMLInputElement).value)"
          />
        </div>

        <!-- Delete page — appears on hover, only when more than 1 page -->
        <UTooltip v-if="canDelete" text="Excluir página">
          <UButton
            icon="i-lucide-trash-2"
            color="neutral"
            variant="ghost"
            size="xs"
            class="opacity-0 group-hover/page-header:opacity-100 mt-1 transition-opacity"
            @click="emit('delete-page')"
          />
        </UTooltip>
      </div>

      <!-- Document editor -->
      <CFormEditorDocument :page="page" @update:blocks="updateBlocks" />
    </div>
  </div>
</template>
