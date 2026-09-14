<script setup lang="ts">
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
defineOptions({ name: 'WorkplaceSettingsPage' })

const overlay = useOverlay()
const { workplace } = useWorkplace()
const router = useRouter()

onMounted(async () => {
  if (workplace.value) {
    const component = resolveComponent('CWorkplaceEditDialog')

    if (typeof component !== 'object') {
      router.push('/dashboard/workplaces')
      return
    }

    const modal = overlay.create(component, {
      props: { workplaceId: workplace.value.id, open: true },
    })

    await modal.open()
  }
  router.push('/dashboard/workplaces')
})
</script>

<template>
  <div class="h-screen w-full flex items-center justify-center">
    <UIcon name="i-lucide-loader-2" class="size-8 animate-spin text-neutral-400" />
  </div>
</template>
