import { API_WORKPLACE_MEMBER_URLS, apiFetch } from '@/app/core/clients/api'
import { useUser } from '@/app/features/user/composables/user'
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
import type { WorkplaceRole, iWorkplaceMember } from '@/app/features/workplace/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'

export const workplaceMemberKeys = {
  root: () => ['workplace-members'] as const,
  list: (workplaceId?: number | string) =>
    workplaceId
      ? (['workplace-members', 'list', String(workplaceId)] as const)
      : (['workplace-members', 'list'] as const),
}

export const useWorkplaceMember = () => {
  const toast = useToast()
  const { user } = useUser()
  const { workplace } = useWorkplace()
  const queryClient = useQueryClient()

  const queryKey = computed(() => workplaceMemberKeys.list(workplace.value?.id))

  const {
    data,
    isLoading,
    refetch: refresh,
  } = useQuery({
    queryKey,
    staleTime: 1000 * 60 * 5,
    queryFn: () =>
      apiFetch<iPaginationNumber<iWorkplaceMember>>(API_WORKPLACE_MEMBER_URLS.LIST, {
        query: { expand: 'profile' },
      }),
    enabled: () => !!workplace.value?.id,
  })

  const members = computed(() => data.value?.results ?? [])

  const myMember = computed(() => members.value.find((m) => m.user === user.value?.id))

  const myRole = computed<WorkplaceRole | null>(() => myMember.value?.role ?? null)

  const isAdmin = computed(() => myRole.value === 'owner' || myRole.value === 'manager')

  const { mutateAsync: addMember, status: addStatus } = useMutation({
    mutationFn: (vars: { user: string; role: WorkplaceRole }) =>
      apiFetch<iWorkplaceMember>(`${API_WORKPLACE_MEMBER_URLS.LIST}/`, {
        method: 'POST',
        body: {
          user: vars.user,
          role: vars.role,
        },
      }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKey.value }),
    onSuccess: () => toast.add({ title: 'Membro adicionado', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao adicionar membro', color: 'error' }),
  })

  const { mutateAsync: updateMemberRole, status: updateStatus } = useMutation({
    mutationFn: (vars: { publicId: string; role: WorkplaceRole }) =>
      apiFetch<iWorkplaceMember>(`${API_WORKPLACE_MEMBER_URLS.LIST}/${vars.publicId}/`, {
        method: 'PATCH',
        body: { role: vars.role },
      }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKey.value }),
    onSuccess: () => toast.add({ title: 'Papel atualizado', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao atualizar papel', color: 'error' }),
  })

  const { mutateAsync: removeMember, status: removeStatus } = useMutation({
    mutationFn: (publicId: string) =>
      apiFetch(`${API_WORKPLACE_MEMBER_URLS.LIST}/${publicId}/`, { method: 'DELETE' }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKey.value }),
    onSuccess: () => toast.add({ title: 'Membro removido', color: 'success' }),
    onError: () => toast.add({ title: 'Erro ao remover membro', color: 'error' }),
  })

  return {
    data,
    members,
    myMember,
    myRole,
    isAdmin,
    isLoading,
    refresh,
    addMember,
    addStatus,
    updateMemberRole,
    updateStatus,
    removeMember,
    removeStatus,
  }
}
