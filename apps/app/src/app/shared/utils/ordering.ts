import { generateKeyBetween } from 'fractional-indexing'

/**
 * Resolve colisões e garante que os limites passados para o fractional-indexing
 * são estritamente ordenados (before < after). Se houver colisão (ex: itens com
 * mesma position "Zz"), busca o próximo elemento estritamente maior.
 */
function safeGenerateKeyBetween(items: { position: string }[], insertIdx: number): string {
  const before = items[insertIdx - 1]?.position ?? null
  let after = items[insertIdx]?.position ?? null

  if (before !== null && after !== null && before >= after) {
    after = null
    for (let i = insertIdx; i < items.length; i++) {
      const item = items[i]
      if (item && item.position > before) {
        after = item.position
        break
      }
    }
  }

  try {
    return generateKeyBetween(before, after)
  } catch {
    // Fallback de segurança se a lib ainda falhar
    return generateKeyBetween(before ?? null, null)
  }
}

/**
 * Calcula uma nova position (fractional index) para reordenação dentro do mesmo grupo.
 */
export function calcReorderPosition(
  items: { id: number; position: string }[],
  initialIndex: number,
  finalIndex: number,
): string {
  const without = [...items]
  without.splice(initialIndex, 1)

  return safeGenerateKeyBetween(without, finalIndex)
}

/**
 * Calcula position para inserir um item em uma lista onde ele NÃO existe (cross-group).
 */
export function calcInsertPosition(
  items: { id: number; position: string }[],
  targetIndex: number,
): string {
  return safeGenerateKeyBetween(items, targetIndex)
}
