import { API_TASK_URLS, apiFetch } from '@/app/core/clients/api'
import { taskKeys } from '@/app/features/task/composables/task'
import type { iTask } from '@/app/features/task/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

// ─── Query Keys ──────────────────────────────────────────────────────────────

const trashedTaskKey = ['tasks', 'trashed'] as const

// ─── Composable ───────────────────────────────────────────────────────────────

/**
 * Composable to list soft-deleted tasks and restore them.
 */
export const useTrashedTasks = () => {
  const toast = useToast()
  const queryClient = useQueryClient()

  const {
    data,
    isLoading,
    refetch: refresh,
  } = useQuery({
    queryKey: trashedTaskKey,
    staleTime: 15_000,
    queryFn: () => apiFetch<iPaginationNumber<iTask>>(`${API_TASK_URLS.LIST}?trashed=true`),
  })

  const trashedTasks = computed(() => data.value?.results ?? [])

  const { mutateAsync: restoreTask, isPending: restoring } = useMutation({
    mutationFn: (public_id: string) =>
      apiFetch(API_TASK_URLS.RESTORE(public_id), { method: 'POST' }),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: trashedTaskKey })
      queryClient.invalidateQueries({ queryKey: taskKeys.root() })
      toast.add({ title: 'Tarefa restaurada', color: 'success' })
    },

    onError: () => toast.add({ title: 'Erro ao restaurar tarefa', color: 'error' }),
  })

  return {
    trashedTasks,
    isLoading,
    refresh,
    restoreTask,
    restoring,
  }
}
