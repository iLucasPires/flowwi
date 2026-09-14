import type { RouteRecordRaw } from 'vue-router'

export const inboxRoutes: RouteRecordRaw[] = [
  { path: 'inbox', component: () => import('./pages/inbox.vue') },
]
