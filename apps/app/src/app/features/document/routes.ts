import type { RouteRecordRaw } from 'vue-router'

export const documentRoutes: RouteRecordRaw[] = [
  { path: 'documents', component: () => import('./pages/documents.vue') },
]
