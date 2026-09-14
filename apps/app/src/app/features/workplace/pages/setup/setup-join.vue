<script setup lang="ts">
import { useWorkplaceMutations } from '@/app/features/workplace/composables/workplace'
defineOptions({ name: 'WorkplaceJoinPage' })

const toast = useToast()
const router = useRouter()
const { joinByKey, joinStatus } = useWorkplaceMutations()

const inviteKey = ref([])
const isComplete = computed(() => inviteKey.value.length === 8)

async function handleSubmit() {
  if (!isComplete.value) return

  try {
    await joinByKey(inviteKey.value.join(''))
    toast.add({ title: 'Vinculado ao workspace!', color: 'success' })
    router.push('/dashboard')
  } catch {
    toast.add({ title: 'Chave inválida ou já utilizada', color: 'error' })
  }
}
</script>

<template>
  <UPageCard
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
