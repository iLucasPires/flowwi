import { API_TASK_STATUS_URLS, apiFetch } from '@/app/core/clients/api'
import type { iTaskStatus } from '@/app/features/task/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'

/**
 * Cache keys for the task statuses domain.
 */
export const taskStatusKeys = {
  root: () => ['task-statuses'] as const,
  list: () => ['task-statuses', 'list'] as const,
}

/**
 * Composable to manage per-workplace task statuses (create, update, reorder, delete).
 */
export const useTaskStatus = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  const {
    data,
    refetch: refresh,
    isLoading,
  } = useQuery({
    queryKey: taskStatusKeys.list(),
    staleTime: 30_000,
    queryFn: () =>
      apiFetch<iPaginationNumber<iTaskStatus>>(`${API_TASK_STATUS_URLS.LIST}?page_size=100`),
  })

  const statuses = computed(() => data.value?.results ?? [])

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: taskStatusKeys.root() })
  }

  const { mutateAsync: createStatus } = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiFetch<iTaskStatus>(API_TASK_STATUS_URLS.LIST, { method: 'POST', body }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao criar status', color: 'error' }),
  })

  const { mutateAsync: updateStatus } = useMutation({
    mutationFn: (vars: { id: number; data: Record<string, unknown> }) =>
      apiFetch<iTaskStatus>(API_TASK_STATUS_URLS.DETAIL(vars.id), {
        method: 'PATCH',
        body: vars.data,
      }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao atualizar status', color: 'error' }),
  })

  const { mutateAsync: reorderStatus } = useMutation({
    mutationFn: (vars: { id: number; position: string }) =>
      apiFetch<iTaskStatus>(`${API_TASK_STATUS_URLS.DETAIL(vars.id)}/reorder`, {
        method: 'POST',
        body: { position: vars.position },
      }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao reordenar status', color: 'error' }),
  })

  const { mutateAsync: deleteStatus } = useMutation({
    mutationFn: (id: number) => apiFetch(API_TASK_STATUS_URLS.DETAIL(id), { method: 'DELETE' }),
    onSuccess: () => invalidate(),
    onError: (error: unknown) => {
      const message =
        (error as { data?: { detail?: string } })?.data?.detail ?? 'Erro ao excluir status'
      toast.add({ title: message, color: 'error' })
    },
  })

  return {
    data,
    statuses,
    isLoading,
    refresh,
    createStatus,
    updateStatus,
    reorderStatus,
    deleteStatus,
    invalidate,
  }
}
