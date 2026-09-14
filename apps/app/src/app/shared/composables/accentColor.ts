import { watch } from 'vue'
import { useLocalStorage } from '@vueuse/core'

export const cAccentColorItems = [
  { label: 'Neutro', value: 'neutral' },
  { label: 'Vermelho', value: 'red' },
  { label: 'Laranja', value: 'orange' },
  { label: 'Âmbar', value: 'amber' },
  { label: 'Verde', value: 'green' },
  { label: 'Esmeralda', value: 'emerald' },
  { label: 'Ciano', value: 'cyan' },
  { label: 'Azul', value: 'blue' },
  { label: 'Índigo', value: 'indigo' },
  { label: 'Violeta', value: 'violet' },
  { label: 'Rosa', value: 'pink' },
]

export const cColorShades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
const shades = cColorShades

const accentColor = useLocalStorage<string>('accent-color', 'neutral')

function applyAccentColor(color: string) {
  const root = document.documentElement
  for (const shade of shades) {
    const property = `--ui-color-primary-${shade}`
    // "neutral" is the build-time default (see vite.config.ts) — clearing the
    // override restores it, since Nuxt UI internally renames the raw Tailwind
    // "neutral" palette to avoid colliding with the semantic "neutral" color.
    if (color === 'neutral') {
      root.style.removeProperty(property)
    } else {
      root.style.setProperty(property, `var(--color-${color}-${shade})`)
    }
  }
}

applyAccentColor(accentColor.value)

export function useAccentColor() {
  watch(accentColor, (value) => applyAccentColor(value))

  return {
    accentColor,
    colorItems: cAccentColorItems,
  }
}
