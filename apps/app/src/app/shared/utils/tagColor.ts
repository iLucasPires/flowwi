/** Soft tinted {bg, fg} pairs for icon tiles/chips, picked deterministically from a
 * seed string so the same item always gets the same color. Values work on both
 * light and dark surfaces since the background is a low-opacity tint. */
const TAG_COLORS = [
  { bg: 'rgba(239, 68, 68, 0.12)', fg: '#ef4444' },
  { bg: 'rgba(249, 115, 22, 0.12)', fg: '#f97316' },
  { bg: 'rgba(234, 179, 8, 0.14)', fg: '#eab308' },
  { bg: 'rgba(34, 197, 94, 0.12)', fg: '#22c55e' },
  { bg: 'rgba(20, 184, 166, 0.12)', fg: '#14b8a6' },
  { bg: 'rgba(6, 182, 212, 0.12)', fg: '#06b6d4' },
  { bg: 'rgba(59, 130, 246, 0.12)', fg: '#3b82f6' },
  { bg: 'rgba(99, 102, 241, 0.12)', fg: '#6366f1' },
  { bg: 'rgba(168, 85, 247, 0.12)', fg: '#a855f7' },
  { bg: 'rgba(236, 72, 153, 0.12)', fg: '#ec4899' },
]

export function getTagColor(seed: string) {
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    hash = (hash << 5) - hash + seed.charCodeAt(i)
    hash |= 0
  }
  return TAG_COLORS[Math.abs(hash) % TAG_COLORS.length]
}
