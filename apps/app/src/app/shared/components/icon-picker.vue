<script setup lang="ts">
import { gitHubEmojis } from '@tiptap/extension-emoji'

const model = defineModel<string>({ default: '' })

const props = defineProps<{
  color?: string
  size?: string
  iconClass?: string
  buttonClass?: string
  fallback?: string
  /** When set and no icon/emoji is picked yet, shows a "+ label" ghost pill instead of the fallback icon. */
  emptyLabel?: string
}>()

const ICONS = [
  'i-lucide-circle-dashed',
  'i-lucide-circle-stop',
  'i-lucide-circle-check',
  'i-lucide-circle-x',
  'i-lucide-circle',
  'i-lucide-eye',
  'i-lucide-clock',
  'i-lucide-hourglass',
  'i-lucide-timer',
  'i-lucide-flag',
  'i-lucide-flame',
  'i-lucide-star',
  'i-lucide-zap',
  'i-lucide-rocket',
  'i-lucide-target',
  'i-lucide-palette',
  'i-lucide-send',
  'i-lucide-video',
  'i-lucide-file-text',
  'i-lucide-box',
  'i-lucide-package',
  'i-lucide-clipboard-list',
  'i-lucide-clipboard-check',
  'i-lucide-list-checks',
  'i-lucide-calendar',
  'i-lucide-calendar-check',
  'i-lucide-bug',
  'i-lucide-wrench',
  'i-lucide-hammer',
  'i-lucide-code',
  'i-lucide-layers',
  'i-lucide-layout',
  'i-lucide-pen-tool',
  'i-lucide-image',
  'i-lucide-camera',
  'i-lucide-megaphone',
  'i-lucide-mail',
  'i-lucide-message-circle',
  'i-lucide-users',
  'i-lucide-user',
  'i-lucide-briefcase',
  'i-lucide-shopping-cart',
  'i-lucide-dollar-sign',
  'i-lucide-trending-up',
  'i-lucide-bar-chart',
  'i-lucide-lightbulb',
  'i-lucide-heart',
  'i-lucide-thumbs-up',
  'i-lucide-alert-triangle',
  'i-lucide-shield',
] as const

const EMOJIS = gitHubEmojis.filter((emoji) => !emoji.name.startsWith('regional_indicator_'))

const open = ref(false)
const tab = ref<'icon' | 'emoji'>('icon')
const query = ref('')

/** Icons are always `i-<collection>-<name>`; anything else picked is a literal emoji character. */
const isEmoji = computed(() => !!model.value && !model.value.startsWith('i-'))
const isEmpty = computed(() => !model.value)

watch(open, (value) => {
  if (value) query.value = ''
})

function iconLabel(icon: string) {
  return icon.replace(/^i-[a-z]+-/, '').replace(/-/g, ' ')
}

const filteredIcons = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return ICONS
  return ICONS.filter((icon) => iconLabel(icon).includes(q))
})

const filteredEmojis = computed(() => {
  const q = query.value.trim().toLowerCase()
  const list = q
    ? EMOJIS.filter(
        (e) =>
          e.name.includes(q) ||
          e.shortcodes.some((s) => s.includes(q)) ||
          e.tags.some((t) => t.includes(q)),
      )
    : EMOJIS
  return list.slice(0, 200)
})

function selectIcon(icon: string) {
  model.value = icon
  open.value = false
}

function selectEmoji(emoji?: string) {
  if (!emoji) return
  model.value = emoji
  open.value = false
}

function clearIcon() {
  model.value = ''
  open.value = false
}
</script>

<template>
  <UPopover v-model:open="open">
    <UButton
      v-if="emptyLabel && isEmpty"
      icon="i-lucide-smile-plus"
      :label="emptyLabel"
      size="xs"
      variant="ghost"
      color="neutral"
      :class="buttonClass"
    />
    <UButton
      v-else
      size="xs"
      variant="subtle"
      color="neutral"
      :class="buttonClass"
    >
      <CIconOrEmoji
        :value="model"
        :fallback="fallback ?? 'i-lucide-shapes'"
        :class="iconClass ?? 'size-2 text-sm'"
      />
    </UButton>

    <template #content>
      <div class="w-72 p-2 space-y-2">
        <UInput
          v-model="query"
          :placeholder="tab === 'icon' ? 'Buscar ícone...' : 'Buscar emoji...'"
          icon="i-lucide-search"
          variant="subtle"
          size="xs"
          autofocus
          class="w-full"
        />

        <div class="flex items-center gap-0.5 rounded-lg bg-elevated p-0.5">
          <UButton
            size="xs"
            color="neutral"
            :variant="tab === 'icon' ? 'solid' : 'ghost'"
            class="flex-1 justify-center text-xs"
            @click="tab = 'icon'"
          >
            Ícones
          </UButton>
          <UButton
            size="xs"
            color="neutral"
            :variant="tab === 'emoji' ? 'solid' : 'ghost'"
            class="flex-1 justify-center text-xs"
            @click="tab = 'emoji'"
          >
            Emoji
          </UButton>
        </div>

        <div v-if="tab === 'icon'" class="grid grid-cols-8 gap-1 max-h-56 overflow-y-auto">
          <button
            v-for="icon in filteredIcons"
            :key="icon"
            type="button"
            :title="iconLabel(icon)"
            class="flex items-center justify-center size-7 rounded-md hover:bg-accented/60 transition-colors"
            :class="{ 'bg-accented': model === icon }"
            @click="selectIcon(icon)"
          >
            <UIcon :name="icon" class="size-4" />
          </button>

          <p v-if="!filteredIcons.length" class="col-span-8 text-xs text-dimmed text-center py-4">
            Nenhum ícone encontrado.
          </p>
        </div>

        <div v-else class="grid grid-cols-8 gap-1 max-h-56 overflow-y-auto">
          <button
            v-for="emojiItem in filteredEmojis"
            :key="emojiItem.name"
            type="button"
            :title="emojiItem.name"
            class="flex items-center justify-center size-7 rounded-md hover:bg-accented/60 transition-colors"
            :class="{ 'bg-accented': model === emojiItem.emoji }"
            @click="selectEmoji(emojiItem.emoji)"
          >
            <span class="text-base leading-none">{{ emojiItem.emoji }}</span>
          </button>

          <p v-if="!filteredEmojis.length" class="col-span-8 text-xs text-dimmed text-center py-4">
            Nenhum emoji encontrado.
          </p>
        </div>

        <UButton
          v-if="model"
          label="Remover ícone"
          icon="i-lucide-x"
          size="xs"
          variant="ghost"
          color="neutral"
          block
          class="justify-start text-dimmed hover:text-error transition-colors"
          @click="clearIcon"
        />
      </div>
    </template>
  </UPopover>
</template>
