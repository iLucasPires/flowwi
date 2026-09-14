import type { iWorkplaceMember } from '@/app/features/workplace/types'

export interface iTag {
  id: number
  name: string
  color: string
  workplace: number
}

export type TaskStatusCategory = 'todo' | 'in_progress' | 'done' | 'cancelled'

export interface iTaskStatus {
  id: number
  name: string
  color: string
  icon: string
  category: TaskStatusCategory
  position: string
  workplace: number
}

export interface iTaskType {
  id: number
  name: string
  color: string
  icon: string
  position: string
  workplace: number
}

export interface iSub {
  id: number
  public_id: string
  task: number
  title: string
  is_done: boolean
  position: string
  assignee: number | null
  created_at: string
  updated_at: string
}

export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface iTask {
  id: number
  public_id: string
  workplace: number | null
  title: string
  description: string
  type: number | null
  status: number | null
  priority: TaskPriority
  origin: string
  deadline: string | null
  completed_at: string | null
  created_by: number | null
  assignees: iWorkplaceMember[]
  tags: iTag[]
  subs?: iSub[]
  position: string
  created_at: string
  updated_at: string
}
