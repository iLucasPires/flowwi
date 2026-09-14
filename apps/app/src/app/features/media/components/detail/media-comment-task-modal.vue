<script setup lang="ts">
import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMedia, iMediaComment } from '@/app/features/media/types'
import { useSubtask } from '@/app/features/task/composables/subtask'
import { useTask } from '@/app/features/task/composables/task'
const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  media: iMedia
  comments: (iMediaComment & { kindTag: string })[]
}>()

const toast = useToast()
const { createTask } = useTask()
const { createSubtask } = useSubtask()

const selectedIds = ref<number[]>([])
const context = ref('')
const submitting = ref(false)

function toggle(id: number) {
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) selectedIds.value.push(id)
  else selectedIds.value.splice(idx, 1)
}

function reset() {
  selectedIds.value = []
  context.value = ''
}

watch(open, (isOpen) => {
  if (isOpen) reset()
})

async function generate() {
  return apiFetch<{ title: string; description: string }>(
    `${API_MEDIA_URLS.LIST}/${props.media.id}/generate-task`,
    {
      method: 'POST',
      body: { comment_ids: selectedIds.value, context: context.value.trim() },
    },
  )
}

async function confirmTask() {
  if (!selectedIds.value.length) return
  submitting.value = true
  try {
    const suggestion = await generate()
    await createTask({ title: suggestion.title, description: suggestion.description })
    toast.add({ title: 'Tarefa criada a partir dos comentários', color: 'success' })
    open.value = false
  } catch {
    toast.add({ title: 'Erro ao gerar tarefa', color: 'error' })
  } finally {
    submitting.value = false
  }
}

async function confirmSubtask() {
  if (!selectedIds.value.length || !props.media.task) return
  submitting.value = true
  try {
    const suggestion = await generate()
    await createSubtask({ task: props.media.task, title: suggestion.title })
    toast.add({ title: 'Subtarefa criada a partir dos comentários', color: 'success' })
    open.value = false
  } catch {
    toast.add({ title: 'Erro ao gerar subtarefa', color: 'error' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UModal
    v-model:open="open"
    title="Criar task a partir de comentários"
    description="Selecione os comentários que devem virar tarefa. A IA usa o texto selecionado e o contexto extra para montar o título e a descrição."
    :ui="{ content: 'sm:max-w-lg' }"
  >
    <template #body>
      <div class="flex flex-col gap-4">
        <div
          class="flex flex-col gap-1 max-h-64 overflow-y-auto rounded-lg border border-default p-1.5"
        >
          <UEmpty
            v-if="comments.length === 0"
            title="Nenhum comentário ainda"
            size="xs"
            variant="naked"
          />
          <label
            v-for="c in comments"
            :key="c.id"
            class="flex items-start gap-2.5 rounded-md p-2 cursor-pointer hover:bg-elevated/60"
          >
            <UCheckbox
              :model-value="selectedIds.includes(c.id)"
              class="mt-0.5"
              @update:model-value="toggle(c.id)"
            />
            <div class="flex flex-col gap-1 min-w-0">
              <UBadge
                size="xs"
                variant="subtle"
                color="neutral"
                class="self-start max-w-full truncate"
              >
                {{ c.kindTag }}
              </UBadge>
              <span class="text-xs text-muted leading-snug">{{ c.content }}</span>
            </div>
          </label>
        </div>

        <UTextarea
          v-model="context"
          :rows="2"
          autoresize
          placeholder="Contexto extra para a IA (opcional)..."
          variant="subtle"
          class="w-full"
        />
      </div>
    </template>

    <template #footer>
      <span class="text-xs text-muted mr-auto">
        {{ selectedIds.length }} selecionado{{ selectedIds.length === 1 ? '' : 's' }}
      </span>
      <UButton label="Cancelar" variant="ghost" color="neutral" size="xs" @click="open = false" />
      <UButton
        v-if="media.task"
        label="Gerar subtarefa"
        variant="subtle"
        size="xs"
        :disabled="!selectedIds.length"
        :loading="submitting"
        @click="confirmSubtask"
      />
      <UButton
        label="Gerar tarefa"
        icon="i-lucide-sparkles"
        size="xs"
        :disabled="!selectedIds.length"
        :loading="submitting"
        @click="confirmTask"
      />
    </template>
  </UModal>
</template>
