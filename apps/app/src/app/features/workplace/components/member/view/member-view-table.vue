<script setup lang="ts">
import {
  useWorkplaceMember,
  usePendingWorkplaceMembers,
} from "@/app/features/workplace/composables/workplaceMember";
import { cWorkplaceRoleBadgeColor } from "@/app/features/workplace/constants";
import type { iWorkplaceMember } from "@/app/features/workplace/types";
import type { TableColumn } from "@nuxt/ui";
import { upperFirst } from "scule";

import type { Row } from "@tanstack/table-core";
import { getPaginationRowModel } from "@tanstack/table-core";

const UButton = resolveComponent("UButton");
const UBadge = resolveComponent("UBadge");
const UDropdownMenu = resolveComponent("UDropdownMenu");
const UCheckbox = resolveComponent("UCheckbox");

const editableRoles: { label: string; value: "manager" | "designer" }[] = [
  { label: "Gerente", value: "manager" },
  { label: "Designer", value: "designer" },
];

const toast = useToast();
const {
  members,
  isLoading: loading,
  isAdmin,
  removeMember,
  updateMemberRole,
} = useWorkplaceMember();
const {
  pendingMembers,
  isLoading: pendingLoading,
  approveMember,
  approveStatus,
  rejectMember,
  rejectStatus,
} = usePendingWorkplaceMembers();
const table = useTemplateRef("table");

const search = defineModel<string>("search");
const role = defineModel<string | undefined>("role");
const rowSelection = ref({});
const columnVisibility = ref();
const pagination = ref({ pageIndex: 0, pageSize: 15 });

function getRowItems(row: Row<iWorkplaceMember>) {
  const canManage = isAdmin.value && row.original.role !== "owner";

  return [
    {
      label: "Copiar ID do membro",
      icon: "i-lucide-copy",
      onSelect() {
        navigator.clipboard.writeText(row.original.public_id);
        toast.add({
          title: "Copiado!",
          description: "ID do membro copiado para a área de transferência.",
        });
      },
    },

    ...(canManage
      ? [
          { type: "separator" },
          {
            label: "Editar papel",
            icon: "i-lucide-shield-half",
            children: editableRoles.map((option) => ({
              label: option.label,
              type: "checkbox" as const,
              checked: row.original.role === option.value,
              onSelect(e?: Event) {
                e?.preventDefault();
                if (row.original.role === option.value) return;

                updateMemberRole({
                  publicId: row.original.public_id,
                  role: option.value,
                });
              },
            })),
          },
          {
            label: "Remover membro",
            icon: "i-lucide-trash",
            color: "error",
            onSelect() {
              removeMember(row.original.public_id);
            },
          },
        ]
      : []),
  ];
}

const columns: TableColumn<iWorkplaceMember>[] = [
  {
    id: "select",
    header: ({ table }) =>
      h(UCheckbox, {
        modelValue: table.getIsSomePageRowsSelected()
          ? "indeterminate"
          : table.getIsAllPageRowsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          table.toggleAllPageRowsSelected(!!value),
        ariaLabel: "Selecionar todos",
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        modelValue: row.getIsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") => row.toggleSelected(!!value),
        ariaLabel: "Selecionar linha",
      }),
  },
  {
    accessorKey: "user",
    header: "Usuário",
    cell: ({ row }) =>
      h("div", { class: "flex items-center gap-3" }, [
        h(resolveComponent("CMemberAvatar"), {
          member: row.original,
          size: "sm",
        }),
        h("div", undefined, [
          h("p", { class: "font-medium text-default" }, row.original.profile?.full_name ?? "—"),
          h("p", { class: "text-xs text-dimmed" }, row.original.profile?.email ?? ""),
        ]),
      ]),
  },
  {
    accessorKey: "role",
    header: "Papel",
    cell: ({ row }) => {
      if (row.original.status === "pending") {
        return h(UBadge, { variant: "subtle", color: "warning", size: "sm" }, () => "Pendente");
      }

      const color = cWorkplaceRoleBadgeColor[row.original.role] ?? "neutral";
      return h(
        UBadge,
        { class: "capitalize", variant: "subtle", color, size: "sm" },
        () => row.original.role,
      );
    },
  },
  {
    accessorKey: "created_at",
    header: ({ column }) => {
      const isSorted = column.getIsSorted();
      return h(UButton, {
        size: "xs",
        color: "neutral",
        variant: "ghost",
        label: "Entrada",
        icon: isSorted
          ? isSorted === "asc"
            ? "i-lucide-arrow-up-narrow-wide"
            : "i-lucide-arrow-down-wide-narrow"
          : "i-lucide-arrow-up-down",
        class: "-mx-2 font-medium text-dimmed text-[11px] uppercase tracking-wider",
        onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
      });
    },
    cell: ({ row }) =>
      row.original.created_at
        ? h(
            "span",
            { class: "text-xs text-dimmed tabular-nums" },
            new Date(row.original.created_at).toLocaleDateString("pt-BR", {
              day: "numeric",
              month: "short",
              year: "numeric",
            }),
          )
        : "—",
  },
  {
    id: "actions",
    cell: ({ row }) => {
      if (row.original.status === "pending") {
        return h("div", { class: "flex items-center justify-end gap-1.5" }, [
          h(UButton, {
            label: "Recusar",
            size: "xs",
            variant: "ghost",
            color: "neutral",
            loading: rejectStatus.value === "pending",
            onClick: () => rejectMember(row.original.public_id),
          }),
          h(UButton, {
            label: "Aprovar",
            icon: "i-lucide-check",
            size: "xs",
            color: "primary",
            loading: approveStatus.value === "pending",
            onClick: () => approveMember(row.original.public_id),
          }),
        ]);
      }

      return h(
        "div",
        { class: "flex items-center justify-end" },
        h(
          UDropdownMenu,
          {
            size: "xs",
            content: { align: "end" },
            items: getRowItems(row),
          },
          () =>
            h(UButton, {
              icon: "i-lucide-more-horizontal",
              size: "xs",
              color: "neutral",
              variant: "ghost",
            }),
        ),
      );
    },
  },
];

const allMembers = computed(() =>
  isAdmin.value ? [...pendingMembers.value, ...members.value] : members.value,
);

const filteredMembers = computed(() => {
  const list = allMembers.value;
  const q = (search.value ?? "").trim().toLowerCase();

  return list.filter((m) => {
    const matchesSearch =
      !q ||
      m.profile?.full_name?.toLowerCase().includes(q) ||
      m.profile?.email?.toLowerCase().includes(q) ||
      m.role?.toLowerCase().includes(q);

    if (!matchesSearch) return false;

    // Pending requests aren't subject to the role filter — they're not "in" a role yet.
    if (m.status === "pending") return true;

    return !role.value || m.role === role.value;
  });
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center justify-end gap-1.5">
      <!-- Bulk delete -->
      <UButton
        v-if="table?.tableApi?.getFilteredSelectedRowModel()?.rows?.length"
        label="Remover"
        color="error"
        variant="subtle"
        icon="i-lucide-trash"
        size="xs"
      >
        <template #trailing>
          <UKbd>{{ table?.tableApi?.getFilteredSelectedRowModel()?.rows?.length }}</UKbd>
        </template>
      </UButton>

      <!-- Column visibility -->
      <UDropdownMenu
        :items="
          table?.tableApi
            ?.getAllColumns()
            ?.filter((column) => column.getCanHide())
            ?.map((column) => ({
              label: upperFirst(column.id),
              type: 'checkbox' as const,
              checked: column.getIsVisible(),
              onUpdateChecked(checked: boolean) {
                table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked);
              },
              onSelect(e?: Event) {
                e?.preventDefault();
              },
            }))
        "
        :content="{ align: 'end' }"
      >
        <UButton
          label="Colunas"
          color="neutral"
          variant="ghost"
          trailing-icon="i-lucide-filter"
          size="xs"
        />
      </UDropdownMenu>
    </div>

    <!-- Table -->
    <div class="rounded-lg overflow-hidden bg-elevated/40">
      <UTable
        ref="table"
        v-model:column-visibility="columnVisibility"
        v-model:row-selection="rowSelection"
        v-model:pagination="pagination"
        :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
        :data="filteredMembers"
        :columns="columns"
        :loading="loading || pendingLoading"
        class="w-full"
        :ui="{
          th: 'py-2.5 px-4 font-semibold text-[11px] uppercase tracking-wider text-dimmed bg-accented/30 focus:outline-none',
          td: 'py-3 px-4 text-sm align-middle',
          tr: 'hover:bg-accented/40 transition-colors',
        }"
      />
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between gap-3 pt-2">
      <div class="text-xs text-dimmed font-medium">
        {{ table?.tableApi?.getFilteredSelectedRowModel()?.rows?.length || 0 }} de
        {{ table?.tableApi?.getFilteredRowModel()?.rows?.length || 0 }} linhas selecionadas.
      </div>
      <UPagination
        v-if="(table?.tableApi?.getPageCount() ?? 0) > 1"
        :default-page="(table?.tableApi?.getState()?.pagination?.pageIndex || 0) + 1"
        :items-per-page="table?.tableApi?.getState()?.pagination?.pageSize || 15"
        :total="table?.tableApi?.getFilteredRowModel()?.rows?.length || 0"
        variant="ghost"
        color="neutral"
        size="xs"
        @update:page="(p: number) => table?.tableApi?.setPageIndex(p - 1)"
      />
    </div>
  </div>
</template>
