<script setup lang="ts">
import { useProfile, useProfileMutations } from '@/app/features/user/composables/profile'
import type { iCoverUpdate } from '@/app/shared/types/cover'
const toast = useToast()
const { profile } = useProfile()
const { updateProfile } = useProfileMutations()

const firstName = ref(profile.value?.first_name || '')
const lastName = ref(profile.value?.last_name || '')
const uploadingPhoto = ref(false)

const previewUrl = computed(() => profile.value?.photo || undefined)
const coverUrl = computed(() => profile.value?.cover || undefined)
const coverStyle = computed(() => profile.value?.cover_style || '')
const coverCredit = computed(() => profile.value?.cover_credit ?? null)

watchDebounced(firstName, (value) => updateProfile({ first_name: value }), { debounce: 800 })
watchDebounced(lastName, (value) => updateProfile({ last_name: value }), { debounce: 800 })

async function onPhotoChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingPhoto.value = true
  try {
    const formData = new FormData()
    formData.append('photo', file)

    await updateProfile(formData)

    toast.add({
      title: 'Foto atualizada',
      color: 'success',
    })
  } catch {
    toast.add({
      title: 'Erro ao enviar foto',
      color: 'error',
    })
  } finally {
    uploadingPhoto.value = false
  }
}

async function saveCover(update: iCoverUpdate) {
  try {
    if (update && 'file' in update) {
      const formData = new FormData()
      formData.append('cover', update.file)
      formData.append('cover_style', '')

      await updateProfile(formData)
    } else if (update && 'style' in update) {
      await updateProfile({ cover: null, cover_style: update.style, cover_credit: update.credit })
    } else {
      await updateProfile({ cover: null, cover_style: '', cover_credit: null })
    }

    toast.add({
      title: 'Capa atualizada',
      color: 'success',
    })
  } catch {
    toast.add({
      title: 'Erro ao atualizar capa',
      color: 'error',
    })
  }
}
</script>

<template>
  <UPageCard variant="ghost" title="profile" :ui="{ root: '', header: 'relative w-full' }">
    <div class="relative">
      <CCoverBanner
        :src="coverUrl"
        :style-value="coverStyle"
        :credit="coverCredit"
        @select-file="saveCover({ file: $event })"
        @select-style="(style, credit) => saveCover({ style, credit })"
        @remove="saveCover(null)"
      />
      <div class="absolute -bottom-7 left-6">
        <CSettingsGeneralProfilePhotoUpload :src="previewUrl" :loading="uploadingPhoto" @change="onPhotoChange" />
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-6">
      <UFormField label="Primeiro nome" size="xs">
        <UInput
          v-model="firstName"
          class="w-full"
          variant="subtle"
          placeholder="Seu nome"
          size="xs"
        />
      </UFormField>
      <UFormField label="Segundo nome" size="xs">
        <UInput
          v-model="lastName"
          class="w-full"
          variant="subtle"
          placeholder="Seu sobrenome"
          size="xs"
        />
      </UFormField>
    </div>
  </UPageCard>
</template>
