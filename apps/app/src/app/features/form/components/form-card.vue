<script setup lang="ts">
import type { tFormOut } from '@/app/features/form/schemas'
import { coverBackgroundStyle, coverImageSrc } from '@/app/shared/utils/cover'
import { formatTimeAgo } from '@vueuse/core'
import type { DropdownMenuItem } from '@nuxt/ui'

defineOptions({ name: 'FormCard' })

const props = defineProps<{
  form: tFormOut
  actions: DropdownMenuItem[][]
}>()

const emit = defineEmits<{ open: [] }>()

const coverImage = computed(() => coverImageSrc(props.form.cover_image, props.form.cover_style))
const coverBackground = computed(() =>
  coverImage.value ? undefined : coverBackgroundStyle(null, props.form.cover_style),
)

const responsesLabel = computed(() => {
  const count = props.form.responses_count
  return `${count} ${count === 1 ? 'resposta' : 'respostas'}`
})
</script>

<template>
  <UCard
    variant="subtle"
    class="cursor-pointer"
    :ui="{ body: 'flex flex-col gap-3', footer: 'flex items-center justify-between' }"
    @click="emit('open')"
  >
    <div
      v-if="coverImage || coverBackground"
      class="aspect-video w-full overflow-hidden rounded-lg"
    >
      <img v-if="coverImage" :src="coverImage" alt="" class="size-full object-cover" />
      <div v-else class="size-full" :style="coverBackground" />
    </div>

    <div class="flex items-start justify-between gap-2">
      <div class="flex items-center gap-2 min-w-0">
        <CIconOrEmoji
          :value="form.icon"
          fallback="i-lucide-file-text"
          class="size-4 text-dimmed shrink-0"
        />
        <CTextBlock weight="bold" size="base" :text="form.title || 'Sem título'" class="line-clamp-1" />
      </div>
      <UDropdownMenu :items="actions" size="xs">
        <UButton
          icon="i-lucide-more-horizontal"
          variant="ghost"
          color="neutral"
          size="xs"
          square
          @click.stop
        />
      </UDropdownMenu>
    </div>

    <CTextBlock
      v-if="form.description"
      size="sm"
      :text="form.description"
      class="line-clamp-2 text-muted"
    />

    <template #footer>
      <div class="flex items-center gap-2">
        <UBadge
          :color="form.is_published ? 'success' : 'neutral'"
          :label="form.is_published ? 'Publicado' : 'Rascunho'"
          size="xs"
          variant="subtle"
        />
        <UBadge
          icon="i-lucide-inbox"
          :label="responsesLabel"
          color="neutral"
          variant="subtle"
          size="xs"
        />
      </div>

      <CTextBlock size="xs" class="text-dimmed" :text="formatTimeAgo(new Date(form.created_at))" />
    </template>
  </UCard>
</template>
