<script setup lang="ts">
import { useAccentColor } from '@/app/shared/composables/accentColor'
const colorMode = useColorMode({ emitAuto: true })
const { accentColor, colorItems } = useAccentColor()

const themeItems = [
  { label: 'Sistema', value: 'auto' as const, icon: 'i-lucide-monitor', preview: 'split' as const },
  { label: 'Claro', value: 'light' as const, icon: 'i-lucide-sun', preview: 'light' as const },
  { label: 'Escuro', value: 'dark' as const, icon: 'i-lucide-moon', preview: 'dark' as const },
]

const selectedTheme = computed({
  get: () => colorMode.store.value,
  set: (value) => (colorMode.store.value = value),
})

const mockupColors = {
  light: { bg: '#ffffff', sidebar: '#f4f4f5', line: '#d4d4d8' },
  dark: { bg: '#0a0a0a', sidebar: '#171717', line: '#404040' },
}

function swatchStyle(color: string) {
  // Raw Tailwind "neutral" is renamed internally by Nuxt UI to avoid
  // colliding with the semantic "neutral" color, so it has no CSS variable.
  if (color === 'neutral') {
    return { backgroundColor: 'var(--ui-color-neutral-500)' }
  }
  return { backgroundColor: `var(--color-${color}-500)` }
}
</script>

<template>
  <div class="space-y-6">
    <UPageCard variant="ghost" title="Tema" description="Selecione o tema de aparência do app.">
      <div class="grid grid-cols-3 gap-3">
        <button
          v-for="item in themeItems"
          :key="item.value"
          type="button"
          class="rounded-lg border-2 p-2 text-left transition-colors cursor-pointer"
          :class="
            selectedTheme === item.value ? 'border-primary' : 'border-default hover:border-accented'
          "
          @click="selectedTheme = item.value"
        >
          <div class="h-16 rounded-md overflow-hidden flex mb-3">
            <template v-if="item.preview === 'split'">
              <div
                v-for="mode in ['light', 'dark'] as const"
                :key="mode"
                class="flex-1 flex"
                :style="{ backgroundColor: mockupColors[mode].bg }"
              >
                <div class="w-2 h-full" :style="{ backgroundColor: mockupColors[mode].sidebar }" />
                <div class="flex-1 p-1.5 space-y-1">
                  <div
                    class="h-1 rounded-full w-3/4"
                    :style="{ backgroundColor: mockupColors[mode].line }"
                  />
                  <div
                    class="h-1 rounded-full w-1/2"
                    :style="{ backgroundColor: mockupColors[mode].line }"
                  />
                </div>
              </div>
            </template>
            <template v-else>
              <div
                class="w-3 h-full"
                :style="{ backgroundColor: mockupColors[item.preview].sidebar }"
              />
              <div
                class="flex-1 p-2 space-y-1.5"
                :style="{ backgroundColor: mockupColors[item.preview].bg }"
              >
                <div
                  class="h-1.5 rounded-full w-3/4"
                  :style="{ backgroundColor: mockupColors[item.preview].line }"
                />
                <div
                  class="h-1.5 rounded-full w-1/2"
                  :style="{ backgroundColor: mockupColors[item.preview].line }"
                />
                <div
                  class="h-1.5 rounded-full w-2/3"
                  :style="{ backgroundColor: mockupColors[item.preview].line }"
                />
              </div>
            </template>
          </div>

          <div class="flex items-center gap-1.5">
            <UIcon :name="item.icon" class="size-3.5 shrink-0 text-dimmed" />
            <CTextBlock size="sm" weight="medium" :text="item.label" />
          </div>
        </button>
      </div>
    </UPageCard>

    <UPageCard
      variant="ghost"
      title="Cor de destaque"
      description="Escolha a cor usada em botões e elementos de destaque."
    >
      <div class="flex flex-wrap gap-3">
        <UTooltip v-for="color in colorItems" :key="color.value" :text="color.label">
          <button
            type="button"
            class="relative size-8 rounded-full transition-transform hover:scale-110 cursor-pointer"
            :style="swatchStyle(color.value)"
            :aria-label="color.label"
            @click="accentColor = color.value"
          >
            <UIcon
              v-if="accentColor === color.value"
              name="i-lucide-check"
              class="absolute inset-0 m-auto size-4 text-white"
            />
          </button>
        </UTooltip>
      </div>
    </UPageCard>
  </div>
</template>
