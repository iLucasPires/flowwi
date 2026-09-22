<script setup lang="ts">
import { useWorkplaceMutations } from '@/app/features/workplace/composables/workplace'
import type { iWorkplace } from '@/app/features/workplace/types'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  workplace: iWorkplace
}>()

const { deleteWorkplace, deleteStatus } = useWorkplaceMutations()

const confirmName = ref('')

watch(open, (isOpen) => {
  if (isOpen) confirmName.value = ''
})

const isConfirmed = computed(() => confirmName.value.trim() === props.workplace.name)

async function confirmDelete() {
  if (!isConfirmed.value) return
  await deleteWorkplace(props.workplace.id)
  // Full reload, not a router push — clears every bit of cached workplace
  // state (queries, cookies-derived context) instead of trusting SPA state
  // to catch up after the workspace it was scoped to no longer exists.
  window.location.href = '/account/setup/workplace/select'
}

defineOptions({ name: 'WorkplaceDeleteDialog' })
</script>

<template>
  <UModal v-model:open="open" title="Excluir workspace?" :ui="{ content: 'sm:max-w-md' }">
    <template #body>
      <div class="flex flex-col gap-3">
        <p class="text-sm text-dimmed">
          Isso remove o acesso ao workspace
          <strong class="text-default">{{ workplace.name }}</strong>
          para todos os membros e não pode ser desfeito pelo app. Para confirmar, digite o nome do
          workspace abaixo.
        </p>
        <UInput v-model="confirmName" :placeholder="workplace.name" variant="subtle" size="sm" />
      </div>
    </template>
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton label="Cancelar" variant="ghost" color="neutral" size="sm" @click="open = false" />
        <UButton
          label="Excluir workspace"
          color="error"
          size="sm"
          :disabled="!isConfirmed"
          :loading="deleteStatus === 'pending'"
          @click="confirmDelete"
        />
      </div>
    </template>
  </UModal>
</template>
