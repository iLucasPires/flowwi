<script setup lang="ts">
import { useFormEditor } from '@/app/features/form/composables/index'
import type { iFormPageDraft } from '@/app/features/form/types'

defineOptions({ name: 'FormEditorPage' })

const route = useRoute()
const router = useRouter()
const toast = useToast()
const overlay = useOverlay()

const carousel = useTemplateRef('carousel')

const {
  formData,
  loading,
  isSaving,
  hasError,
  lastSavedAt,
  selectedPage,
  pages,
  allBlocks,
  load,
  addPage,
  removePage,
  onTitleInput,
  updateIcon,
  updateCover,
  updateTheme,
} = useFormEditor(String(route.params.id))

async function openThemeDialog() {
  if (!formData.value) return
  const component = resolveComponent('CFormThemeDialog')
  if (typeof component !== 'object') return

  const result = (await overlay
    .create(component, { props: { form: formData.value } })
    .open()) as { themeId?: number | null } | undefined

  if (result && 'themeId' in result) {
    updateTheme(result.themeId ?? null)
  }
}

provide('formEditorAllBlocks', allBlocks)

function scrollTo(index: number) {
  selectedPage.value = index
  carousel.value?.emblaApi?.scrollTo(index)
}

function handleAddPage() {
  addPage()
  nextTick(() => {
    carousel.value?.emblaApi?.reInit()
    nextTick(() => scrollTo(pages.value.length - 1))
  })
}

function handleUpdatePage(value: iFormPageDraft) {
  pages.value[selectedPage.value] = value
}

function handleDeletePage() {
  if (pages.value.length <= 1) return
  const indexToRemove = selectedPage.value

  removePage(indexToRemove)
  const newIndex = Math.min(indexToRemove, pages.value.length - 1)

  nextTick(() => {
    carousel.value?.emblaApi?.reInit()
    nextTick(() => scrollTo(newIndex))
  })
}

function onCarouselSelect(index: number) {
  selectedPage.value = index
}

function copyPublicLink() {
  if (!formData.value) return
  navigator.clipboard.writeText(`${window.location.origin}/public/form/${formData.value.public_id}`)
  toast.add({ title: 'Link copiado!', color: 'success' })
}

onMounted(load)
</script>

<template>
  <!-- Full-height layout, Tally-style: own header, no card wrapper -->
  <div class="flex flex-col h-full min-h-0 bg-default">
    <!-- Top bar -->
    <header class="shrink-0 flex items-center gap-3 px-4 h-11 border-b border-default">
      <!-- Left: back -->
      <UTooltip text="Voltar para formulários">
        <UButton
          icon="i-lucide-arrow-left"
          color="neutral"
          variant="ghost"
          size="sm"
          @click="router.push('/dashboard/forms')"
        />
      </UTooltip>

      <!-- Center: form title inline-editable + page indicators -->
      <div class="flex-1 flex items-center justify-center gap-4 min-w-0">
        <template v-if="formData">
          <input
            :value="formData.title"
            type="text"
            placeholder="Sem título"
            class="bg-transparent text-sm font-medium text-highlighted border-0 p-0 focus:outline-none focus:ring-0 placeholder:text-dimmed max-w-56 truncate text-center"
            @input="onTitleInput(($event.target as HTMLInputElement).value)"
          />

          <!-- Page indicators -->
          <div v-if="pages.length > 0" class="flex items-center gap-1.5">
            <button
              v-for="(_, pageIdx) in pages"
              :key="pageIdx"
              type="button"
              class="rounded-full transition-all duration-150"
              :class="
                pageIdx === selectedPage
                  ? 'w-4 h-1.5 bg-highlighted'
                  : 'w-1.5 h-1.5 bg-muted hover:bg-toned'
              "
              @click="scrollTo(pageIdx)"
            />
            <UTooltip text="Adicionar página">
              <button
                type="button"
                class="size-4 flex items-center justify-center rounded-full text-muted hover:text-highlighted hover:bg-elevated transition-colors"
                @click="handleAddPage"
              >
                <UIcon name="i-lucide-plus" class="size-3" />
              </button>
            </UTooltip>
          </div>
        </template>
      </div>

      <!-- Right: actions -->
      <div class="flex items-center gap-2 shrink-0">
        <UBadge
          v-if="formData"
          :label="formData.is_published ? 'Publicado' : 'Rascunho'"
          variant="subtle"
          :color="formData.is_published ? 'success' : 'neutral'"
          size="sm"
        />
        <UTooltip text="Tema">
          <UButton
            icon="i-lucide-palette"
            color="neutral"
            variant="ghost"
            size="sm"
            @click="openThemeDialog"
          />
        </UTooltip>
        <UTooltip text="Copiar link público">
          <UButton
            icon="i-lucide-link"
            color="neutral"
            variant="ghost"
            size="sm"
            @click="copyPublicLink"
          />
        </UTooltip>
      </div>
    </header>

    <!-- Body -->
    <div class="flex-1 min-h-0 overflow-hidden" :class="{ 'animate-shake': hasError }">
      <!-- Loading -->
      <div v-if="loading" class="h-full flex items-center justify-center">
        <UIcon name="i-lucide-loader" class="size-5 animate-spin text-muted" />
      </div>

      <template v-else>
        <!-- Slide area: plain overflow-hidden, UCarousel hidden. We drive it programmatically. -->
        <UCarousel
          class="h-full"
          ref="carousel"
          :items="pages"
          :watch-drag="false"
          :ui="{
            viewport: 'h-full',
            container: 'h-full',
            item: 'h-full',
          }"
          @select="onCarouselSelect"
        >
          <template #default="{ item: page, index }">
            <CFormEditorPageSlide
              :page="page"
              :page-index="index"
              :total-pages="pages.length"
              :form-icon="formData?.icon"
              :form-cover-image="formData?.cover_image"
              :form-cover-style="formData?.cover_style"
              :form-cover-credit="formData?.cover_credit"
              @update:page="handleUpdatePage"
              @delete-page="handleDeletePage"
              @update:icon="updateIcon"
              @update:cover="updateCover"
            />
          </template>
        </UCarousel>
      </template>
    </div>

    <!-- Save status — bottom center, unobtrusive -->
    <CFormEditorStatusBadge :is-saving="isSaving" :has-error="hasError" :last-saved-at="lastSavedAt" />
  </div>
</template>
