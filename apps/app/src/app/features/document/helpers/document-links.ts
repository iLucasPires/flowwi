import type { iDocument } from "@/app/features/document/types";

const WIKILINK_RE = /\[\[([^\]]+)\]\]/g;

export function linksOf(doc: iDocument): string[] {
  const content = doc.versions[0]?.content ?? "";
  const links: string[] = [];

  WIKILINK_RE.lastIndex = 0;

  let match: RegExpExecArray | null;
  while ((match = WIKILINK_RE.exec(content))) {
    const title = match[1];
    if (title && !links.includes(title)) {
      links.push(title);
    }
  }

  return links;
}
