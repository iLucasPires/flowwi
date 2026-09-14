<script setup lang="ts">
import type { iWorkplace } from '@/app/features/workplace/types'
import { useWorkplace } from '@/app/features/workplace'

defineOptions({ name: 'WorkplaceListPage' })

const router = useRouter()
const { workplaces, setCurrent, refreshWorkplaces } = useWorkplace()

const search = ref('')

onMounted(() => {
  refreshWorkplaces()
})

const filteredWorkplaces = computed(() => {
  if (!search.value) return workplaces.value
  const q = search.value.toLowerCase()
  return workplaces.value.filter((w) => w.name.toLowerCase().includes(q))
})

async function enterWorkplace(w: iWorkplace) {
  await setCurrent(w)
  router.push('/dashboard')
}
</script>

<template>
  <div class="size-full flex flex-col overflow-hidden">
    <div class="flex items-center justify-between px-6 py-4">
      <UPageFeature
        title="Workspaces"
        description="Seus workspaces e ambientes de colaboração"
        color="neutral"
        size="sm"
      />

      <div class="flex items-center gap-2">
        <UInput
          v-model="search"
          placeholder="Buscar..."
          icon="i-lucide-search"
          variant="subtle"
          size="sm"
        />
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-6 py-4">
      <div
        v-if="filteredWorkplaces.length"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
      >
        <CWorkplaceCard
          v-for="w in filteredWorkplaces"
          :key="w.id"
          :workplace="w"
          @enter="enterWorkplace(w)"
        />
      </div>

      <UEmpty
        v-else
        title="Nenhum workspace"
        description="Você ainda não faz parte de nenhum workspace."
        icon="i-lucide-layout-grid"
        variant="subtle"
        size="sm"
        class="h-full"
      />
    </div>
  </div>
</template>
