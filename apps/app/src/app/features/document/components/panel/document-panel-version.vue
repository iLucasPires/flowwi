<script setup lang="ts">
import type { iDocumentVersion, iDocumentVersionStatus } from '@/app/features/document/types'
defineProps<{
  versions: iDocumentVersion[]
  activeIndex: number
}>()

const emit = defineEmits<{
  selectVersion: [index: number]
  newRevision: []
  setStatus: [status: iDocumentVersionStatus]
}>()

function timeAgoLabel(iso: string) {
  const diffMs = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diffMs / 60_000)

  if (mins < 1) return 'Agora'
  if (mins < 60) return `${mins} min atrás`

  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h atrás`

  const days = Math.floor(hours / 24)
  return `${days}d atrás`
}

function formatFullDate(iso: string) {
  try {
    const date = new Date(iso)
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  } catch {
    return iso
  }
}

defineOptions({
  name: 'DocumentPanelVersion',
})
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-center justify-between px-0.5">
      <div class="flex items-center gap-1.5">
        <UIcon name="i-lucide-history" class="size-3.5 text-muted" />
        <span class="text-xs font-semibold text-highlighted">Versões</span>
        <UBadge
          v-if="versions.length"
          :label="String(versions.length)"
          size="xs"
          variant="subtle"
          color="neutral"
          class="text-[10px] px-1.5 py-0 h-4"
        />
      </div>

      <UTooltip text="Criar nova versão">
        <UButton
          color="neutral"
          icon="i-lucide-plus"
          size="xs"
          variant="ghost"
          @click="emit('newRevision')"
        />
      </UTooltip>
    </div>

    <USeparator class="my-0.5" />

    <div v-if="versions.length" class="flex flex-col gap-0.5 max-h-80 overflow-y-auto">
      <UTooltip
        v-for="(version, index) in versions"
        :key="version.id"
        :text="formatFullDate(version.created_at)"
        :content="{ side: 'left' }"
      >
        <!-- Active version: not a button (it's already open) — shows the draft/published switch. -->
        <div
          v-if="index === activeIndex"
          class="flex items-center justify-between px-2.5 py-2 rounded-md bg-elevated"
        >
          <div class="flex items-center gap-2.5 min-w-0">
            <UIcon name="i-lucide-check-circle-2" class="size-3.5 shrink-0 text-primary" />

            <div class="flex flex-col items-start min-w-0 gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-semibold text-highlighted">v{{ version.number }}</span>

                <UBadge
                  v-if="index === 0"
                  label="Atual"
                  size="xs"
                  variant="subtle"
                  color="neutral"
                  class="text-[9px] px-1 py-0 h-3.5 leading-none"
                />
              </div>

              <span class="text-[11px] text-dimmed leading-none">
                {{ timeAgoLabel(version.created_at) }}
              </span>
            </div>
          </div>

          <CDocumentVersionStatusSelect
            :model-value="version.status"
            size="xs"
            @update:model-value="emit('setStatus', $event as iDocumentVersionStatus)"
          />
        </div>

        <UButton
          v-else
          block
          color="neutral"
          variant="ghost"
          class="justify-between px-2.5 py-2 text-start h-auto rounded-md group"
          @click="emit('selectVersion', index)"
        >
          <div class="flex items-center gap-2.5 min-w-0">
            <UIcon
              name="i-lucide-clock-3"
              class="size-3.5 shrink-0 text-dimmed group-hover:text-muted transition-colors"
            />

            <div class="flex flex-col items-start min-w-0 gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-medium text-default">v{{ version.number }}</span>

                <UBadge
                  v-if="index === 0"
                  label="Atual"
                  size="xs"
                  variant="subtle"
                  color="neutral"
                  class="text-[9px] px-1 py-0 h-3.5 leading-none"
                />

                <UBadge
                  v-if="version.status === 'published'"
                  label="Publicada"
                  size="xs"
                  variant="subtle"
                  color="success"
                  class="text-[9px] px-1 py-0 h-3.5 leading-none"
                />
              </div>

              <span class="text-[11px] text-dimmed leading-none">
                {{ timeAgoLabel(version.created_at) }}
              </span>
            </div>
          </div>
        </UButton>
      </UTooltip>
    </div>
  </div>
</template>
