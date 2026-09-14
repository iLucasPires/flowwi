import { useUser } from '@/app/features/user/composables/user'
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
import { isNoWorkplacePage, isPublicPage } from '@/app/shared/utils/router'
import type { NavigationGuard } from 'vue-router'

export const workplaceGuard: NavigationGuard = async (to) => {
  if (isPublicPage(to.path) || isNoWorkplacePage(to.path)) return

  const user = useUser()
  if (!user.isLogged.value) return

  const workplace = useWorkplace()

  if (!workplace.hasCurrent.value) {
    try {
      await workplace.refreshWorkplaces()
    } catch {
      return '/account/setup/workplace/select'
    }

    if (workplace.savedWorkplaceId.value) {
      const savedWorkplace = workplace.workplaces.value.find(
        (item) => String(item.id) === workplace.savedWorkplaceId.value,
      )

      if (savedWorkplace) {
        await workplace.setCurrent(savedWorkplace)
        return
      }
    }

    return '/account/setup/workplace/select'
  }
}
