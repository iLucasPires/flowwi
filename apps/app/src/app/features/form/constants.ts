import type { tFormBlockType } from '@/app/features/form/types'

export const cFormPublishedItems = [
  { label: 'Publicado', value: true, icon: 'i-lucide-globe', color: 'text-green-400' },
  { label: 'Rascunho', value: false, icon: 'i-lucide-file-edit', color: 'text-neutral-400' },
]

export const cFormBlockTypeItems = [
  { label: 'Texto', value: 'text', icon: 'i-lucide-type', color: 'text-blue-400' },
  { label: 'Email', value: 'email', icon: 'i-lucide-mail', color: 'text-cyan-400' },
  { label: 'Número', value: 'number', icon: 'i-lucide-hash', color: 'text-orange-400' },
  { label: 'Hora', value: 'time', icon: 'i-lucide-clock', color: 'text-yellow-400' },
  { label: 'Data', value: 'date', icon: 'i-lucide-calendar', color: 'text-green-400' },
  { label: 'Select', value: 'select', icon: 'i-lucide-list', color: 'text-purple-400' },
  { label: 'Escolha', value: 'choice', icon: 'i-lucide-check-circle', color: 'text-pink-400' },
  { label: 'Arquivo', value: 'file', icon: 'i-lucide-paperclip', color: 'text-neutral-400' },
  { label: 'Texto livre', value: 'content', icon: 'i-lucide-text', color: 'text-neutral-400' },
]

export const cFormBlockOperationItems = [
  { label: 'Igual a', value: 'eq', icon: 'i-lucide-equal' },
  { label: 'Diferente de', value: 'neq', icon: 'i-lucide-ban' },
  { label: 'Maior que', value: 'gt', icon: 'i-lucide-chevron-right' },
  { label: 'Maior ou igual', value: 'gte', icon: 'i-lucide-chevrons-right' },
  { label: 'Menor que', value: 'lt', icon: 'i-lucide-chevron-left' },
  { label: 'Menor ou igual', value: 'lte', icon: 'i-lucide-chevrons-left' },
  { label: 'Existe', value: 'exists', icon: 'i-lucide-eye' },
  { label: 'Não existe', value: 'not_exists', icon: 'i-lucide-eye-off' },
]

export const cFormChoiceKeys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

export const cFormDefaultBlockConfigs: Partial<Record<tFormBlockType, Record<string, unknown>>> = {
  select: {
    options: [],
    multiple: false,
  },
  choice: {
    options: [],
    multiple: false,
  },
  text: {
    min_length: 0,
    max_length: 255,
    long: false,
  },
  email: {
    min_length: 0,
    max_length: 255,
  },
  number: {
    min: 0,
    max: 100,
    step: 1,
  },
  file: {
    multiple: false,
  },
  date: {},
  time: {},
  content: {
    node: null,
  },
}
