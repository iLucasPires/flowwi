<script setup lang="ts">
import { useWorkplace, useWorkplaceMutations } from '@/app/features/workplace/composables/workplace'
defineOptions({ name: 'WorkplaceSelectPage' })

const router = useRouter()
const { workplaces, setCurrent } = useWorkplace()
const { workplacesStatus } = useWorkplaceMutations()

const workplaceItems = computed(() =>
  workplaces.value.map((item) => ({
    label: item.name,
    value: item.id,
  })),
)

const selectedWorkplace = ref<number | undefined>(undefined)

function handleContinue() {
  if (selectedWorkplace.value) {
    const workplaceItem = workplaces.value.find((item) => item.id === selectedWorkplace.value)

    if (workplaceItem) {
      setCurrent(workplaceItem)
      router.push('/dashboard')
    }
  }
}
</script>

<template>
  <UPageCard
    class="w-md"
    title="Selecionar workspace"
    description="Selecione um workspace para continuar."
  >
    <template #default>
      <UEmpty
        v-if="workplacesStatus === 'success' && !workplaces.length"
        title="Nenhum workspace ainda"
        description="Crie seu primeiro workspace para começar."
        icon="i-lucide-layout-grid"
        variant="subtle"
        class="h-64"
        size="sm"
      />
      <div v-else class="space-y-2 max-h-72 overflow-y-auto p-1">
        <URadioGroup
          v-model="selectedWorkplace"
          :items="workplaceItems"
          orientation="vertical"
          variant="card"
          color="primary"
        />
      </div>
      <UButton
        size="xs"
        label="Continuar"
        block
        :disabled="!selectedWorkplace"
        @click="handleContinue"
      />
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
          to="/account/setup/workplace/create"
          label="Criar novo workspace"
          variant="link"
          color="neutral"
          block
        />
      </div>
    </template>
  </UPageCard>
</template>
