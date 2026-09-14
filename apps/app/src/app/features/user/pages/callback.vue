<script setup lang="ts">
import { API_ACCOUNT_URLS, apiFetch } from '@/app/core/clients/api'
import { useUser } from '@/app/features/user/composables/user'
import { FetchError } from 'ofetch'

defineOptions({ name: 'AuthCallbackPage' })

const router = useRouter()
const route = useRoute()
const toast = useToast()
const user = useUser()

onMounted(async () => {
  if (route.query.error) {
    toast.add({
      title: 'Erro no login social',
      description: `Não foi possível autenticar: ${route.query.error}`,
      color: 'error',
    })
    router.replace('/account/login')
    return
  }

  try {
    await user.fetchAndSetUser()
    await router.replace('/dashboard')
  } catch (err: unknown) {
    if (!(err instanceof FetchError)) {
      router.replace('/account/login')
      return
    }

    // Allauth headless returns pending flows when provider_signup is needed
    const flows = err.data?.data?.flows as { id: string; is_pending?: boolean }[] | undefined

    const hasPendingSignup = flows?.some((f) => f.id === 'provider_signup' && f.is_pending)

    if (hasPendingSignup) {
      try {
        await apiFetch(API_ACCOUNT_URLS.PROVIDER_SIGNUP, {
          method: 'POST',
          body: {},
        })
        await user.fetchAndSetUser()
        router.replace('/dashboard')
        return
      } catch {
        toast.add({
          title: 'Erro ao finalizar cadastro social',
          description: 'Não foi possível completar o registro. Tente novamente.',
          color: 'error',
        })
      }
    }

    router.replace('/account/login')
  }
})
</script>

<template>
  <div class="flex items-center justify-center min-h-screen">
    <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-neutral-400" />
  </div>
</template>
