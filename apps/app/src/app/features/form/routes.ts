import type { RouteRecordRaw } from 'vue-router'

/** Mounted under /dashboard. */
export const formRoutes: RouteRecordRaw[] = [
  { path: 'forms', component: () => import('./pages/form-list.vue') },
  { path: 'forms/:id', component: () => import('./pages/form-editor.vue') },
]

/** Mounted under /public. */
export const formPublicRoutes: RouteRecordRaw[] = [
  { path: 'form/:id', component: () => import('./pages/form-public.vue') },
]
