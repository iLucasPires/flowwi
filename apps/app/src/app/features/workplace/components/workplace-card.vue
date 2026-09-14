<script setup lang="ts">
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
import type { iWorkplace } from '@/app/features/workplace/types'
import { getAvatar } from '@/app/shared/utils/avatar'
import { coverBackgroundStyle, coverImageSrc } from '@/app/shared/utils/cover'
const props = defineProps<{ workplace: iWorkplace }>()
const emit = defineEmits<{ enter: [] }>()

const overlay = useOverlay()
const router = useRouter()
const { setCurrent } = useWorkplace()

function openGeneralSettings() {
  const component = resolveComponent('CWorkplaceEditDialog')

  if (typeof component === 'object') {
    const modal = overlay.create(component, {
      props: { workplaceId: props.workplace.id },
    })

    modal.open()
  }
}

async function openWorkplaceSection(section: 'members' | 'webhooks') {
  await setCurrent(props.workplace)
  router.push(`/dashboard/workplaces/${section}`)
}

function workplaceAvatar(name: string) {
  return getAvatar(name)
}

const coverImage = computed(() => coverImageSrc(props.workplace.photo, props.workplace.cover_style))
const coverBackground = computed(() =>
  coverImage.value ? undefined : coverBackgroundStyle(null, props.workplace.cover_style),
)
</script>

<template>
  <div
    class="group rounded-lg overflow-hidden bg-elevated/40 transition-colors hover:bg-elevated/70"
  >
    <div
      class="block aspect-video bg-accented/40 overflow-hidden cursor-pointer relative"
      @click="emit('enter')"
    >
      <img
        v-if="coverImage"
        :src="coverImage"
        class="size-full object-cover transition-transform duration-200 group-hover:scale-105"
      />
      <div v-else-if="coverBackground" class="size-full" :style="coverBackground" />
      <div v-else class="size-full flex items-center justify-center">
        <UAvatar :src="workplaceAvatar(workplace.name)" size="3xl" class="size-20 rounded-2xl" />
      </div>

      <!-- Overlay status -->
      <div class="absolute top-3 right-3">
        <UBadge
          v-if="!workplace.is_active"
          label="inativo"
          variant="subtle"
          color="neutral"
          size="xs"
          class="capitalize backdrop-blur-sm bg-accented/60"
        />
      </div>
    </div>

    <div class="p-4 sm:p-5">
      <div class="flex items-center gap-1.5 mb-1">
        <UIcon name="i-lucide-layout-grid" class="size-3.5 shrink-0 text-muted" />
        <span class="text-[10px] text-dimmed uppercase tracking-wide">
          Workspace • ID {{ workplace.id }}
        </span>
      </div>

      <p class="text-sm font-medium leading-snug truncate">{{ workplace.name }}</p>

      <div class="flex items-center gap-2 mt-4">
        <UButton
          label="Entrar"
          icon="i-lucide-log-in"
          color="primary"
          variant="solid"
          size="sm"
          class="flex-1"
          @click="emit('enter')"
        />

        <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <UButton
            label="Geral"
            icon="i-lucide-settings"
            size="sm"
            variant="ghost"
            color="neutral"
            @click="openGeneralSettings"
          />
          <UButton
            label="Membros"
            icon="i-lucide-users"
            size="sm"
            variant="ghost"
            color="neutral"
            @click="openWorkplaceSection('members')"
          />
          <UButton
            label="Webhooks"
            icon="i-lucide-webhook"
            size="sm"
            variant="ghost"
            color="neutral"
            @click="openWorkplaceSection('webhooks')"
          />
        </div>
      </div>
    </div>
  </div>
</template>
