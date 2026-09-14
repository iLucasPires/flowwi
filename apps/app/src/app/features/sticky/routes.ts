import type { RouteRecordRaw } from 'vue-router'

export const stickyRoutes: RouteRecordRaw[] = [
  { path: 'stickies', component: () => import('./pages/stickies.vue') },
]
