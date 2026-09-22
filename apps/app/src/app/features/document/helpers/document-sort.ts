import type { iDocument } from "@/app/features/document/types";
import type { iDocSortOrder } from "../types/document-vault";

export function sortDocuments(documents: iDocument[], order: iDocSortOrder): iDocument[] {
  const sorted = [...documents];

  if (order === "title") {
    return sorted.sort((a, b) =>
      (a.title || "Sem título").localeCompare(b.title || "Sem título"),
    );
  }

  return sorted.sort((a, b) => {
    const diff = new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    return order === "newest" ? diff : -diff;
  });
}
