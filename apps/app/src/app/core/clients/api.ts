import { ofetch } from 'ofetch'
import { useCookies } from '@vueuse/integrations/useCookies'

const API_BASE = '/api'
const API_ACCOUNT_BASE = '/api/browser/v1'

export const API_ACCOUNT_URLS = Object.freeze({
  CONFIG: `${API_ACCOUNT_BASE}/config`,
  LOGIN: `${API_ACCOUNT_BASE}/auth/login`,
  SIGNUP: `${API_ACCOUNT_BASE}/auth/signup`,
  SESSION: `${API_ACCOUNT_BASE}/auth/session`,
  LOGOUT: `${API_ACCOUNT_BASE}/auth/session`,
  VERIFY_EMAIL: `${API_ACCOUNT_BASE}/auth/email/verify`,
  REQUEST_PASSWORD_RESET: `${API_ACCOUNT_BASE}/auth/password/request`,
  RESET_PASSWORD: `${API_ACCOUNT_BASE}/auth/password/reset`,
  CHANGE_PASSWORD: `${API_ACCOUNT_BASE}/account/password/change`,
  EMAIL: `${API_ACCOUNT_BASE}/account/email`,
  PROVIDER_REDIRECT: `${API_ACCOUNT_BASE}/auth/provider/redirect`,
  PROVIDER_SIGNUP: `${API_ACCOUNT_BASE}/auth/provider/signup`,
})

export const API_PROFILE_URLS = Object.freeze({
  LIST: `${API_BASE}/profiles`,
  ME: `${API_BASE}/profiles/me`,
})

export const API_USER_URLS = Object.freeze({
  DEACTIVATE: `${API_BASE}/members/deactivate`,
})

export const API_INBOX_URLS = Object.freeze({
  LIST: `${API_BASE}/inbox`,
  READ_ALL: `${API_BASE}/inbox/read-all`,
  DELETE_ALL: `${API_BASE}/inbox/delete-all`,
  READ: (id: string | number) => `${API_BASE}/inbox/${id}/read`,
})

export const API_NOTIFICATION_URLS = Object.freeze({
  EVENT: `${API_BASE}/inbox/sse`,
})

export const API_SYNC_URLS = Object.freeze({
  /** Generic per-user SSE stream (`apps.common.streaming.views.stream_view`) — Task,
   * Document and Sticky changes are pushed here, fanned out to every workplace member. */
  EVENT: `${API_BASE}/stream`,
})

export const API_WORKPLACE_URLS = Object.freeze({
  LIST: `${API_BASE}/workplaces`,
  JOIN: `${API_BASE}/workplaces/join`,
  DESELECT: `${API_BASE}/workplaces/deselect`,
  DETAIL: (id: string | number) => `${API_BASE}/workplaces/${id}`,
  SELECT: (id: string | number) => `${API_BASE}/workplaces/${id}/select`,
  REGENERATE_INVITE_KEY: (id: string | number) =>
    `${API_BASE}/workplaces/${id}/regenerate-invite-key`,
})

export const API_WORKPLACE_MEMBER_URLS = Object.freeze({
  LIST: `${API_BASE}/workplace-members`,
})

export const API_TASK_URLS = Object.freeze({
  LIST: `${API_BASE}/tasks`,
  DETAIL: (id: string | number) => `${API_BASE}/tasks/${id}`,
  RESTORE: (id: string | number) => `${API_BASE}/tasks/${id}/restore`,
})

export const API_SUBTASK_URLS = Object.freeze({
  LIST: `${API_BASE}/tasksubs`,
  DETAIL: (id: string | number) => `${API_BASE}/tasksubs/${id}`,
})

export const API_TASK_TAG_URLS = Object.freeze({
  LIST: `${API_BASE}/tasktags`,
  DETAIL: (id: string | number) => `${API_BASE}/tasktags/${id}`,
})

export const API_TASK_STATUS_URLS = Object.freeze({
  LIST: `${API_BASE}/task-statuses`,
  DETAIL: (id: string | number) => `${API_BASE}/task-statuses/${id}`,
})

export const API_TASK_TYPE_URLS = Object.freeze({
  LIST: `${API_BASE}/task-types`,
  DETAIL: (id: string | number) => `${API_BASE}/task-types/${id}`,
})

export const API_MEDIA_URLS = Object.freeze({
  LIST: `${API_BASE}/medias`,
  VERSIONS: `${API_BASE}/media-versions`,
  FEEDBACKS: `${API_BASE}/media-feedbacks`,
  COMMENTS: `${API_BASE}/media-comments`,
  DETAIL: (id: string | number) => `${API_BASE}/medias/${id}`,
})

export const API_DOCUMENT_URLS = Object.freeze({
  LIST: `${API_BASE}/documents`,
  VERSIONS: `${API_BASE}/document-versions`,
  FEEDBACKS: `${API_BASE}/document-feedbacks`,
  COMMENTS: `${API_BASE}/document-comments`,
  DETAIL: (id: string | number) => `${API_BASE}/documents/${id}`,
  NEW_REVISION: (versionId: string | number) =>
    `${API_BASE}/document-versions/${versionId}/new-revision`,
  GENERATE_TASK: (id: string | number) => `${API_BASE}/documents/${id}/generate-task`,
  AI_ASSIST: (id: string | number) => `${API_BASE}/documents/${id}/ai-assist`,
})

export const API_DOCUMENT_TYPE_URLS = Object.freeze({
  LIST: `${API_BASE}/document-types`,
  DETAIL: (id: string | number) => `${API_BASE}/document-types/${id}`,
})

export const API_FORM_URLS = Object.freeze({
  LIST: `${API_BASE}/forms`,
  BLOCKS: `${API_BASE}/form-blocks`,
  PAGES: `${API_BASE}/form-pages`,
  RESPONSES: `${API_BASE}/form-responses`,
  DETAIL: (id: string | number) => `${API_BASE}/forms/${id}`,
})

export const API_FORM_THEME_URLS = Object.freeze({
  LIST: `${API_BASE}/form-themes`,
  GENERATE: `${API_BASE}/form-themes/generate`,
  DETAIL: (id: string | number) => `${API_BASE}/form-themes/${id}`,
  DUPLICATE: (id: string | number) => `${API_BASE}/form-themes/${id}/duplicate`,
})

export const API_STICKY_URLS = Object.freeze({
  LIST: `${API_BASE}/stickies`,
  DETAIL: (id: string | number) => `${API_BASE}/stickies/${id}`,
  RESTORE: (id: string | number) => `${API_BASE}/stickies/${id}/restore`,
})

export const API_WEBHOOK_URLS = Object.freeze({
  LIST: `${API_BASE}/webhooks`,
  DETAIL: (id: string | number) => `${API_BASE}/webhooks/${id}`,
})

export const API_UNSPLASH_URLS = Object.freeze({
  PHOTOS: `${API_BASE}/unsplash/photos`,
  DOWNLOAD: `${API_BASE}/unsplash/download`,
})

export const API_GOOGLE_DRIVE_URLS = Object.freeze({
  LIST: `${API_BASE}/google-drive`,
  DETAIL: (id: string | number) => `${API_BASE}/google-drive/${id}`,
})

/**
 * Ensures a CSRF token cookie is available.
 * Fetches one from the config endpoint if missing.
 */
let csrfPromise: Promise<void> | null = null

export async function ensureCsrf(): Promise<void> {
  const cookies = useCookies()

  if (cookies.get('csrftoken')) return

  if (!csrfPromise) {
    csrfPromise = ofetch(API_ACCOUNT_URLS.CONFIG, { credentials: 'include' })
      .then(() => {})
      .finally(() => {
        csrfPromise = null
      })
  }

  return csrfPromise
}

export const apiFetch = ofetch.create({
  credentials: 'include',

  async onRequest({ options }) {
    await ensureCsrf()

    const cookies = useCookies()
    const csrf = cookies.get('csrftoken')

    const headers = new Headers(options.headers)

    if (csrf) {
      headers.set('X-CSRFToken', csrf)
    }

    options.headers = headers
  },

  onResponseError({ request, response }) {
    if (response.status === 401) {
      const router = useRouter()
      const isLogout = typeof request === 'string' && request === API_ACCOUNT_URLS.LOGOUT

      if (!isLogout && !router.currentRoute.value.path.startsWith('/auth')) {
        router.push('/account/login')
      }

      return
    }

    if (response.status >= 500) {
      const toast = useToast()

      toast.add({
        title: 'Erro interno do servidor',
        color: 'error',
      })
    }
  },
})
