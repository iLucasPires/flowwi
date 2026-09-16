import { API_TASK_URLS, apiFetch } from '@/app/core/clients/api'
import type { iTask } from '@/app/features/task/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

/**
 * Cache keys for the tasks domain.
 */
export const taskKeys = {
  root: () => ['tasks'] as const,
  list: () => ['tasks', 'list'] as const,
}

/**
 * Composable to manage tasks, including creation, updates, and status changes.
 */
export const useTask = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  /**
   * Defined query for fetching the task list.
   */
  const {
    data,
    refetch: refresh,
    isLoading,
  } = useQuery({
    queryKey: taskKeys.list(),
    staleTime: 30_000,
    queryFn: () =>
      apiFetch<iPaginationNumber<iTask>>(`${API_TASK_URLS.LIST}?expand=assignees,profile`),
  })

  /**
   * Computed property for easy access to the list of tasks.
   */
  const tasks = computed(() => data.value?.results ?? [])

  function getCachedList() {
    return queryClient.getQueryData<iPaginationNumber<iTask>>(taskKeys.list())
  }

  function setCachedList(next: iPaginationNumber<iTask> | undefined) {
    queryClient.setQueryData(taskKeys.list(), next)
  }

  function updateTaskInList(public_id: string, patch: Record<string, unknown>) {
    const cached = getCachedList()
    if (!cached) return
    const nextResults = (cached.results ?? []).map((t) =>
      t.public_id === public_id ? { ...t, ...patch } : t,
    )
    setCachedList({ ...cached, results: nextResults as iTask[] })
  }

  function updateTaskInDetail(public_id: string, patch: Record<string, unknown>) {
    const key = ['task', public_id] as const
    const cached = queryClient.getQueryData<iTask>(key)
    if (!cached) return
    queryClient.setQueryData(key, { ...cached, ...patch })
  }

  /**
   * Invalidates all task-related queries to trigger a refresh.
   */
  function invalidate() {
    queryClient.invalidateQueries({ queryKey: taskKeys.root() })
  }

  /**
   * Mutation to create a new task.
   */
  const { mutateAsync: createTask } = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiFetch<iTask>(API_TASK_URLS.LIST, {
        method: 'POST',
        body,
      }),

    onSettled: () => invalidate(),

    onSuccess: () =>
      toast.add({
        title: 'Tarefa criada',
        color: 'success',
      }),

    onError: () =>
      toast.add({
        title: 'Erro ao criar tarefa',
        color: 'error',
      }),
  })

  /**
   * Mutation to update an existing task.
   */
  const { mutateAsync: updateTask } = useMutation({
    mutationFn: (vars: { public_id: string; data: Record<string, unknown> }) =>
      apiFetch<unknown>(`${API_TASK_URLS.LIST}/${vars.public_id}`, {
        method: 'PATCH',
        body: vars.data,
      }),

    onMutate: async (vars) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.list() })
      await queryClient.cancelQueries({ queryKey: ['task', vars.public_id] })

      const oldList = getCachedList()
      const oldDetail = queryClient.getQueryData<iTask>(['task', vars.public_id])

      updateTaskInList(vars.public_id, vars.data)
      updateTaskInDetail(vars.public_id, vars.data)

      return {
        oldList,
        oldDetail,
        nextList: getCachedList(),
        nextDetail: queryClient.getQueryData<iTask>(['task', vars.public_id]),
        public_id: vars.public_id,
      }
    },

    onSuccess: (updated, vars) => {
      if (updated && typeof updated === 'object') {
        const task = updated as Partial<iTask>
        const pid = task.public_id ?? vars.public_id
        updateTaskInList(pid, task)
        updateTaskInDetail(pid, task)
      }
    },

    onError: (_err, vars, ctx) => {
      const cachedList = getCachedList()
      if (ctx && ctx.nextList === cachedList) setCachedList(ctx.oldList)

      const cachedDetail = queryClient.getQueryData<iTask>(['task', vars.public_id])
      if (ctx && ctx.nextDetail === cachedDetail) {
        queryClient.setQueryData(['task', vars.public_id], ctx.oldDetail)
      }

      toast.add({
        title: 'Erro ao atualizar',
        color: 'error',
      })
    },
  })

  /**
   * Mutation to update ONLY the status of a task.
   */
  const { mutateAsync: updateStatus } = useMutation({
    mutationFn: (vars: { public_id: string; status: number }) =>
      apiFetch<unknown>(`${API_TASK_URLS.LIST}/${vars.public_id}`, {
        method: 'PATCH',
        body: { status: vars.status },
      }),

    onMutate: async (vars) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.list() })

      const oldList = getCachedList()
      const oldDetail = queryClient.getQueryData<iTask>(['task', vars.public_id])

      updateTaskInList(vars.public_id, { status: vars.status })
      updateTaskInDetail(vars.public_id, { status: vars.status })

      return {
        oldList,
        oldDetail,
        nextList: getCachedList(),
        nextDetail: queryClient.getQueryData<iTask>(['task', vars.public_id]),
        public_id: vars.public_id,
      }
    },

    onSuccess: (updated, vars) => {
      if (!updated || typeof updated !== 'object') return
      const task = updated as Partial<iTask>
      const pid = task.public_id ?? vars.public_id

      updateTaskInList(pid, task)
      updateTaskInDetail(pid, task)
    },

    onError: (_err, vars, ctx) => {
      const cachedList = getCachedList()
      if (ctx && ctx.nextList === cachedList) setCachedList(ctx.oldList)

      const cachedDetail = queryClient.getQueryData<iTask>(['task', vars.public_id])
      if (ctx && ctx.nextDetail === cachedDetail) {
        queryClient.setQueryData(['task', vars.public_id], ctx.oldDetail)
      }

      toast.add({
        title: 'Erro ao atualizar status',
        color: 'error',
      })
    },
  })

  /**
   * Mutation to delete a task.
   */
  const { mutateAsync: deleteTask } = useMutation({
    mutationFn: (public_id: string) =>
      apiFetch(`${API_TASK_URLS.LIST}/${public_id}`, { method: 'DELETE' }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Tarefa removida', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao remover tarefa', color: 'error' }),
  })

  /**
   * Mutation to reorder a task (update position).
   */
  const { mutateAsync: reorderTask } = useMutation({
    mutationFn: (vars: { public_id: string; position: string; status: number }) =>
      apiFetch<iTask>(`${API_TASK_URLS.LIST}/${vars.public_id}/reorder?expand=assignees,profile`, {
        method: 'POST',
        body: { position: vars.position, status: vars.status },
      }),

    onMutate: async (vars) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.list() })
      await queryClient.cancelQueries({ queryKey: ['task', vars.public_id] })

      const oldList = getCachedList()
      const oldDetail = queryClient.getQueryData<iTask>(['task', vars.public_id])

      updateTaskInList(vars.public_id, { position: vars.position, status: vars.status })
      updateTaskInDetail(vars.public_id, { position: vars.position, status: vars.status })

      return {
        oldList,
        oldDetail,
        nextList: getCachedList(),
        nextDetail: queryClient.getQueryData<iTask>(['task', vars.public_id]),
        public_id: vars.public_id,
      }
    },

    onSuccess: (updated, vars) => {
      if (!updated || typeof updated !== 'object') return
      const task = updated as Partial<iTask>
      const pid = task.public_id ?? vars.public_id

      updateTaskInList(pid, task)
      updateTaskInDetail(pid, task)
    },

    onError: (_err, vars, ctx) => {
      const cachedList = getCachedList()
      if (ctx && ctx.nextList === cachedList) setCachedList(ctx.oldList)

      const cachedDetail = queryClient.getQueryData<iTask>(['task', vars.public_id])
      if (ctx && ctx.nextDetail === cachedDetail) {
        queryClient.setQueryData(['task', vars.public_id], ctx.oldDetail)
      }

      toast.add({
        title: 'Erro ao reordenar tarefa',
        color: 'error',
      })
    },
  })

  return {
    data,
    tasks,
    isLoading,
    refresh,
    createTask,
    updateTask,
    updateStatus,
    reorderTask,
    deleteTask,
    invalidate,
  }
}
