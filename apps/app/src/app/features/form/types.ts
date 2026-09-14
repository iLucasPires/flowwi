export type tFormBlockType =
  | 'text'
  | 'email'
  | 'number'
  | 'time'
  | 'date'
  | 'file'
  | 'select'
  | 'choice'
  | 'content'

export type tFormConditionOperator =
  | 'eq'
  | 'neq'
  | 'gt'
  | 'gte'
  | 'lt'
  | 'lte'
  | 'exists'
  | 'not_exists'

export interface iFormBlockTypeMeta {
  label: string
  icon: string
  color: string
}

export type tFormBlockTypesMap = Record<string, iFormBlockTypeMeta>

export interface iFormBlockCondition {
  client_id: string
  operator: tFormConditionOperator
  value?: unknown
}

export interface iFormBlockDraft {
  key: string
  title: string
  type: tFormBlockType
  required: boolean
  config: Record<string, unknown>
  col_span: number
  col_start: number
  condition: iFormBlockCondition | Record<string, never>
}

export interface iFormBlockOption {
  label: string
  value: string | number
}

export interface iFormPageDraft {
  key: string
  title: string
  description: string
  order: number
  blocks: iFormBlockDraft[]
}
