import { API_DOCUMENT_URLS, apiFetch } from '@/app/core/clients/api'
import { documentKeys } from '@/app/features/document/composables/document'
import type { iDocument } from '@/app/features/document/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

// ─── Query Keys ──────────────────────────────────────────────────────────────

const trashedDocumentKey = ['documents', 'trashed'] as const

// ─── Composable ───────────────────────────────────────────────────────────────

/**
 * Composable to list soft-deleted documents and restore them.
 */
export const useTrashedDocuments = () => {
  const toast = useToast()
  const queryClient = useQueryClient()

  const {
    data,
    isLoading,
    refetch: refresh,
  } = useQuery({
    queryKey: trashedDocumentKey,
    staleTime: 15_000,
    queryFn: () => apiFetch<iPaginationNumber<iDocument>>(`${API_DOCUMENT_URLS.LIST}?trashed=true`),
  })

  const trashedDocuments = computed(() => data.value?.results ?? [])

  const { mutateAsync: restoreDocument, isPending: restoring } = useMutation({
    mutationFn: (id: string | number) => apiFetch(API_DOCUMENT_URLS.RESTORE(id), { method: 'POST' }),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: trashedDocumentKey })
      queryClient.invalidateQueries({ queryKey: documentKeys.root() })
      toast.add({ title: 'Documento restaurado', color: 'success' })
    },

    onError: () => toast.add({ title: 'Erro ao restaurar documento', color: 'error' }),
  })

  return {
    trashedDocuments,
    isLoading,
    refresh,
    restoreDocument,
    restoring,
  }
}
