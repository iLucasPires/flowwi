import type { iDocument, iDocumentType } from "@/app/features/document/types";
import type { iDocSortOrder, iDocTreeItem } from "../types/document-vault";
import { sortDocuments } from "./document-sort";

interface BuildDocumentTreeOptions {
  documents: iDocument[];
  types: iDocumentType[];
  typeFilter: (number | null)[];
  sortOrder: iDocSortOrder;
  onOpen: (id: number) => void;
}

export function buildDocumentTree({
  documents,
  types,
  typeFilter,
  sortOrder,
  onOpen,
}: BuildDocumentTreeOptions): iDocTreeItem[] {
  const byType = new Map<number, iDocument[]>();
  const untyped: iDocument[] = [];

  for (const document of documents) {
    if (document.type == null) {
      untyped.push(document);
      continue;
    }
    const list = byType.get(document.type) ?? [];
    list.push(document);
    byType.set(document.type, list);
  }

  const showAll = typeFilter.length === 0;
  const groups: iDocTreeItem[] = [];

  for (const type of types) {
    if (!showAll && !typeFilter.includes(type.id)) continue;
    const list = byType.get(type.id);
    if (!list?.length) continue;
    groups.push({
      label: type.name,
      icon: type.icon || "i-lucide-tag",
      color: type.color,
      value: `type:${type.id}`,
      docId: null,
      type: type.id,
      badge: "",
      defaultExpanded: true,
      children: sortDocuments(list, sortOrder).map((document) => ({
        label: document.title || "Sem título",
        icon: document.icon || "i-lucide-file-edit",
        value: `doc:${document.id}`,
        docId: document.id,
        type: document.type,
        badge: document.comments.length ? String(document.comments.length) : "",
        onSelect: () => onOpen(document.id),
      })),
    });
  }

  if ((showAll || typeFilter.includes(null)) && untyped.length) {
    groups.push({
      label: "Sem tipo",
      icon: "i-lucide-file-question",
      value: "type:none",
      docId: null,
      type: null,
      badge: "",
      defaultExpanded: true,
      children: sortDocuments(untyped, sortOrder).map((document) => ({
        label: document.title || "Sem título",
        icon: document.icon || "i-lucide-file-edit",
        value: `doc:${document.id}`,
        docId: document.id,
        type: document.type,
        badge: document.comments.length ? String(document.comments.length) : "",
        onSelect: () => onOpen(document.id),
      })),
    });
  }

  return groups;
}
