<script setup lang="ts">
import { useWorkplaceMember } from '@/app/features/workplace/composables/workplaceMember'
const open = defineModel<boolean>('open', { required: true })

const { addMember, addStatus } = useWorkplaceMember()
const inviteEmail = ref('')
const inviteRole = ref<'manager' | 'designer'>('designer')
const roleOptions = [
  { label: 'Gerente', value: 'manager' },
  { label: 'Designer', value: 'designer' },
]

async function invite() {
  if (!inviteEmail.value) return
  await addMember({ user: inviteEmail.value, role: inviteRole.value })
  inviteEmail.value = ''
  open.value = false
}
</script>

<template>
  <UModal v-model:open="open" title="Adicionar membro" :ui="{ header: 'border-none' }">
    <template #body>
      <div class="flex flex-col gap-4">
        <UInput
          v-model="inviteEmail"
          placeholder="Email do usuário"
          size="md"
          variant="subtle"
          icon="i-lucide-mail"
          class="w-full"
          autofocus
        />

        <USelect
          v-model="inviteRole"
          :items="roleOptions"
          placeholder="Papel do membro"
          size="md"
          variant="subtle"
          icon="i-lucide-shield-half"
          class="w-full"
        />
      </div>
    </template>
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton label="Cancelar" variant="ghost" color="neutral" size="md" @click="open = false" />
        <UButton
          label="Adicionar"
          icon="i-lucide-plus"
          color="primary"
          size="md"
          :disabled="!inviteEmail.trim()"
          :loading="addStatus === 'pending'"
          @click="invite"
        />
      </div>
    </template>
  </UModal>
</template>
