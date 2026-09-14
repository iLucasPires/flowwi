import { computed, ref, unref, watch, type MaybeRef } from 'vue'
import { refDebounced } from '@vueuse/core'
import { keepPreviousData, useQuery } from '@tanstack/vue-query'
import type { iUnsplashPhoto, iUnsplashPhotoPage } from '@/app/shared/types/unsplash'
import { apiFetch, API_UNSPLASH_URLS } from '@/app/core/clients/api'

const PHOTOS_PER_PAGE = 24
const SEARCH_DEBOUNCE_MS = 450

/**
 * Photo search backed by the API proxy — the Unsplash key stays on the server and
 * every listing is cached there, so typing in the picker does not burn the quota.
 *
 * @param enabled keeps the query idle until the Unsplash tab is actually open.
 */
export const useUnsplash = (enabled: MaybeRef<boolean> = true) => {
  const searchTerm = ref('')
  const debouncedTerm = refDebounced(searchTerm, SEARCH_DEBOUNCE_MS)
  const page = ref(1)

  watch(debouncedTerm, () => {
    page.value = 1
  })

  const { data, isLoading, isFetching, isError } = useQuery({
    queryKey: ['unsplash', 'photos', debouncedTerm, page],
    queryFn: () =>
      apiFetch<iUnsplashPhotoPage>(API_UNSPLASH_URLS.PHOTOS, {
        query: {
          query: debouncedTerm.value.trim(),
          page: page.value,
          per_page: PHOTOS_PER_PAGE,
        },
      }),
    enabled: computed(() => unref(enabled)),
    placeholderData: keepPreviousData,
    staleTime: 1000 * 60 * 30,
  })

  const photos = computed<iUnsplashPhoto[]>(() => data.value?.results ?? [])

  const hasNextPage = computed(() => {
    const totalPages = data.value?.total_pages

    if (totalPages != null) {
      return page.value < totalPages
    }

    // The popular feed has no page count — keep paging while it returns a full page.
    return photos.value.length === PHOTOS_PER_PAGE
  })

  const hasPreviousPage = computed(() => page.value > 1)

  function nextPage() {
    if (hasNextPage.value) {
      page.value += 1
    }
  }

  function previousPage() {
    if (hasPreviousPage.value) {
      page.value -= 1
    }
  }

  /**
   * Unsplash requires a download to be registered whenever a user actually picks a
   * photo. Fire-and-forget: failing to report it must never block the selection.
   */
  function trackDownload(photo: iUnsplashPhoto) {
    if (!photo.download_location) return

    apiFetch(API_UNSPLASH_URLS.DOWNLOAD, {
      method: 'POST',
      body: { download_location: photo.download_location },
    }).catch(() => {})
  }

  return {
    searchTerm,
    photos,
    page,
    isLoading,
    isFetching,
    isError,
    hasNextPage,
    hasPreviousPage,
    nextPage,
    previousPage,
    trackDownload,
  }
}
