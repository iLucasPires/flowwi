<script setup lang="ts">
import type { iDocumentSelectionAnchor } from '@/app/features/document/types'
defineOptions({ name: 'DocumentCommentComposer' })

const props = defineProps<{
  selection: iDocumentSelectionAnchor
  submitting?: boolean
}>()

const emit = defineEmits<{
  'update:open': [boolean]
  submit: [{ quote: string; content: string }]
}>()

/** Minimum space needed above the selection to place the trigger there instead of below. */
const TOOLBAR_CLEARANCE = 48
const GAP = 8
const EDGE_PADDING = 12

const open = ref(false)
const quote = ref('')
const text = ref('')

const placeAbove = computed(() => props.selection.top > TOOLBAR_CLEARANCE)

/** Centered on the selection, clamped so the floating trigger never spills past the
 * viewport edge — the popover content itself doesn't need this, Floating UI's own
 * collision handling (`collisionPadding`, defaulted by `UPopover`) takes care of it. */
const clampedCenterX = computed(() => {
  if (typeof window === 'undefined') return props.selection.centerX

  return Math.min(Math.max(props.selection.centerX, EDGE_PADDING), window.innerWidth - EDGE_PADDING)
})

const triggerStyle = computed(() => ({
  left: `${clampedCenterX.value}px`,
  top: placeAbove.value ? `${props.selection.top - GAP}px` : `${props.selection.bottom + GAP}px`,
  transform: placeAbove.value ? 'translate(-50%, -100%)' : 'translate(-50%, 0)',
}))

// `UPopover` positions its content off a real trigger element by default — this
// composer has none (the trigger button below is a plain floating affordance, not a
// Reka-managed anchor). `reference` is Nuxt UI/Floating UI's documented escape hatch
// for exactly this: anchor to a virtual element (anything with
// `getBoundingClientRect`) instead. Content is portaled to `<body>` by default too,
// so it's immune to any ancestor stacking context the editor layout might create.
const virtualReference = computed(() => {
  const { top, bottom, centerX } = props.selection
  return {
    getBoundingClientRect: () => ({
      x: centerX,
      y: top,
      top,
      bottom,
      left: centerX,
      right: centerX,
      width: 0,
      height: bottom - top,
    }),
  }
})

function setOpen(value: boolean) {
  open.value = value
  emit('update:open', value)
  if (value) {
    quote.value = props.selection.text
    text.value = ''
  }
}

async function submit() {
  if (!text.value.trim()) return
  emit('submit', { quote: quote.value, content: text.value.trim() })
  setOpen(false)
}
</script>

<template>
  <UButton
    v-if="!open"
    label="Comentar"
    icon="i-lucide-message-square-plus"
    size="xs"
    variant="subtle"
    color="neutral"
    class="fixed z-40 backdrop-blur-md bg-default/90 hover:bg-default text-highlighted shadow-lg rounded-full origin-bottom"
    :style="triggerStyle"
    @mousedown.prevent="setOpen(true)"
  />

  <UPopover
    :open="open"
    :reference="virtualReference"
    :content="{ side: placeAbove ? 'top' : 'bottom', align: 'center', sideOffset: 6 }"
    @update:open="setOpen"
  >
    <template #content>
      <div class="w-72 p-2.5 flex flex-col gap-2">
        <span
          class="text-[11px] text-primary bg-primary/10 rounded px-1.5 py-0.5 self-start max-w-full truncate"
        >
          "{{ quote }}"
        </span>
        <UTextarea
          v-model="text"
          :rows="2"
          autoresize
          autofocus
          placeholder="O que precisa ajustar aqui?"
          variant="subtle"
          size="xs"
          class="w-full"
          @keydown.enter.exact.prevent="submit"
        />
        <div class="flex justify-end gap-1.5">
          <UButton
            label="Cancelar"
            variant="ghost"
            color="neutral"
            size="xs"
            @click="setOpen(false)"
          />
          <UButton
            label="Comentar"
            size="xs"
            :disabled="!text.trim()"
            :loading="submitting"
            @click="submit"
          />
        </div>
      </div>
    </template>
  </UPopover>
</template>
