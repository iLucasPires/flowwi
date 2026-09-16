<script setup lang="ts">
import { useTaskStatus } from "@/app/features/task/composables/taskStatus";
import type { TaskStatusCategory, iTaskStatus } from "@/app/features/task/types";
const open = defineModel<boolean>("open", { required: true });

const props = defineProps<{
  status?: iTaskStatus;
}>();

const { createStatus, updateStatus } = useTaskStatus();

const categoryOptions = [
  { label: "A fazer", value: "todo" },
  { label: "Em progresso", value: "in_progress" },
  { label: "Concluído", value: "done" },
  { label: "Cancelado", value: "cancelled" },
];

const isEditing = computed(() => !!props.status);

const name = ref(props.status?.name ?? "");
const color = ref(props.status?.color ?? "#5CFCD4");
const icon = ref(props.status?.icon ?? "");
const category = ref<TaskStatusCategory>(props.status?.category ?? "todo");

const saving = ref(false);

async function save() {
  if (!name.value.trim()) return;
  saving.value = true;
  try {
    const data = {
      name: name.value,
      color: color.value,
      icon: icon.value,
      category: category.value,
    };

    if (isEditing.value && props.status) {
      await updateStatus({ id: props.status.id, data });
    } else {
      await createStatus(data);
    }

    open.value = false;
  } finally {
    saving.value = false;
  }
}
const chip = computed(() => ({ backgroundColor: color.value }));
</script>

<template>
  <UModal
    v-model:open="open"
    :title="isEditing ? 'Editar status' : 'Novo status'"
    :ui="{ content: 'sm:max-w-md' }"
  >
    <template #body>
      <div class="flex flex-col gap-4">
        <UFormField label="Cor" size="xs">
          <UPopover class="w-full">
            <UButton :label="color" size="xs" color="neutral" variant="subtle">
              <template #leading>
                <span :style="chip" class="size-3 rounded-full" />
              </template>
            </UButton>
            <template #content>
              <UColorPicker v-model="color" class="p-2" />
            </template>
          </UPopover>
        </UFormField>

        <UFormField label="Ícone" size="lg">
          <CIconPicker v-model="icon" :color="color" size="md" />
        </UFormField>

        <UFormField label="Nome" size="xs">
          <UInput
            v-model="name"
            placeholder="Nome do status"
            size="xs"
            variant="subtle"
            class="w-full"
            autofocus
          />
        </UFormField>

        <UFormField label="Tipo" size="xs">
          <USelectMenu
            v-model="category"
            :items="categoryOptions"
            value-key="value"
            placeholder="Categoria"
            size="xs"
            variant="subtle"
            class="w-full"
          />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton label="Cancelar" variant="ghost" color="neutral" size="md" @click="open = false" />
        <UButton
          label="Salvar"
          color="primary"
          size="md"
          :disabled="!name.trim()"
          :loading="saving"
          @click="save"
        />
      </div>
    </template>
  </UModal>
</template>
