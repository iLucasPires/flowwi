<script setup lang="ts">
import { useWorkplaceMutations } from '@/app/features/workplace/composables/workplace'
defineOptions({ name: 'WorkplaceJoinPage' })

const toast = useToast()
const router = useRouter()
const { joinByKey, joinStatus } = useWorkplaceMutations()

const inviteKey = ref([])
const isComplete = computed(() => inviteKey.value.length === 8)
const pendingApproval = ref(false)

async function handleSubmit() {
  if (!isComplete.value) return

  try {
    const result = await joinByKey(inviteKey.value.join(''))
    if (result.status === 'pending') {
      pendingApproval.value = true
      return
    }
    toast.add({ title: 'Vinculado ao workspace!', color: 'success' })
    router.push('/dashboard')
  } catch {
    toast.add({ title: 'Chave inválida ou já utilizada', color: 'error' })
  }
}
</script>

<template>
  <UPageCard
    v-if="pendingApproval"
    class="w-md"
    title="Pedido enviado"
    description="Um administrador do workspace precisa aprovar sua entrada antes que você tenha acesso."
  >
    <div class="flex flex-col w-full">
      <UButton
        to="/account/setup/workplace/select"
        label="Ver outros workspaces"
        variant="link"
        color="neutral"
        size="xs"
        block
      />
    </div>
  </UPageCard>

  <UPageCard
    v-else
    class="w-md"
    title="Vincular ao workspace"
    description="Use um código de acesso do workspace."
  >
    <UForm class="flex flex-col gap-4" @submit.prevent="handleSubmit">
      <UFormField label="Chave de convite" size="xs">
        <UPinInput
          v-model="inviteKey"
          size="xs"
          variant="subtle"
          autofocus
          :length="8"
          :ui="{
            root: 'justify-between w-full',
            base: 'w-full',
          }"
        />
      </UFormField>

      <UButton
        size="xs"
        type="submit"
        label="Entrar no workspace"
        icon="i-lucide-arrow-right"
        color="primary"
        block
        :loading="joinStatus === 'pending'"
        :disabled="!isComplete"
      />
    </UForm>

    <div class="flex flex-col w-full">
      <UButton
        to="/account/setup/workplace/select"
        label="Selecionar workspace existente"
        variant="link"
        color="neutral"
        size="xs"
        block
      />
      <UButton
        to="/account/setup/workplace/create"
        label="Criar novo workspace"
        variant="link"
        color="neutral"
        size="xs"
        block
      />
    </div>
  </UPageCard>
</template>
