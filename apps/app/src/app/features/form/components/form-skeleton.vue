<script setup lang="ts">
defineOptions({ name: 'FormSkeleton' })
defineProps<{ count?: number }>()
</script>

<template>
  <UPageGrid>
    <USkeleton v-for="i in count ?? 12" :key="i" class="h-40 rounded-xl" />
  </UPageGrid>
</template>
