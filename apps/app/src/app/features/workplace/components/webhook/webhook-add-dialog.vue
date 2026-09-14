<script setup lang="ts">
import { API_WEBHOOK_URLS, apiFetch } from '@/app/core/clients/api'
import { useMutation, useQueryClient } from '@tanstack/vue-query'

const open = defineModel<boolean>('open', { required: true })

const toast = useToast()
const queryClient = useQueryClient()

const url = ref('')
const events = ref<string[]>(['form.response.created'])
const eventOptions = [
  {
    label: 'Resposta de Formulário',
    value: 'form.response.created',
    icon: 'i-lucide-message-square',
    color: 'text-blue-500',
  },
  {
    label: 'Tarefa Criada',
    value: 'task.created',
    icon: 'i-lucide-check-circle-2',
    color: 'text-green-500',
  },
  {
    label: 'Tarefa Atualizada',
    value: 'task.updated',
    icon: 'i-lucide-refresh-cw',
    color: 'text-amber-500',
  },
  {
    label: 'Mídia Criada',
    value: 'media.created',
    icon: 'i-lucide-palette',
    color: 'text-purple-500',
  },
  {
    label: 'Feedback Recebido',
    value: 'media.feedback.created',
    icon: 'i-lucide-message-circle',
    color: 'text-pink-500',
  },
  {
    label: 'Membro Adicionado',
    value: 'workplace.member.added',
    icon: 'i-lucide-user-plus',
    color: 'text-indigo-500',
  },
]

const { mutateAsync: addWebhook, status: addStatus } = useMutation({
  mutationFn: () =>
    apiFetch(API_WEBHOOK_URLS.LIST, {
      method: 'POST',
      body: { url: url.value, events: events.value, is_active: true },
    }),
  onSettled: () => queryClient.invalidateQueries({ queryKey: ['webhooks'] }),
  onSuccess: () => {
    toast.add({ title: 'Webhook adicionado', color: 'success' })
    url.value = ''
    open.value = false
  },
  onError: () => toast.add({ title: 'Erro ao adicionar webhook', color: 'error' }),
})

async function save() {
  if (!url.value) return
  await addWebhook()
}
</script>

<template>
  <UModal v-model:open="open" title="Adicionar Webhook" :ui="{ header: 'border-none' }">
    <template #body>
      <div class="flex flex-col gap-4">
        <UInput
          v-model="url"
          placeholder="URL de destino (ex: https://api.exemplo.com/webhook)"
          size="md"
          variant="subtle"
          icon="i-lucide-link"
          class="w-full"
          autofocus
        />

        <USelectMenu
          v-model="events"
          :items="eventOptions"
          placeholder="Eventos"
          size="md"
          variant="subtle"
          icon="i-lucide-zap"
          class="w-full"
          multiple
          value-key="value"
        >
          <template #item="{ item }">
            <UIcon :name="item.icon" :class="['size-4', item.color]" />
            <span>{{ item.label }}</span>
          </template>
        </USelectMenu>
      </div>
    </template>
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton label="Cancelar" variant="ghost" color="neutral" size="md" @click="open = false" />
        <UButton
          label="Adicionar"
          icon="i-lucide-plus"
          color="primary"
          size="md"
          :disabled="!url.trim() || events.length === 0"
          :loading="addStatus === 'pending'"
          @click="save"
        />
      </div>
    </template>
  </UModal>
</template>
