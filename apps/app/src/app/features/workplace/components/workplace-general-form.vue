<script setup lang="ts">
import { useWorkplaceMutations } from '@/app/features/workplace/composables/workplace'
import { useWorkplaceMember } from '@/app/features/workplace/composables/workplaceMember'
import type { iWorkplace } from '@/app/features/workplace/types'
import type { iCoverUpdate } from '@/app/shared/types/cover'
const props = defineProps<{
  workplace: iWorkplace
}>()

const toast = useToast()
const { updateWorkplace, regenerateInviteKey } = useWorkplaceMutations()
const { myRole } = useWorkplaceMember()
const isOwner = computed(() => myRole.value === 'owner')

const name = ref('')
const copyingKey = ref(false)
const regenerating = ref(false)
const showDeleteDialog = ref(false)

watch(
  () => props.workplace.name,
  (v) => {
    if (v) name.value = v
  },
  { immediate: true },
)

watchDebounced(
  name,
  (value) => {
    if (value.trim() && value.trim() !== props.workplace.name) {
      updateWorkplace({ id: props.workplace.id, data: { name: value.trim() } })
    }
  },
  { debounce: 800 },
)

async function saveCover(update: iCoverUpdate) {
  try {
    let data: Record<string, unknown>

    if (update && 'file' in update) {
      const formData = new FormData()
      formData.append('photo', update.file)
      formData.append('cover_style', '')
      data = formData as unknown as Record<string, unknown>
    } else if (update && 'style' in update) {
      data = { photo: null, cover_style: update.style, cover_credit: update.credit }
    } else {
      data = { photo: null, cover_style: '', cover_credit: null }
    }

    await updateWorkplace({ id: props.workplace.id, data })
    toast.add({ title: 'Capa atualizada', color: 'success' })
  } catch {
    toast.add({ title: 'Erro ao atualizar capa', color: 'error' })
  }
}

function copyKey() {
  copyingKey.value = true
  navigator.clipboard.writeText(props.workplace.invite_key)
  toast.add({ title: 'Chave copiada!', color: 'info' })
  setTimeout(() => {
    copyingKey.value = false
  }, 2000)
}

async function regenerateKey() {
  regenerating.value = true
  try {
    await regenerateInviteKey(props.workplace.id)
    toast.add({ title: 'Nova chave gerada', color: 'success' })
  } catch {
    toast.add({ title: 'Erro ao gerar chave', color: 'error' })
  } finally {
    regenerating.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <CCoverBanner
      :src="workplace.photo"
      :style-value="workplace.cover_style"
      :credit="workplace.cover_credit"
      @select-file="saveCover({ file: $event })"
      @select-style="(style, credit) => saveCover({ style, credit })"
      @remove="saveCover(null)"
    />

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <UFormField label="Nome do Workspace" size="xs">
        <UInput v-model="name" class="w-full" variant="subtle" size="xs" />
      </UFormField>

      <UFormField label="Chave de convite" size="xs">
        <div class="flex gap-2">
          <UInput
            :model-value="workplace.invite_key"
            disabled
            class="flex-1 font-mono text-sm"
            variant="subtle"
            size="xs"
          />
          <UButton
            :icon="copyingKey ? 'i-lucide-check' : 'i-lucide-copy'"
            color="neutral"
            variant="subtle"
            size="xs"
            @click="copyKey"
          />
          <UButton
            icon="i-lucide-refresh-cw"
            variant="subtle"
            color="neutral"
            size="xs"
            :loading="regenerating"
            @click="regenerateKey"
          />
        </div>
      </UFormField>
    </div>

    <UAlert
      v-if="isOwner"
      title="Zona de Perigo"
      description="A exclusão de um workspace é permanente e não pode ser desfeita."
      variant="subtle"
      color="error"
      size="xs"
      icon="i-lucide-triangle-alert"
      :actions="[
        {
          label: 'Excluir Workspace',
          color: 'error',
          variant: 'solid',
          onClick: () => (showDeleteDialog = true),
        },
      ]"
    />

    <CWorkplaceDeleteDialog v-model:open="showDeleteDialog" :workplace="workplace" />
  </div>
</template>
