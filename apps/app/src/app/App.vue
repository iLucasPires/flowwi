<script setup lang="ts">
import { watch } from 'vue'
import { useUser } from '@/app/features/user'
import { useNotification } from '@/app/features/inbox'
import { useWorkplaceSync } from '@/app/features/workplace'
import { useAccentColor } from '@/app/shared/composables/accentColor'

const toaster = { expand: false }

const { isLogged } = useUser()
const notifications = useNotification()
const workplaceSync = useWorkplaceSync()

useAccentColor()

watch(
  isLogged,
  (v) => {
    if (v) {
      notifications.connect()
      workplaceSync.connect()
    } else {
      notifications.disconnect()
      workplaceSync.disconnect()
    }
  },
  { immediate: true },
)
</script>

<template>
  <UApp :toaster="toaster">
    <router-view />
  </UApp>
</template>
