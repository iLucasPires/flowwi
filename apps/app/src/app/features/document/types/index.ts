import type { iCoverCredit } from "@/app/shared/types/cover";

export * from "./document-vault";

/** Who currently holds the pessimistic edit lock on a document, if anyone. */
export interface iDocumentLock {
  user_id: number;
  username: string;
}

/** Viewport-relative anchor for the select-to-comment floating toolbar. */
export interface iDocumentSelectionAnchor {
  text: string;
  top: number;
  bottom: number;
  centerX: number;
}

export interface iDocumentFeedback {
  id: number;
  document: number;
  version: number | null;
  given_by: number;
  decision: 1 | 2;
  created_at: string;
}

export interface iDocumentComment {
  id: number;
  document: number;
  version: number | null;
  author: number | null;
  content: string;
  block_index: number | null;
  quote: string;
  created_at: string;
}

export interface iDocumentType {
  id: number;
  name: string;
  color: string;
  icon: string;
  position: string;
  /** Starting markdown content used to seed a new document's first version. */
  default_content: string;
  workplace: number;
}

export type iDocumentVersionStatus = "draft" | "published";

/** Who besides the author and workplace admins can see a document. */
export type iDocumentVisibility = "private" | "workplace";

export interface iDocumentVersion {
  id: number;
  document: number;
  number: number;
  content: string;
  status: iDocumentVersionStatus;
  feedbacks: iDocumentFeedback[];
  comments: iDocumentComment[];
  created_at: string;
}

export interface iDocument {
  id: number;
  task: number | null;
  type: number | null;
  author: number | null;
  title: string;
  icon: string;
  cover: string | null;
  cover_style: string;
  cover_credit: iCoverCredit;
  notes: string;
  folder: string;
  visibility: iDocumentVisibility;
  allow_member_edit: boolean;
  /** Computed by the backend for the requesting user — never derive this on the frontend. */
  can_edit: boolean;
  /** Whether the requesting user may change `visibility`/`allow_member_edit` (author or admin). */
  can_manage_sharing: boolean;
  /** Whether the requesting user is a workplace admin (owner/manager) — sees/edits everything. */
  is_admin_view: boolean;
  versions: iDocumentVersion[];
  feedbacks: iDocumentFeedback[];
  comments: iDocumentComment[];
  deleted_at: string | null;
  deleted_by: number | null;
  created_at: string;
  updated_at: string;
}
