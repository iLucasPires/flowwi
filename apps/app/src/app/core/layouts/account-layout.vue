<template>
  <div class="w-full h-screen relative">
    <!-- Logo Icon -->
    <UIcon
      name="i-lucide-tree-palm"
      class="text-2xl absolute top-5 left-5 z-10"
      aria-label="logo"
      aria-hidden="true"
    />

    <!-- Centered Router View Container -->
    <div class="absolute inset-0 flex items-center justify-center">
      <RouterView />
    </div>
  </div>
</template>
