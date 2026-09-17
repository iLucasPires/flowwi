import type { RouteRecordRaw } from 'vue-router'

export const homeRoutes: RouteRecordRaw[] = [
  { path: '', component: () => import('./pages/home.vue') },
]
