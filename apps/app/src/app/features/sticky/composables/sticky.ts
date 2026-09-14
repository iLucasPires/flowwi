import { API_STICKY_URLS, apiFetch } from '@/app/core/clients/api'
import type { iSticky } from '@/app/features/sticky/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

// ─── Types ───────────────────────────────────────────────────────────────────

type StickyListResponse = iPaginationNumber<iSticky> | iSticky[]

// ─── Query Keys ──────────────────────────────────────────────────────────────

export const stickyKeys = {
  root: () => ['stickies'] as const,
  list: () => ['stickies', 'list'] as const,
}

// ─── Shared Query ─────────────────────────────────────────────────────────────

function useStickyListQuery() {
  const { data, refetch, isLoading } = useQuery({
    queryKey: stickyKeys.list(),
    staleTime: 30_000,
    queryFn: () => apiFetch<StickyListResponse>(API_STICKY_URLS.LIST),
  })

  return { data, refetch, isLoading }
}

// ─── Composable ───────────────────────────────────────────────────────────────

export const useSticky = () => {
  const toast = useToast()
  const queryClient = useQueryClient()

  const { data, refetch, isLoading } = useStickyListQuery()

  // ── Cache helpers ──────────────────────────────────────────────────────────

  function getCachedList() {
    return queryClient.getQueryData<StickyListResponse>(stickyKeys.list())
  }

  function setCachedList(next: StickyListResponse | undefined) {
    queryClient.setQueryData(stickyKeys.list(), next)
  }

  /** Insere ou atualiza um sticky no cache sem refetch. */
  function upsertStickyInList(updated: iSticky) {
    const cached = getCachedList()
    if (!cached) return

    if (Array.isArray(cached)) {
      const exists = cached.some((s) => s.id === updated.id)
      const next = exists
        ? cached.map((s) => (s.id === updated.id ? { ...s, ...updated } : s))
        : [updated, ...cached]
      setCachedList(next)
      return
    }

    const results = cached.results ?? []
    const exists = results.some((s) => s.id === updated.id)
    const nextResults = exists
      ? results.map((s) => (s.id === updated.id ? { ...s, ...updated } : s))
      : [updated, ...results]

    setCachedList({ ...cached, results: nextResults })
  }

  // ── Derived state ──────────────────────────────────────────────────────────

  const stickies = computed<iSticky[]>(() => {
    const v = data.value
    if (!v) return []
    return Array.isArray(v) ? v : (v.results ?? [])
  })

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: stickyKeys.root() })
  }

  // ── Mutations ──────────────────────────────────────────────────────────────

  const { mutateAsync: createSticky } = useMutation({
    mutationFn: (body: Pick<iSticky, 'text' | 'color' | 'visibility'>) =>
      apiFetch<iSticky>(API_STICKY_URLS.LIST, { method: 'POST', body }),

    onSuccess: (created) => {
      const cached = getCachedList()

      if (!cached) {
        setCachedList([created])
      } else if (Array.isArray(cached)) {
        setCachedList([created, ...cached])
      } else {
        setCachedList({
          ...cached,
          count: (cached.count ?? 0) + 1,
          results: [created, ...(cached.results ?? [])],
        })
      }
    },

    onError: () => toast.add({ title: 'Erro ao criar sticky', color: 'error' }),
  })

  const { mutateAsync: deleteSticky } = useMutation({
    mutationFn: (id: number) => apiFetch(`${API_STICKY_URLS.LIST}/${id}`, { method: 'DELETE' }),

    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: stickyKeys.list() })
      const oldList = getCachedList()
      if (!oldList) return { oldList, nextList: oldList, deletedId: id }

      const nextList = Array.isArray(oldList)
        ? oldList.filter((s) => s.id !== id)
        : {
            ...oldList,
            count: Math.max(0, (oldList.count ?? 0) - 1),
            results: (oldList.results ?? []).filter((s) => s.id !== id),
          }

      setCachedList(nextList)
      return { oldList, nextList, deletedId: id }
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stickies', 'trashed'] })
    },

    onError: (_err, _id, ctx) => {
      if (ctx && ctx.nextList === getCachedList()) setCachedList(ctx.oldList)
      toast.add({ title: 'Erro ao remover sticky', color: 'error' })
    },
  })

  const { mutateAsync: updateSticky } = useMutation({
    mutationFn: (vars: {
      id: number
      data: Partial<Pick<iSticky, 'text' | 'color' | 'visibility'>>
    }) =>
      apiFetch<iSticky>(`${API_STICKY_URLS.LIST}/${vars.id}`, {
        method: 'PATCH',
        body: vars.data,
      }),

    onMutate: async (vars) => {
      await queryClient.cancelQueries({ queryKey: stickyKeys.list() })
      const oldList = getCachedList()
      if (!oldList) return { oldList, nextList: oldList, id: vars.id }

      const applyUpdate = (s: iSticky) => (s.id === vars.id ? { ...s, ...vars.data } : s)

      const nextList = Array.isArray(oldList)
        ? oldList.map(applyUpdate)
        : { ...oldList, results: (oldList.results ?? []).map(applyUpdate) }

      setCachedList(nextList)
      return { oldList, nextList, id: vars.id }
    },

    onSuccess: (updated) => upsertStickyInList(updated),

    onError: (_err, _vars, ctx) => {
      if (ctx && ctx.nextList === getCachedList()) setCachedList(ctx.oldList)
      toast.add({ title: 'Erro ao salvar sticky', color: 'error' })
    },
  })

  const { mutateAsync: reorderSticky } = useMutation({
    mutationFn: (vars: { id: number; position: string }) =>
      apiFetch<iSticky>(`${API_STICKY_URLS.LIST}/${vars.id}/reorder`, {
        method: 'POST',
        body: { position: vars.position },
      }),

    onMutate: async (vars) => {
      await queryClient.cancelQueries({ queryKey: stickyKeys.list() })
      const oldList = getCachedList()
      if (!oldList) return { oldList }

      const applyUpdate = (s: iSticky) => (s.id === vars.id ? { ...s, position: vars.position } : s)

      const nextList = Array.isArray(oldList)
        ? oldList.map(applyUpdate)
        : { ...oldList, results: (oldList.results ?? []).map(applyUpdate) }

      setCachedList(nextList)
      return { oldList }
    },

    onSuccess: (updated) => upsertStickyInList(updated),

    onError: (_err, _vars, ctx) => {
      if (ctx?.oldList) setCachedList(ctx.oldList)
      toast.add({ title: 'Erro ao reordenar sticky', color: 'error' })
    },
  })

  // ── Public API ─────────────────────────────────────────────────────────────

  return {
    data,
    stickies,
    refresh: refetch,
    isLoading,
    invalidate,
    createSticky,
    deleteSticky,
    updateSticky,
    reorderSticky,
  }
}
