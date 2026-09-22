import { API_DOCUMENT_URLS, apiFetch } from '@/app/core/clients/api'
import type { iDocument, iDocumentVersion } from '@/app/features/document/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

export const documentKeys = {
  root: () => ['documents'] as const,
  list: () => ['documents', 'list'] as const,
}

function useDocumentListQuery() {
  const { data, refetch, isLoading } = useQuery({
    queryKey: documentKeys.list(),
    staleTime: 30_000,
    queryFn: () => apiFetch<iPaginationNumber<iDocument>>(API_DOCUMENT_URLS.LIST),
  })
  return { data, refetch, isLoading }
}

export const useDocument = () => {
  const toast = useToast()
  const queryClient = useQueryClient()
  const { data, refetch, isLoading } = useDocumentListQuery()

  const documents = computed(() => data.value?.results ?? [])

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: documentKeys.root() })
  }

  const { mutateAsync: createDocument, status: createStatus } = useMutation({
    mutationFn: async (body: {
      title: string
      task?: number | null
      type?: number | null
      notes?: string
      folder?: string
      content?: string
    }) => {
      const { content, ...documentBody } = body
      const document = await apiFetch<iDocument>(API_DOCUMENT_URLS.LIST, {
        method: 'POST',
        body: documentBody,
      })

      const version = await apiFetch<iDocumentVersion>(API_DOCUMENT_URLS.VERSIONS, {
        method: 'POST',
        body: { document: document.id, content: content ?? '' },
      })

      return { ...document, versions: [version] }
    },
    onSettled: () => invalidate(),
    onError: () => toast.add({ title: 'Erro ao criar documento', color: 'error' }),
  })

  const { mutateAsync: updateDocument, status: updateStatus } = useMutation({
    mutationFn: (vars: { id: number; data: Partial<iDocument> }) =>
      apiFetch<iDocument>(`${API_DOCUMENT_URLS.LIST}/${vars.id}`, {
        method: 'PATCH',
        body: vars.data,
      }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Documento atualizado', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao atualizar', color: 'error' }),
  })

  const { mutateAsync: deleteDocument, status: deleteStatus } = useMutation({
    mutationFn: (id: number) => apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: 'DELETE' }),
    onSettled: () => invalidate(),
    onSuccess: () => toast.add({ title: 'Documento removido', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao remover', color: 'error' }),
  })

  return {
    data,
    documents,
    isLoading,
    refresh: refetch,
    invalidate,
    createDocument,
    createStatus,
    updateDocument,
    updateStatus,
    deleteDocument,
    deleteStatus,
  }
}
