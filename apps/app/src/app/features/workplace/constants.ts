import type { WorkplaceRole } from '@/app/features/workplace/types'

export const cWorkplaceRoleBadgeColor: Record<
  WorkplaceRole,
  'primary' | 'success' | 'warning' | 'info' | 'error' | 'neutral'
> = {
  owner: 'primary',
  manager: 'neutral',
  designer: 'neutral',
}
