<script setup lang="ts">
import { API_ACCOUNT_URLS, apiFetch } from '@/app/core/clients/api'
import { toastError } from '@/app/shared/utils/toast'
import { FetchError } from 'ofetch'

defineOptions({ name: 'ForgotPasswordPage' })

const toast = useToast()
const email = ref('')
const loading = ref(false)
const sent = ref(false)

async function handleSubmit() {
  if (!email.value) return
  loading.value = true
  try {
    await apiFetch(API_ACCOUNT_URLS.REQUEST_PASSWORD_RESET, {
      method: 'POST',
      body: { email: email.value },
    })
    sent.value = true
    toast.add({
      title: 'Email enviado!',
      description: 'Verifique sua caixa de entrada.',
      color: 'success',
    })
  } catch (error) {
    if (error instanceof FetchError) toastError(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UPageCard
    title="Esqueceu sua senha?"
    description="Digite seu email para receber um link de recuperação"
  >
    <div v-if="sent" class="space-y-4 text-center">
      <UIcon name="i-lucide-mail-check" class="text-4xl text-primary" />
      <p class="text-sm text-neutral-600 dark:text-neutral-400">
        Se o email estiver cadastrado, você receberá um link para redefinir sua senha.
      </p>
      <UButton label="Voltar ao login" to="/account/login" variant="link" />
    </div>

    <UForm v-else class="space-y-4" @submit.prevent="handleSubmit">
      <UFormField label="Email" size="xs">
        <UInput
          v-model="email"
          type="email"
          size="xs"
          placeholder="Digite seu email"
          class="w-full"
          required
          autofocus
        />
      </UFormField>
      <UButton size="xs" type="submit" label="Enviar link" block :loading="loading" />
      <UButton
        size="xs"
        label="Voltar ao login"
        to="/account/login"
        variant="link"
        block
        color="neutral"
      />
    </UForm>
  </UPageCard>
</template>
