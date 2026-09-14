<script setup lang="ts">
import { API_ACCOUNT_URLS, apiFetch } from '@/app/core/clients/api'
import { toastError } from '@/app/shared/utils/toast'
import { FetchError } from 'ofetch'

defineOptions({ name: 'VerifyEmailPage' })

const route = useRoute()
const router = useRouter()
const toast = useToast()

const key = computed(() => route.params.key as string)
const loading = ref(true)
const success = ref(false)

onMounted(async () => {
  try {
    await apiFetch(API_ACCOUNT_URLS.VERIFY_EMAIL, {
      method: 'POST',
      body: { key: key.value },
    })
    success.value = true
    toast.add({ title: 'Email verificado!', color: 'success' })
  } catch (error) {
    if (error instanceof FetchError) toastError(error)
  } finally {
    loading.value = false
  }
})

function goToApp() {
  router.push('/dashboard')
}
</script>

<template>
  <UPageCard title="Verificação de Email">
    <div v-if="loading" class="flex flex-col items-center gap-4 py-8">
      <UIcon name="i-lucide-loader-2" class="text-4xl animate-spin text-primary" />
      <p class="text-sm text-neutral-500">Verificando seu email...</p>
    </div>

    <div v-else-if="success" class="flex flex-col items-center gap-4 py-8 text-center">
      <UIcon name="i-lucide-check-circle" class="text-4xl text-success-500" />
      <p class="text-sm text-neutral-600 dark:text-neutral-400">
        Seu email foi verificado com sucesso!
      </p>
      <UButton label="Ir para o app" @click="goToApp" />
    </div>

    <div v-else class="flex flex-col items-center gap-4 py-8 text-center">
      <UIcon name="i-lucide-x-circle" class="text-4xl text-error-500" />
      <p class="text-sm text-neutral-600 dark:text-neutral-400">
        Não foi possível verificar seu email. O link pode ter expirado.
      </p>
      <UButton label="Voltar ao login" to="/account/login" variant="link" />
    </div>
  </UPageCard>
</template>
