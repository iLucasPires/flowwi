<script setup lang="ts">
import { useDocumentAi } from "@/app/features/document/composables/documentAi";
import { useDocumentComments } from "@/app/features/document/composables/documentComments";
import { useDocumentEditing } from "@/app/features/document/composables/documentEditing";
import { useDocumentVault } from "@/app/features/document/composables/documentVault";

defineOptions({ name: "DocumentVaultView" });

const {
  docs,
  isLoading,
  activeId,
  activeDoc,
  openDoc,
  treeItems,
  documentTypes,
  sortOrder,
  typeFilter,
  outline,
  outlinks,
  backlinks,
  graph,
  createFromTemplate,
  removeDoc,
  updateDocType,
  updateDocTitle,
  updateDocIcon,
  updateDocCover,
  updateDocSharing,
  duplicateDoc,
} = useDocumentVault();

const {
  saving,
  versions,
  activeIndex,
  selectVersion,
  currentVersion,
  isReadonly,
  lockedBy,
  isLockedByOther,
  onContentChange,
  setVersionStatus,
  newRevision,
  onTitleInput,
} = useDocumentEditing(activeDoc);

const {
  canComment,
  submitAnchored,
  submittingAnchored,
  generalDraft,
  submitGeneral,
  submittingGeneral,
} = useDocumentComments(activeDoc, currentVersion);

const {
  prompt: aiPrompt,
  output: aiOutput,
  activeLabel: aiLabel,
  running: aiRunning,
  runningKey: aiRunningKey,
  run: runAi,
  clear: clearAi,
  insert: insertAi,
} = useDocumentAi(activeDoc, currentVersion);

const splitOpen = ref(false);
const splitDocId = ref<number | null>(null);

const overlay = useOverlay();
let paletteModalId: symbol | null = null;

const route = useRoute();
const queryDocId = Number(route.query.doc);
if (Number.isFinite(queryDocId) && route.query.doc) openDoc(queryDocId);

watch(docs, (list) => {
  if (splitDocId.value == null && list.length) splitDocId.value = list[0]!.id;
});

function toggleSplit() {
  splitOpen.value = !splitOpen.value;
}

const splitterItems = computed(() => {
  const items = [
    {
      id: "tree",
      slot: "tree",
      defaultSize: 22,
      minSize: 15,
      maxSize: 35,
    },
    {
      id: "editor",
      slot: "editor",
      minSize: 30,
      maxSize: 100,
    },
  ];

  if (activeDoc.value && splitOpen.value)
    items.push({
      id: "split",
      slot: "split",
      defaultSize: 24,
      minSize: 15,
      maxSize: 45,
    });

  return items;
});

useEventListener(window, "keydown", (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    openPalette();
  }
});

function truncate(text: string, n = 28) {
  return text.length > n ? `${text.slice(0, n)}…` : text;
}

const taskModalComments = computed(() => {
  const doc = activeDoc.value;
  if (!doc) return [];

  return doc.comments.map((c) => ({
    ...c,
    kindTag: c.quote ? `"${truncate(c.quote)}"` : "Geral",
  }));
});

function openTaskModal() {
  if (!activeDoc.value) return;

  const component = resolveComponent("CDocumentCommentTaskModal");
  if (typeof component === "string") return;

  const modal = overlay.create(component, {
    props: {
      document: activeDoc.value,
      comments: taskModalComments.value,
    },
  });

  modal.open();
}

function openPalette() {
  if (paletteModalId && overlay.isOpen(paletteModalId)) {
    overlay.close(paletteModalId);
    return;
  }

  const component = resolveComponent("CDocumentCommandPalette");
  if (typeof component === "string") return;

  const modal = overlay.create(component, { props: { docs: docs.value } });
  paletteModalId = modal.id;

  modal.open().then((id) => {
    if (id != null) openDoc(id);
  });
}

function openGraphModal() {
  const component = resolveComponent("CDocumentGraphModal");
  if (typeof component === "string") return;

  const modal = overlay.create(component, {
    props: {
      nodes: graph.value.nodes,
      edges: graph.value.edges,
    },
  });

  modal.open();
}
</script>

<template>
  <div v-if="isLoading" class="size-full flex items-center justify-center">
    <UIcon name="i-lucide-loader-2" class="size-6 animate-spin text-dimmed" />
  </div>

  <div v-else class="size-full overflow-hidden">
    <USplitter
      id="document-vault"
      class="rounded-lg border border-default overflow-hidden bg-elevated/50"
      :items="splitterItems"
    >
      <template #tree>
        <CDocumentLeftSplitter
          v-model:sort-order="sortOrder"
          v-model:type-filter="typeFilter"
          :tree-items="treeItems"
          :active-id="activeId"
          :document-types="documentTypes"
          @open-palette="openPalette"
          @open-graph="openGraphModal"
          @create-from-template="createFromTemplate"
          @delete-doc="removeDoc"
          @rename-doc="updateDocTitle"
          @duplicate-doc="duplicateDoc"
          @update-type="updateDocType"
        />
      </template>

      <template #editor>
        <CDocumentCenterSplitter
          v-if="activeDoc"
          :doc="activeDoc"
          :current-version="currentVersion"
          :active-index="activeIndex"
          :is-readonly="isReadonly"
          :locked-by="lockedBy"
          :is-locked-by-other="isLockedByOther"
          :saving="saving"
          :split-open="splitOpen"
          :can-comment="canComment"
          :submitting-anchored="submittingAnchored"
          @title-input="onTitleInput"
          @update-icon="(icon) => updateDocIcon(activeDoc!.id, icon)"
          @select-cover-file="(file) => updateDocCover(activeDoc!.id, { file })"
          @select-cover-style="(style, credit) => updateDocCover(activeDoc!.id, { style, credit })"
          @remove-cover="updateDocCover(activeDoc!.id, null)"
          @content-change="onContentChange"
          @toggle-split="toggleSplit"
          @submit-comment="submitAnchored"
        >
          <template #side-panel>
            <CDocumentRightSplitter
              :outline="outline"
              :outlinks="outlinks"
              :backlinks="backlinks"
              :comments="activeDoc.comments"
              :versions="versions"
              :active-index="activeIndex"
              :can-comment="canComment"
              :ai-output="aiOutput"
              :ai-label="aiLabel"
              :ai-running="aiRunning"
              :ai-running-key="aiRunningKey"
              :ai-prompt="aiPrompt"
              :general-draft="generalDraft"
              :submitting-general="submittingGeneral"
              :visibility="activeDoc.visibility"
              :allow-member-edit="activeDoc.allow_member_edit"
              :can-manage-sharing="activeDoc.can_manage_sharing"
              :is-admin-view="activeDoc.is_admin_view"
              @select-version="selectVersion"
              @new-revision="newRevision"
              @set-status="setVersionStatus"
              @create-task="openTaskModal"
              @run-ai="(key) => runAi(key)"
              @insert-ai="insertAi"
              @clear-ai="clearAi"
              @update:ai-prompt="aiPrompt = $event"
              @update:general-draft="generalDraft = $event"
              @submit-general="submitGeneral"
              @update:visibility="(value) => updateDocSharing(activeDoc!.id, { visibility: value })"
              @update:allow-member-edit="
                (value) => updateDocSharing(activeDoc!.id, { allow_member_edit: value })
              "
            />
          </template>
        </CDocumentCenterSplitter>
      </template>
    </USplitter>
  </div>
</template>

<style>
html.dark .tiptap .shiki,
html.dark .tiptap .shiki span {
  color: var(--shiki-dark) !important;
  background-color: var(--ui-bg-muted) !important;
}
</style>
