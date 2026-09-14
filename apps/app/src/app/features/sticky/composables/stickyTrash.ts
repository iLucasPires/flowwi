import { API_STICKY_URLS, apiFetch } from '@/app/core/clients/api'
import { stickyKeys } from '@/app/features/sticky/composables/sticky'
import type { iSticky } from '@/app/features/sticky/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

// ─── Types ───────────────────────────────────────────────────────────────────

type TrashedStickyListResponse = iPaginationNumber<iSticky> | iSticky[]

// ─── Query Keys ──────────────────────────────────────────────────────────────

const trashedStickyKey = ['stickies', 'trashed'] as const

// ─── Composable ───────────────────────────────────────────────────────────────

/**
 * Composable to list soft-deleted stickies and restore them.
 */
export const useTrashedStickies = () => {
  const toast = useToast()
  const queryClient = useQueryClient()

  const {
    data,
    isLoading,
    refetch: refresh,
  } = useQuery({
    queryKey: trashedStickyKey,
    staleTime: 15_000,
    queryFn: () => apiFetch<TrashedStickyListResponse>(`${API_STICKY_URLS.LIST}?trashed=true`),
  })

  const trashedStickies = computed<iSticky[]>(() => {
    const value = data.value
    if (!value) return []
    return Array.isArray(value) ? value : (value.results ?? [])
  })

  const { mutateAsync: restoreSticky, isPending: restoring } = useMutation({
    mutationFn: (id: number) => apiFetch(API_STICKY_URLS.RESTORE(id), { method: 'POST' }),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: trashedStickyKey })
      queryClient.invalidateQueries({ queryKey: stickyKeys.root() })
      toast.add({ title: 'Sticky restaurado', color: 'success' })
    },

    onError: () => toast.add({ title: 'Erro ao restaurar sticky', color: 'error' }),
  })

  return {
    trashedStickies,
    isLoading,
    refresh,
    restoreSticky,
    restoring,
  }
}
