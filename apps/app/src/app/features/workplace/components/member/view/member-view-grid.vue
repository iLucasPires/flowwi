<script setup lang="ts">
import { useWorkplaceMember } from '@/app/features/workplace/composables/workplaceMember'
import { cWorkplaceRoleBadgeColor } from '@/app/features/workplace/constants'
import type { WorkplaceRole, iWorkplaceMember } from '@/app/features/workplace/types'
import type { DropdownMenuItem } from '@nuxt/ui'

const search = defineModel<string>('search')
const role = defineModel<string | undefined>('role')

const toast = useToast()
const { members, isLoading, removeMember } = useWorkplaceMember()

const filteredMembers = computed(() => {
  const list = members.value ?? []
  const q = (search.value ?? '').trim().toLowerCase()

  return list.filter(
    (m) =>
      (!q ||
        m.profile?.full_name?.toLowerCase().includes(q) ||
        m.profile?.email?.toLowerCase().includes(q) ||
        m.role?.toLowerCase().includes(q)) &&
      (!role.value || m.role === role.value),
  )
})

function roleBadgeColor(role: string) {
  return cWorkplaceRoleBadgeColor[role as WorkplaceRole] ?? 'neutral'
}

function getMemberItems(member: iWorkplaceMember): DropdownMenuItem[] {
  return [
    { type: 'label' as const, label: 'Ações' },
    {
      label: 'Copiar ID do membro',
      icon: 'i-lucide-copy',
      onSelect() {
        navigator.clipboard.writeText(member.public_id)
        toast.add({
          title: 'Copiado!',
          description: 'ID do membro copiado para a área de transferência.',
        })
      },
    },
    ...(member.role !== 'owner'
      ? ([
          { type: 'separator' as const },
          {
            label: 'Remover membro',
            icon: 'i-lucide-trash',
            color: 'error' as const,
            onSelect() {
              removeMember(member.public_id)
            },
          },
        ] satisfies DropdownMenuItem[])
      : []),
  ] satisfies DropdownMenuItem[]
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <UEmpty
      v-if="!isLoading && filteredMembers.length === 0"
      title="Nenhum membro encontrado"
      description="Tente ajustar a busca ou os filtros."
      icon="i-lucide-users"
      variant="subtle"
      class="h-64"
      size="sm"
    />

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="m in filteredMembers"
        :key="m.public_id"
        class="rounded-lg overflow-hidden bg-elevated/40 p-4 transition-colors hover:bg-elevated/70"
      >
        <div class="flex items-start gap-3">
          <UAvatar
            :src="m.profile?.photo ?? undefined"
            :alt="m.profile?.full_name ?? m.profile?.email ?? 'Avatar'"
            size="md"
          />

          <div class="min-w-0 flex-1">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="font-medium text-sm text-default truncate">
                  {{ m.profile?.full_name ?? '—' }}
                </p>
                <p class="text-xs text-dimmed truncate">
                  {{ m.profile?.email ?? '' }}
                </p>
              </div>

              <UDropdownMenu :content="{ align: 'end' }" :items="getMemberItems(m)">
                <UButton icon="i-lucide-more-horizontal" color="neutral" variant="ghost" />
              </UDropdownMenu>
            </div>

            <div class="mt-3 flex flex-wrap items-center gap-2">
              <UBadge class="capitalize" variant="subtle" size="xs" :color="roleBadgeColor(m.role)">
                {{ m.role }}
              </UBadge>

              <span class="text-xs text-dimmed tabular-nums">
                {{
                  m.created_at
                    ? new Date(m.created_at).toLocaleDateString('pt-BR', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })
                    : '—'
                }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
