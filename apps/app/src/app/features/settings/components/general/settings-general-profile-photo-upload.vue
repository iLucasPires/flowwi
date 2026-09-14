<script setup lang="ts">
defineProps<{
  src?: string
  loading?: boolean
}>()

const emit = defineEmits<{
  change: [event: Event]
}>()

const fileInput = useTemplateRef('fileInput')
</script>

<template>
  <div class="relative">
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      class="hidden"
      @change="emit('change', $event)"
    />
    <div class="relative group cursor-pointer" @click="fileInput?.click()">
      <UAvatar
        :src="src"
        class="size-24 ring-4 ring-white dark:ring-neutral-900"
        icon="i-lucide-user"
        size="3xl"
      />
      <div
        class="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-full"
      >
        <UIcon
          :name="loading ? 'i-lucide-loader-2' : 'i-lucide-camera'"
          class="text-white size-5"
          :class="{ 'animate-spin': loading }"
        />
      </div>
    </div>
  </div>
</template>
