import { API_ACCOUNT_URLS, API_FORM_URLS, apiFetch } from '@/app/core/clients/api'
import type { tFormBlockOut, tFormOut } from '@/app/features/form/schemas'

type FormStage =
  | 'loading'
  | 'error'
  | 'gate-auth'
  | 'gate-identity'
  | 'welcome'
  | 'questions'
  | 'submitting'
  | 'complete'

interface PublicFormPage {
  id: number
  title: string
  description: string
  order: number
  blocks: tFormBlockOut[]
}

interface PublicFormData {
  form: tFormOut
  blocks: tFormBlockOut[]
  pages: PublicFormPage[]
}

export function usePublicForm(publicId: string) {
  const stage = ref<FormStage>('loading')
  const errorMessage = ref('')
  const formData = ref<PublicFormData | null>(null)
  const answers = ref<Record<number, unknown>>({})
  const currentPageIndex = ref(0)
  const respondentEmail = ref('')
  const respondentPhone = ref('')

  // Flat list of all blocks, in display order — used to resolve condition targets across pages.
  const allBlocks = computed(() => {
    if (!formData.value) return []
    const { pages, blocks } = formData.value

    if (pages.length) {
      return [...pages]
        .sort((a, b) => a.order - b.order)
        .flatMap((p) => [...p.blocks].sort((a, b) => a.order - b.order))
    }

    return [...blocks].sort((a, b) => a.order - b.order)
  })

  // One Tally-style page = every visible block on it, rendered together.
  const pages = computed(() => {
    if (!formData.value) return []
    const { pages: rawPages } = formData.value

    const grouped = rawPages.length
      ? [...rawPages].sort((a, b) => a.order - b.order)
      : [{ id: 0, title: '', description: '', order: 0, blocks: allBlocks.value }]

    return grouped.map((page) => ({
      ...page,
      blocks: [...page.blocks]
        .sort((a, b) => a.order - b.order)
        .filter((block) => isBlockVisible(block, allBlocks.value)),
    }))
  })

  const currentPage = computed(() => pages.value[currentPageIndex.value] ?? null)
  const totalPages = computed(() => pages.value.length)
  const progress = computed(() =>
    totalPages.value > 0 ? ((currentPageIndex.value + 1) / totalPages.value) * 100 : 0,
  )
  const isFirstPage = computed(() => currentPageIndex.value === 0)
  const isLastPage = computed(() => currentPageIndex.value === totalPages.value - 1)
  const form = computed(() => formData.value?.form ?? null)

  // --- Visibility engine ---
  function isBlockVisible(block: tFormBlockOut, referenceBlocks: tFormBlockOut[]): boolean {
    const cond = block.condition as
      | { client_id?: string; operator?: string; value?: unknown }
      | undefined
    if (!cond?.operator || !cond?.client_id) return true

    const target = referenceBlocks.find((b) => b.client_id === cond.client_id)
    if (!target) return true

    const answer = answers.value[target.id]
    const exists = answer !== undefined && answer !== null && answer !== ''

    switch (cond.operator) {
      case 'exists':
        return exists
      case 'not_exists':
        return !exists
      case 'eq':
        return String(answer) === String(cond.value)
      case 'neq':
        return String(answer) !== String(cond.value)
      case 'gt':
        return Number(answer) > Number(cond.value)
      case 'gte':
        return Number(answer) >= Number(cond.value)
      case 'lt':
        return Number(answer) < Number(cond.value)
      case 'lte':
        return Number(answer) <= Number(cond.value)

      default:
        return true
    }
  }

  // --- Validation ---
  function isCurrentValid(): boolean {
    const page = currentPage.value
    if (!page) return true

    return page.blocks.every((block) => {
      if (block.type === 'content' || !block.required) return true
      const value = answers.value[block.id]
      if (value === undefined || value === null) return false
      if (typeof value === 'string' && !value.trim()) return false
      if (Array.isArray(value) && value.length === 0) return false
      return true
    })
  }

  // --- Navigation ---
  function nextPage(): boolean {
    if (!isCurrentValid()) return false
    if (isLastPage.value) return false
    currentPageIndex.value++
    return true
  }

  function prevPage(): boolean {
    if (isFirstPage.value) return false
    currentPageIndex.value--
    return true
  }

  // --- Lifecycle ---
  async function load() {
    stage.value = 'loading'
    try {
      const data = await apiFetch<PublicFormData & { id: number; public_id: string }>(
        `${API_FORM_URLS.LIST}/public/${publicId}`,
      )
      const { blocks: rawBlocks, pages: rawPages, ...rest } = data
      formData.value = {
        form: rest as unknown as tFormOut,
        blocks: rawBlocks ?? [],
        pages: (rawPages ?? []) as PublicFormPage[],
      }

      // Check auth
      try {
        const session = await apiFetch<{ email: string }>(API_ACCOUNT_URLS.SESSION)
        respondentEmail.value = session.email

        if (formData.value.form.require_auth || formData.value.form.require_identity) {
          // Auth satisfied
        }
      } catch {
        if (formData.value.form.require_auth) {
          stage.value = 'gate-auth'
          return
        }
      }

      if (formData.value.form.require_identity && !respondentEmail.value) {
        stage.value = 'gate-identity'
        return
      }

      stage.value = 'welcome'
    } catch {
      errorMessage.value = 'Este formulário não pôde ser encontrado ou não está disponível.'
      stage.value = 'error'
    }
  }

  function submitIdentity(email: string, phone: string) {
    respondentEmail.value = email
    respondentPhone.value = phone
    stage.value = 'welcome'
  }

  function start() {
    currentPageIndex.value = 0
    stage.value = 'questions'
  }

  async function submit() {
    if (!isCurrentValid()) return
    if (!formData.value) return

    stage.value = 'submitting'
    try {
      const payload: Record<string, unknown> = {
        answers: allBlocks.value
          .filter((b) => {
            if (b.type === 'content') return false
            const val = answers.value[b.id]
            return (
              val !== undefined &&
              val !== null &&
              val !== '' &&
              !(Array.isArray(val) && val.length === 0)
            )
          })
          .map((b) => ({ block: b.id, value: answers.value[b.id] })),
      }

      if (formData.value.form.require_identity) {
        payload.respondent_email = respondentEmail.value
        payload.respondent_phone = respondentPhone.value
      }

      await apiFetch(`${API_FORM_URLS.LIST}/public/${publicId}/respond`, {
        method: 'POST',
        body: payload,
      })

      stage.value = 'complete'
    } catch {
      errorMessage.value = 'Erro ao enviar resposta. Verifique sua conexão e tente novamente.'
      stage.value = 'questions'
    }
  }

  return {
    stage,
    errorMessage,
    form,
    pages,
    currentPage,
    currentPageIndex,
    totalPages,
    progress,
    isFirstPage,
    isLastPage,
    answers,
    respondentEmail,
    respondentPhone,
    isCurrentValid,
    nextPage,
    prevPage,
    load,
    submitIdentity,
    start,
    submit,
  }
}
