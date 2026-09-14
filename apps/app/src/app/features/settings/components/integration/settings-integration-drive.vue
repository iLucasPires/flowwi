<script setup lang="ts">
import { useGoogleDrive } from '@/app/shared/composables/drive/googleDrive'
const { connected, connecting, connect, disconnect } = useGoogleDrive()
</script>

<template>
  <main class="flex flex-col gap-4 h-full p-1">
    <header class="flex justify-between items-center">
      <UPageFeature
        title="Google"
        description="Conecte sua conta do Google Drive para vincular arquivos e pastas ao Media do workspace."
        icon="i-logos-google-drive"
      />
      <UButton
        size="sm"
        class="font-bold rounded-full"
        :label="connected ? 'Desconectar' : 'Conectar'"
        :icon="connected ? 'i-lucide-unplug' : 'i-lucide-plug'"
        :color="connected ? 'error' : 'primary'"
        :variant="connected ? 'subtle' : undefined"
        :loading="connecting"
        @click="connected ? disconnect() : connect()"
      />
    </header>
  </main>
</template>
