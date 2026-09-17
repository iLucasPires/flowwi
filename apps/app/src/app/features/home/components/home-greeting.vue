<script setup lang="ts">
import { useProfile } from "@/app/features/user/composables/profile";

const { profile } = useProfile();

const now = useNow({ interval: 60_000 });

const greeting = computed(() => {
  const hour = now.value.getHours();
  if (hour < 12) return "Bom dia";
  if (hour < 18) return "Boa tarde";
  return "Boa noite";
});

const emoji = computed(() => {
  const hour = now.value.getHours();
  if (hour < 6) return "🌙";
  if (hour < 12) return "☀️";
  if (hour < 18) return "🌤️";
  return "🌙";
});

const displayName = computed(() => profile.value?.first_name || profile.value?.full_name || "");

const dateLabel = computed(() =>
  now.value.toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" }),
);

const timeLabel = computed(() =>
  now.value.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
);
</script>

<template>
  <div class="text-center">
    <h1 class="text-2xl font-semibold">
      {{ greeting }}<span v-if="displayName">, {{ displayName }}</span>
    </h1>
    <p class="text-sm text-dimmed mt-1.5 flex items-center justify-center gap-1.5 capitalize">
      <span>{{ emoji }}</span>
      <span>{{ dateLabel }}, {{ timeLabel }}</span>
    </p>
  </div>
</template>
