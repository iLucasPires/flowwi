export type StickyVisibility = 'private' | 'workplace'

export interface iSticky {
  id: number
  workplace: number
  created_by: number
  visibility: StickyVisibility
  color: string
  text: string
  position: string
  created_at: string
  updated_at: string
  deleted_at: string | null
  deleted_by: number | null
}
