<script setup lang="ts">
import type { iWorkplaceMember } from '@/app/features/workplace/types'
const props = defineProps<{
  member: iWorkplaceMember | number | null
}>()

function getMemberPhoto() {
  const member = props.member

  if (typeof member !== 'object') {
    return ''
  }

  const profile = member?.profile

  if (typeof profile !== 'object') {
    return ''
  }

  return profile.photo || ''
}

function getMemberName() {
  const member = props.member

  if (typeof member !== 'object') {
    return ''
  }

  const profile = member?.profile

  if (typeof profile !== 'object') {
    return ''
  }

  return profile.username || ''
}
</script>

<template>
  <UAvatar :src="getMemberPhoto()" :alt="getMemberName()" />
</template>
