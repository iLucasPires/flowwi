import type { CSSProperties, ComputedRef, InjectionKey } from 'vue'
import { API_FORM_THEME_URLS, apiFetch } from '@/app/core/clients/api'
import { cColorShades } from '@/app/shared/composables/accentColor'
import { coverBackgroundStyle } from '@/app/shared/utils/cover'
import {
  FormThemeAccentColors,
  FormThemeRadii,
  FormThemeInputSizes,
  FormThemeFonts,
  type tFormThemeOut,
} from '@/app/features/form/schemas'

export interface iGeneratedFormTheme {
  name: string
  accent_color: (typeof FormThemeAccentColors)[number]
  radius: (typeof FormThemeRadii)[number]
  input_size: (typeof FormThemeInputSizes)[number]
  font: (typeof FormThemeFonts)[number]
  background_style: string
  custom_css: string
}

/**
 * Class/id contract every public form element can rely on, independent of the internal
 * Tailwind classes (which can change): `#ft-form` (root), `.ft-root` (theme scope, also the
 * `custom_css` anchor via `@scope`), `.ft-progress`/`.ft-progress-bar`, `.ft-page-title`/
 * `.ft-page-description`, `.ft-question`/`.ft-question-label`/`.ft-question-required`,
 * `.ft-field`, `.ft-content`, `.ft-nav`/`.ft-btn-prev`/`.ft-btn-next`, `.ft-welcome*`,
 * `.ft-complete`. Documented here so the theme dialog's "CSS avançado" help text and the
 * backend's `theme_generator_agent` system prompt stay in sync with what the markup exposes.
 */
export const FORM_THEME_CSS_HOOKS = [
  '#ft-form',
  '.ft-root',
  '.ft-progress',
  '.ft-progress-bar',
  '.ft-page-title',
  '.ft-page-description',
  '.ft-question',
  '.ft-question-label',
  '.ft-question-required',
  '.ft-field',
  '.ft-content',
  '.ft-nav',
  '.ft-btn-prev',
  '.ft-btn-next',
  '.ft-welcome',
  '.ft-welcome-title',
  '.ft-welcome-description',
  '.ft-welcome-start',
  '.ft-complete',
] as const

export const FORM_THEME_KEY: InjectionKey<ComputedRef<tFormThemeOut | null | undefined>> =
  Symbol('formTheme')

const RADIUS_VALUES: Record<string, string> = {
  none: '0rem',
  sm: '0.25rem',
  md: '0.5rem',
  lg: '0.75rem',
  xl: '1rem',
}

const FONT_STACKS: Record<string, string> = {
  serif: 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
  mono: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
}

/** Only the fields `formThemeStyleVars` actually reads — lets a not-yet-saved draft (which
 * has no `id`/`is_preset`/etc. yet) feed the same preview logic as a real saved theme. */
export type iFormThemeStyleInput = Pick<
  tFormThemeOut,
  'accent_color' | 'radius' | 'font' | 'cover_style' | 'background_image'
>

/** Pure `theme` → CSS custom properties, scoped to whatever element receives this style. */
export function formThemeStyleVars(theme?: iFormThemeStyleInput | null): CSSProperties {
  if (!theme) return {}

  const vars: Record<string, string> = {}

  // "neutral" is left unset on purpose — it falls back to whatever the ancestor already
  // has (the app's own accent color), same convention as `accentColor.ts`.
  if (theme.accent_color && theme.accent_color !== 'neutral') {
    for (const shade of cColorShades) {
      vars[`--ui-color-primary-${shade}`] = `var(--color-${theme.accent_color}-${shade})`
    }
  }

  vars['--ui-radius'] = RADIUS_VALUES[theme.radius] ?? RADIUS_VALUES.md!

  const background = coverBackgroundStyle(theme.background_image, theme.cover_style)
  const fontFamily = FONT_STACKS[theme.font]

  return {
    ...vars,
    ...background,
    ...(fontFamily ? { fontFamily } : {}),
  } as CSSProperties
}

/** `custom_css` wrapped in `@scope` so it can never leak past the `.ft-root` wrapper. */
export function formThemeScopedCss(theme?: tFormThemeOut | null): string {
  if (!theme?.custom_css?.trim()) return ''
  return `@scope (.ft-root) {\n${theme.custom_css}\n}`
}

/** The theme provided by an ancestor `CFormThemeScope`, if any — `undefined` outside one. */
export function useFormTheme() {
  return inject(FORM_THEME_KEY, undefined)
}

/** Read by every public/preview input to size itself consistently with the active theme. */
export function useFormThemeSize(): ComputedRef<'sm' | 'md' | 'lg'> {
  const theme = useFormTheme()
  return computed(() => (theme?.value?.input_size as 'sm' | 'md' | 'lg') ?? 'md')
}

export function useFormThemes() {
  const themes = ref<tFormThemeOut[]>([])
  const loading = ref(false)

  async function list() {
    loading.value = true
    try {
      themes.value = await apiFetch<tFormThemeOut[]>(API_FORM_THEME_URLS.LIST)
    } finally {
      loading.value = false
    }
  }

  function replaceInList(theme: tFormThemeOut) {
    const index = themes.value.findIndex((t) => t.id === theme.id)
    if (index !== -1) themes.value[index] = theme
    else themes.value.push(theme)
  }

  async function create(data: Record<string, unknown>) {
    const created = await apiFetch<tFormThemeOut>(API_FORM_THEME_URLS.LIST, {
      method: 'POST',
      body: data,
    })
    replaceInList(created)
    return created
  }

  async function update(id: number, data: Record<string, unknown>) {
    const updated = await apiFetch<tFormThemeOut>(API_FORM_THEME_URLS.DETAIL(id), {
      method: 'PATCH',
      body: data,
    })
    replaceInList(updated)
    return updated
  }

  /** Uploaded file goes in its own multipart request, same pattern as the form cover. */
  async function uploadBackground(id: number, file: File) {
    const formData = new FormData()
    formData.append('background_image', file)
    formData.append('cover_style', '')

    const updated = await apiFetch<tFormThemeOut>(API_FORM_THEME_URLS.DETAIL(id), {
      method: 'PATCH',
      body: formData,
    })
    replaceInList(updated)
    return updated
  }

  async function remove(id: number) {
    await apiFetch(API_FORM_THEME_URLS.DETAIL(id), { method: 'DELETE' })
    themes.value = themes.value.filter((t) => t.id !== id)
  }

  async function duplicate(id: number) {
    const created = await apiFetch<tFormThemeOut>(API_FORM_THEME_URLS.DUPLICATE(id), {
      method: 'POST',
    })
    replaceInList(created)
    return created
  }

  /** Only returns a draft for the caller to review — never saves anything by itself. */
  async function generate(prompt: string) {
    return apiFetch<iGeneratedFormTheme>(API_FORM_THEME_URLS.GENERATE, {
      method: 'POST',
      body: { prompt },
    })
  }

  return {
    themes,
    loading,
    list,
    create,
    update,
    uploadBackground,
    remove,
    duplicate,
    generate,
  }
}
