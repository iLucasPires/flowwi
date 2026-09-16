<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
}>();
</script>

<template>
  <UCard
    variant="subtle"
    :ui="{
      root: 'size-full flex flex-col overflow-hidden',
      body: 'flex-1 overflow-auto p-1',
      header: 'flex justify-between items-center p-2',
      description: 'flex items-center gap-2',
    }"
  >
    <template #header>
      <div class="flex items-center gap-2 min-w-0">
        <slot name="leading" />
        <h2 class="text-sm font-medium truncate" v-text="title" />
      </div>
      <div v-if="$slots.actions" class="flex items-center gap-2 shrink-0">
        <slot name="actions" />
      </div>
    </template>

    <slot />
  </UCard>
</template>
