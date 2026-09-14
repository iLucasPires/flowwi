import type { RouteRecordRaw } from 'vue-router'

/** Mounted under /dashboard. */
export const workplaceRoutes: RouteRecordRaw[] = [
  { path: 'workplaces', component: () => import('./pages/workplace-list.vue') },
  { path: 'workplaces/members', component: () => import('./pages/workplace-members.vue') },
  { path: 'workplaces/settings', component: () => import('./pages/workplace-settings.vue') },
  { path: 'workplaces/webhooks', component: () => import('./pages/workplace-webhooks.vue') },
]

/** Mounted under /account — the "no workplace yet" onboarding flow. */
export const workplaceSetupRoutes: RouteRecordRaw[] = [
  { path: 'setup/workplace/create', component: () => import('./pages/setup/setup-create.vue') },
  { path: 'setup/workplace/join', component: () => import('./pages/setup/setup-join.vue') },
  { path: 'setup/workplace/select', component: () => import('./pages/setup/setup-select.vue') },
]
