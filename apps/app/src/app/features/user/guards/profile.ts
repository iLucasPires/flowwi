import { useProfile } from '@/app/features/user/composables/profile'
import { useUser } from '@/app/features/user/composables/user'
import { isAuthPage, isPublicPage } from '@/app/shared/utils/router'
import type { NavigationGuard } from 'vue-router'

export const profileGuard: NavigationGuard = async (to) => {
  if (isPublicPage(to.path) || isAuthPage(to.path)) return

  const user = useUser()
  if (!user.isLogged.value) return

  const profile = useProfile()

  if (!profile.profile.value) {
    try {
      const profileData = await profile.fetchProfile()
      if (profileData) profile.setCurrent(profileData)
    } catch {
      // Profile fetch failure is non-blocking — continue navigation
    }
  }
}
