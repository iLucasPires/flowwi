<script setup lang="ts">
defineProps<{
  outline: { text: string; pad: string; weight: number; color: string }[]
}>()

defineOptions({ name: 'DocumentPanelOutline' })
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-center justify-between px-0.5">
      <div class="flex items-center gap-1.5">
        <UIcon name="i-lucide-list" class="size-3.5 text-muted" />
        <span class="text-xs font-semibold text-highlighted">Sumário</span>
        <UBadge
          v-if="outline.length"
          :label="String(outline.length)"
          size="xs"
          variant="subtle"
          color="neutral"
          class="text-[10px] px-1.5 py-0 h-4"
        />
      </div>
    </div>

    <USeparator class="my-0.5" />

    <div v-if="outline.length" class="flex flex-col gap-0.5 max-h-80 overflow-y-auto">
      <UButton
        v-for="(item, index) in outline"
        :key="index"
        block
        color="neutral"
        variant="ghost"
        class="justify-start text-start px-2 py-1.5 text-xs rounded-md group hover:bg-elevated/60 transition-colors h-auto"
        :style="{ paddingLeft: item.pad || '8px' }"
      >
        <span
          class="truncate leading-snug group-hover:text-highlighted transition-colors"
          :style="{ fontWeight: item.weight, color: item.color || undefined }"
        >
          {{ item.text }}
        </span>
      </UButton>
    </div>

    <UEmpty
      v-else
      icon="i-lucide-list-collapse"
      title="Sem títulos"
      description="Adicione títulos (H1, H2, H3) ao documento para visualizá-los no sumário."
      variant="naked"
      size="xs"
    />
  </div>
</template>
