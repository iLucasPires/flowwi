import { API_WORKPLACE_URLS, apiFetch } from '@/app/core/clients'
import type { iWorkplace } from '@/app/features/workplace/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'
import { useQueryClient, useMutation, useQuery } from '@tanstack/vue-query'

export const workplaceKeys = {
  root: () => ['workplaces'] as const,
  list: () => ['workplaces', 'list'] as const,
}

const savedWorkplaceId = useLocalStorage<string | null>('workplace-id', null)

/**
 * Internal workplace state (no vue-query dependency).
 */
const workplacesState = ref<iWorkplace[]>([])

/**
 * Safe to call anywhere (guards, components, etc).
 * Does NOT use useQuery/useMutation.
 */
export const useWorkplace = () => {
  const workplaces = computed(() => workplacesState.value)

  const workplace = computed<iWorkplace | null>(() => {
    if (!savedWorkplaceId.value) return null
    return workplaces.value.find((w) => String(w.id) === savedWorkplaceId.value) ?? null
  })

  const hasCurrent = computed(() => !!workplace.value)

  async function refreshWorkplaces() {
    const res = await apiFetch<iPaginationNumber<iWorkplace>>(API_WORKPLACE_URLS.LIST)
    workplacesState.value = res.results ?? []
    return res
  }

  async function setCurrent(w: iWorkplace) {
    const prev = savedWorkplaceId.value
    const nextId = String(w.id)
    await apiFetch(API_WORKPLACE_URLS.SELECT(w.id), { method: 'POST' })
    savedWorkplaceId.value = nextId

    return prev !== nextId
  }

  function clearCurrent() {
    savedWorkplaceId.value = null
    apiFetch(API_WORKPLACE_URLS.DESELECT, { method: 'POST' })
  }

  return {
    workplace,
    workplaces,
    savedWorkplaceId,
    hasCurrent,
    setCurrent,
    clearCurrent,
    refreshWorkplaces,
  }
}

/**
 * Workplace mutations and queries that require component setup context.
 * Only call inside <script setup> or a running effect scope.
 */
export const useWorkplaceMutations = () => {
  const queryClient = useQueryClient()
  const { setCurrent, clearCurrent } = useWorkplace()

  const {
    refetch: refetchWorkplaces,
    status: workplacesStatus,
  } = useQuery({
    queryKey: workplaceKeys.list(),
    staleTime: 60_000,
    queryFn: () => apiFetch<iPaginationNumber<iWorkplace>>(API_WORKPLACE_URLS.LIST),
  })

  const { mutateAsync: createWorkplace, status: createStatus } = useMutation({
    mutationFn: (name: string) =>
      apiFetch<iWorkplace>(API_WORKPLACE_URLS.LIST, { method: 'POST', body: { name } }),
    onSuccess: async (_data) => {
      await queryClient.invalidateQueries({ queryKey: workplaceKeys.list() })
      await setCurrent(_data)
    },
  })

  const { mutateAsync: updateWorkplace, status: updateStatus } = useMutation({
    mutationFn: (vars: { id: number; data: Partial<iWorkplace> }) =>
      apiFetch<iWorkplace>(API_WORKPLACE_URLS.DETAIL(vars.id), {
        method: 'PATCH',
        body: vars.data,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: workplaceKeys.list() }),
  })

  const { mutateAsync: deleteWorkplace, status: deleteStatus } = useMutation({
    mutationFn: (id: number) => apiFetch(API_WORKPLACE_URLS.DETAIL(id), { method: 'DELETE' }),
    onSuccess: () => {
      clearCurrent()
      queryClient.invalidateQueries({ queryKey: workplaceKeys.list() })
    },
  })

  const { mutateAsync: regenerateInviteKey } = useMutation({
    mutationFn: (id: number) =>
      apiFetch<iWorkplace>(API_WORKPLACE_URLS.REGENERATE_INVITE_KEY(id), { method: 'POST' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: workplaceKeys.list() }),
  })

  const { mutateAsync: joinByKey, status: joinStatus } = useMutation({
    mutationFn: (inviteKey: string) =>
      apiFetch<iWorkplace>(API_WORKPLACE_URLS.JOIN, {
        method: 'POST',
        body: { invite_key: inviteKey },
      }),
    onSuccess: async (_data) => {
      await queryClient.invalidateQueries({ queryKey: workplaceKeys.list() })
      await setCurrent(_data)
    },
  })

  return {
    workplacesStatus,
    refetchWorkplaces,
    createWorkplace,
    createStatus,
    updateWorkplace,
    updateStatus,
    deleteWorkplace,
    deleteStatus,
    regenerateInviteKey,
    joinByKey,
    joinStatus,
  }
}
