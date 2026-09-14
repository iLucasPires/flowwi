<script setup lang="ts">
import type { iCoverCredit } from '@/app/shared/types/cover'
import type { iUnsplashPhoto } from '@/app/shared/types/unsplash'
import type { TabsItem } from '@nuxt/ui'

const emit = defineEmits<{
  selectFile: [file: File]
  selectStyle: [style: string, credit: iCoverCredit]
}>()

const GALLERY: { label: string; value: string }[] = [
  { label: 'Coral', value: '#f5765b' },
  { label: 'Âmbar', value: '#d4a017' },
  { label: 'Azul', value: '#3b82f6' },
  { label: 'Marfim', value: '#f5f0e6' },
  { label: 'Ciano', value: '#5fd4d6' },
  { label: 'Rosa', value: '#ec4899' },
  { label: 'Verde', value: '#22c55e' },
  { label: 'Violeta', value: '#8b5cf6' },
  { label: 'Névoa', value: 'linear-gradient(135deg, #a8c0ff, #f5f0e6)' },
  { label: 'Pôr do sol', value: 'linear-gradient(135deg, #ff9966, #ff5e62)' },
  { label: 'Aurora', value: 'linear-gradient(135deg, #7f7fd5, #86a8e7, #91eae4)' },
  { label: 'Oceano', value: 'linear-gradient(135deg, #2193b0, #6dd5ed)' },
]

const tabItems: TabsItem[] = [
  { value: 'gallery', label: 'Galeria', icon: 'i-lucide-palette', slot: 'gallery' },
  { value: 'unsplash', label: 'Unsplash', icon: 'i-lucide-image', slot: 'unsplash' },
  { value: 'upload', label: 'Upload', icon: 'i-lucide-upload', slot: 'upload' },
  { value: 'link', label: 'Link', icon: 'i-lucide-link', slot: 'link' },
]

const activeTab = ref('gallery')
const linkUrl = ref('')
const uploadFile = ref<File | null>(null)

watch(uploadFile, (file) => {
  if (file) {
    emit('selectFile', file)
    uploadFile.value = null
  }
})

function selectGallery(value: string) {
  emit('selectStyle', value, null)
}

function selectUnsplash(photo: iUnsplashPhoto) {
  emit('selectStyle', photo.cover_url, photo.credit)
}

function applyLink() {
  const url = linkUrl.value.trim()

  if (!url) return

  emit('selectStyle', url, null)
  linkUrl.value = ''
}

defineOptions({ name: 'CoverPicker' })
</script>

<template>
  <div class="w-96 p-2 flex flex-col gap-1">
    <UTabs
      v-model="activeTab"
      :items="tabItems"
      size="xs"
      variant="pill"
      color="neutral"
      class="w-full"
    >
      <template #gallery>
        <div class="grid grid-cols-4 gap-2 pt-2">
          <UButton
            v-for="swatch in GALLERY"
            :key="swatch.label"
            class="h-11 rounded-lg ring-1 ring-default hover:ring-2 hover:ring-primary transition-all p-0 overflow-hidden"
            :style="{ background: swatch.value }"
            :title="swatch.label"
            @click="selectGallery(swatch.value)"
          />
        </div>
      </template>

      <template #unsplash>
        <!-- Mounted only when the tab opens, so the API quota is untouched otherwise. -->
        <CCoverUnsplashGrid v-if="activeTab === 'unsplash'" @select="selectUnsplash" />
      </template>

      <template #upload>
        <div class="pt-2">
          <UFileUpload
            v-model="uploadFile"
            accept="image/*"
            label="Escolha uma imagem"
            description="PNG, JPG ou GIF (máx. 5MB)"
            :preview="false"
            class="min-h-28"
          />
        </div>
      </template>

      <template #link>
        <div class="pt-2 flex items-center gap-2">
          <UInput
            v-model="linkUrl"
            placeholder="Cole o link da imagem..."
            icon="i-lucide-link"
            size="xs"
            variant="subtle"
            class="flex-1"
            @keydown.enter="applyLink"
          />
          <UButton
            label="Aplicar"
            size="xs"
            color="primary"
            :disabled="!linkUrl.trim()"
            @click="applyLink"
          />
        </div>
      </template>
    </UTabs>
  </div>
</template>
