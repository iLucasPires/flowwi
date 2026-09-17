import { API_QUICKLINK_URLS, apiFetch } from '@/app/core/clients/api'
import type { iQuickLink } from '@/app/features/home/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

export const quicklinkKeys = {
  root: () => ['quicklinks'] as const,
  list: () => ['quicklinks', 'list'] as const,
}

/**
 * Composable to list, create and remove Home page quicklinks.
 */
export const useQuicklink = () => {
  const toast = useToast()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: quicklinkKeys.list(),
    staleTime: 30_000,
    queryFn: () =>
      apiFetch<iPaginationNumber<iQuickLink>>(`${API_QUICKLINK_URLS.LIST}?page_size=100`),
  })

  const quicklinks = computed(() => data.value?.results ?? [])

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: quicklinkKeys.root() })
  }

  const { mutateAsync: createQuicklink, isPending: creating } = useMutation({
    mutationFn: (body: { title: string; url: string; icon?: string }) =>
      apiFetch<iQuickLink>(API_QUICKLINK_URLS.LIST, { method: 'POST', body }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao adicionar link', color: 'error' }),
  })

  const { mutateAsync: deleteQuicklink } = useMutation({
    mutationFn: (id: number) => apiFetch(API_QUICKLINK_URLS.DETAIL(id), { method: 'DELETE' }),
    onSuccess: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao remover link', color: 'error' }),
  })

  return {
    quicklinks,
    isLoading,
    createQuicklink,
    creating,
    deleteQuicklink,
  }
}
