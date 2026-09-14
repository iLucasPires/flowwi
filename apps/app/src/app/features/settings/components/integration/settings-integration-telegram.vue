<script setup lang="ts">
const toast = useToast()
const connected = ref(false)
const connecting = ref(false)

async function connectTelegram() {
  connecting.value = true
  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    connected.value = true
    toast.add({ title: 'Telegram conectado com sucesso', color: 'success' })
  } catch {
    toast.add({ title: 'Erro ao conectar Telegram', color: 'error' })
  } finally {
    connecting.value = false
  }
}

async function disconnect() {
  try {
    connected.value = false
    toast.add({ title: 'Telegram desconectado', color: 'success' })
  } catch {
    toast.add({ title: 'Erro ao desconectar', color: 'error' })
  }
}
</script>

<template>
  <main class="flex flex-col gap-4 h-full p-1">
    <header class="flex justify-between items-center">
      <UPageFeature
        title="Telegram"
        description="Conecte sua conta do Telegram para vincular arquivos e pastas ao Media do workspace."
        icon="i-logos-telegram"
      />
      <UButton
        size="sm"
        class="font-bold rounded-full"
        :label="connected ? 'Desconectar' : 'Conectar'"
        :icon="connected ? 'i-lucide-unplug' : 'i-lucide-plug'"
        :color="connected ? 'error' : 'primary'"
        :variant="connected ? 'subtle' : undefined"
        :loading="connecting"
        @click="connected ? disconnect() : connectTelegram()"
      />
    </header>
  </main>
</template>
