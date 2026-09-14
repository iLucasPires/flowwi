<script setup lang="ts">
import { useSticky } from '@/app/features/sticky/composables/sticky'
import type { StickyVisibility, iSticky } from '@/app/features/sticky/types'
import { useUser } from '@/app/features/user/composables/user'
import { getTextColor } from '@/app/shared/utils/color'
const props = defineProps<{ sticky: iSticky; autofocus?: boolean }>()
const emit = defineEmits<{ remove: [] }>()

const { updateSticky } = useSticky()
const { user } = useUser()

const text = ref(props.sticky.text ?? '')
const saving = ref(false)
const lastSavedText = ref(text.value)

let textSaveSeq = 0
async function saveNow() {
  const valueToSave = text.value
  if (valueToSave === lastSavedText.value) return

  const seq = ++textSaveSeq
  saving.value = true

  try {
    await updateSticky({
      id: props.sticky.id,
      data: { text: valueToSave },
    })

    if (seq === textSaveSeq) lastSavedText.value = valueToSave
  } finally {
    if (seq === textSaveSeq) saving.value = false
  }
}

const color = ref(props.sticky.color)
const lastSavedColor = ref(color.value)

const textColor = computed(() => getTextColor(color.value))

const canEditVisibility = computed(() => {
  const userId = user.value?.id
  if (!userId) return false
  return userId === props.sticky.created_by
})

const visibility = ref(props.sticky.visibility)
const lastSavedVisibility = ref(visibility.value)
watch(
  () => props.sticky.visibility,
  (v) => {
    visibility.value = v
    lastSavedVisibility.value = v
  },
)

const visibilityIcon = computed(() =>
  visibility.value === 'private' ? 'i-lucide-lock' : 'i-lucide-users',
)
const visibilityTooltip = computed(() =>
  visibility.value === 'private' ? 'Privado (só você)' : 'Workplace (todos do workplace)',
)

let visibilitySaveSeq = 0
const savingVisibility = ref(false)
async function onVisibilityChange(next: StickyVisibility) {
  if (!canEditVisibility.value || next === visibility.value) return

  const previous = visibility.value
  visibility.value = next

  const seq = ++visibilitySaveSeq
  savingVisibility.value = true

  try {
    await updateSticky({
      id: props.sticky.id,
      data: { visibility: next },
    })

    if (seq === visibilitySaveSeq) lastSavedVisibility.value = next
  } catch {
    if (seq === visibilitySaveSeq) visibility.value = previous
  } finally {
    if (seq === visibilitySaveSeq) savingVisibility.value = false
  }
}

let colorSaveSeq = 0
const savingColor = ref(false)

const updateColor = useDebounceFn(async () => {
  const newColor = color.value
  if (newColor === lastSavedColor.value) return

  const seq = ++colorSaveSeq
  savingColor.value = true

  try {
    await updateSticky({
      id: props.sticky.id,
      data: { color: newColor },
    })

    if (seq === colorSaveSeq) lastSavedColor.value = newColor
  } finally {
    if (seq === colorSaveSeq) savingColor.value = false
  }
}, 800)

watch(color, () => {
  updateColor()
})

const debouncedSave = useDebounceFn(saveNow, 900)
</script>

<template>
  <div
    class="rounded-xl p-4 flex flex-col justify-between h-64 transition-colors duration-200 ease-out"
    :style="{ backgroundColor: color, color: textColor }"
  >
    <div class="flex-1 overflow-y-auto">
      <CRichTextEditor
        v-model="text"
        placeholder="Click to type here"
        :autofocus="autofocus"
        @update:model-value="debouncedSave"
        @blur="saveNow"
      />
    </div>

    <!-- FOOTER TOOLBAR -->
    <div class="flex items-center justify-between mt-3 opacity-70">
      <div class="flex items-center gap-3">
        <UPopover>
          <UButton
            size="xs"
            variant="ghost"
            icon="i-lucide-palette"
            :style="{ color: textColor }"
          />
          <template #content>
            <UColorPicker v-model="color" class="p-2" />
          </template>
        </UPopover>

        <UPopover>
          <UTooltip :text="visibilityTooltip">
            <UButton
              size="xs"
              variant="ghost"
              :icon="savingVisibility ? 'i-lucide-loader-circle' : visibilityIcon"
              :style="{ color: textColor }"
              :class="savingVisibility ? 'animate-spin' : ''"
            />
          </UTooltip>

          <template #content>
            <div class="p-3">
              <CStickyPanelShare
                :visibility="visibility"
                :can-edit-visibility="canEditVisibility"
                @update:visibility="onVisibilityChange"
              />
            </div>
          </template>
        </UPopover>

        <CMemberOwnerIndicator :user-id="sticky.created_by" compact />
      </div>

      <UButton
        icon="i-lucide-trash-2"
        size="xs"
        variant="ghost"
        @click="emit('remove')"
        :style="{ color: textColor }"
      />
    </div>
  </div>
</template>
