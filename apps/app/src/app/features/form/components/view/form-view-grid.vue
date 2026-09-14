<script setup lang="ts">
import type { tFormOut } from '@/app/features/form/schemas'
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  forms: tFormOut[]
  actions: (form: tFormOut) => DropdownMenuItem[][]
}>()

const emit = defineEmits<{
  open: [form: tFormOut]
  answers: [form: tFormOut]
  'copy-link': [form: tFormOut]
}>()
</script>

<template>
  <UPageGrid>
    <CFormCard
      v-for="form in forms"
      :key="form.id"
      :form="form"
      :actions="actions(form)"
      @open="emit('open', form)"
      @answers="emit('answers', form)"
      @copy-link="emit('copy-link', form)"
    />
  </UPageGrid>
</template>
