<script setup lang="ts">
defineOptions({ name: "HomePage" });
</script>

<template>
  <CDashboardContent title="Home">
    <div class="max-w-6xl mx-auto flex flex-col gap-8 py-6 px-4 sm:px-6">
      <CHomeGreeting />
      <CHomeQuicklinks />
      <CHomeRecents />
    </div>
  </CDashboardContent>
</template>
