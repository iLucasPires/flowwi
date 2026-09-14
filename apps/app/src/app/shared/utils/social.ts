import { API_ACCOUNT_URLS, ensureCsrf } from '@/app/core/clients/api'
import { useCookies } from '@vueuse/integrations/useCookies'

export async function redirectToProvider(provider: string) {
  await ensureCsrf()

  const cookies = useCookies()
  const csrf = cookies.get('csrftoken')

  if (!csrf) {
    throw new Error('CSRF token não disponível. Tente novamente.')
  }

  const form = document.createElement('form')

  form.method = 'POST'
  form.action = API_ACCOUNT_URLS.PROVIDER_REDIRECT

  const fields: Record<string, string> = {
    provider,
    callback_url: `${window.location.origin}/account/callback`,
    process: 'login',
    csrfmiddlewaretoken: csrf,
  }

  for (const [key, value] of Object.entries(fields)) {
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = key
    input.value = value
    form.appendChild(input)
  }

  document.body.appendChild(form)
  form.submit()
}
