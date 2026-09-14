<script setup lang="ts">
import { useTrashedTasks } from '@/app/features/task/composables/taskTrash'
const open = ref(false)

const { trashedTasks, restoreTask, restoring } = useTrashedTasks()
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
        v-if="trashedTasks.length === 0"
        title="Nenhuma tarefa excluída"
        icon="i-lucide-trash-2"
        variant="subtle"
        size="sm"
      />

      <div v-else class="flex flex-col gap-0.5">
        <div
          v-for="task in trashedTasks"
          :key="task.public_id"
          class="flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 hover:bg-elevated/50"
        >
          <span class="text-sm font-medium truncate">{{ task.title }}</span>

          <UButton
            label="Restaurar"
            icon="i-lucide-undo-2"
            size="xs"
            variant="subtle"
            :loading="restoring"
            @click="restoreTask(task.public_id)"
          />
        </div>
      </div>
    </template>
  </USlideover>
</template>
