import type { RouteRecordRaw } from 'vue-router'

/** Mounted under /account. */
export const userRoutes: RouteRecordRaw[] = [
  { path: 'login', component: () => import('./pages/login.vue') },
  { path: 'register', component: () => import('./pages/register.vue') },
  { path: 'callback', component: () => import('./pages/callback.vue') },
  { path: 'verify-email/:key', component: () => import('./pages/verify-email.vue') },
  { path: 'forgot-password', component: () => import('./pages/forgot-password.vue') },
  { path: 'reset-password/:key', component: () => import('./pages/reset-password.vue') },
]
