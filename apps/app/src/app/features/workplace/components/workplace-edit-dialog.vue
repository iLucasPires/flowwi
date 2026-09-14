<script setup lang="ts">
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
const props = defineProps<{
  workplaceId: number
}>()

const open = defineModel<boolean>('open', { required: true })

const { workplaces } = useWorkplace()

const workplace = computed(() => workplaces.value.find((w) => w.id === props.workplaceId) ?? null)
</script>

<template>
  <UModal
    v-model:open="open"
    :title="`Configurações Gerais: ${workplace?.name || 'Workspace'}`"
    :ui="{ content: 'sm:max-w-4xl' }"
  >
    <template #body>
      <div class="p-6">
        <CWorkplaceGeneralForm v-if="workplace" :workplace="workplace" />
      </div>

      <div class="flex justify-end gap-2 px-6 pb-6">
        <UButton label="Fechar" variant="ghost" color="neutral" @click="open = false" />
      </div>
    </template>
  </UModal>
</template>
