<script setup lang="ts">
import {
  formThemeStyleVars,
  useFormThemes,
  type iFormThemeStyleInput,
  type iGeneratedFormTheme,
} from '@/app/features/form/composables/formTheme'
import {
  FormThemeAccentColors,
  FormThemeFonts,
  FormThemeInputSizes,
  FormThemeRadii,
  type tFormThemeOut,
} from '@/app/features/form/schemas'
import type { iCoverCredit } from '@/app/shared/types/cover'
import { coverBackgroundStyle, coverImageSrc } from '@/app/shared/utils/cover'

defineOptions({ name: 'FormThemeDialog' })

const props = defineProps<{
  form: { id: number; theme?: number | tFormThemeOut | null }
}>()

const emit = defineEmits<{ close: [result?: { themeId: number | null }] }>()

const toast = useToast()
const { themes, loading, list, create, update, uploadBackground, remove, duplicate, generate } =
  useFormThemes()

const currentThemeId = computed(() =>
  typeof props.form.theme === 'object' ? (props.form.theme?.id ?? null) : (props.form.theme ?? null),
)

const selectedId = ref<number | null>(currentThemeId.value)
const draft = reactive<{
  name: string
  accent_color: (typeof FormThemeAccentColors)[number]
  radius: (typeof FormThemeRadii)[number]
  input_size: (typeof FormThemeInputSizes)[number]
  font: (typeof FormThemeFonts)[number]
  cover_style: string
  cover_credit: iCoverCredit
  custom_css: string
}>({
  name: '',
  accent_color: 'neutral',
  radius: 'md',
  input_size: 'md',
  font: 'sans',
  cover_style: '',
  cover_credit: null,
  custom_css: '',
})
const pendingBackgroundFile = ref<File | null>(null)
const localBackgroundUrl = ref<string | null>(null)
const saving = ref(false)
const aiPrompt = ref('')
const aiLoading = ref(false)

const selectedTheme = computed(() => themes.value.find((t) => t.id === selectedId.value) ?? null)
const isEditable = computed(() => !!selectedTheme.value && !selectedTheme.value.is_preset)

function loadDraft(theme: tFormThemeOut | null) {
  pendingBackgroundFile.value = null
  releaseLocalBackground()
  if (!theme) return
  draft.name = theme.name
  draft.accent_color = theme.accent_color
  draft.radius = theme.radius
  draft.input_size = theme.input_size
  draft.font = theme.font
  draft.cover_style = theme.cover_style
  draft.cover_credit = theme.cover_credit
  draft.custom_css = theme.custom_css
}

watch(selectedTheme, (theme) => loadDraft(theme))

function releaseLocalBackground() {
  if (localBackgroundUrl.value) {
    URL.revokeObjectURL(localBackgroundUrl.value)
    localBackgroundUrl.value = null
  }
}

function selectTheme(theme: tFormThemeOut) {
  selectedId.value = theme.id
}

async function createTheme(fields: Record<string, unknown> = {}) {
  const created = await create({ name: 'Novo tema', ...fields })
  selectedId.value = created.id
  return created
}

async function duplicateTheme(theme: tFormThemeOut) {
  const copy = await duplicate(theme.id)
  selectedId.value = copy.id
  toast.add({ title: 'Tema duplicado — já pode ser customizado', color: 'success' })
}

async function deleteTheme(theme: tFormThemeOut) {
  await remove(theme.id)
  if (selectedId.value === theme.id) selectedId.value = null
}

function onSelectBackgroundFile(file: File) {
  releaseLocalBackground()
  pendingBackgroundFile.value = file
  localBackgroundUrl.value = URL.createObjectURL(file)
  draft.cover_style = ''
  draft.cover_credit = null
}

function onSelectBackgroundStyle(style: string, credit: iCoverCredit) {
  releaseLocalBackground()
  pendingBackgroundFile.value = null
  draft.cover_style = style
  draft.cover_credit = credit
}

async function saveDraft() {
  if (!selectedTheme.value) return
  saving.value = true
  try {
    await update(selectedTheme.value.id, {
      name: draft.name,
      accent_color: draft.accent_color,
      radius: draft.radius,
      input_size: draft.input_size,
      font: draft.font,
      cover_style: draft.cover_style,
      cover_credit: draft.cover_credit,
      custom_css: draft.custom_css,
    })
    if (pendingBackgroundFile.value) {
      await uploadBackground(selectedTheme.value.id, pendingBackgroundFile.value)
      pendingBackgroundFile.value = null
    }
    toast.add({ title: 'Tema salvo', color: 'success' })
  } catch {
    toast.add({ title: 'Erro ao salvar tema', color: 'error' })
  } finally {
    saving.value = false
  }
}

async function runAiGenerate() {
  if (!aiPrompt.value.trim() || aiLoading.value) return
  aiLoading.value = true
  try {
    const result = await generate(aiPrompt.value)
    if (!isEditable.value) {
      await createTheme({ name: result.name || 'Tema gerado' })
    }
    applyGenerated(result)
    toast.add({ title: 'Sugestão aplicada — revise e salve', color: 'success' })
  } catch {
    toast.add({ title: 'Erro ao gerar tema', color: 'error' })
  } finally {
    aiLoading.value = false
  }
}

function applyGenerated(result: iGeneratedFormTheme) {
  if (result.name) draft.name = result.name
  draft.accent_color = result.accent_color
  draft.radius = result.radius
  draft.input_size = result.input_size
  draft.font = result.font
  if (result.background_style) {
    releaseLocalBackground()
    pendingBackgroundFile.value = null
    draft.cover_style = result.background_style
    draft.cover_credit = null
  }
  draft.custom_css = result.custom_css
}

const backgroundPreview = computed(
  () => localBackgroundUrl.value ?? coverImageSrc(selectedTheme.value?.background_image, draft.cover_style),
)
const backgroundStyle = computed(() =>
  backgroundPreview.value ? undefined : coverBackgroundStyle(null, draft.cover_style),
)

const previewTheme = computed<iFormThemeStyleInput>(() => ({
  accent_color: draft.accent_color,
  radius: draft.radius,
  font: draft.font,
  cover_style: draft.cover_style,
  background_image: localBackgroundUrl.value ?? selectedTheme.value?.background_image ?? null,
}))
const previewVars = computed(() => formThemeStyleVars(previewTheme.value))

const radiusLabels: Record<string, string> = { none: 'Nenhum', sm: 'Pequeno', md: 'Médio', lg: 'Grande', xl: 'Extra' }
const sizeLabels: Record<string, string> = { sm: 'Pequeno', md: 'Médio', lg: 'Grande' }
const fontLabels: Record<string, string> = { sans: 'Sem serifa', serif: 'Serifa', mono: 'Monoespaçada' }
const fontPreviewStacks: Record<string, string> = {
  serif: 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
  mono: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
}

onMounted(list)
</script>

<template>
  <UModal :open="true" :dismissible="false" :close="false" title="Temas do formulário" :ui="{ content: 'sm:max-w-6xl' }">
    <template #body>
      <div class="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-6 min-h-[28rem]">
        <!-- Gallery -->
        <div class="flex flex-col gap-2 overflow-y-auto max-h-[32rem] pr-1">
          <UButton
            label="Novo tema"
            icon="i-lucide-plus"
            color="neutral"
            variant="subtle"
            size="sm"
            block
            @click="createTheme()"
          />

          <UCard
            v-for="theme in themes"
            :key="theme.id"
            class="cursor-pointer transition-colors"
            :class="selectedId === theme.id ? 'ring-2 ring-primary' : 'hover:bg-elevated'"
            :ui="{ body: 'p-3' }"
            @click="selectTheme(theme)"
          >
            <div class="flex items-center gap-2">
              <span
                class="size-4 rounded-full shrink-0"
                :style="{ background: `var(--color-${theme.accent_color}-500)` }"
              />
              <span class="text-sm font-medium truncate flex-1">{{ theme.name }}</span>
              <UBadge v-if="theme.is_preset" label="Preset" size="xs" variant="subtle" color="neutral" />
            </div>
          </UCard>

          <p v-if="!loading && !themes.length" class="text-xs text-muted px-1">Nenhum tema ainda.</p>
        </div>

        <!-- Editor + preview -->
        <div v-if="selectedTheme" class="flex flex-col gap-5 overflow-y-auto max-h-[32rem] pl-1">
          <!-- Preset: read-only -->
          <div v-if="!isEditable" class="flex flex-col gap-3">
            <p class="text-sm text-muted">
              Este é um tema padrão e não pode ser editado diretamente. Duplique para customizar.
            </p>
            <UButton
              label="Duplicar para editar"
              icon="i-lucide-copy"
              size="sm"
              class="self-start"
              @click="duplicateTheme(selectedTheme)"
            />
          </div>

          <!-- Editable fields -->
          <template v-else>
            <UInput v-model="draft.name" placeholder="Nome do tema" size="sm" />

            <!-- Background -->
            <div class="flex flex-col gap-2">
              <span class="text-xs font-medium text-muted">Fundo</span>
              <div class="flex items-center gap-3">
                <div
                  class="size-12 rounded-lg overflow-hidden border border-default shrink-0"
                  :style="backgroundStyle"
                >
                  <img v-if="backgroundPreview" :src="backgroundPreview" alt="" class="size-full object-cover" />
                </div>
                <UPopover>
                  <UButton label="Escolher fundo" icon="i-lucide-image" size="sm" variant="subtle" color="neutral" />
                  <template #content>
                    <CCoverPicker @select-file="onSelectBackgroundFile" @select-style="onSelectBackgroundStyle" />
                  </template>
                </UPopover>
              </div>
            </div>

            <!-- Accent color -->
            <div class="flex flex-col gap-2">
              <span class="text-xs font-medium text-muted">Cor de destaque</span>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="color in FormThemeAccentColors"
                  :key="color"
                  type="button"
                  class="size-7 rounded-full border-2 transition-transform"
                  :class="draft.accent_color === color ? 'scale-110 border-highlighted' : 'border-transparent'"
                  :style="{ background: `var(--color-${color}-500)` }"
                  :title="color"
                  @click="draft.accent_color = color"
                />
              </div>
            </div>

            <!-- Radius -->
            <div class="flex flex-col gap-2">
              <span class="text-xs font-medium text-muted">Raio da borda</span>
              <UFieldGroup size="sm">
                <UButton
                  v-for="radius in FormThemeRadii"
                  :key="radius"
                  :label="radiusLabels[radius]"
                  :color="draft.radius === radius ? 'primary' : 'neutral'"
                  :variant="draft.radius === radius ? 'solid' : 'subtle'"
                  @click="draft.radius = radius"
                />
              </UFieldGroup>
            </div>

            <!-- Input size -->
            <div class="flex flex-col gap-2">
              <span class="text-xs font-medium text-muted">Tamanho de inputs e botões</span>
              <UFieldGroup size="sm">
                <UButton
                  v-for="size in FormThemeInputSizes"
                  :key="size"
                  :label="sizeLabels[size]"
                  :color="draft.input_size === size ? 'primary' : 'neutral'"
                  :variant="draft.input_size === size ? 'solid' : 'subtle'"
                  @click="draft.input_size = size"
                />
              </UFieldGroup>
            </div>

            <!-- Font -->
            <div class="flex flex-col gap-2">
              <span class="text-xs font-medium text-muted">Fonte</span>
              <UFieldGroup size="sm">
                <UButton
                  v-for="font in FormThemeFonts"
                  :key="font"
                  :label="fontLabels[font]"
                  :style="{ fontFamily: fontPreviewStacks[font] }"
                  :color="draft.font === font ? 'primary' : 'neutral'"
                  :variant="draft.font === font ? 'solid' : 'subtle'"
                  @click="draft.font = font"
                />
              </UFieldGroup>
            </div>

            <!-- Advanced CSS -->
            <UAccordion :items="[{ label: 'CSS avançado', slot: 'css' }]">
              <template #css>
                <p class="text-xs text-muted mb-2">
                  Escopado automaticamente — use seletores como
                  <code class="text-highlighted">.ft-page-title</code>,
                  <code class="text-highlighted">.ft-question</code>,
                  <code class="text-highlighted">.ft-field</code>,
                  <code class="text-highlighted">.ft-btn-next</code>.
                </p>
                <UTextarea
                  v-model="draft.custom_css"
                  placeholder=".ft-page-title { letter-spacing: -0.02em; }"
                  :rows="5"
                  class="w-full font-mono text-xs"
                />
              </template>
            </UAccordion>

            <div class="flex items-center gap-2">
              <UButton label="Salvar alterações" :loading="saving" size="sm" @click="saveDraft" />
              <UButton
                label="Excluir tema"
                icon="i-lucide-trash-2"
                color="error"
                variant="ghost"
                size="sm"
                @click="deleteTheme(selectedTheme)"
              />
            </div>
          </template>

          <!-- Live preview -->
          <div class="ft-root rounded-xl border border-default p-6 flex flex-col gap-4" :style="previewVars">
            <span class="text-sm font-medium">Exemplo</span>
            <UInput placeholder="Digite sua resposta..." :size="(draft.input_size as 'sm' | 'md' | 'lg')" class="w-full" />
            <UButton label="Próxima página" trailing icon="i-lucide-arrow-right" :size="(draft.input_size as 'sm' | 'md' | 'lg')" color="primary" class="self-start" />
          </div>

          <!-- AI assistant -->
          <div class="flex flex-col gap-2 rounded-xl border border-default p-4">
            <span class="text-sm font-medium flex items-center gap-1.5">
              <UIcon name="i-lucide-sparkles" class="size-4" />
              Personalizar com IA
            </span>
            <UTextarea
              v-model="aiPrompt"
              placeholder="Ex: tema escuro e elegante para um formulário de casamento, com tons de dourado"
              :rows="2"
              class="w-full"
            />
            <UButton
              label="Gerar tema"
              icon="i-lucide-wand-2"
              size="sm"
              :loading="aiLoading"
              class="self-start"
              @click="runAiGenerate"
            />
          </div>
        </div>

        <div v-else class="flex items-center justify-center text-sm text-muted">
          Selecione ou crie um tema.
        </div>
      </div>
    </template>

    <template #footer>
      <UButton label="Cancelar" variant="ghost" color="neutral" size="sm" @click="emit('close')" />
      <UButton
        label="Usar este tema"
        size="sm"
        :disabled="selectedId === currentThemeId"
        @click="emit('close', { themeId: selectedId })"
      />
    </template>
  </UModal>
</template>
