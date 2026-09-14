<template>
  <div class="flex flex-col gap-8 h-full w-1/2 mx-auto py-8">
    <!-- Title -->
    <USkeleton class="h-10 w-3/4 rounded-md" />

    <!-- Description -->
    <USkeleton class="h-24 w-full rounded-xl" />

    <!-- Selects row -->
    <div class="flex gap-2">
      <USkeleton class="h-7 w-20 rounded-md" />
      <USkeleton class="h-7 w-20 rounded-md" />
      <USkeleton class="h-7 w-20 rounded-md" />
      <USkeleton class="h-7 w-20 rounded-md" />
    </div>

    <!-- Subtasks -->
    <div class="space-y-3">
      <USkeleton class="h-4 w-24 rounded" />
      <div class="space-y-2">
        <USkeleton class="h-6 w-3/5 rounded" />
        <USkeleton class="h-6 w-2/3 rounded" />
        <USkeleton class="h-6 w-1/2 rounded" />
      </div>
    </div>
  </div>
</template>
