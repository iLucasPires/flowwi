import { API_SUBTASK_URLS, apiFetch } from '@/app/core/clients/api'
import type { iSub } from '@/app/features/task/types'
import { useMutation } from '@tanstack/vue-query'

export const useSubtask = () => {
  const toast = useToast()

  const { mutateAsync: createSubtask, status: createStatus } = useMutation({
    mutationFn: (body: { task: number; title: string }) =>
      apiFetch<iSub>(`${API_SUBTASK_URLS.LIST}`, { method: 'POST', body }),
    onError: () => toast.add({ title: 'Erro ao criar subtarefa', color: 'error' }),
  })

  const { mutateAsync: toggleSubtask } = useMutation({
    mutationFn: (vars: { public_id: string; is_done: boolean }) =>
      apiFetch<iSub>(`${API_SUBTASK_URLS.LIST}/${vars.public_id}`, {
        method: 'PATCH',
        body: { is_done: vars.is_done },
      }),
  })

  const { mutateAsync: deleteSubtask } = useMutation({
    mutationFn: (vars: { public_id: string }) =>
      apiFetch(`${API_SUBTASK_URLS.LIST}/${vars.public_id}`, { method: 'DELETE' }),
    onError: () => toast.add({ title: 'Erro ao remover subtarefa', color: 'error' }),
  })

  const { mutateAsync: reorderSubtask } = useMutation({
    mutationFn: (vars: { public_id: string; position: string }) =>
      apiFetch<iSub>(`${API_SUBTASK_URLS.LIST}/${vars.public_id}/reorder`, {
        method: 'POST',
        body: { position: vars.position },
      }),
  })

  return {
    createSubtask,
    toggleSubtask,
    deleteSubtask,
    reorderSubtask,
    isCreating: computed(() => createStatus.value === 'pending'),
  }
}
