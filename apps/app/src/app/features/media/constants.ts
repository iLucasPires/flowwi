export const cMediaTypeItems = [
  {
    label: 'Imagem',
    value: 1,
    icon: 'i-lucide-image',
  },
  {
    label: 'Vídeo',
    value: 2,
    icon: 'i-lucide-film',
  },
  {
    label: 'Documento',
    value: 3,
    icon: 'i-lucide-file-type',
  },
  {
    label: 'Arte',
    value: 4,
    icon: 'i-lucide-palette',
  },
]

export const cMediaVersionItems = [
  {
    label: 'Rascunho',
    value: '1',
    icon: 'i-lucide-pencil',
    color: 'text-neutral-400',
    badgeColor: 'neutral',
  },
  {
    label: 'Revisão',
    value: '2',
    icon: 'i-lucide-eye',
    color: 'text-yellow-400',
    badgeColor: 'warning',
  },
  {
    label: 'Final',
    value: '3',
    icon: 'i-lucide-check-circle',
    color: 'text-green-400',
    badgeColor: 'success',
  },
]

export function getMediaVersionNumberColor(n: number): string {
  if (n <= 1) return 'info'
  if (n === 2) return 'primary'
  if (n === 3) return 'warning'
  if (n === 4) return 'error'
  return 'neutral'
}
