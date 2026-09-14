import type { iCoverCredit } from '@/app/shared/types/cover'
import type { iProfile } from '@/app/features/user/profile'

export type WorkplaceRole = 'owner' | 'manager' | 'designer'

export interface iWorkplace {
  id: number
  public_id: string
  name: string
  slug: string
  photo: string | null
  cover_style: string
  cover_credit: iCoverCredit
  is_active: boolean
  invite_key: string
  created_at: string
  updated_at: string
}

export interface iWorkplaceMember {
  id: number
  public_id: string
  workplace: { id: number; name: string; slug: string }
  user: number
  profile: iProfile
  role: WorkplaceRole
  created_at: string
  updated_at: string
}

export type WebhookEvent =
  | 'form.response.created'
  | 'task.created'
  | 'task.updated'
  | 'media.created'
  | 'media.feedback.created'
  | 'workplace.member.added'

export interface iWebhook {
  id: number
  public_id: string
  workplace: number
  url: string
  events: WebhookEvent[]
  is_active: boolean
  created_at: string
  updated_at: string
}
