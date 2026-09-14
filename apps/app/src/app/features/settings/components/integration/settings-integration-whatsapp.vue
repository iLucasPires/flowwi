<script setup lang="ts">
const toast = useToast()
const connected = ref(false)
const phoneNumber = ref('')
const connecting = ref(false)

async function connectWhatsapp() {
  connecting.value = true
  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    connected.value = true
    toast.add({
      title: 'WhatsApp conectado com sucesso',
      color: 'success',
    })
  } catch {
    toast.add({
      title: 'Erro ao conectar WhatsApp',
      color: 'error',
    })
  } finally {
    connecting.value = false
  }
}

async function disconnect() {
  try {
    connected.value = false
    phoneNumber.value = ''
    toast.add({
      title: 'WhatsApp desconectado',
      color: 'success',
    })
  } catch {
    toast.add({
      title: 'Erro ao desconectar',
      color: 'error',
    })
  }
}
</script>

<template>
  <main class="flex flex-col gap-4 h-full p-1">
    <header class="flex justify-between items-center">
      <UPageFeature
        title="WhatsApp"
        description="Receba notificações do workspace diretamente no seu WhatsApp."
        icon="i-logos-whatsapp-icon"
      />
      <UButton
        size="sm"
        class="font-bold rounded-full"
        :label="connected ? 'Desconectar' : 'Conectar'"
        :icon="connected ? 'i-lucide-unplug' : 'i-lucide-plug'"
        :color="connected ? 'error' : 'primary'"
        :variant="connected ? 'subtle' : undefined"
        :loading="!connected && connecting"
        :disabled="!connected && !phoneNumber"
        @click="connected ? disconnect() : connectWhatsapp()"
      />
    </header>
  </main>
</template>
