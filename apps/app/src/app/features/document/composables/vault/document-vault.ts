import { API_DOCUMENT_URLS, apiFetch } from "@/app/core/clients/api";
import type { iCoverUpdate } from "@/app/shared/types/cover";
import type { iDocument, iDocumentVisibility } from "@/app/features/document/types";
import type { iDocSortOrder } from "../../types/document-vault";
import { useDocument } from "../../data/document";
import { useDocumentType } from "../../data/document-type";
import { linksOf } from "../../helpers/document-links";
import { buildDocumentTree } from "../../helpers/document-tree";

export function useDocumentVault() {
  const toast = useToast();

  const { documents, isLoading, createDocument, deleteDocument } = useDocument();
  const { types: documentTypes } = useDocumentType();

  const docs = ref<iDocument[]>([]);
  const activeId = ref<number | null>(null);

  const sortOrder = ref<iDocSortOrder>("newest");
  const typeFilter = ref<(number | null)[]>([]);

  watch(
    documents,
    (list) => {
      if (isLoading.value) return;

      const activeIdValue = activeId.value;
      docs.value = list.map(
        (d) =>
          (d.id === activeIdValue ? docs.value.find((x) => x.id === d.id) : undefined) ??
          structuredClone(toRaw(d)),
      );

      if (activeIdValue == null) {
        if (docs.value.length) activeId.value = docs.value[0]!.id;
      } else if (!docs.value.some((d) => d.id === activeIdValue)) {
        activeId.value = docs.value[0]?.id ?? null;
      }
    },
    { immediate: true },
  );

  const activeDoc = computed(() => docs.value.find((d) => d.id === activeId.value));

  function openDoc(id: number) {
    activeId.value = id;
  }

  function openByTitle(title: string) {
    const document = docs.value.find((d) => d.title === title);
    if (document) openDoc(document.id);
  }

  const treeItems = computed(() =>
    buildDocumentTree({
      documents: docs.value,
      types: documentTypes.value,
      typeFilter: typeFilter.value,
      sortOrder: sortOrder.value,
      onOpen: openDoc,
    }),
  );

  const outline = computed(() => {
    const version = activeDoc.value?.versions[0];
    if (!version) return [];
    return version.content
      .split("\n")
      .filter((raw) => /^#{1,3} /.test(raw))
      .map((raw) => {
        const lvl = raw.match(/^#+/)![0].length;
        return {
          text: raw.replace(/^#+ /, ""),
          pad: `${8 + (lvl - 1) * 12}px`,
          weight: lvl === 1 ? 600 : lvl === 2 ? 500 : 400,
          color:
            lvl === 1
              ? "var(--ui-text-highlighted)"
              : lvl === 2
                ? "var(--ui-text-toned)"
                : "var(--ui-text-dimmed)",
        };
      });
  });

  const outlinks = computed(() => {
    const doc = activeDoc.value;
    if (!doc) return [];
    return linksOf(doc).map((title) => {
      const exists = docs.value.some((d) => d.title === title);
      return {
        title: exists ? title : `${title} · não existe`,
        exists,
        onOpen: () => openByTitle(title),
      };
    });
  });

  const backlinks = computed(() => {
    const doc = activeDoc.value;
    if (!doc) return [];
    return docs.value
      .filter((d) => d.id !== doc.id && linksOf(d).includes(doc.title))
      .map((d) => {
        const version = d.versions[0];
        const hit = version?.content.split("\n").find((l) => l.includes(`[[${doc.title}]]`)) || "";
        return {
          id: d.id,
          title: d.title || "Sem título",
          excerpt: hit
            .replace(/^[#>\-\d.\s[\]x]*/, "")
            .replace(/\[\[|\]\]|\*\*|`/g, "")
            .trim()
            .slice(0, 110),
          onOpen: () => openDoc(d.id),
        };
      });
  });

  const graph = computed(() => {
    const list = docs.value;
    const pos: Record<string, { x: number; y: number }> = {};
    list.forEach((d, i) => {
      const a = (i / list.length) * Math.PI * 2 - Math.PI / 2;
      pos[d.title] = { x: 410 + Math.cos(a) * 290, y: 250 + Math.sin(a) * 175 };
    });

    const edges: { x1: number; y1: number; x2: number; y2: number; stroke: string; w: number }[] =
      [];
    for (const d of list) {
      for (const title of linksOf(d)) {
        const target = pos[title];
        const source = pos[d.title];
        if (!target || !source) continue;
        const isActive = d.id === activeId.value || title === activeDoc.value?.title;
        edges.push({
          x1: source.x,
          y1: source.y,
          x2: target.x,
          y2: target.y,
          stroke: isActive ? "var(--ui-text-muted)" : "var(--ui-border)",
          w: isActive ? 1.4 : 1,
        });
      }
    }

    const degree: Record<string, number> = {};
    for (const d of list) degree[d.title] = 0;
    for (const d of list) {
      for (const title of linksOf(d)) {
        if (pos[title] == null) continue;
        degree[title] = (degree[title] ?? 0) + 1;
        degree[d.title] = (degree[d.title] ?? 0) + 1;
      }
    }

    const nodes = list.map((d) => {
      const on = d.id === activeId.value;
      const size = 10 + Math.min(degree[d.title] ?? 0, 5) * 3;
      const p = pos[d.title]!;
      return {
        id: d.id,
        left: `${p.x}px`,
        top: `${p.y}px`,
        size: `${size}px`,
        fill: on ? "var(--ui-text-highlighted)" : "var(--ui-border-accented)",
        ring: on ? "var(--ui-text-highlighted)" : "var(--ui-border-accented)",
        color: on ? "var(--ui-text-highlighted)" : "var(--ui-text-dimmed)",
        title: (d.title || "Sem título").replace(/^(Roteiro|Briefing|Escaleta|Template) — /, ""),
        onOpen: () => openDoc(d.id),
      };
    });

    return { nodes, edges };
  });

  async function createFromTemplate(typeId: number | null) {
    const type = typeId != null ? documentTypes.value.find((t) => t.id === typeId) : undefined;
    try {
      const created = await createDocument({
        title: type ? `Novo — ${type.name}` : "",
        type: type?.id ?? null,
        content: type?.default_content ?? "",
      });
      docs.value.push(created);
      activeId.value = created.id;
    } catch {
      toast.add({ title: "Erro ao criar documento", color: "error" });
    }
  }

  async function removeDoc(id: number) {
    await deleteDocument(id);
    docs.value = docs.value.filter((d) => d.id !== id);
    if (activeId.value === id) activeId.value = docs.value[0]?.id ?? null;
  }

  async function updateDocTitle(id: number, title: string) {
    const doc = docs.value.find((d) => d.id === id);
    if (!doc) return;
    const previous = doc.title;
    doc.title = title;
    try {
      await apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: "PATCH", body: { title } });
    } catch {
      doc.title = previous;
      toast.add({ title: "Erro ao renomear documento", color: "error" });
    }
  }

  async function duplicateDoc(id: number) {
    const doc = docs.value.find((d) => d.id === id);
    if (!doc) return;
    try {
      const created = await createDocument({
        title: doc.title ? `${doc.title} (cópia)` : "",
        folder: doc.folder,
        type: doc.type,
        content: doc.versions[0]?.content ?? "",
      });
      docs.value.push(created);
      activeId.value = created.id;
    } catch {
      toast.add({ title: "Erro ao duplicar documento", color: "error" });
    }
  }

  async function updateDocType(id: number, type: number | null) {
    const doc = docs.value.find((d) => d.id === id);
    if (!doc) return;
    const previous = doc.type;
    doc.type = type;
    try {
      await apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: "PATCH", body: { type } });
    } catch {
      doc.type = previous;
      toast.add({ title: "Erro ao atualizar tipo", color: "error" });
    }
  }

  async function updateDocIcon(id: number, icon: string) {
    const doc = docs.value.find((d) => d.id === id);
    if (!doc) return;
    const previous = doc.icon;
    doc.icon = icon;
    try {
      await apiFetch(`${API_DOCUMENT_URLS.LIST}/${id}`, { method: "PATCH", body: { icon } });
    } catch {
      doc.icon = previous;
      toast.add({ title: "Erro ao atualizar ícone", color: "error" });
    }
  }

  async function updateDocCover(id: number, update: iCoverUpdate) {
    const doc = docs.value.find((d) => d.id === id);
    if (!doc) return;
    const previousCover = doc.cover;
    const previousStyle = doc.cover_style;
    const previousCredit = doc.cover_credit;
    try {
      let body: FormData | Record<string, unknown>;
      if (update && "file" in update) {
        body = new FormData();
        body.append("cover", update.file);
        body.append("cover_style", "");
      } else if (update && "style" in update) {
        body = { cover: null, cover_style: update.style, cover_credit: update.credit };
      } else {
        body = { cover: null, cover_style: "", cover_credit: null };
      }
      const updated = await apiFetch<iDocument>(`${API_DOCUMENT_URLS.LIST}/${id}`, {
        method: "PATCH",
        body,
      });
      doc.cover = updated.cover;
      doc.cover_style = updated.cover_style;
      doc.cover_credit = updated.cover_credit;
    } catch {
      doc.cover = previousCover;
      doc.cover_style = previousStyle;
      doc.cover_credit = previousCredit;
      toast.add({ title: "Erro ao atualizar capa", color: "error" });
    }
  }

  async function updateDocSharing(
    id: number,
    update: { visibility?: iDocumentVisibility; allow_member_edit?: boolean },
  ) {
    const doc = docs.value.find((d) => d.id === id);
    if (!doc) return;
    const previousVisibility = doc.visibility;
    const previousAllowMemberEdit = doc.allow_member_edit;
    Object.assign(doc, update);
    try {
      const updated = await apiFetch<iDocument>(`${API_DOCUMENT_URLS.LIST}/${id}`, {
        method: "PATCH",
        body: update,
      });
      doc.visibility = updated.visibility;
      doc.allow_member_edit = updated.allow_member_edit;
    } catch {
      doc.visibility = previousVisibility;
      doc.allow_member_edit = previousAllowMemberEdit;
      toast.add({ title: "Erro ao atualizar compartilhamento", color: "error" });
    }
  }

  return {
    docs,
    isLoading,
    activeId,
    activeDoc,
    openDoc,
    openByTitle,
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
  };
}
