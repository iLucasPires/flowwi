import { API_TASK_TYPE_URLS, apiFetch } from '@/app/core/clients/api'
import type { iTaskType } from '@/app/features/task/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'

/**
 * Cache keys for the task types domain.
 */
export const taskTypeKeys = {
  root: () => ['task-types'] as const,
  list: () => ['task-types', 'list'] as const,
}

/**
 * Composable to manage per-workplace task types (create, update, reorder, delete).
 */
export const useTaskType = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  const {
    data,
    refetch: refresh,
    isLoading,
  } = useQuery({
    queryKey: taskTypeKeys.list(),
    staleTime: 30_000,
    queryFn: () =>
      apiFetch<iPaginationNumber<iTaskType>>(`${API_TASK_TYPE_URLS.LIST}?page_size=100`),
  })

  const types = computed(() => data.value?.results ?? [])

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: taskTypeKeys.root() })
  }

  const { mutateAsync: createType } = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiFetch<iTaskType>(API_TASK_TYPE_URLS.LIST, { method: 'POST', body }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao criar tipo', color: 'error' }),
  })

  const { mutateAsync: updateType } = useMutation({
    mutationFn: (vars: { id: number; data: Record<string, unknown> }) =>
      apiFetch<iTaskType>(API_TASK_TYPE_URLS.DETAIL(vars.id), {
        method: 'PATCH',
        body: vars.data,
      }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao atualizar tipo', color: 'error' }),
  })

  const { mutateAsync: reorderType } = useMutation({
    mutationFn: (vars: { id: number; position: string }) =>
      apiFetch<iTaskType>(`${API_TASK_TYPE_URLS.DETAIL(vars.id)}/reorder`, {
        method: 'POST',
        body: { position: vars.position },
      }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao reordenar tipo', color: 'error' }),
  })

  const { mutateAsync: deleteType } = useMutation({
    mutationFn: (id: number) => apiFetch(API_TASK_TYPE_URLS.DETAIL(id), { method: 'DELETE' }),
    onSuccess: () => invalidate(),
    onError: (error: unknown) => {
      const message =
        (error as { data?: { detail?: string } })?.data?.detail ?? 'Erro ao excluir tipo'
      toast.add({ title: message, color: 'error' })
    },
  })

  return {
    data,
    types,
    isLoading,
    refresh,
    createType,
    updateType,
    reorderType,
    deleteType,
    invalidate,
  }
}
