<script setup lang="ts">
import { API_ACCOUNT_URLS, apiFetch } from '@/app/core/clients/api'
import { useUser } from '@/app/features/user/composables/user'
import type { tAuthSocialProvider } from '@/app/shared/types/auth'
import { redirectToProvider } from '@/app/shared/utils/social'
import { parseError } from '@/app/shared/utils/toast'
import { FetchError } from 'ofetch'

defineOptions({ name: 'LoginPage' })

const router = useRouter()
const user = useUser()

const loginForm = reactive({
  email: '',
  password: '',
})

const loading = ref(false)
const socialLoading = ref<string | null>(null)
const showPassword = ref(false)
const formError = ref<{ title: string; description: string; color: 'error' | 'warning' } | null>(
  null,
)

async function onLogin() {
  formError.value = null
  loading.value = true

  try {
    await apiFetch(API_ACCOUNT_URLS.LOGIN, {
      method: 'POST',
      body: loginForm,
    })

    await user.fetchAndSetUser()
    router.push('/dashboard')
  } catch (error) {
    if (error instanceof FetchError) {
      formError.value = {
        title: 'Erro ao entrar',
        description: parseError(error),
        color: 'error',
      }
    }
  } finally {
    loading.value = false
  }
}

async function socialLogin(provider: tAuthSocialProvider) {
  formError.value = null
  socialLoading.value = provider
  try {
    await redirectToProvider(provider)
  } catch (error) {
    const message = error instanceof Error ? error.message : `Erro ao conectar com ${provider}`
    formError.value = { title: 'Erro ao conectar', description: message, color: 'error' }
    socialLoading.value = null
  }
}
</script>

<template>
  <UPageCard title="Bem-vindo de volta" description="Entre na sua conta para continuar">
    <div class="space-y-6">
      <UForm class="space-y-4" @submit.prevent="onLogin">
        <UFormField size="sm" label="Email">
          <UInput
            v-model="loginForm.email"
            size="sm"
            type="email"
            placeholder="Digite seu email"
            class="w-full"
            required
          />
        </UFormField>
        <UFormField size="sm" label="Senha">
          <UInput
            v-model="loginForm.password"
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
        <UAlert
          v-if="formError"
          size="xs"
          :title="formError.title"
          :description="formError.description"
          :color="formError.color"
          :ui="{
            title: 'text-xs',
            description: 'text-xs',
            icon: 'size-4',
          }"
          variant="subtle"
          icon="i-lucide-circle-alert"
        />
        <UButton size="sm" type="submit" label="Entrar" block :loading="loading" />
        <UButton
          size="sm"
          label="Esqueceu a senha?"
          to="/account/forgot-password"
          variant="link"
          block
          color="neutral"
        />
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
        Não tem uma conta?
        <ULink to="/account/register" class="font-medium">Registre-se </ULink>
      </p>
    </div>
  </UPageCard>
</template>
