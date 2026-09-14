import { ref, computed } from 'vue'
import { useMutation } from '@tanstack/vue-query'
import type { iUserOut } from '@/app/features/user/types'
import { apiFetch, API_ACCOUNT_URLS, API_USER_URLS } from '@/app/core/clients/api'

/**
 * Global user state to maintain a single session across the app.
 */
const user = ref<iUserOut | null | undefined>(undefined)

/**
 * Composable to handle user session, authentication state, and account actions.
 * Safe to call anywhere (guards, components, etc).
 */
export const useUser = () => {
  const isLogged = computed(() => !!user.value)
  const isPending = computed(() => user.value === undefined)

  async function fetchUser(): Promise<iUserOut> {
    const session = await apiFetch(API_ACCOUNT_URLS.SESSION)
    const userData = session?.data?.user
    if (!userData) throw new Error('Session user not found')
    return userData
  }

  async function fetchAndSetUser(): Promise<iUserOut> {
    const userData = await fetchUser()
    user.value = userData
    return userData
  }

  function setCurrent(data: iUserOut) {
    user.value = data
  }

  function clearCurrent() {
    user.value = null
  }

  function reset() {
    user.value = undefined
  }

  return {
    user,
    isLogged,
    isPending,
    fetchUser,
    fetchAndSetUser,
    setCurrent,
    clearCurrent,
    reset,
  }
}

/**
 * Mutations that require component setup context.
 * Only call inside <script setup> or a running effect scope.
 */
export const useUserMutations = () => {
  const { clearCurrent } = useUser()

  const { mutateAsync: deactivateUser, status: deactivateStatus } = useMutation({
    mutationFn: () => apiFetch(API_USER_URLS.DEACTIVATE, { method: 'POST' }),
  })

  const { mutateAsync: logoutUser, status: logoutStatus } = useMutation({
    mutationFn: () =>
      apiFetch(API_ACCOUNT_URLS.LOGOUT, { method: 'DELETE' }).catch((error) => {
        if (error?.response?.status === 401) return
        throw error
      }),
    onSuccess: () => clearCurrent(),
  })

  return {
    deactivateUser,
    deactivateStatus,
    logoutUser,
    logoutStatus,
  }
}
