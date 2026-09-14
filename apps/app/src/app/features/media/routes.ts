import type { RouteRecordRaw } from 'vue-router'

/** Mounted under /dashboard. */
export const mediaRoutes: RouteRecordRaw[] = [
  { path: 'media', component: () => import('./pages/media-list.vue') },
  { path: 'media/:id', component: () => import('./pages/media-detail.vue') },
]

/** Mounted under /public. */
export const mediaPublicRoutes: RouteRecordRaw[] = [
  { path: 'media/:id', component: () => import('./pages/media-public.vue') },
]
