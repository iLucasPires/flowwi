import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

// ----------------------------------------------------------------------------
// Layouts
// ----------------------------------------------------------------------------
import AccountLayout from '@/app/core/layouts/account-layout.vue'
import PublicLayout from '@/app/core/layouts/public-layout.vue'
import DashboardLayout from '@/app/core/layouts/dashboard-layout.vue'

// ----------------------------------------------------------------------------
// Routes
// ----------------------------------------------------------------------------
import { taskRoutes } from '@/app/features/task/routes'
import { userRoutes } from '@/app/features/user/routes'
import { documentRoutes } from '@/app/features/document/routes'
import { formPublicRoutes, formRoutes } from '@/app/features/form/routes'
import { inboxRoutes } from '@/app/features/inbox/routes'
import { mediaPublicRoutes, mediaRoutes } from '@/app/features/media/routes'
import { stickyRoutes } from '@/app/features/sticky/routes'
import { workplaceRoutes, workplaceSetupRoutes } from '@/app/features/workplace/routes'

// ----------------------------------------------------------------------------
// Guards
// ----------------------------------------------------------------------------
import { profileGuard } from '@/app/features/user/guards/profile'
import { userGuard } from '@/app/features/user/guards/user'
import { workplaceGuard } from '@/app/features/workplace/guard'

const routes: RouteRecordRaw[] = [
  {
    path: '/account',
    component: () => AccountLayout,
    children: [...userRoutes, ...workplaceSetupRoutes],
  },
  {
    path: '/public',
    component: () => PublicLayout,
    children: [...formPublicRoutes, ...mediaPublicRoutes],
  },
  {
    path: '/dashboard',
    component: () => DashboardLayout,
    children: [
      ...documentRoutes,
      ...inboxRoutes,
      ...stickyRoutes,
      ...formRoutes,
      ...mediaRoutes,
      ...taskRoutes,
      ...workplaceRoutes,
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(userGuard)
router.beforeEach(workplaceGuard)
router.beforeEach(profileGuard)

export default router
