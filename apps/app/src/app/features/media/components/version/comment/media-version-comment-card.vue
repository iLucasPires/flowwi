<script setup lang="ts">
import type { iMediaComment } from '@/app/features/media/types'
import { marked } from 'marked'

defineProps<{
  comment: iMediaComment
  selectable?: boolean
  selected?: boolean
}>()

const emit = defineEmits<{ toggle: [id: number] }>()
</script>

<template>
  <div
    class="flex gap-2.5 px-3 py-2 rounded-lg bg-elevated hover:bg-accented/30 transition-colors cursor-pointer relative"
    @click="selectable ? emit('toggle', comment.id) : null"
  >
    <UCheckbox
      v-if="selectable"
      :model-value="selected"
      class="mt-1"
      @click.stop="emit('toggle', comment.id)"
    />
    <UAvatar v-else size="xs" :text="String(comment.author)" class="mt-0.5 shrink-0" />
    <div class="flex-1 min-w-0">
      <p class="text-[10px] text-dimmed leading-none mb-1">
        #{{ comment.author }} ·
        {{
          new Date(comment.created_at).toLocaleDateString('pt-BR', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit',
          })
        }}
      </p>
      <div
        class="text-xs text-default prose prose-xs prose-neutral dark:prose-invert max-w-none [&_p]:my-0.5 [&_h1]:text-sm [&_h2]:text-sm [&_h3]:text-xs"
        v-html="marked(comment.content)"
      />
    </div>
  </div>
</template>
