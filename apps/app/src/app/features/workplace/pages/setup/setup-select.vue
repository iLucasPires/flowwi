<script setup lang="ts">
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
defineOptions({ name: 'WorkplaceSelectPage' })

const { workplaces, setCurrent, refreshWorkplaces } = useWorkplace()

const workplaceItems = computed(() =>
  workplaces.value.map((item) => ({
    label: item.name,
    value: item.id,
  })),
)

const selectedWorkplace = ref<number | undefined>(undefined)
const entering = ref(false)
const loaded = ref(false)

onMounted(async () => {
  await refreshWorkplaces()
  loaded.value = true
})

async function handleContinue() {
  if (!selectedWorkplace.value) return

  const workplaceItem = workplaces.value.find((item) => item.id === selectedWorkplace.value)
  if (!workplaceItem) return

  entering.value = true
  await setCurrent(workplaceItem)
  // Full reload, not a router push — guarantees every composable/query starts
  // fresh against the newly-selected workplace instead of possibly racing the
  // "select" request that sets the workplace cookie.
  window.location.href = '/dashboard'
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
        v-if="loaded && !workplaces.length"
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
        :loading="entering"
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
