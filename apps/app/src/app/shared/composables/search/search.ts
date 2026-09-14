import { API_FORM_URLS, API_TASK_URLS, API_WORKPLACE_MEMBER_URLS, apiFetch } from '@/app/core/clients/api'
import type { iTask } from '@/app/features/task/types'
import type { iWorkplaceMember } from '@/app/features/workplace/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { ref, computed } from 'vue'
import { refDebounced } from '@vueuse/core'
import { useQuery } from '@tanstack/vue-query'

interface iFormSearchResult {
  id: number
  title: string
  public_id: string
}

export interface iSearchResults {
  tasks: iTask[]
  forms: iFormSearchResult[]
  members: iWorkplaceMember[]
}

const EMPTY_RESULTS: iSearchResults = { tasks: [], forms: [], members: [] }

export const searchKeys = {
  root: () => ['search'] as const,
  query: (query: string) => ['search', query] as const,
}

export const useSearch = () => {
  const queryText = ref('')
  const debouncedQuery = refDebounced(queryText, 300)

  const { data, status: searchStatus } = useQuery({
    queryKey: computed(() => searchKeys.query(debouncedQuery.value)),
    queryFn: async () => {
      const q = debouncedQuery.value.trim()
      if (!q) return EMPTY_RESULTS

      const [tasks, forms, members] = await Promise.all([
        apiFetch<iPaginationNumber<iTask>>(API_TASK_URLS.LIST, { params: { search: q } }),
        apiFetch<iPaginationNumber<iFormSearchResult>>(API_FORM_URLS.LIST, {
          params: { search: q },
        }),
        apiFetch<iPaginationNumber<iWorkplaceMember>>(API_WORKPLACE_MEMBER_URLS.LIST, {
          params: { search: q },
        }),
      ])

      return { tasks: tasks.results, forms: forms.results, members: members.results }
    },
  })

  const results = computed(() =>
    debouncedQuery.value.trim() && data.value ? data.value : EMPTY_RESULTS,
  )

  function search(q: string) {
    queryText.value = q
  }

  function clear() {
    queryText.value = ''
  }

  return { queryText, results, search, searchStatus, clear }
}
