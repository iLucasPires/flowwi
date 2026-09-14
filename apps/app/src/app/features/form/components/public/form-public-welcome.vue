<script setup lang="ts">
import { useFormTheme } from '@/app/features/form/composables/formTheme'
import type { iCoverCredit } from '@/app/shared/types/cover'
import { coverBackgroundStyle, coverImageSrc } from '@/app/shared/utils/cover'
defineOptions({ name: 'FormPublicWelcome' })

const props = defineProps<{
  title: string
  description?: string
  coverImage?: string | null
  coverStyle?: string
  coverCredit?: iCoverCredit
}>()

const emit = defineEmits<{ start: [] }>()

const coverImage = computed(() => coverImageSrc(props.coverImage, props.coverStyle))
const coverBackground = computed(() =>
  coverImage.value ? undefined : coverBackgroundStyle(null, props.coverStyle),
)

const theme = useFormTheme()
// Only shrink to the theme's size once a theme is actually set — otherwise this keeps its
// original prominent "xl" default.
const startSize = computed(() => theme?.value?.input_size ?? 'xl')
const hasAccentTheme = computed(() => !!theme?.value && theme.value.accent_color !== 'neutral')
</script>

<template>
  <div class="ft-welcome flex-1 flex flex-col items-center justify-center px-6">
    <div class="w-full max-w-xl flex flex-col gap-8">
      <!-- Cover image -->
      <div v-if="coverImage || coverBackground" class="w-full">
        <img
          v-if="coverImage"
          :src="coverImage"
          alt=""
          class="w-full max-h-48 object-cover rounded"
        />
        <div v-else class="w-full h-48 rounded" :style="coverBackground" />
        <CCoverCredit :credit="coverCredit" class="text-xs text-neutral-400 mt-1" />
      </div>

      <!-- Title & description -->
      <div class="flex flex-col gap-3">
        <h1 class="ft-welcome-title text-3xl font-bold tracking-tight text-neutral-900 dark:text-white">
          {{ title }}
        </h1>
        <p v-if="description" class="text-[15px] text-neutral-500 dark:text-neutral-400 leading-relaxed">
          {{ description }}
        </p>
      </div>

      <!-- Start button: Tally style -->
      <div>
        <button
          class="ft-input px-6 py-2.5 font-medium bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 border-neutral-900! hover:opacity-90 transition-opacity"
          :class="hasAccentTheme ? 'bg-[var(--ui-primary)]! text-white! border-[var(--ui-primary)]!' : ''"
          @click="emit('start')"
        >
          Iniciar
        </button>
      </div>
    </div>
  </div>
</template>
