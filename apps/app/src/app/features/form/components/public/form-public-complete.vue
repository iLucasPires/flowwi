<script setup lang="ts">
defineOptions({ name: 'FormPublicComplete' })
</script>

<template>
  <div class="flex-1 flex flex-col items-center justify-center px-6 gap-8">
    <div class="flex flex-col items-center gap-6 max-w-sm text-center">
      <div class="size-12 rounded-full flex items-center justify-center bg-neutral-100 dark:bg-neutral-900">
        <UIcon name="i-lucide-check" class="size-5 text-neutral-900 dark:text-white" />
      </div>
      <div class="flex flex-col gap-2">
        <h2 class="ft-page-title text-2xl font-semibold tracking-tight text-neutral-900 dark:text-white">
          Tudo certo!
        </h2>
        <p class="text-sm text-neutral-400 dark:text-neutral-500 leading-relaxed">
          Suas respostas foram enviadas com sucesso. Obrigado pelo seu tempo.
        </p>
      </div>
    </div>
  </div>
</template>
