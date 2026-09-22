import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";

import { apiFetch, API_DOCUMENT_URLS } from "@/app/core/clients/api";
import { documentKeys } from './document'
import type { iDocument } from "@/app/features/document/types";
import type { iPaginationNumber } from "@/app/shared/types/pagination";

const trashedDocumentKey = ["documents", "trashed"] as const;

export const useTrashedDocuments = () => {
  const toast = useToast();
  const queryClient = useQueryClient();

  // Query

  const {
    data,
    isLoading,
    refetch: refresh,
  } = useQuery({
    queryKey: trashedDocumentKey,
    queryFn: () => apiFetch<iPaginationNumber<iDocument>>(`${API_DOCUMENT_URLS.LIST}?trashed=true`),
    staleTime: 15_000,
  });

  const trashedDocuments = computed(() => data.value?.results ?? []);

  // Mutation

  const { mutateAsync: restoreDocument, isPending: restoring } = useMutation({
    mutationFn: (id: string | number) =>
      apiFetch(API_DOCUMENT_URLS.RESTORE(id), {
        method: "POST",
      }),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: trashedDocumentKey,
      });

      queryClient.invalidateQueries({
        queryKey: documentKeys.root(),
      });

      toast.add({
        title: "Documento restaurado",
        color: "success",
      });
    },

    onError: () => {
      toast.add({
        title: "Erro ao restaurar documento",
        color: "error",
      });
    },
  });

  return {
    trashedDocuments,
    isLoading,
    refresh,
    restoreDocument,
    restoring,
  };
};
