<script setup lang="ts">
import { API_FORM_URLS, apiFetch } from '@/app/core/clients/api'
import type { tFormOut } from '@/app/features/form/schemas'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import type { DropdownMenuItem } from '@nuxt/ui/runtime/components/DropdownMenu.d.vue.js'

const toast = useToast()
const router = useRouter()
const queryClient = useQueryClient()
const overlay = useOverlay()
const search = ref('')
const filterPublished = ref<boolean | undefined>(undefined)
const viewMode = ref<'grid' | 'list' | 'table'>('grid')

const viewOptions = [
  { value: 'grid' as const, icon: 'i-lucide-layout-grid' },
  { value: 'list' as const, icon: 'i-lucide-list' },
  { value: 'table' as const, icon: 'i-lucide-table' },
]

function openEditor(formId: number | string) {
  router.push(`/dashboard/forms/${formId}`)
}

async function openCreate() {
  const component = resolveComponent('CFormUpsertDialog')
  if (typeof component !== 'object') return

  const result = (await overlay.create(component).open()) as { created?: true; id?: number } | undefined
  refresh()

  if (result?.id) {
    openEditor(result.id)
  }
}

const { data: forms, isLoading } = useQuery({
  queryKey: ['forms'],
  queryFn: () => apiFetch<iPaginationNumber<tFormOut>>(API_FORM_URLS.LIST).then((r) => r.results),
})

function refresh() {
  queryClient.invalidateQueries({ queryKey: ['forms'] })
}

const showInitialLoading = computed(() => isLoading.value && (forms.value ?? []).length === 0)

const filteredForms = computed(() => {
  let list = forms.value ?? []
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(
      (f) => f.title.toLowerCase().includes(q) || (f.description || '').toLowerCase().includes(q),
    )
  }
  if (filterPublished.value !== undefined)
    list = list.filter((f) => f.is_published === filterPublished.value)
  return list
})

async function deleteForm(form: tFormOut) {
  try {
    await apiFetch(`${API_FORM_URLS.LIST}/${form.id}`, { method: 'DELETE' })
    toast.add({ title: 'Formulário removido', color: 'success' })
    refresh()
  } catch {
    toast.add({ title: 'Erro ao remover', color: 'error' })
  }
}

async function openEdit(form: tFormOut) {
  const component = resolveComponent('CFormUpsertDialog')

  if (typeof component !== 'object') return

  const modal = overlay.create(component, {
    props: { form },
  })

  modal.open()
}

function getActions(form: tFormOut): DropdownMenuItem[][] {
  return [
    [
      { label: 'Editar', icon: 'i-lucide-pencil', onSelect: () => openEdit(form) },
      { label: 'Editor', icon: 'i-lucide-layers', onSelect: () => openEditor(form.id) },
    ],
    [
      {
        label: 'Respostas',
        icon: 'i-lucide-bar-chart-3',
        onSelect: () =>
          router.push({ path: '/dashboard/form/answers', query: { formId: String(form.id) } }),
      },
      {
        label: 'Copiar link',
        icon: 'i-lucide-link',
        onSelect: () => copyPublicLink(form.public_id),
      },
    ],
    [
      {
        label: 'Apagar',
        icon: 'i-lucide-trash-2',
        color: 'error' as const,
        onSelect: () => deleteForm(form),
      },
    ],
  ]
}

function copyPublicLink(publicId: string) {
  navigator.clipboard.writeText(`${window.location.origin}/public/form/${publicId}`)
  toast.add({ title: 'Link copiado!', color: 'success' })
}

function handleOpen(form: tFormOut) {
  openEditor(form.id)
}

function handleAnswers(form: tFormOut) {
  router.push({ path: '/dashboard/form/answers', query: { formId: String(form.id) } })
}

function handleCopyLink(form: tFormOut) {
  copyPublicLink(form.public_id)
}
</script>

<template>
  <CDashboardContent title="Templates" description="Modelos de formulário">
    <template #actions>
      <UInput
        v-model="search"
        placeholder="Buscar..."
        icon="i-lucide-search"
        variant="subtle"
        size="xs"
      />
      <UFieldGroup size="xs">
        <UButton
          v-for="opt in viewOptions"
          :key="opt.value"
          :icon="opt.icon"
          :variant="viewMode === opt.value ? 'solid' : 'ghost'"
          :color="viewMode === opt.value ? 'primary' : 'neutral'"
          square
          @click="viewMode = opt.value"
        />
      </UFieldGroup>
      <CFormFilterPopover v-model:published="filterPublished" />
      <UButton
        label="Novo"
        icon="i-lucide-plus"
        color="primary"
        variant="solid"
        size="xs"
        @click="openCreate"
      />
    </template>

    <CFormSkeleton v-if="showInitialLoading" />

    <template v-else-if="filteredForms.length">
      <CFormViewGrid
        v-if="viewMode === 'grid'"
        :forms="filteredForms"
        :actions="getActions"
        @open="handleOpen"
        @answers="handleAnswers"
        @copy-link="handleCopyLink"
      />
      <CFormViewList
        v-else-if="viewMode === 'list'"
        :forms="filteredForms"
        :actions="getActions"
        @open="handleOpen"
        @answers="handleAnswers"
        @copy-link="handleCopyLink"
      />
      <CFormViewTable
        v-else
        :forms="filteredForms"
        :actions="getActions"
        @open="handleOpen"
        @answers="handleAnswers"
        @copy-link="handleCopyLink"
      />
    </template>

    <CFormEmpty v-else @create="openCreate" />
  </CDashboardContent>
</template>
