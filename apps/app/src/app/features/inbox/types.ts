import type { WorkplaceMemberStatus, iWorkplaceMember } from '@/app/features/workplace/types'

export interface iInbox {
  id: number
  public_id: string
  member: number
  sender: number | iWorkplaceMember | null
  type: number
  title: string
  message: string
  is_read: boolean
  /** The membership this notification is about (e.g. a pending join request), if any. */
  related_member: { public_id: string; status: WorkplaceMemberStatus } | null
  created_at: string
  updated_at: string
}
