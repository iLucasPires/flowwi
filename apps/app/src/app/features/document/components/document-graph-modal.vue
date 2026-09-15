<script setup lang="ts">
const open = defineModel<boolean>('open', { required: true })

defineProps<{
  nodes: {
    id: number
    left: string
    top: string
    size: string
    fill: string
    ring: string
    color: string
    title: string
    onOpen: () => void
  }[]
  edges: { x1: number; y1: number; x2: number; y2: number; stroke: string; w: number }[]
}>()

const emit = defineEmits<{
  close: []
}>()

function pick(onOpen: () => void) {
  onOpen()
  emit('close')
}

defineOptions({ name: 'DocumentGraphModal' })
</script>

<template>
  <UModal
    v-model:open="open"
    :ui="{ content: 'sm:max-w-3xl' }"
    title="Grafo de conexões"
    :description="`${nodes.length} nós · ${edges.length} conexões`"
  >
    <template #body>
      <div class="h-[520px] relative overflow-hidden">
        <svg viewBox="0 0 820 500" class="absolute inset-0 size-full">
          <line
            v-for="(e, i) in edges"
            :key="i"
            :x1="e.x1"
            :y1="e.y1"
            :x2="e.x2"
            :y2="e.y2"
            :stroke="e.stroke"
            :stroke-width="e.w"
          />
        </svg>
        <div
          v-for="n in nodes"
          :key="n.id"
          class="absolute flex flex-col items-center gap-1.5 cursor-pointer w-[120px] -translate-x-1/2 -translate-y-1/2"
          :style="{ left: n.left, top: n.top }"
          @click="pick(n.onOpen)"
        >
          <span
            class="rounded-full border-[1.5px]"
            :style="{ width: n.size, height: n.size, backgroundColor: n.fill, borderColor: n.ring }"
          />
          <span class="text-[10.5px] text-center leading-tight" :style="{ color: n.color }">{{
            n.title
          }}</span>
        </div>
      </div>
    </template>
  </UModal>
</template>
