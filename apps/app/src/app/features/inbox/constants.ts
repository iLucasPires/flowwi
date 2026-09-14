export const cInboxTypeItems: Record<number, { icon: string; color: string; label: string }> = {
  1: { icon: 'i-lucide-monitor', color: 'text-neutral-400', label: 'Sistema' },
  2: { icon: 'i-lucide-shopping-bag', color: 'text-amber-500', label: 'Pedido' },
  3: { icon: 'i-lucide-message-circle', color: 'text-green-500', label: 'Mensagem' },
  4: { icon: 'i-lucide-check-circle-2', color: 'text-yellow-500', label: 'Tarefa' },
  5: { icon: 'i-lucide-message-square', color: 'text-emerald-500', label: 'Comentário' },
  6: { icon: 'i-lucide-user-plus', color: 'text-blue-500', label: 'Novo membro' },
}

export function getInboxTypeMeta(type: number) {
  return cInboxTypeItems[type] ?? cInboxTypeItems[1]!
}
