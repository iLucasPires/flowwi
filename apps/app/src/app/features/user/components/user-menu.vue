<script setup lang="ts">
import { useProfile } from '@/app/features/user/composables/profile'
import { useUserMutations } from '@/app/features/user/composables/user'
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
import { coverBackgroundStyle } from '@/app/shared/utils/cover'
import type { DropdownMenuItem } from '@nuxt/ui'

defineProps<{
  collapsed?: boolean
}>()

const router = useRouter()
const overlay = useOverlay()
const { profile } = useProfile()

/** The menu header shows the uploaded cover, falling back to the picked style/URL. */
const coverBackground = computed(() =>
  coverBackgroundStyle(profile.value?.cover, profile.value?.cover_style),
)

const { logoutUser } = useUserMutations()
const { clearCurrent: clearWorkplace } = useWorkplace()

const logout = async () => {
  await logoutUser()
  await router.push('/account/login')
}

const leaveWorkplace = () => {
  clearWorkplace()
  router.push('/account/setup/workplace/select')
}

function openSettings() {
  const component = resolveComponent('CSettingsDialog')

  if (typeof component === 'string') {
    return
  }

  const modal = overlay.create(component, {
    props: { open: true },
  })

  modal.open()
}

const items = computed<DropdownMenuItem[][]>(() => [
  [
    {
      slot: 'account',
      disabled: true,
    },
  ],
  [
    {
      label: 'Configurações',
      icon: 'i-lucide-settings',
      onSelect: openSettings,
    },
  ],
  [
    {
      label: 'Sair do workspace',
      icon: 'i-lucide-workflow',
      onSelect: leaveWorkplace,
    },
    {
      label: 'Sair do sistema',
      icon: 'i-lucide-log-out',
      onSelect: logout,
    },
  ],
])
</script>

<template>
  <UDropdownMenu
    :items="items"
    size="xs"
    :content="{
      align: 'end',
      side: 'bottom',
      sideOffset: 8,
    }"
    :ui="{
      content: 'w-72',
    }"
  >
    <UButton
      as="button"
      size="xs"
      color="neutral"
      variant="ghost"
      :block="!collapsed"
      :square="collapsed"
      :trailing-icon="collapsed ? undefined : 'i-lucide-chevron-down'"
      :label="collapsed ? undefined : profile?.username"
      :avatar="{
        src: `${profile?.photo}`,
        alt: `profile-${profile?.full_name}`,
        loading: 'lazy',
        size: 'xs',
        class: collapsed ? '' : 'me-2',
        icon: 'i-lucide-image',
      }"
    />

    <template #account>
      <div
        class="h-14 w-full bg-muted bg-cover bg-center rounded-md"
        :style="coverBackground"
      />
    </template>
  </UDropdownMenu>
</template>
