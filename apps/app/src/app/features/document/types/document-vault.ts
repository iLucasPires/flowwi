export type iDocSortOrder = "newest" | "oldest" | "title";

export interface iDocTreeItem {
  label: string;
  icon?: string;
  color?: string;
  value: string;
  docId: number | null;
  type: number | null;
  badge: string;
  defaultExpanded?: boolean;
  children?: iDocTreeItem[];
  onSelect?: () => void;
}

export const DOC_SORT_ITEMS: { label: string; value: iDocSortOrder }[] = [
  { label: "Mais recentes", value: "newest" },
  { label: "Mais antigos", value: "oldest" },
  { label: "Alfabética", value: "title" },
];
