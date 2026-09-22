<script setup lang="ts">
import type { iDocumentType } from "@/app/features/document/types";
import type { DropdownMenuItem } from "@nuxt/ui";
import type { iDocSortOrder } from "@/app/features/document/types/document-vault";

const props = defineProps<{
  documentTypes: iDocumentType[];
}>();

const emit = defineEmits<{
  openPalette: [];
  openGraph: [];
  /** `null` creates a blank document; otherwise the picked type's own `default_content`. */
  createFromTemplate: [typeId: number | null];
}>();

const sortOrder = defineModel<iDocSortOrder>("sortOrder", { required: true });
const typeFilter = defineModel<(number | null)[]>("typeFilter", { default: () => [] });

// One menu entry per document type — each type's own `default_content` (configured in
// Settings → Tipos de documento) is what seeds the new document, plus a blank fallback.
const templateMenuItems = computed<DropdownMenuItem[][]>(() => [
  [
    ...props.documentTypes.map((type) => ({
      label: type.name,
      icon: type.icon || "i-lucide-file-plus",
      onSelect: () => emit("createFromTemplate", type.id),
    })),
    {
      label: "Documento em branco",
      icon: "i-lucide-file",
      onSelect: () => emit("createFromTemplate", null),
    },
  ],
]);

defineOptions({ name: "DocumentTreeHeader" });
</script>

<template>
  <header class="flex shrink-0 flex-col gap-3 px-4 pt-4 pb-3">
    <div class="flex items-center justify-between">
      <h2 class="text-[13px] font-semibold text-highlighted">Vault criativo</h2>

      <div class="flex gap-1">
        <UTooltip text="Grafo de conexões">
          <UButton
            icon="i-lucide-git-branch"
            variant="ghost"
            color="neutral"
            size="xs"
            @click="emit('openGraph')"
          />
        </UTooltip>

        <CDocumentTreeFilterPopover
          v-model:sort-order="sortOrder"
          v-model:type-filter="typeFilter"
          :types="documentTypes"
        />

        <UDropdownMenu size="xs" :items="templateMenuItems" :content="{ align: 'end' }">
          <UButton
            icon="i-lucide-plus"
            variant="ghost"
            color="neutral"
            size="xs"
            aria-label="Novo documento"
          />
        </UDropdownMenu>
      </div>
    </div>
  </header>
</template>
