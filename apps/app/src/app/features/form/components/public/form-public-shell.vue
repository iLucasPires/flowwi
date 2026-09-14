<script setup lang="ts">
import { usePublicForm } from '@/app/features/form/composables/index'
import type { tFormBlockOut } from '@/app/features/form/schemas'

defineOptions({ name: 'FormPublicShell' })

const props = defineProps<{ publicId: string }>()

interface iFormRow {
  columns: number
  blocks: tFormBlockOut[]
}

const {
  stage,
  errorMessage,
  form,
  currentPage,
  isFirstPage,
  isLastPage,
  progress,
  answers,
  isCurrentValid,
  nextPage,
  prevPage,
  load,
  submitIdentity,
  start,
  submit,
} = usePublicForm(props.publicId)

const validationError = ref('')

/**
 * Groups the page's blocks into rows. A run of `n` consecutive fields sharing the same
 * `col_start` (set by the editor's doc converter to "how many columns this row has") becomes
 * one `n`-column row; everything else renders as its own full-width row — mirrors the grouping
 * `formDocConverter.ts` does for the editor, since both read the same flat block list.
 */
const rows = computed<iFormRow[]>(() => {
  const blocks = currentPage.value?.blocks ?? []
  const result: iFormRow[] = []
  let i = 0

  while (i < blocks.length) {
    const block = blocks[i]!
    const rowWidth = block.col_start

    if (block.type !== 'content' && rowWidth >= 2) {
      const row: tFormBlockOut[] = []
      let j = i
      while (j < blocks.length && row.length < rowWidth) {
        const candidate = blocks[j]!
        if (candidate.type === 'content' || candidate.col_start !== rowWidth) break
        row.push(candidate)
        j++
      }
      if (row.length === rowWidth) {
        result.push({ columns: rowWidth, blocks: row })
        i = j
        continue
      }
    }

    result.push({ columns: 1, blocks: [block] })
    i++
  }

  return result
})

function handleNext() {
  validationError.value = ''
  if (!isCurrentValid()) {
    validationError.value = 'Preencha os campos obrigatórios.'
    return
  }
  if (isLastPage.value) {
    submit()
  } else {
    nextPage()
  }
}

function handlePrev() {
  validationError.value = ''
  prevPage()
}

// Submit/advance on Enter, unless the focus is a multi-line field.
const theme = computed(() => (typeof form.value?.theme === 'object' ? form.value.theme : null))
const themeSize = computed(() => theme.value?.input_size ?? 'md')
// Only override the CTA's color once a real accent was chosen — otherwise it keeps its
// original hardcoded black/white look untouched (see comment on the button below).
const hasAccentTheme = computed(() => !!theme.value && theme.value.accent_color !== 'neutral')

function onKeydown(event: KeyboardEvent) {
  if (stage.value !== 'questions') return
  if (event.key !== 'Enter' || event.shiftKey) return
  if (event.target instanceof HTMLTextAreaElement) return
  event.preventDefault()
  handleNext()
}

onMounted(() => {
  load()
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <CFormThemeScope
    :theme="theme"
    root-id="ft-form"
    class="min-h-dvh flex flex-col bg-white dark:bg-[#0f0f0f]"
  >
    <!-- Progress bar -->
    <div
      v-if="stage === 'questions'"
      class="ft-progress fixed top-0 inset-x-0 z-20 h-[2px] bg-neutral-100 dark:bg-neutral-800"
    >
      <div
        class="ft-progress-bar h-full bg-neutral-900 dark:bg-white transition-all duration-700 ease-out"
        :style="{ width: `${progress}%` }"
      />
    </div>

    <!-- Loading -->
    <div v-if="stage === 'loading'" class="flex-1 flex items-center justify-center">
      <UIcon name="i-lucide-loader" class="size-6 animate-spin text-neutral-400" />
    </div>

    <!-- Error -->
    <div
      v-else-if="stage === 'error'"
      class="flex-1 flex flex-col items-center justify-center px-6 gap-5"
    >
      <UIcon name="i-lucide-alert-circle" class="size-10 text-neutral-400" />
      <p class="text-sm font-medium text-neutral-600 dark:text-neutral-400 text-center max-w-sm">
        {{ errorMessage }}
      </p>
    </div>

    <!-- Auth gate -->
    <CFormPublicGate v-else-if="stage === 'gate-auth'" mode="auth" :public-id="publicId" />

    <!-- Identity gate -->
    <CFormPublicGate
      v-else-if="stage === 'gate-identity'"
      mode="identity"
      :public-id="publicId"
      @submit="submitIdentity"
    />

    <!-- Welcome -->
    <CFormPublicWelcome
      v-else-if="stage === 'welcome' && form"
      :title="form.title"
      :description="form.description"
      :cover-image="form.cover_image"
      :cover-style="form.cover_style"
      :cover-credit="form.cover_credit"
      @start="start"
    />

    <!-- Questions: one scrollable page at a time, Tally-style -->
    <template v-else-if="stage === 'questions' && currentPage">
      <div class="flex-1 overflow-y-auto px-6 py-16">
        <Transition name="slide" mode="out-in">
          <div :key="currentPage.id" class="w-full max-w-xl mx-auto flex flex-col gap-8">
            <div v-if="currentPage.title || currentPage.description" class="flex flex-col gap-1">
              <h1
                v-if="currentPage.title"
                class="ft-page-title text-2xl font-semibold tracking-tight text-neutral-900 dark:text-white"
              >
                {{ currentPage.title }}
              </h1>
              <p
                v-if="currentPage.description"
                class="ft-page-description text-sm text-neutral-500 dark:text-neutral-400"
              >
                {{ currentPage.description }}
              </p>
            </div>

            <div class="flex flex-col gap-8">
              <div
                v-for="(row, rowIndex) in rows"
                :key="rowIndex"
                class="grid gap-x-6"
                :style="{ gridTemplateColumns: `repeat(${row.columns}, 1fr)` }"
              >
                <CFormPublicQuestion
                  v-for="block in row.blocks"
                  :key="block.id"
                  :block="block"
                  v-model="answers[block.id]"
                />
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Validation error -->
      <div v-if="validationError" class="fixed bottom-20 left-1/2 -translate-x-1/2 z-30">
        <p class="text-sm text-red-500 bg-white dark:bg-neutral-900 px-3 py-1.5 rounded border border-red-200 dark:border-red-800">
          {{ validationError }}
        </p>
      </div>

      <!-- Bottom navigation — Tally style: minimal, left-aligned -->
      <div class="ft-nav fixed bottom-0 inset-x-0 z-10 pointer-events-none">
        <div class="max-w-xl mx-auto px-6 py-5 flex items-center gap-3">
          <button
            :disabled="isLastPage ? false : false"
            class="ft-btn-next pointer-events-auto ft-input px-5 py-2 font-medium bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 border-neutral-900! hover:opacity-90 transition-opacity"
            :class="hasAccentTheme ? 'bg-[var(--ui-primary)]! text-white! border-[var(--ui-primary)]!' : ''"
            @click="handleNext"
          >
            {{ isLastPage ? 'Enviar' : 'Continuar' }}
          </button>
          <button
            v-if="!isFirstPage"
            class="ft-btn-prev pointer-events-auto text-sm text-neutral-400 dark:text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 transition-colors"
            @click="handlePrev"
          >
            Voltar
          </button>
        </div>
      </div>
    </template>

    <!-- Submitting -->
    <div v-else-if="stage === 'submitting'" class="flex-1 flex items-center justify-center">
      <UIcon name="i-lucide-loader" class="size-6 animate-spin text-neutral-400" />
    </div>

    <!-- Complete -->
    <CFormPublicComplete v-else-if="stage === 'complete'" class="ft-complete" />
  </CFormThemeScope>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
