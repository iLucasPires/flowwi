import { API_INBOX_URLS, apiFetch } from '@/app/core/clients/api'
import type { iInbox } from '@/app/features/inbox/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

export const inboxKeys = {
  root: () => ['inbox'] as const,
  list: () => ['inbox', 'list'] as const,
}

function useInboxQuery() {
  const { data, refetch } = useQuery({
    queryKey: inboxKeys.list(),
    staleTime: 15_000,
    queryFn: () => apiFetch<iPaginationNumber<iInbox>>(`${API_INBOX_URLS.LIST}?expand=sender`),
  })
  return { data, refetch }
}

export const useInbox = () => {
  const queryClient = useQueryClient()
  const { data, refetch } = useInboxQuery()

  const items = computed(() => data.value?.results ?? [])
  const unreadCount = computed(() => items.value.filter((i) => !i.is_read).length)

  const { mutateAsync: markAsRead } = useMutation({
    mutationFn: (id: string | number) => apiFetch(API_INBOX_URLS.READ(id), { method: 'POST' }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: inboxKeys.root() }),
  })

  const { mutateAsync: markAllAsRead } = useMutation({
    mutationFn: () => apiFetch(API_INBOX_URLS.READ_ALL, { method: 'POST' }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: inboxKeys.root() }),
  })

  const { mutateAsync: deleteNotification } = useMutation({
    mutationFn: (id: string | number) =>
      apiFetch(`${API_INBOX_URLS.LIST}/${id}`, { method: 'DELETE' }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: inboxKeys.root() }),
  })

  const { mutateAsync: deleteAll } = useMutation({
    mutationFn: () => apiFetch(API_INBOX_URLS.DELETE_ALL, { method: 'DELETE' }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: inboxKeys.root() }),
  })

  return {
    data,
    items,
    unreadCount,
    refresh: refetch,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    deleteAll,
  }
}
