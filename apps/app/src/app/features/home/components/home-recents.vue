<script setup lang="ts">
import { useDocument } from '@/app/features/document/composables/data/document'
import { useTask } from '@/app/features/task/composables/task'
import { useTaskType } from '@/app/features/task/composables/taskType'
import { getTaskTypeMeta } from '@/app/features/task/utils'
import { getTagColor } from '@/app/shared/utils/tagColor'
import { formatTimeAgoIntl } from '@vueuse/core'

interface RecentItem {
  id: string
  icon: string
  color?: string
  title: string
  updatedAt: string
  to: string
}

const router = useRouter()
const { tasks } = useTask()
const { documents } = useDocument()
const { types } = useTaskType()

const recents = computed<RecentItem[]>(() => {
  const taskItems: RecentItem[] = tasks.value.map((t) => {
    const typeMeta = getTaskTypeMeta(types.value, t.type)

    return {
      id: `task-${t.public_id}`,
      icon: typeMeta?.icon || 'i-lucide-kanban',
      color: typeMeta?.color,
      title: t.title,
      updatedAt: t.updated_at,
      to: `/dashboard/tasks/${t.public_id}`,
    }
  })

  const documentItems: RecentItem[] = documents.value.map((d) => ({
    id: `document-${d.id}`,
    icon: 'i-lucide-file-edit',
    title: d.title || 'Sem título',
    updatedAt: d.updated_at,
    to: `/dashboard/documents?doc=${d.id}`,
  }))

  return [...taskItems, ...documentItems]
    .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
    .slice(0, 8)
})

function timeAgo(date: string) {
  return formatTimeAgoIntl(new Date(date), { locale: 'pt-BR' })
}

function tileStyle(item: RecentItem) {
  if (item.color) return { backgroundColor: `${item.color}1f`, color: item.color }

  const tag = getTagColor(item.id)
  return { backgroundColor: tag.bg, color: tag.fg }
}

function open(item: RecentItem) {
  router.push(item.to)
}
</script>

<template>
  <UCard variant="subtle">
    <template #header>
      <span class="text-sm font-medium">Recentes</span>
    </template>

    <UEmpty
      v-if="recents.length === 0"
      title="Nada por aqui ainda"
      icon="i-lucide-clock"
      variant="ghost"
      size="sm"
    />

    <div v-else class="flex flex-col gap-0.5">
      <div
        v-for="item in recents"
        :key="item.id"
        class="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-elevated/60 cursor-pointer transition-colors"
        @click="open(item)"
      >
        <div
          class="flex items-center justify-center size-8 rounded-lg shrink-0"
          :style="tileStyle(item)"
        >
          <UIcon :name="item.icon" class="size-4" />
        </div>
        <span class="flex-1 text-sm truncate">{{ item.title }}</span>
        <span class="text-xs text-dimmed shrink-0">{{ timeAgo(item.updatedAt) }}</span>
      </div>
    </div>
  </UCard>
</template>
