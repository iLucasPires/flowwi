<script
  setup
  lang="ts"
  generic="T extends { id: number; name: string; color: string; icon: string }"
>
import { useSortable } from "@dnd-kit/vue/sortable";

const props = defineProps<{
  type: T;
  index: number;
  /** Set for document types, which also carry a `default_content` template —
   * task types have no equivalent, so this stays unset there. */
  hasTemplate?: boolean;
  autoEdit: boolean;
}>();

const emit = defineEmits<{
  update: [type: T, data: Partial<T>];
  delete: [type: T];
  editTemplate: [type: T];
  autoEditDone: [];
}>();

const elementRef = useTemplateRef<HTMLElement>("elementRef");
const handleRef = useTemplateRef<HTMLElement>("handleRef");
const nameInputRef = useTemplateRef("nameInputRef");

const { isDragSource } = useSortable({
  id: computed(() => props.type.id),
  index: computed(() => props.index),
  element: elementRef,
  handle: handleRef,
});

// ── Inline name editing — click the name to rename it, like a Linear table cell. ──
const isEditingName = ref(false);
const draftName = ref(props.type.name);

function startEditingName() {
  draftName.value = props.type.name;
  isEditingName.value = true;
  nextTick(() => {
    const el = nameInputRef.value?.$el?.querySelector("input") as HTMLInputElement | undefined;
    el?.focus();
    el?.select();
  });
}

function commitName() {
  isEditingName.value = false;
  const trimmed = draftName.value.trim();
  if (!trimmed || trimmed === props.type.name) return;
  emit("update", props.type, { name: trimmed } as Partial<T>);
}

function cancelEditingName() {
  isEditingName.value = false;
  draftName.value = props.type.name;
}

watch(
  () => props.autoEdit,
  (value) => {
    if (!value) return;
    startEditingName();
    emit("autoEditDone");
  },
  { immediate: true },
);

// ── Color + icon — a single popover edits both, committed as soon as either changes. ──
function updateColor(color: string) {
  emit("update", props.type, { color } as Partial<T>);
}

function updateIcon(icon: string) {
  emit("update", props.type, { icon } as Partial<T>);
}
</script>

<template>
  <li
    ref="elementRef"
    class="flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-accented/40"
    :class="{ 'opacity-50': isDragSource }"
  >
    <span ref="handleRef" class="cursor-grab active:cursor-grabbing text-dimmed shrink-0">
      <UIcon name="i-lucide-grip-vertical" class="size-4" />
    </span>

    <UPopover>
      <UButton size="xs" variant="ghost" color="neutral" class="p-1 shrink-0">
        <span class="size-4 rounded-full ring-1 ring-default" :style="{ backgroundColor: type.color }" />
      </UButton>
      <template #content>
        <UColorPicker :model-value="type.color" class="p-2" @update:model-value="updateColor" />
      </template>
    </UPopover>

    <CIconPicker
      :model-value="type.icon"
      :color="type.color"
      fallback="i-lucide-box"
      icon-class="size-4"
      button-class="p-1 shrink-0"
      @update:model-value="updateIcon"
    />

    <UInput
      v-if="isEditingName"
      ref="nameInputRef"
      v-model="draftName"
      size="sm"
      variant="none"
      class="flex-1"
      :ui="{ base: 'px-1.5' }"
      @keydown.enter="commitName"
      @keydown.escape="cancelEditingName"
      @blur="commitName"
    />
    <button
      v-else
      type="button"
      class="flex-1 text-start text-sm font-medium px-1.5 py-1 rounded-md hover:bg-accented/60 transition-colors truncate"
      @click="startEditingName"
    >
      {{ type.name }}
    </button>

    <UButton
      v-if="hasTemplate"
      label="Editar template"
      icon="i-lucide-file-text"
      size="xs"
      variant="ghost"
      color="neutral"
      class="shrink-0"
      @click="emit('editTemplate', type)"
    />

    <UButton
      icon="i-lucide-trash-2"
      size="xs"
      variant="ghost"
      color="error"
      class="shrink-0"
      @click="emit('delete', type)"
    />
  </li>
</template>
