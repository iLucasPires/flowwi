<script setup lang="ts">
import { useTaskStatus } from '@/app/features/task/composables/taskStatus'
import { getTaskStatusMeta } from '@/app/features/task/utils'
import { useSearch } from '@/app/shared/composables/search/search'

const router = useRouter()
const open = ref(false)
const query = ref('')
const { results, searchStatus, search } = useSearch()
const { statuses } = useTaskStatus()
const loading = computed(() => searchStatus.value === 'pending')

const debouncedSearch = useDebounceFn((q: string) => search(q), 300)
watch(query, (val) => debouncedSearch(val))

const hasResults = computed(
  () =>
    results.value.tasks.length > 0 ||
    results.value.forms.length > 0 ||
    results.value.members.length > 0,
)

function taskStatusLabel(statusId: number | null) {
  return getTaskStatusMeta(statuses.value, statusId)?.name
}

function select(to: string) {
  open.value = false
  query.value = ''
  router.push(to)
}

defineShortcuts({
  meta_k: () => {
    open.value = true
  },
})
</script>

<template>
  <UModal :ui="{ content: 'sm:max-w-xl' }">
    <template #content>
      <div class="flex flex-col">
        <div class="flex items-center gap-3 px-4 py-3">
          <UIcon name="i-lucide-search" class="size-5 text-dimmed shrink-0" />
          <UInput
            v-model="query"
            placeholder="Buscar tasks, formulários, membros..."
            variant="ghost"
            autofocus
            class="flex-1"
          />
          <UIcon v-if="loading" name="i-lucide-loader-2" class="size-4 text-dimmed animate-spin" />
        </div>

        <div class="max-h-80 overflow-y-auto p-2">
          <template v-if="!query">
            <UEmpty
              title="Digite para buscar..."
              icon="i-lucide-search"
              variant="naked"
              size="xs"
            />
          </template>

          <template v-else-if="!loading && !hasResults">
            <UEmpty
              title="Nenhum resultado encontrado"
              icon="i-lucide-search-x"
              variant="naked"
              size="xs"
            />
          </template>

          <template v-else>
            <div v-if="results.tasks.length">
              <p class="px-3 py-1.5 text-xs font-medium text-dimmed uppercase">Tasks</p>
              <button
                v-for="task in results.tasks"
                :key="task.public_id"
                class="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-accented/60 transition-colors text-left"
                @click="select(`/dashboard/tasks/${task.public_id}`)"
              >
                <UIcon name="i-lucide-check-square" class="size-4 text-dimmed" />
                <span class="text-sm text-default truncate">{{ task.title }}</span>
                <UBadge
                  :label="taskStatusLabel(task.status)"
                  size="xs"
                  variant="subtle"
                  class="ml-auto"
                />
              </button>
            </div>

            <div v-if="results.forms.length">
              <p class="px-3 py-1.5 text-xs font-medium text-dimmed uppercase">Formulários</p>
              <button
                v-for="form in results.forms"
                :key="form.id"
                class="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-accented/60 transition-colors text-left"
                @click="select(`/dashboard/form/templates/${form.id}`)"
              >
                <UIcon name="i-lucide-file-text" class="size-4 text-dimmed" />
                <span class="text-sm text-default truncate">{{ form.title }}</span>
              </button>
            </div>

            <div v-if="results.members.length">
              <p class="px-3 py-1.5 text-xs font-medium text-dimmed uppercase">Membros</p>
              <div
                v-for="member in results.members"
                :key="member.id"
                class="flex items-center gap-3 px-3 py-2 rounded-md"
              >
                <UIcon name="i-lucide-user" class="size-4 text-dimmed" />
                <span class="text-sm text-default">{{ member.role }}</span>
                <UBadge :label="member.role" size="xs" variant="subtle" class="ml-auto" />
              </div>
            </div>
          </template>
        </div>
      </div>
    </template>
  </UModal>
</template>
