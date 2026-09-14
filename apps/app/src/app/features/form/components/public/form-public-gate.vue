<script setup lang="ts">
defineProps<{
  mode: 'auth' | 'identity'
  publicId: string
}>()

const emit = defineEmits<{ submit: [email: string, phone: string] }>()

const email = ref('')
const phone = ref('')

function onSubmit() {
  if (!email.value && !phone.value) return
  emit('submit', email.value, phone.value)
}
</script>

<template>
  <!-- Auth gate -->
  <div v-if="mode === 'auth'" class="flex-1 flex flex-col items-center justify-center px-6 gap-6">
    <UAvatar icon="i-lucide-lock" color="warning" variant="subtle" />
    <div class="text-center space-y-2">
      <h2 class="text-2xl font-bold">Acesso restrito</h2>
      <p class="text-sm text-muted max-w-sm">
        Este formulário requer que você esteja logado para responder.
      </p>
    </div>
    <UButton
      label="Fazer login"
      icon="i-lucide-log-in"
      size="lg"
      :href="`/account/login?redirect=/public/form/${publicId}`"
    />
  </div>

  <!-- Identity gate -->
  <div v-else class="flex-1 flex flex-col items-center justify-center px-6 gap-6">
    <UAvatar icon="i-lucide-user-circle" color="info" variant="subtle" />
    <div class="text-center space-y-2 max-w-sm">
      <h2 class="text-xl font-bold">Identificação</h2>
      <p class="text-sm text-muted">Informe seu e-mail ou telefone para continuar.</p>
    </div>
    <div class="w-full max-w-xs flex flex-col gap-3">
      <UInput
        v-model="email"
        placeholder="E-mail"
        type="email"
        icon="i-lucide-mail"
        size="lg"
        variant="subtle"
      />
      <USeparator label="ou" />
      <UInput
        v-model="phone"
        placeholder="Telefone"
        type="tel"
        icon="i-lucide-phone"
        size="lg"
        variant="subtle"
      />
      <UButton
        label="Continuar"
        icon="i-lucide-arrow-right"
        trailing
        size="lg"
        block
        :disabled="!email && !phone"
        @click="onSubmit"
      />
    </div>
  </div>
</template>
