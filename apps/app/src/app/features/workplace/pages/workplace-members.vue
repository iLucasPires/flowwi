<script setup lang="ts">
defineOptions({ name: 'WorkplaceMembersPage' })

const overlay = useOverlay()

const search = ref('')
const filterRole = ref<string | undefined>(undefined)
const viewTab = ref<'table' | 'cards'>('table')

const viewItems = [
  { value: 'table', icon: 'i-lucide-table-2' },
  { value: 'cards', icon: 'i-lucide-layout-grid' },
]

const activeFiltersCount = computed(() => {
  let count = 0
  if (filterRole.value) count++
  return count
})

function openAddMember() {
  const component = resolveComponent('CMemberAddDialog')

  if (typeof component === 'object') {
    const modal = overlay.create(component)

    modal.open()
  }
}

async function openFilters() {
  const component = resolveComponent('CMemberFilterSlideover')

  if (typeof component === 'object') {
    const slideover = overlay.create(component, {
      props: {
        role: filterRole.value,
      },
    })

    const raw = (await slideover.open()) as unknown
    if (!raw || typeof raw !== 'object') return
    const result = raw as { role?: string }

    filterRole.value = result.role
  }
}
</script>

<template>
  <CDashboardContent title="Membros" description="Gerencie quem tem acesso a este workspace">
    <template #actions>
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Buscar por nome, e-mail ou papel..."
        variant="subtle"
        size="sm"
      />
      <UTabs
        v-model="viewTab"
        :items="viewItems"
        size="sm"
        :content="false"
        :ui="{
          indicator: 'bg-neutral-400',
        }"
      />
      <UButton
        label="Filtros"
        icon="i-lucide-filter"
        color="neutral"
        variant="subtle"
        size="sm"
        @click="openFilters"
      >
        <template v-if="activeFiltersCount > 0" #trailing>
          <UBadge :label="activeFiltersCount" size="xs" variant="subtle" />
        </template>
      </UButton>
      <UButton label="Adicionar Membro" icon="i-lucide-plus" size="sm" @click="openAddMember" />
    </template>

    <CMemberViewTable
      v-if="viewTab === 'table'"
      v-model:search="search"
      v-model:role="filterRole"
    />

    <CMemberViewGrid v-else v-model:search="search" v-model:role="filterRole" />
  </CDashboardContent>
</template>
