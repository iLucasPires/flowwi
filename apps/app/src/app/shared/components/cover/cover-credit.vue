<script setup lang="ts">
import type { iCoverCredit } from '@/app/shared/types/cover'
defineProps<{
  credit?: iCoverCredit
}>()

defineOptions({ name: 'CoverCredit' })
</script>

<template>
  <span
    v-if="credit?.source === 'unsplash' && credit.author_name"
    class="text-[10px] text-white/90 drop-shadow-sm"
  >
    Foto de
    <a
      :href="credit.author_url"
      target="_blank"
      rel="noopener noreferrer"
      class="underline underline-offset-2 hover:text-white"
    >
      {{ credit.author_name }}
    </a>
    no
    <a
      :href="credit.photo_url"
      target="_blank"
      rel="noopener noreferrer"
      class="underline underline-offset-2 hover:text-white"
    >
      Unsplash
    </a>
  </span>
</template>
