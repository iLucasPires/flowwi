<script setup lang="ts">
import { useTrashedTasks } from "@/app/features/task/composables/taskTrash";
import type { iTask } from "@/app/features/task/types";
import { useTrashedStickies } from "@/app/features/sticky/composables/stickyTrash";
import type { iSticky } from "@/app/features/sticky/types";
import { useTrashedDocuments } from "@/app/features/document/composables/data/document-trash";
import type { iDocument } from "@/app/features/document/types";
import type { TableColumn } from "@nuxt/ui";

const UButton = resolveComponent("UButton");
const CTaskTypeBadge = resolveComponent("CTaskTypeBadge");
const CIconOrEmoji = resolveComponent("CIconOrEmoji");
const CMemberOwnerIndicator = resolveComponent("CMemberOwnerIndicator");

const tab = ref<"tasks" | "stickies" | "documents">("tasks");

const {
  trashedTasks,
  isLoading: tasksLoading,
  restoreTask,
  restoring: restoringTask,
} = useTrashedTasks();
const {
  trashedStickies,
  isLoading: stickiesLoading,
  restoreSticky,
  restoring: restoringSticky,
} = useTrashedStickies();
const {
  trashedDocuments,
  isLoading: documentsLoading,
  restoreDocument,
  restoring: restoringDocument,
} = useTrashedDocuments();

const tabItems = computed(() => [
  {
    label: `Tarefas${trashedTasks.value.length ? ` (${trashedTasks.value.length})` : ""}`,
    value: "tasks",
  },
  {
    label: `Stickies${trashedStickies.value.length ? ` (${trashedStickies.value.length})` : ""}`,
    value: "stickies",
  },
  {
    label: `Documentos${trashedDocuments.value.length ? ` (${trashedDocuments.value.length})` : ""}`,
    value: "documents",
  },
]);

function deletedAtLabel(deletedAt: string | null) {
  if (!deletedAt) return "—";
  return new Date(deletedAt).toLocaleDateString("pt-BR", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const taskColumns: TableColumn<iTask>[] = [
  {
    accessorKey: "title",
    header: "Título",
    cell: ({ row }) =>
      h("div", { class: "flex items-center gap-2 min-w-0" }, [
        h(CTaskTypeBadge, { type: row.original.type }),
        h("span", { class: "text-sm font-medium truncate" }, row.original.title),
      ]),
  },
  {
    accessorKey: "deleted_at",
    header: "Excluído em",
    cell: ({ row }) =>
      h(
        "span",
        { class: "text-xs text-dimmed tabular-nums" },
        deletedAtLabel(row.original.deleted_at),
      ),
  },
  {
    accessorKey: "deleted_by",
    header: "Excluído por",
    cell: ({ row }) =>
      h(CMemberOwnerIndicator, { userId: row.original.deleted_by, label: "Excluído por" }),
  },
  {
    id: "actions",
    cell: ({ row }) =>
      h("div", { class: "flex items-center justify-end" }, [
        h(UButton, {
          label: "Restaurar",
          icon: "i-lucide-undo-2",
          size: "xs",
          variant: "subtle",
          loading: restoringTask.value,
          onClick: () => restoreTask(row.original.public_id),
        }),
      ]),
  },
];

const stickyColumns: TableColumn<iSticky>[] = [
  {
    accessorKey: "text",
    header: "Sticky",
    cell: ({ row }) =>
      h("div", { class: "flex items-center gap-2 min-w-0" }, [
        h("span", {
          class: "size-3 rounded-full shrink-0 border border-default",
          style: { backgroundColor: row.original.color },
        }),
        h("span", { class: "text-sm truncate" }, row.original.text || "(sem texto)"),
      ]),
  },
  {
    accessorKey: "deleted_at",
    header: "Excluído em",
    cell: ({ row }) =>
      h(
        "span",
        { class: "text-xs text-dimmed tabular-nums" },
        deletedAtLabel(row.original.deleted_at),
      ),
  },
  {
    accessorKey: "deleted_by",
    header: "Excluído por",
    cell: ({ row }) =>
      h(CMemberOwnerIndicator, { userId: row.original.deleted_by, label: "Excluído por" }),
  },
  {
    id: "actions",
    cell: ({ row }) =>
      h("div", { class: "flex items-center justify-end" }, [
        h(UButton, {
          label: "Restaurar",
          icon: "i-lucide-undo-2",
          size: "xs",
          variant: "subtle",
          loading: restoringSticky.value,
          onClick: () => restoreSticky(row.original.id),
        }),
      ]),
  },
];

const documentColumns: TableColumn<iDocument>[] = [
  {
    accessorKey: "title",
    header: "Título",
    cell: ({ row }) =>
      h("div", { class: "flex items-center gap-2 min-w-0" }, [
        h(CIconOrEmoji, {
          value: row.original.icon,
          fallback: "i-lucide-file-text",
          class: "size-4 shrink-0",
        }),
        h("span", { class: "text-sm font-medium truncate" }, row.original.title || "(sem título)"),
      ]),
  },
  {
    accessorKey: "deleted_at",
    header: "Excluído em",
    cell: ({ row }) =>
      h(
        "span",
        { class: "text-xs text-dimmed tabular-nums" },
        deletedAtLabel(row.original.deleted_at),
      ),
  },
  {
    accessorKey: "deleted_by",
    header: "Excluído por",
    cell: ({ row }) =>
      h(CMemberOwnerIndicator, { userId: row.original.deleted_by, label: "Excluído por" }),
  },
  {
    id: "actions",
    cell: ({ row }) =>
      h("div", { class: "flex items-center justify-end" }, [
        h(UButton, {
          label: "Restaurar",
          icon: "i-lucide-undo-2",
          size: "xs",
          variant: "subtle",
          loading: restoringDocument.value,
          onClick: () => restoreDocument(row.original.id),
        }),
      ]),
  },
];
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold">Lixeira</h2>
        <p class="text-sm text-dimmed mt-1">Itens excluídos de tarefas, stickies e documentos.</p>
      </div>

      <UTabs v-model="tab" :items="tabItems" size="xs" :content="false" />
    </div>

    <div class="rounded-lg overflow-hidden bg-elevated/40">
      <UTable
        v-if="tab === 'tasks'"
        :data="trashedTasks"
        :columns="taskColumns"
        :loading="tasksLoading"
        class="w-full"
        :ui="{
          th: 'py-2.5 px-4 font-semibold text-[11px] uppercase tracking-wider text-dimmed bg-accented/30 focus:outline-none',
          td: 'py-3 px-4 text-sm align-middle',
          tr: 'hover:bg-accented/40 transition-colors',
        }"
      >
        <template #empty>
          <UEmpty
            title="Nenhuma tarefa excluída"
            description="Tarefas apagadas aparecem aqui e podem ser restauradas."
            icon="i-lucide-trash-2"
            variant="ghost"
            size="sm"
          />
        </template>
      </UTable>

      <UTable
        v-else-if="tab === 'stickies'"
        :data="trashedStickies"
        :columns="stickyColumns"
        :loading="stickiesLoading"
        class="w-full"
        :ui="{
          th: 'py-2.5 px-4 font-semibold text-[11px] uppercase tracking-wider text-dimmed bg-accented/30 focus:outline-none',
          td: 'py-3 px-4 text-sm align-middle',
          tr: 'hover:bg-accented/40 transition-colors',
        }"
      >
        <template #empty>
          <UEmpty
            title="Nenhuma sticky excluída"
            icon="i-lucide-trash-2"
            variant="ghost"
            size="sm"
          />
        </template>
      </UTable>

      <UTable
        v-else
        :data="trashedDocuments"
        :columns="documentColumns"
        :loading="documentsLoading"
        class="w-full"
        :ui="{
          th: 'py-2.5 px-4 font-semibold text-[11px] uppercase tracking-wider text-dimmed bg-accented/30 focus:outline-none',
          td: 'py-3 px-4 text-sm align-middle',
          tr: 'hover:bg-accented/40 transition-colors',
        }"
      >
        <template #empty>
          <UEmpty
            title="Nenhum documento excluído"
            description="Documentos apagados aparecem aqui e podem ser restaurados."
            icon="i-lucide-trash-2"
            variant="ghost"
            size="sm"
          />
        </template>
      </UTable>
    </div>
  </div>
</template>
