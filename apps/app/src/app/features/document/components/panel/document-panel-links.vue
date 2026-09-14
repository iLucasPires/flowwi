<script setup lang="ts">
defineProps<{
  outlinks: { title: string; exists: boolean; onOpen: () => void }[]
  backlinks: { id: number; title: string; excerpt: string; onOpen: () => void }[]
}>()

defineOptions({ name: 'DocumentPanelLinks' })
</script>

<template>
  <div class="flex flex-col gap-3">
    <section class="space-y-1.5">
      <div class="flex items-center justify-between px-0.5">
        <div class="flex items-center gap-1.5">
          <UIcon name="i-lucide-corner-down-left" class="size-3.5 text-muted" />
          <span class="text-xs font-semibold text-highlighted">Backlinks</span>
          <UBadge
            v-if="backlinks.length"
            :label="String(backlinks.length)"
            size="xs"
            variant="subtle"
            color="neutral"
            class="text-[10px] px-1.5 py-0 h-4"
          />
        </div>
      </div>

      <div v-if="backlinks.length" class="flex flex-col gap-1">
        <UButton
          v-for="backlink in backlinks"
          :key="backlink.id"
          block
          color="neutral"
          variant="ghost"
          class="justify-start px-2.5 py-2 text-start h-auto rounded-md group hover:bg-elevated/60 transition-colors"
          @click="backlink.onOpen"
        >
          <div class="flex items-start gap-2.5 min-w-0 w-full">
            <UIcon
              name="i-lucide-file-text"
              class="size-3.5 shrink-0 mt-0.5 text-dimmed group-hover:text-primary transition-colors"
            />

            <div class="flex flex-col min-w-0 flex-1 gap-0.5">
              <div class="flex items-center justify-between gap-1">
                <span class="text-xs font-medium text-highlighted truncate">
                  {{ backlink.title }}
                </span>
                <UIcon
                  name="i-lucide-arrow-up-right"
                  class="size-3 shrink-0 text-dimmed opacity-0 group-hover:opacity-100 transition-opacity"
                />
              </div>

              <p class="text-[11px] text-dimmed line-clamp-2 leading-relaxed font-normal">
                {{ backlink.excerpt }}
              </p>
            </div>
          </div>
        </UButton>
      </div>

      <UEmpty
        v-else
        icon="i-lucide-link-2-off"
        title="Nenhum backlink"
        description="Nenhum documento aponta para este documento."
        variant="naked"
        size="xs"
      />
    </section>

    <USeparator class="my-0.5" />

    <section class="space-y-1.5">
      <div class="flex items-center justify-between px-0.5">
        <div class="flex items-center gap-1.5">
          <UIcon name="i-lucide-arrow-up-right" class="size-3.5 text-muted" />
          <span class="text-xs font-semibold text-highlighted">Links de saída</span>
          <UBadge
            v-if="outlinks.length"
            :label="String(outlinks.length)"
            size="xs"
            variant="subtle"
            color="neutral"
            class="text-[10px] px-1.5 py-0 h-4"
          />
        </div>
      </div>

      <div v-if="outlinks.length" class="flex flex-col gap-0.5">
        <UButton
          v-for="(outlink, index) in outlinks"
          :key="index"
          block
          color="neutral"
          variant="ghost"
          class="justify-between px-2.5 py-1.5 text-start h-auto rounded-md group hover:bg-elevated/60 transition-colors"
          @click="outlink.onOpen"
        >
          <div class="flex items-center gap-2 min-w-0">
            <UIcon
              :name="outlink.exists ? 'i-lucide-file-text' : 'i-lucide-file-question'"
              class="size-3.5 shrink-0"
              :class="outlink.exists ? 'text-muted group-hover:text-primary' : 'text-dimmed'"
            />

            <span
              class="text-xs font-medium truncate"
              :class="
                outlink.exists
                  ? 'text-default group-hover:text-highlighted'
                  : 'text-dimmed line-through'
              "
            >
              {{ outlink.title }}
            </span>
          </div>

          <UIcon
            name="i-lucide-arrow-up-right"
            class="size-3 shrink-0 text-dimmed group-hover:text-default transition-colors"
          />
        </UButton>
      </div>

      <UEmpty
        v-else
        icon="i-lucide-link-2-off"
        title="Nenhum link de saída"
        description="Este documento não possui links para outros documentos."
        variant="naked"
        size="xs"
      />
    </section>
  </div>
</template>
