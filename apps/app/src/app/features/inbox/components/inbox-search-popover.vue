<script setup lang="ts">
const search = defineModel<string>({ default: '' })
</script>

<template>
  <UPopover size="xs" :content="{ align: 'end', sideOffset: 8 }">
    <UButton icon="i-lucide-search" variant="ghost" color="neutral" size="xs" />

    <template #content>
      <UInput
        v-model="search"
        placeholder="Buscar..."
        icon="i-lucide-search"
        variant="subtle"
        size="xs"
        autofocus
        class="m-2 w-56"
      />
    </template>
  </UPopover>
</template>
