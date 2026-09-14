<script setup lang="ts">
import { API_ACCOUNT_URLS, apiFetch } from '@/app/core/clients/api'
import { useUser } from '@/app/features/user/composables/user'
import type { tAuthSocialProvider } from '@/app/shared/types/auth'
import { redirectToProvider } from '@/app/shared/utils/social'
import { toastError } from '@/app/shared/utils/toast'
import { FetchError } from 'ofetch'

defineOptions({ name: 'RegisterPage' })

const toast = useToast()
const router = useRouter()
const user = useUser()

const registerForm = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

const loading = ref(false)
const socialLoading = ref<string | null>(null)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

async function onRegister() {
  if (registerForm.password !== registerForm.confirmPassword) {
    toast.add({ title: 'As senhas não coincidem', color: 'error' })
    return
  }

  loading.value = true

  try {
    await apiFetch(API_ACCOUNT_URLS.SIGNUP, {
      method: 'POST',
      body: {
        email: registerForm.email,
        password: registerForm.password,
      },
    })

    await user.fetchAndSetUser()
    router.push('/dashboard')
  } catch (error) {
    if (error instanceof FetchError) {
      toastError(error)
    }
  } finally {
    loading.value = false
  }
}

async function socialLogin(provider: tAuthSocialProvider) {
  socialLoading.value = provider
  try {
    await redirectToProvider(provider)
  } catch (error) {
    const message = error instanceof Error ? error.message : `Erro ao conectar com ${provider}`
    toast.add({ title: message, color: 'error' })
    socialLoading.value = null
  }
}
</script>

<template>
  <UPageCard title="Crie sua conta" description="Preencha os dados para começar">
    <div class="space-y-6">
      <UForm class="space-y-4" @submit.prevent="onRegister">
        <UFormField size="sm" label="Email">
          <UInput
            v-model="registerForm.email"
            size="sm"
            type="email"
            placeholder="Digite seu email"
            class="w-full"
            required
          />
        </UFormField>
        <UFormField size="sm" label="Senha">
          <UInput
            v-model="registerForm.password"
            size="sm"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Digite sua senha"
            class="w-full"
            required
          >
            <template #trailing>
              <UButton
                size="xs"
                variant="ghost"
                color="neutral"
                :icon="showPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                @mousedown="showPassword = true"
                @mouseup="showPassword = false"
                @mouseleave="showPassword = false"
                @touchstart.prevent="showPassword = true"
                @touchend="showPassword = false"
              />
            </template>
          </UInput>
        </UFormField>
        <UFormField size="sm" label="Confirmar senha">
          <UInput
            v-model="registerForm.confirmPassword"
            size="sm"
            :type="showConfirmPassword ? 'text' : 'password'"
            placeholder="Confirme sua senha"
            class="w-full"
            required
          >
            <template #trailing>
              <UButton
                size="xs"
                variant="ghost"
                color="neutral"
                :icon="showConfirmPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                @mousedown="showConfirmPassword = true"
                @mouseup="showConfirmPassword = false"
                @mouseleave="showConfirmPassword = false"
                @touchstart.prevent="showConfirmPassword = true"
                @touchend="showConfirmPassword = false"
              />
            </template>
          </UInput>
        </UFormField>
        <UButton size="sm" type="submit" label="Registrar" block :loading="loading" />
      </UForm>

      <USeparator label="ou" />

      <div class="space-y-3">
        <UButton
          size="sm"
          label="Continuar com Google"
          icon="i-lucide-chrome"
          color="neutral"
          variant="subtle"
          block
          :loading="socialLoading === 'google'"
          @click="socialLogin('google')"
        />
        <UButton
          size="sm"
          label="Continuar com GitHub"
          icon="i-lucide-github"
          color="neutral"
          variant="subtle"
          block
          :loading="socialLoading === 'github'"
          @click="socialLogin('github')"
        />
      </div>

      <p class="text-center text-xs text-muted">
        Já tem uma conta?
        <ULink to="/account/login" class="font-medium">Fazer login</ULink>
      </p>
    </div>
  </UPageCard>
</template>
