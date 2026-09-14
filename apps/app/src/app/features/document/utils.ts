import type { iDocumentType } from '@/app/features/document/types'
export function getDocumentTypeMeta(types: iDocumentType[], id: number | null) {
  return types.find((t) => t.id === id)
}
