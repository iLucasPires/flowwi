import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia } from '@/app/features/media/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

export const artKeys = {
  root: () => ['medias'] as const,
  list: () => ['medias', 'list'] as const,
}

function useMediaListQuery() {
  const { data, refetch, isLoading } = useQuery({
    queryKey: artKeys.list(),
    staleTime: 30_000,
    queryFn: () => apiFetch<iPaginationNumber<iMedia>>(API_MEDIA_URLS.LIST),
  })
  return { data, refetch, isLoading }
}

export const useMedia = () => {
  const toast = useToast()
  const queryClient = useQueryClient()
  const { data, refetch, isLoading } = useMediaListQuery()

  const media = computed(() => data.value?.results ?? [])

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: artKeys.root() })
  }

  const { mutateAsync: createMedia, status: createStatus } = useMutation({
    mutationFn: (body: { title: string; task?: number | null; notes?: string; type?: number }) =>
      apiFetch<iMedia>(API_MEDIA_URLS.LIST, { method: 'POST', body }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Mídia criada', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao criar mídia', color: 'error' }),
  })

  const { mutateAsync: updateMedia, status: updateStatus } = useMutation({
    mutationFn: (vars: { id: number; data: Partial<iMedia> }) =>
      apiFetch<iMedia>(`${API_MEDIA_URLS.LIST}/${vars.id}`, { method: 'PATCH', body: vars.data }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Mídia atualizada', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao atualizar', color: 'error' }),
  })

  const { mutateAsync: deleteMedia, status: deleteStatus } = useMutation({
    mutationFn: (id: number) => apiFetch(`${API_MEDIA_URLS.LIST}/${id}`, { method: 'DELETE' }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Mídia removida', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao remover', color: 'error' }),
  })

  return {
    data,
    media,
    isLoading,
    refresh: refetch,
    invalidate,
    createMedia,
    createStatus,
    updateMedia,
    updateStatus,
    deleteMedia,
    deleteStatus,
  }
}
