<script setup lang="ts">
import { API_ACCOUNT_URLS, apiFetch } from '@/app/core/clients/api'
import { toastError } from '@/app/shared/utils/toast'
import { FetchError } from 'ofetch'

defineOptions({ name: 'ResetPasswordPage' })

const route = useRoute()
const router = useRouter()
const toast = useToast()

const key = computed(() => route.params.key as string)
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

async function handleSubmit() {
  if (password.value !== confirmPassword.value) {
    toast.add({ title: 'As senhas não coincidem', color: 'error' })
    return
  }
  loading.value = true
  try {
    await apiFetch(API_ACCOUNT_URLS.RESET_PASSWORD, {
      method: 'POST',
      body: {
        key: key.value,
        password: password.value,
      },
    })

    toast.add({
      title: 'Senha redefinida com sucesso!',
      color: 'success',
    })

    router.push('/account/login')
  } catch (error) {
    if (error instanceof FetchError) toastError(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UPageCard title="Nova senha" description="Digite sua nova senha">
    <UForm class="space-y-4" @submit.prevent="handleSubmit">
      <UFormField size="xs" label="Nova senha">
        <UInput
          v-model="password"
          type="password"
          size="xs"
          placeholder="Digite a nova senha"
          class="w-full"
          required
          autofocus
        />
      </UFormField>
      <UFormField size="xs" label="Confirmar senha">
        <UInput
          v-model="confirmPassword"
          type="password"
          size="xs"
          placeholder="Confirme a nova senha"
          class="w-full"
          required
        />
      </UFormField>
      <UButton size="xs" type="submit" label="Redefinir senha" block :loading="loading" />
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
