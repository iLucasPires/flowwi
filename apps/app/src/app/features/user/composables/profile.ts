import { ref } from 'vue'
import { useMutation } from '@tanstack/vue-query'
import type { iProfile } from '@/app/features/user/profile'
import { apiFetch, API_PROFILE_URLS } from '@/app/core/clients/api'

/**
 * Global profile state to ensure consistency across components.
 */
const profile = ref<iProfile | null>(null)

/**
 * Composable to manage the current user's profile information.
 * Safe to call anywhere (guards, components, etc).
 */
export const useProfile = () => {
  async function fetchProfile(): Promise<iProfile> {
    return apiFetch<iProfile>(API_PROFILE_URLS.ME)
  }

  function setCurrent(data: iProfile) {
    profile.value = data
  }

  function clearCurrent() {
    profile.value = null
  }

  return {
    profile,
    fetchProfile,
    setCurrent,
    clearCurrent,
  }
}

/**
 * Profile mutations that require component setup context.
 * Only call inside <script setup> or a running effect scope.
 */
export const useProfileMutations = () => {
  const { mutateAsync: updateProfile, status: updateProfileStatus } = useMutation({
    mutationFn: (data: Partial<iProfile> | FormData) => {
      return apiFetch<iProfile>(API_PROFILE_URLS.ME, {
        method: 'PATCH',
        body: data,
      })
    },
    onSuccess: (updated) => {
      profile.value = updated
    },
  })

  return {
    updateProfile,
    updateProfileStatus,
  }
}
