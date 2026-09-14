<script setup lang="ts">
defineOptions({ name: 'WorkplaceWebhooksPage' })

const props = defineProps<{
  workplaceId: number
}>()

const overlay = useOverlay()
const search = ref('')
const filterIsActive = ref<boolean | undefined>(undefined)

const activeFiltersCount = computed(() => {
  let count = 0
  if (filterIsActive.value !== undefined) count++
  return count
})

function openWebhookModal() {
  const component = resolveComponent('CWorkplaceWebhookAddDialog')
  if (typeof component === 'object') {
    const modal = overlay.create(component, {
      props: { workplaceId: props.workplaceId },
    })
    modal.open()
  }
}

async function openFilters() {
  const component = resolveComponent('CWorkplaceWebhookFilterSlideover')

  if (typeof component === 'object') {
    const slideover = overlay.create(component, {
      props: {
        isActive: filterIsActive.value,
      },
    })

    const raw = (await slideover.open()) as unknown
    if (!raw || typeof raw !== 'object') return
    const result = raw as { isActive?: boolean }

    filterIsActive.value = result.isActive
  }
}
</script>

<template>
  <CDashboardContent
    title="Webhooks"
    description="Integre o Flowwi com outros serviços via eventos HTTP"
  >
    <template #actions>
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Buscar webhook..."
        variant="subtle"
        size="sm"
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
      <UButton label="Adicionar Webhook" icon="i-lucide-plus" size="sm" @click="openWebhookModal" />
    </template>

    <CWorkplaceWebhookTable
      v-model:search="search"
      v-model:is-active="filterIsActive"
      :workplace-id="workplaceId"
    />
  </CDashboardContent>
</template>
