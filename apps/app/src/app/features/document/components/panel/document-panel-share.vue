<script setup lang="ts">
import type { iDocumentVisibility } from '@/app/features/document/types'
const props = defineProps<{
  visibility: iDocumentVisibility
  allowMemberEdit: boolean
  canManageSharing: boolean
  isAdminView: boolean
}>()

const emit = defineEmits<{
  'update:visibility': [iDocumentVisibility]
  'update:allowMemberEdit': [boolean]
}>()

const VISIBILITY_ITEMS: {
  value: iDocumentVisibility
  label: string
  icon: string
  description: string
}[] = [
  {
    value: 'private',
    label: 'Privado',
    icon: 'i-lucide-lock',
    description: 'Só você e os administradores do workplace.',
  },
  {
    value: 'workplace',
    label: 'Workplace',
    icon: 'i-lucide-users',
    description: 'Todo mundo no workplace pode ver.',
  },
]

const memberEditDisabled = computed(() => props.visibility === 'private' || !props.canManageSharing)

function selectVisibility(value: iDocumentVisibility) {
  if (!props.canManageSharing || value === props.visibility) return
  emit('update:visibility', value)
}

defineOptions({ name: 'DocumentPanelShare' })
</script>

<template>
  <div class="flex flex-col gap-2.5 w-72">
    <div class="flex items-center gap-1.5 px-0.5">
      <UIcon name="i-lucide-share-2" class="size-3.5 text-muted" />
      <span class="text-xs font-semibold text-highlighted">Compartilhamento</span>
    </div>

    <USeparator class="my-0.5" />

    <div class="flex flex-col gap-1">
      <span class="text-[11px] font-medium text-dimmed px-0.5">Quem pode ver</span>

      <UButton
        v-for="item in VISIBILITY_ITEMS"
        :key="item.value"
        variant="ghost"
        color="neutral"
        block
        :disabled="!canManageSharing"
        class="justify-start px-2.5 py-2 h-auto rounded-md"
        :class="visibility === item.value ? 'bg-elevated' : ''"
        @click="selectVisibility(item.value)"
      >
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          <UIcon
            :name="item.icon"
            class="size-3.5 shrink-0"
            :class="visibility === item.value ? 'text-primary' : 'text-dimmed'"
          />
          <div class="flex flex-col items-start min-w-0">
            <span class="text-xs font-medium text-default">{{ item.label }}</span>
            <span class="text-[10.5px] text-dimmed leading-tight text-start">
              {{ item.description }}
            </span>
          </div>
        </div>
        <UIcon
          v-if="visibility === item.value"
          name="i-lucide-check"
          class="size-3.5 shrink-0 text-primary"
        />
      </UButton>
    </div>

    <USeparator class="my-0.5" />

    <label
      class="flex items-center justify-between gap-2 px-0.5 cursor-pointer select-none"
      :class="{ 'opacity-50 pointer-events-none': memberEditDisabled }"
    >
      <div class="flex flex-col">
        <span class="text-xs font-medium text-default">Membros podem editar</span>
        <span class="text-[10.5px] text-dimmed leading-tight">
          Além de você e os administradores.
        </span>
      </div>
      <USwitch
        :model-value="allowMemberEdit"
        size="xs"
        :disabled="memberEditDisabled"
        @update:model-value="emit('update:allowMemberEdit', $event)"
      />
    </label>

    <p
      v-if="isAdminView"
      class="text-[10.5px] text-dimmed leading-tight flex items-start gap-1.5 px-0.5"
    >
      <UIcon name="i-lucide-shield-check" class="size-3 shrink-0 mt-0.5 text-primary" />
      Como administrador do workplace, você sempre vê e edita todos os documentos, independente
      destas configurações.
    </p>

    <p v-else-if="!canManageSharing" class="text-[10.5px] text-dimmed leading-tight px-0.5">
      Só o autor ou administradores do workplace podem alterar o compartilhamento.
    </p>
  </div>
</template>
