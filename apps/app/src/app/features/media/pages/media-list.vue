<script setup lang="ts">
import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import { MEDIA_VERSION_TYPE_TEXT, MEDIA_VERSION_TYPE_VIDEO } from '@/app/features/media/types'
import type { iMedia } from '@/app/features/media/types'
import type { iPaginationNumber } from '@/app/shared/types/pagination'
import { useQuery, useQueryClient } from '@tanstack/vue-query'

defineOptions({ name: 'MediaFilesPage' })

const search = ref('')
const filterType = ref<number[]>([])
const groupBy = ref<'none' | 'day' | 'hour'>('none')
const sortOrder = ref<'recent' | 'oldest'>('recent')

const WEEKDAY = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb']
const MONTH = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

function dayLabel(d: Date) {
  return `${WEEKDAY[d.getDay()]}, ${d.getDate()} ${MONTH[d.getMonth()]}`
}

function hourLabel(d: Date) {
  const h = d.getHours()
  return `${String(h).padStart(2, '0')}h – ${String((h + 1) % 24).padStart(2, '0')}h`
}

const toast = useToast()
const overlay = useOverlay()
const router = useRouter()
const queryClient = useQueryClient()

const { data: media, isLoading } = useQuery({
  queryKey: ['medias'],
  queryFn: () => apiFetch<iPaginationNumber<iMedia>>(API_MEDIA_URLS.LIST).then((r) => r.results),
})

function refresh() {
  queryClient.invalidateQueries({ queryKey: ['medias'] })
}

const showInitialLoading = computed(() => isLoading.value && (media.value ?? []).length === 0)

const filteredMedias = computed(() => {
  let list = media.value ?? []
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter((a) => (a.notes || '').toLowerCase().includes(q))
  }
  if (filterType.value.length) {
    list = list.filter((a) => filterType.value.includes(a.type))
  }

  const direction = sortOrder.value === 'recent' ? -1 : 1
  return [...list].sort(
    (a, b) => direction * (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()),
  )
})

interface iMediaGroup {
  key: string
  label: string
  showHeader: boolean
  count: number | ''
  items: iMedia[]
}

const mediaGroups = computed<iMediaGroup[]>(() => {
  const list = filteredMedias.value

  if (groupBy.value === 'none') {
    return [{ key: 'all', label: '', showHeader: false, count: '', items: list }]
  }

  const map = new Map<string, iMedia[]>()

  for (const item of list) {
    const date = new Date(item.created_at)
    const key = groupBy.value === 'day' ? dayLabel(date) : hourLabel(date)
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(item)
  }

  const direction = sortOrder.value === 'recent' ? -1 : 1

  return [...map.entries()]
    .sort(
      ([, a], [, b]) =>
        direction *
        (new Date(a[0]?.created_at ?? 0).getTime() - new Date(b[0]?.created_at ?? 0).getTime()),
    )
    .map(([label, items]) => ({ key: label, label, showHeader: true, count: items.length, items }))
})

async function deleteMedia(media: iMedia) {
  try {
    await apiFetch(`${API_MEDIA_URLS.LIST}/${media.id}`, { method: 'DELETE' })
    toast.add({
      title: 'Media removida',
      color: 'success',
    })

    refresh()
  } catch {
    toast.add({
      title: 'Erro ao remover',
      color: 'error',
    })
  }
}

function downloadMedia(media: iMedia) {
  const latest = media.versions[0]
  const url = latest?.file
  if (!url) return

  const a = document.createElement('a')

  a.href = url
  a.download = ''
  a.click()
}

async function openUpload() {
  const component = resolveComponent('CMediaUploadDialog')
  if (typeof component === 'string') return

  const modal = overlay.create(component)
  const { result } = modal.open()
  const value = await result
  if (value?.uploaded) refresh()
}

async function openDetail(media: iMedia) {
  const latestType = media.versions[0]?.type
  if (latestType === MEDIA_VERSION_TYPE_VIDEO || latestType === MEDIA_VERSION_TYPE_TEXT) {
    router.push(`/dashboard/media/${media.id}`)
    return
  }

  const component = resolveComponent('CMediaDetailDialog')
  if (typeof component === 'string') return

  const modal = overlay.create(component, { props: { media } })
  const { result } = modal.open()

  const value = await result
  if (value?.changed) refresh()
}

async function openEdit(media: iMedia) {
  const component = resolveComponent('CMediaUpsertDialog')
  if (typeof component === 'string') return

  const modal = overlay.create(component, { props: { media } })

  const { result } = modal.open()
  const value = await result

  if (value?.changed) refresh()
}

function shareMedia(media: iMedia) {
  const url = `${window.location.origin}/public/media/${media.share_token}`

  navigator.clipboard.writeText(url)
  toast.add({ title: 'Link copiado!', color: 'success' })
}
</script>

<template>
  <CDashboardContent title="Media">
    <template #actions>
      <UInput
        v-model="search"
        placeholder="Buscar..."
        icon="i-lucide-search"
        variant="subtle"
        size="sm"
      />

      <CMediaFilterPopover
        v-model:type="filterType"
        v-model:group-by="groupBy"
        v-model:sort-order="sortOrder"
      />

      <UButton
        label="Upload media"
        icon="i-lucide-upload"
        color="primary"
        variant="solid"
        size="xs"
        @click="openUpload"
      />
    </template>

    <div
      v-if="showInitialLoading"
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
    >
      <USkeleton v-for="i in 8" :key="i" class="h-48 rounded-xl" />
    </div>

    <div v-else-if="filteredMedias.length" class="flex flex-col gap-5 overflow-y-auto">
      <div v-for="group in mediaGroups" :key="group.key" class="flex flex-col gap-3">
        <div v-if="group.showHeader" class="flex items-center gap-2">
          <span class="text-[12.5px] font-semibold text-highlighted">{{ group.label }}</span>
          <span class="text-[11px] text-dimmed">{{ group.count }}</span>
          <div class="flex-1 h-px bg-default" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <CMediaCard
            v-for="media in group.items"
            :key="media.id"
            :media="media"
            @click="openDetail(media)"
            @edit="openEdit(media)"
            @share="shareMedia(media)"
            @delete="deleteMedia(media)"
            @download="downloadMedia(media)"
          />
        </div>
      </div>
    </div>

    <UEmpty
      v-else
      variant="subtle"
      size="sm"
      title="Nenhuma media encontrada"
      description="Faça upload da primeira media para começar."
      icon="i-lucide-image"
      class="h-full"
    >
      <template #actions>
        <UButton
          label="Upload media"
          icon="i-lucide-upload"
          color="primary"
          variant="solid"
          size="sm"
          @click="openUpload"
        />
      </template>
    </UEmpty>
  </CDashboardContent>
</template>
