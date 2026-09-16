<script setup lang="ts">
import type { iDocumentComment, iDocumentVersion, iDocumentVersionStatus, iDocumentVisibility } from '@/app/features/document/types'
const props = defineProps<{
  outline: { text: string; pad: string; weight: number; color: string }[]
  outlinks: { title: string; exists: boolean; onOpen: () => void }[]
  backlinks: { id: number; title: string; excerpt: string; onOpen: () => void }[]
  comments: iDocumentComment[]
  versions: iDocumentVersion[]
  activeIndex: number
  canComment: boolean
  aiOutput: string
  aiLabel: string
  aiRunning: boolean
  aiRunningKey: string | null
  aiPrompt: string
  generalDraft: string
  submittingGeneral: boolean
  visibility: iDocumentVisibility
  allowMemberEdit: boolean
  canManageSharing: boolean
  isAdminView: boolean
}>()

const emit = defineEmits<{
  selectVersion: [index: number]
  newRevision: []
  setStatus: [status: iDocumentVersionStatus]
  createTask: []
  runAi: [actionKey?: string]
  insertAi: []
  clearAi: []
  'update:aiPrompt': [value: string]
  'update:generalDraft': [value: string]
  submitGeneral: []
  'update:visibility': [iDocumentVisibility]
  'update:allowMemberEdit': [boolean]
}>()

const shareIcon = computed(() =>
  props.visibility === 'private' ? 'i-lucide-lock' : 'i-lucide-users',
)

const popoverContent = { align: 'end' as const, side: 'bottom' as const, sideOffset: 8 }

defineOptions({ name: 'DocumentRightPanel' })
</script>

<template>
  <div class="flex items-center gap-2">
    <UPopover :content="popoverContent">
      <UTooltip text="Sumário">
        <UButton icon="i-lucide-list" variant="ghost" color="neutral" size="xs" />
      </UTooltip>

      <template #content>
        <div class="w-72 max-h-96 overflow-y-auto p-3">
          <CDocumentPanelOutline :outline="outline" />
        </div>
      </template>
    </UPopover>

    <UPopover :content="popoverContent">
      <UTooltip text="Links">
        <UChip
          :text="outlinks.length + backlinks.length"
          :show="outlinks.length + backlinks.length > 0"
          size="xs"
        >
          <UButton icon="i-lucide-link" variant="ghost" color="neutral" size="xs" />
        </UChip>
      </UTooltip>

      <template #content>
        <div class="w-80 max-h-96 overflow-y-auto p-3 flex flex-col gap-3.5">
          <CDocumentPanelLinks :outlinks="outlinks" :backlinks="backlinks" />
        </div>
      </template>
    </UPopover>

    <UPopover :content="popoverContent">
      <UTooltip text="Comentários">
        <UChip :text="comments.length" :show="comments.length > 0" size="xs">
          <UButton icon="i-lucide-message-square" variant="ghost" color="neutral" size="xs" />
        </UChip>
      </UTooltip>

      <template #content>
        <div class="w-80 p-3">
          <CDocumentPanelComment
            :comments="comments"
            :can-comment="canComment"
            :general-draft="generalDraft"
            :submitting-general="submittingGeneral"
            @create-task="emit('createTask')"
            @update:general-draft="emit('update:generalDraft', $event)"
            @submit-general="emit('submitGeneral')"
          />
        </div>
      </template>
    </UPopover>

    <UPopover :content="popoverContent">
      <UTooltip text="Histórico de versões">
        <UButton icon="i-lucide-history" variant="ghost" color="neutral" size="xs" />
      </UTooltip>

      <template #content>
        <div class="w-80 p-3">
          <CDocumentPanelVersion
            :versions="versions"
            :active-index="activeIndex"
            @select-version="(index) => emit('selectVersion', index)"
            @new-revision="emit('newRevision')"
            @set-status="(status) => emit('setStatus', status)"
          />
        </div>
      </template>
    </UPopover>

    <UPopover :content="popoverContent">
      <UTooltip text="Assistente de IA">
        <UButton
          icon="i-lucide-sparkles"
          variant="ghost"
          color="neutral"
          size="xs"
          :loading="aiRunning"
        />
      </UTooltip>

      <template #content>
        <div class="w-80 max-h-96 overflow-y-auto p-3">
          <CDocumentPanelAi
            :ai-output="aiOutput"
            :ai-label="aiLabel"
            :ai-running="aiRunning"
            :ai-running-key="aiRunningKey"
            :ai-prompt="aiPrompt"
            @run-ai="(key) => emit('runAi', key)"
            @insert-ai="emit('insertAi')"
            @clear-ai="emit('clearAi')"
            @update:ai-prompt="emit('update:aiPrompt', $event)"
          />
        </div>
      </template>
    </UPopover>

    <div class="w-px h-4 bg-border shrink-0 mx-0.5" />

    <UPopover :content="popoverContent">
      <UTooltip text="Compartilhamento">
        <UButton :icon="shareIcon" variant="ghost" color="neutral" size="xs" />
      </UTooltip>

      <template #content>
        <div class="p-3">
          <CDocumentPanelShare
            :visibility="visibility"
            :allow-member-edit="allowMemberEdit"
            :can-manage-sharing="canManageSharing"
            :is-admin-view="isAdminView"
            @update:visibility="emit('update:visibility', $event)"
            @update:allow-member-edit="emit('update:allowMemberEdit', $event)"
          />
        </div>
      </template>
    </UPopover>
  </div>
</template>
