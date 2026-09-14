<script setup lang="ts">
import type { iDocumentComment } from '@/app/features/document/types'
defineProps<{
  comments: iDocumentComment[]
  canComment: boolean
  generalDraft: string
  submittingGeneral: boolean
}>()

const emit = defineEmits<{
  createTask: []
  'update:generalDraft': [value: string]
  submitGeneral: []
}>()

function truncate(text: string, max = 40) {
  return text.length > max ? `${text.slice(0, max)}…` : text
}

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

defineOptions({ name: 'DocumentPanelComment' })
</script>

<template>
  <div class="flex flex-col gap-2.5">
    <div class="flex items-center justify-between px-0.5">
      <div class="flex items-center gap-1.5">
        <UIcon name="i-lucide-message-square" class="size-3.5 text-muted" />
        <span class="text-xs font-semibold text-highlighted">Comentários</span>
        <UBadge
          v-if="comments.length"
          :label="String(comments.length)"
          size="xs"
          variant="subtle"
          color="neutral"
          class="text-[10px] px-1.5 py-0 h-4"
        />
      </div>

      <UButton
        v-if="comments.length"
        label="Criar task"
        icon="i-lucide-sparkles"
        size="xs"
        variant="ghost"
        color="neutral"
        @click="emit('createTask')"
      />
    </div>

    <USeparator class="my-0.5" />

    <div v-if="comments.length" class="flex flex-col gap-2 max-h-72 overflow-y-auto pr-0.5">
      <div
        v-for="comment in comments"
        :key="comment.id"
        class="flex flex-col gap-1.5 p-2.5 rounded-lg bg-elevated/40 hover:bg-elevated/70 border border-default/50 transition-colors"
      >
        <div v-if="comment.quote" class="flex items-center gap-1.5 min-w-0">
          <UIcon name="i-lucide-quote" class="size-3 shrink-0 text-primary" />
          <span class="text-[11px] font-mono text-dimmed truncate">
            "{{ truncate(comment.quote, 36) }}"
          </span>
        </div>
        <div v-else class="flex items-center gap-1.5">
          <UBadge
            label="Geral"
            size="xs"
            variant="subtle"
            color="neutral"
            class="text-[9px] px-1 py-0 h-3.5 leading-none"
          />
        </div>

        <p class="text-xs text-default leading-relaxed whitespace-pre-wrap">
          {{ comment.content }}
        </p>

        <span class="text-[10px] text-dimmed self-end">
          {{ timeAgoLabel(comment.created_at) }}
        </span>
      </div>
    </div>

    <UEmpty
      v-else
      icon="i-lucide-message-square-dashed"
      title="Sem comentários"
      description="Use o ícone de comentário nas linhas do texto ou deixe um comentário geral abaixo."
      variant="naked"
      size="xs"
    />

    <USeparator class="my-0.5" />

    <div
      v-if="!canComment"
      class="flex items-center gap-2 p-2 rounded-md bg-elevated/30 text-dimmed text-xs"
    >
      <UIcon name="i-lucide-lock" class="size-3.5 shrink-0" />
      <span>Publique o documento para comentar.</span>
    </div>

    <div v-else class="flex flex-col gap-2">
      <UTextarea
        :model-value="generalDraft"
        :rows="2"
        autoresize
        placeholder="Adicionar um comentário geral..."
        variant="subtle"
        size="xs"
        class="w-full"
        @update:model-value="emit('update:generalDraft', String($event))"
      />
      <UButton
        label="Comentar"
        icon="i-lucide-send"
        size="xs"
        color="primary"
        class="self-end"
        :disabled="!generalDraft.trim()"
        :loading="submittingGeneral"
        @click="emit('submitGeneral')"
      />
    </div>
  </div>
</template>
