import { API_TASK_URLS, apiFetch } from '@/app/core/clients/api'
import type { iTask } from '@/app/features/task/types'
import { computed, type Ref } from 'vue'
import { useQuery, useQueryClient } from '@tanstack/vue-query'

/**
 * Composable to fetch and manage the details of a single task.
 *
 * @param taskId - Reactive reference to the public_id of the task to fetch.
 */
export const useTaskDetail = (taskId: Ref<string | null>, enabled?: Ref<boolean>) => {
  const queryClient = useQueryClient()

  /**
   * Dynamic query key that updates when the taskId changes.
   */
  const queryKey = computed(() => ['task', taskId.value] as const)

  /**
   * Main query to fetch the task details.
   */
  const {
    data,
    isLoading,
    refetch: refresh,
  } = useQuery({
    queryKey,
    staleTime: 60_000,
    queryFn: () => apiFetch<iTask>(`${API_TASK_URLS.LIST}/${taskId.value}?expand=subs,assignees`),
    enabled: () => taskId.value != null && (enabled?.value ?? true),
  })

  /**
   * Manually invalidates the task cache for this specific ID.
   */
  function invalidate() {
    if (taskId.value != null) {
      queryClient.invalidateQueries({ queryKey: ['task', taskId.value] })
    }
  }

  return {
    task: data,
    isLoading,
    refresh,
    invalidate,
  }
}
