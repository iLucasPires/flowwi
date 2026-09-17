<script setup lang="ts">
import { useQuicklink } from '@/app/features/home/composables/quicklink'
import { getTagColor } from '@/app/shared/utils/tagColor'
import { formatTimeAgoIntl } from '@vueuse/core'

const { quicklinks, deleteQuicklink } = useQuicklink()
const overlay = useOverlay()

function openCreate() {
  const component = resolveComponent('CHomeQuicklinkCreateDialog')
  if (typeof component === 'object') overlay.create(component).open()
}

function timeAgo(date: string) {
  return formatTimeAgoIntl(new Date(date), { locale: 'pt-BR' })
}
</script>

<template>
  <UCard variant="subtle" :ui="{ header: 'flex items-center justify-between' }">
    <template #header>
      <span class="text-sm font-medium">Quicklinks</span>
      <UButton
        label="Adicionar link"
        icon="i-lucide-plus"
        variant="link"
        color="primary"
        size="xs"
        @click="openCreate"
      />
    </template>

    <UEmpty
      v-if="quicklinks.length === 0"
      title="Nenhum link ainda"
      description="Adicione atalhos para páginas que você acessa com frequência."
      icon="i-lucide-link"
      variant="ghost"
      size="sm"
    />

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div
        v-for="link in quicklinks"
        :key="link.id"
        class="group relative rounded-lg bg-elevated/50 hover:bg-elevated hover:-translate-y-0.5 hover:shadow-sm transition-all duration-150"
      >
        <a
          :href="link.url"
          target="_blank"
          rel="noopener noreferrer"
          class="flex items-center gap-3 p-3"
        >
          <div
            class="flex items-center justify-center size-9 rounded-lg shrink-0"
            :style="{ backgroundColor: getTagColor(String(link.id)).bg, color: getTagColor(String(link.id)).fg }"
          >
            <UIcon :name="link.icon || 'i-lucide-link'" class="size-4" />
          </div>
          <div class="min-w-0">
            <p class="text-sm font-medium truncate">{{ link.title }}</p>
            <p class="text-xs text-dimmed">{{ timeAgo(link.created_at) }}</p>
          </div>
        </a>

        <UButton
          icon="i-lucide-x"
          size="2xs"
          variant="ghost"
          color="neutral"
          class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
          @click="deleteQuicklink(link.id)"
        />
      </div>
    </div>
  </UCard>
</template>
