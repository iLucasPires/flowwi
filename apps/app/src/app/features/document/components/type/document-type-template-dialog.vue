<script setup lang="ts">
import type { iDocumentType } from "@/app/features/document/types";
import { useDocumentType } from "@/app/features/document/composables/data/document-type";

const open = defineModel<boolean>("open", { required: true });

const props = defineProps<{
  type: iDocumentType;
}>();

const { updateType } = useDocumentType();

const defaultContent = ref(props.type.default_content);
const saving = ref(false);

async function save() {
  saving.value = true;
  try {
    await updateType({ id: props.type.id, data: { default_content: defaultContent.value } });
    open.value = false;
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <UModal v-model:open="open" title="Editar template" :ui="{ content: 'sm:max-w-3xl' }">
    <template #body>
      <UFormField
        label="Texto base do documento"
        description="Conteúdo inicial de todo documento criado com este tipo — deixe em branco para começar vazio."
        size="xs"
      >
        <div class="h-96 overflow-y-auto rounded-md border border-default bg-elevated/30 px-3 py-2">
          <CDocumentTypeTemplateEditor
            v-model="defaultContent"
            placeholder="Escreva a estrutura padrão — pressione '/' para comandos..."
          />
        </div>
      </UFormField>
    </template>
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton label="Cancelar" variant="ghost" color="neutral" size="md" @click="open = false" />
        <UButton label="Salvar" color="primary" size="md" :loading="saving" @click="save" />
      </div>
    </template>
  </UModal>
</template>
