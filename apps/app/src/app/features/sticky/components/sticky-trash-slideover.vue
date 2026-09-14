<script setup lang="ts">
import { useTrashedStickies } from '@/app/features/sticky/composables/stickyTrash'
const open = ref(false)

const { trashedStickies, restoreSticky, restoring } = useTrashedStickies()
</script>

<template>
  <USlideover v-model:open="open" title="Itens excluídos" side="right">
    <UButton
      icon="i-lucide-trash-2"
      variant="ghost"
      color="neutral"
      size="xs"
      @click="open = true"
    />

    <template #body>
      <UEmpty
        v-if="trashedStickies.length === 0"
        title="Nenhuma sticky excluída"
        icon="i-lucide-trash-2"
        variant="subtle"
        size="sm"
      />

      <div v-else class="flex flex-col gap-0.5">
        <div
          v-for="sticky in trashedStickies"
          :key="sticky.id"
          class="flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 hover:bg-elevated/50"
        >
          <div class="flex items-center gap-2 min-w-0">
            <span
              class="size-3 rounded-full shrink-0 border border-default"
              :style="{ backgroundColor: sticky.color }"
            />
            <span class="text-sm truncate">{{ sticky.text || '(sem texto)' }}</span>
          </div>

          <UButton
            label="Restaurar"
            icon="i-lucide-undo-2"
            size="xs"
            variant="subtle"
            :loading="restoring"
            @click="restoreSticky(sticky.id)"
          />
        </div>
      </div>
    </template>
  </USlideover>
</template>
