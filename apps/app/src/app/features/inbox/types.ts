import type { iWorkplaceMember } from '@/app/features/workplace/types'

export interface iInbox {
  id: number
  public_id: string
  member: number
  sender: number | iWorkplaceMember | null
  type: number
  title: string
  message: string
  is_read: boolean
  created_at: string
  updated_at: string
}
