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

/** Minimum space needed above the selection to place the toolbar there instead of below. */
const TOOLBAR_CLEARANCE = 48
const GAP = 8
const EDGE_PADDING = 12

const open = ref(false)
const quote = ref('')
const text = ref('')
const panelRef = useTemplateRef('panelRef')

const placeAbove = computed(() => props.selection.top > TOOLBAR_CLEARANCE)

/** Centered on the selection, clamped so the toolbar never spills past the viewport edge. */
const clampedCenterX = computed(() => {
  if (typeof window === 'undefined') return props.selection.centerX

  return Math.min(Math.max(props.selection.centerX, EDGE_PADDING), window.innerWidth - EDGE_PADDING)
})

// Both the trigger button and the open panel anchor from the same point — the panel
// just grows into a bigger box from wherever the button would've sat, so switching
// between them never jumps.
const anchorStyle = computed(() => ({
  left: `${clampedCenterX.value}px`,
  top: placeAbove.value ? `${props.selection.top - GAP}px` : `${props.selection.bottom + GAP}px`,
  transform: placeAbove.value ? 'translate(-50%, -100%)' : 'translate(-50%, 0)',
}))

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

// A `UPopover` here fought with its own Floating-UI positioning against this
// composer's `fixed`, selection-anchored trigger — the popover closed itself the
// instant it opened. This panel positions and dismisses itself instead: same
// coordinates as the trigger, closed on an outside click or Escape.
onClickOutside(panelRef, () => open.value && setOpen(false))

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && open.value) setOpen(false)
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
    :style="anchorStyle"
    @mousedown.prevent="setOpen(true)"
  />

  <Transition
    enter-active-class="transition duration-150 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-100 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <div
      v-if="open"
      ref="panelRef"
      class="fixed z-40 w-72 p-2.5 flex flex-col gap-2 rounded-lg bg-default border border-default shadow-lg origin-bottom"
      :style="anchorStyle"
      @keydown="onKeydown"
    >
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
  </Transition>
</template>
