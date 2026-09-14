import type { RouteRecordRaw } from 'vue-router'

export const taskRoutes: RouteRecordRaw[] = [
  { path: 'tasks', component: () => import('./pages/task-list.vue') },
  { path: 'tasks/:id', component: () => import('./pages/task-detail.vue') },
]
