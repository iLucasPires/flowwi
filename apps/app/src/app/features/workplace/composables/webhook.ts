import { API_WEBHOOK_URLS, apiFetch } from '@/app/core/clients/api'
import type { WebhookEvent, iWebhook } from '@/app/features/workplace/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

export const webhookKeys = {
  root: () => ['webhooks'] as const,
  list: () => ['webhooks', 'list'] as const,
}

function useWebhookListQuery() {
  const {
    data,
    refetch: refresh,
    isLoading,
  } = useQuery({
    queryKey: webhookKeys.list(),
    queryFn: () => apiFetch<iPaginationNumber<iWebhook>>(API_WEBHOOK_URLS.LIST),
  })
  return { data, refresh, isLoading }
}

export const useWebhook = () => {
  const toast = useToast()
  const queryClient = useQueryClient()
  const { data, refresh, isLoading } = useWebhookListQuery()

  const webhooks = computed(() => data.value?.results ?? [])

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: webhookKeys.root() })
  }

  const { mutateAsync: createWebhook } = useMutation({
    mutationFn: (body: { url: string; events: WebhookEvent[]; is_active?: boolean }) =>
      apiFetch<iWebhook>(API_WEBHOOK_URLS.LIST, { method: 'POST', body }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Webhook criado', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao criar webhook', color: 'error' }),
  })

  const { mutateAsync: updateWebhook } = useMutation({
    mutationFn: (vars: {
      id: number
      data: Partial<Pick<iWebhook, 'url' | 'events' | 'is_active'>>
    }) =>
      apiFetch<iWebhook>(`${API_WEBHOOK_URLS.LIST}/${vars.id}`, {
        method: 'PATCH',
        body: vars.data,
      }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Webhook atualizado', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao atualizar webhook', color: 'error' }),
  })

  const { mutateAsync: deleteWebhook } = useMutation({
    mutationFn: (id: number) => apiFetch(`${API_WEBHOOK_URLS.LIST}/${id}`, { method: 'DELETE' }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Webhook removido', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao remover webhook', color: 'error' }),
  })

  return {
    data,
    webhooks,
    isLoading,
    refresh,
    invalidate,
    createWebhook,
    updateWebhook,
    deleteWebhook,
  }
}
