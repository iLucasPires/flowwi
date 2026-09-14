<script setup lang="ts">
import type { tFormOut } from '@/app/features/form/schemas'
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  forms: tFormOut[]
  actions: (form: tFormOut) => DropdownMenuItem[][]
}>()

const emit = defineEmits<{
  open: [form: tFormOut]
  answers: [form: tFormOut]
  'copy-link': [form: tFormOut]
}>()

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('pt-BR')
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <UCard
      v-for="form in forms"
      :key="form.id"
      variant="subtle"
      class="cursor-pointer"
      @click="emit('open', form)"
    >
      <div class="flex items-center gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <CTextBlock weight="bold" size="base" :text="form.title" class="truncate" />
            <UBadge
              :color="form.is_published ? 'success' : 'neutral'"
              :label="form.is_published ? 'Publicado' : 'Rascunho'"
              size="xs"
              variant="subtle"
            />
          </div>
          <CTextBlock
            v-if="form.description"
            size="sm"
            :text="form.description"
            class="truncate text-muted mt-1"
          />
        </div>

        <CTextBlock size="xs" :text="formatDate(form.created_at)" class="text-muted shrink-0" />

        <UDropdownMenu :items="actions(form)" size="xs">
          <UButton
            icon="i-lucide-more-horizontal"
            variant="ghost"
            color="neutral"
            size="xs"
            square
            @click.stop
          />
        </UDropdownMenu>
      </div>
    </UCard>
  </div>
</template>
