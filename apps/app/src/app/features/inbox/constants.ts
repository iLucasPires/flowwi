/** Matches apps.domains.inbox.models.InboxType.MEMBER_JOIN_REQUESTED on the backend. */
export const INBOX_TYPE_MEMBER_JOIN_REQUESTED = 7

export const cInboxTypeItems: Record<number, { icon: string; color: string; label: string }> = {
  1: { icon: 'i-lucide-monitor', color: 'text-neutral-400', label: 'Sistema' },
  2: { icon: 'i-lucide-shopping-bag', color: 'text-amber-500', label: 'Pedido' },
  3: { icon: 'i-lucide-message-circle', color: 'text-green-500', label: 'Mensagem' },
  4: { icon: 'i-lucide-check-circle-2', color: 'text-yellow-500', label: 'Tarefa' },
  5: { icon: 'i-lucide-message-square', color: 'text-emerald-500', label: 'Comentário' },
  6: { icon: 'i-lucide-user-plus', color: 'text-blue-500', label: 'Novo membro' },
  7: { icon: 'i-lucide-user-round-plus', color: 'text-amber-500', label: 'Pedido de entrada' },
}

export function getInboxTypeMeta(type: number) {
  return cInboxTypeItems[type] ?? cInboxTypeItems[1]!
}

/** Which body component renders an inbox item's content, keyed by type — falls
 * back to a plain message for any type with no dedicated body. */
export const cInboxBodyComponents: Record<number, string> = {
  [INBOX_TYPE_MEMBER_JOIN_REQUESTED]: 'CInboxBodyJoinRequest',
}

export function getInboxBodyComponent(type: number) {
  return cInboxBodyComponents[type] ?? 'CInboxBodyDefault'
}
