<script setup lang="ts">
import { useWorkplaceMutations } from '@/app/features/workplace/composables/workplace'
defineOptions({ name: 'WorkplaceCreatePage' })

const toast = useToast()
const router = useRouter()
const { createWorkplace, createStatus } = useWorkplaceMutations()

const name = ref('')

async function handleSubmit() {
  if (!name.value) return

  try {
    await createWorkplace(name.value)
    toast.add({ title: 'Workspace criado!', color: 'success' })
    router.push('/dashboard')
  } catch {
    toast.add({ title: 'Erro ao criar workspace', color: 'error' })
  }
}
</script>

<template>
  <UPageCard
    class="w-md"
    title="Criar workspace"
    description="Defina o nome do workspace que você deseja criar."
  >
    <UForm class="flex flex-col gap-4" @submit.prevent="handleSubmit">
      <UInput
        v-model="name"
        size="xs"
        variant="subtle"
        icon="i-lucide-box"
        class="w-full"
        placeholder="Nome do workspace"
        autofocus
      />
      <UButton
        size="xs"
        type="submit"
        label="Criar workspace"
        icon="i-lucide-plus"
        color="primary"
        block
        :loading="createStatus === 'pending'"
        :disabled="!name.trim()"
      />
    </UForm>

    <div class="flex flex-col w-full">
      <UButton
        size="xs"
        to="/account/setup/workplace/join"
        label="Vincular com chave de convite"
        variant="link"
        color="neutral"
        block
      />
      <UButton
        size="xs"
        to="/account/setup/workplace/select"
        label="Selecionar workspace existente"
        variant="link"
        color="neutral"
        block
      />
    </div>
  </UPageCard>
</template>
