<script setup lang="ts">
import { API_MEDIA_URLS, apiFetch } from '@/app/core/clients/api'
import type { iMediaComment, iMediaFeedback, iMediaVersion } from '@/app/features/media/types'
import { marked } from 'marked'

defineOptions({ name: 'MediaPublicPage' })

const route = useRoute()
const token = route.params.id as string

interface PublicMedia {
  id: number
  title: string
  notes: string
  is_approved: boolean
  versions: iMediaVersion[]
  comments: iMediaComment[]
  feedbacks: iMediaFeedback[]
  created_at: string
}

const media = ref<PublicMedia | null>(null)
const loading = ref(true)
const error = ref('')
const activeIndex = ref(0)
const guestName = ref('')
const commentBody = ref('')
const sending = ref(false)

const versions = computed(() => media.value?.versions ?? [])
const currentVersion = computed(() => versions.value[activeIndex.value])

const activeComments = computed(() => {
  if (!media.value) return []
  return [
    ...media.value.comments.filter((c) => !c.version),
    ...(currentVersion.value?.comments ?? []),
  ].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
})

const score = computed(() => {
  if (!media.value) return 0
  const all = [...media.value.feedbacks, ...(currentVersion.value?.feedbacks ?? [])]
  return all.filter((f) => f.decision === 1).length - all.filter((f) => f.decision === 2).length
})

async function load() {
  try {
    media.value = await apiFetch<PublicMedia>(`${API_MEDIA_URLS.LIST}/public/${token}`)
  } catch {
    error.value = 'Esta media não pôde ser encontrada ou não está disponível.'
  } finally {
    loading.value = false
  }
}

async function sendComment() {
  if (!commentBody.value.trim() || !guestName.value.trim()) return
  sending.value = true
  try {
    await apiFetch(`${API_MEDIA_URLS.LIST}/public/${token}/comment`, {
      method: 'POST',
      body: {
        content: commentBody.value,
        version: currentVersion.value?.id ?? null,
      },
    })
    commentBody.value = ''
    await load()
  } finally {
    sending.value = false
  }
}

async function sendFeedback(decision: 1 | 2) {
  await apiFetch(`${API_MEDIA_URLS.LIST}/public/${token}/feedback`, {
    method: 'POST',
    body: {
      decision,
      version: currentVersion.value?.id ?? null,
    },
  })
  await load()
}

onMounted(load)
</script>

<template>
  <UContainer class="mt-20">
    <!-- Loading -->
    <div v-if="loading" class="min-h-dvh flex items-center justify-center">
      <UIcon name="i-lucide-loader" class="size-5 animate-spin text-neutral-400" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="min-h-dvh flex flex-col items-center justify-center px-6 gap-4">
      <UIcon name="i-lucide-alert-circle" class="size-8 text-neutral-300 dark:text-neutral-600" />
      <p class="text-sm text-neutral-500 text-center max-w-xs">
        {{ error }}
      </p>
    </div>

    <!-- Media -->
    <div v-else-if="media" class="max-w-2xl mx-auto w-full">
      <!-- Image -->
      <div
        class="bg-neutral-50 dark:bg-neutral-900/50 flex items-center justify-center min-h-48 sm:min-h-80"
      >
        <template v-if="currentVersion">
          <img
            v-if="currentVersion.file"
            :key="currentVersion.id"
            :src="currentVersion.file"
            class="max-w-full max-h-[55dvh] object-contain"
          />
        </template>
        <div
          v-else
          class="flex flex-col items-center gap-2 py-10 text-neutral-300 dark:text-neutral-600"
        >
          <UIcon name="i-lucide-image-off" class="size-6" />
          <span class="text-xs">Sem versões</span>
        </div>
      </div>

      <!-- Versions -->
      <div v-if="versions.length > 1" class="flex gap-1.5 px-4 py-2.5 overflow-x-auto">
        <button
          v-for="(v, i) in versions"
          :key="v.id"
          class="size-9 shrink-0 rounded overflow-hidden outline-none transition-all"
          :class="
            activeIndex === i
              ? 'ring-2 ring-neutral-900 dark:ring-white'
              : 'ring-1 ring-neutral-200 dark:ring-neutral-700 opacity-40 hover:opacity-70'
          "
          @click="activeIndex = i"
        >
          <img v-if="v.file" :src="v.file" class="size-full object-cover" loading="lazy" />
          <div
            v-else
            class="size-full bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center"
          >
            <UIcon name="i-lucide-link" class="size-3 text-neutral-400" />
          </div>
        </button>
      </div>

      <!-- Title + feedback -->
      <div class="flex items-center justify-between gap-3 px-4 py-3">
        <div class="min-w-0">
          <h1 class="text-sm font-semibold text-neutral-900 dark:text-white truncate">
            {{ media.title || 'Media' }}
          </h1>
          <p v-if="media.notes" class="text-xs text-neutral-500 truncate mt-0.5">
            {{ media.notes }}
          </p>
        </div>
        <div class="flex items-center gap-0.5 shrink-0">
          <UButton
            icon="i-lucide-thumbs-up"
            size="xs"
            variant="ghost"
            color="neutral"
            @click="sendFeedback(1)"
          />
          <span
            class="text-xs font-medium tabular-nums min-w-4 text-center"
            :class="{
              'text-green-600 dark:text-green-400': score > 0,
              'text-red-500': score < 0,
              'text-neutral-400': score === 0,
            }"
            >{{ score }}</span
          >
          <UButton
            icon="i-lucide-thumbs-down"
            size="xs"
            variant="ghost"
            color="neutral"
            @click="sendFeedback(2)"
          />
        </div>
      </div>

      <!-- Comments -->
      <div class="px-4 py-4 space-y-3">
        <div v-for="c in activeComments" :key="c.id" class="flex gap-2.5">
          <UAvatar size="xs" :text="String(c.author)" class="mt-0.5 shrink-0" />
          <div class="min-w-0">
            <p class="text-xs text-neutral-500">
              <span class="font-medium text-neutral-900 dark:text-white">{{ `#${c.author}` }}</span>
              ·
              {{
                new Date(c.created_at).toLocaleDateString('pt-BR', {
                  day: 'numeric',
                  month: 'short',
                  hour: '2-digit',
                  minute: '2-digit',
                })
              }}
            </p>
            <div
              class="text-sm text-neutral-700 dark:text-neutral-300 mt-0.5 [&_p]:my-0"
              v-html="marked(c.content)"
            />
          </div>
        </div>
      </div>

      <!-- Write comment -->
      <div class="px-4 pb-6 pt-2 space-y-3">
        <UTextarea
          v-model="commentBody"
          :rows="4"
          :maxrows="8"
          placeholder="Escreva um comentário..."
          variant="outline"
          autoresize
          size="md"
          :ui="{ root: 'w-full' }"
          @keydown.meta.enter="sendComment"
          @keydown.ctrl.enter="sendComment"
        />
        <UButton
          label="Enviar comentário"
          icon="i-lucide-send"
          size="md"
          color="neutral"
          variant="solid"
          class="w-full bg-neutral-900 dark:bg-white text-white dark:text-black hover:bg-neutral-800 dark:hover:bg-neutral-200 justify-center"
          :loading="sending"
          :disabled="!commentBody.trim() || !guestName.trim()"
          @click="sendComment"
        />
      </div>
    </div>
  </UContainer>
</template>
