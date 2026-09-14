import { useUser } from '@/app/features/user/composables/user'
import { isAuthPage, isPublicPage } from '@/app/shared/utils/router'
import type { NavigationGuard } from 'vue-router'

export const userGuard: NavigationGuard = async (to) => {
  if (isPublicPage(to.path)) return

  const toast = useToast()
  const user = useUser()

  // Only fetch session if state is unknown (first load or hard refresh)
  if (user.isPending.value) {
    try {
      user.setCurrent(await user.fetchUser())
    } catch (error: unknown) {
      const status = (error as { response?: { status?: number } })?.response?.status

      if (status === 401 || status === 403) {
        user.clearCurrent()
      } else {
        toast.add({
          title: 'Erro ao validar sessão',
          description: 'Não foi possível validar sua sessão. Tente novamente.',
          color: 'error',
        })
        return false
      }
    }
  }

  if (!user.isLogged.value) {
    if (isAuthPage(to.path)) return

    toast.add({
      title: 'Sessão expirada',
      description: 'Faça login novamente para continuar.',
      color: 'error',
    })

    return '/account/login'
  }

  if (
    to.path === '/' ||
    !to.matched.length ||
    (isAuthPage(to.path) && !to.path.startsWith('/account/setup'))
  ) {
    return '/dashboard'
  }
}
