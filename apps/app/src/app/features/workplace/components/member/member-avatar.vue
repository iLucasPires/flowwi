<script setup lang="ts">
import type { iWorkplaceMember } from '@/app/features/workplace/types'
import { getAvatar } from '@/app/shared/utils/avatar'

const props = defineProps<{
  member: iWorkplaceMember | number | null
  size?: string
}>()

const profile = computed(() => {
  const member = props.member
  return typeof member === 'object' ? member?.profile : null
})

const name = computed(() => profile.value?.full_name || profile.value?.username || '')

const src = computed(() => {
  if (!profile.value) return ''
  return profile.value.photo || getAvatar(profile.value.username)
})
</script>

<template>
  <UAvatar :src="src" :alt="name" :size="size" />
</template>
