<script setup lang="ts">
import { useWorkplaceMember } from '@/app/features/workplace/composables/workplaceMember'

const { isAdmin } = useWorkplaceMember()
const search = ref('')
const role = ref<string | undefined>(undefined)
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold">Membros</h2>
        <p class="text-sm text-dimmed mt-1">Gerencie os membros do seu workspace.</p>
      </div>

      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Buscar..."
        variant="subtle"
        size="sm"
      />
    </div>

    <CMemberPendingList v-if="isAdmin" />

    <CMemberViewTable v-model:search="search" v-model:role="role" />
  </div>
</template>
