import type { iCoverCredit } from '@/app/shared/types/cover'

export interface iProfile {
  id: number
  photo: string | null
  cover: string | null
  cover_style: string
  cover_credit: iCoverCredit
  username: string
  email: string
  full_name: string
  first_name: string
  last_name: string
}
