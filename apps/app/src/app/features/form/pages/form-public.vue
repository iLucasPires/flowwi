<script setup lang="ts">
defineOptions({ name: 'FormPublicPage' })

const route = useRoute()
const publicId = route.params.id as string
</script>

<template>
  <CFormPublicShell :public-id="publicId" />
</template>
