<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = defineModel<boolean>('open', { required: true })

const activeTab = ref('profile')

const tabs: Record<string, ReturnType<typeof resolveComponent>> = {
  profile: resolveComponent('CSettingsGeneralProfile'),
  appearance: resolveComponent('CSettingsGeneralAppearance'),
  notifications: resolveComponent('CSettingsGeneralNotifications'),
  workspace: resolveComponent('CSettingsWorkplace'),
  members: resolveComponent('CSettingsWorkplaceMembers'),
  trash: resolveComponent('CTrashPanel'),
  taskStatuses: resolveComponent('CSettingsWorkplaceStatuses'),
  taskTypes: resolveComponent('CSettingsWorkplaceTypes'),
  documentTypes: resolveComponent('CSettingsWorkplaceDocumentTypes'),
  drive: resolveComponent('CSettingsIntegrationDrive'),
  telegram: resolveComponent('CSettingsIntegrationTelegram'),
  whatsapp: resolveComponent('CSettingsIntegrationWhatsapp'),
}

const navItems = computed<NavigationMenuItem[][]>(() => [
  [
    { label: 'Geral', type: 'label' },
    {
      label: 'Perfil',
      icon: 'i-lucide-user',
      onSelect: () => (activeTab.value = 'profile'),
      active: activeTab.value === 'profile',
    },
    {
      label: 'Aparência',
      icon: 'i-lucide-palette',
      onSelect: () => (activeTab.value = 'appearance'),
      active: activeTab.value === 'appearance',
    },
    {
      label: 'Notificações',
      icon: 'i-lucide-bell',
      onSelect: () => (activeTab.value = 'notifications'),
      active: activeTab.value === 'notifications',
    },
  ],
  [
    { label: 'Workspace', type: 'label' },
    {
      label: 'Geral',
      icon: 'i-lucide-building-2',
      onSelect: () => (activeTab.value = 'workspace'),
      active: activeTab.value === 'workspace',
    },
    {
      label: 'Membros',
      icon: 'i-lucide-users',
      onSelect: () => (activeTab.value = 'members'),
      active: activeTab.value === 'members',
    },
    {
      label: 'Lixeira',
      icon: 'i-lucide-trash-2',
      onSelect: () => (activeTab.value = 'trash'),
      active: activeTab.value === 'trash',
    },
  ],
  [
    { label: 'Tarefa', type: 'label' },
    {
      label: 'Status',
      icon: 'i-lucide-circle-dashed',
      onSelect: () => (activeTab.value = 'taskStatuses'),
      active: activeTab.value === 'taskStatuses',
    },
    {
      label: 'Tipos',
      icon: 'i-lucide-shapes',
      onSelect: () => (activeTab.value = 'taskTypes'),
      active: activeTab.value === 'taskTypes',
    },
  ],
  [
    { label: 'Documento', type: 'label' },
    {
      label: 'Tipos',
      icon: 'i-lucide-tags',
      onSelect: () => (activeTab.value = 'documentTypes'),
      active: activeTab.value === 'documentTypes',
    },
  ],
  [
    { label: 'Integrações', type: 'label' },
    {
      label: 'Google Drive',
      icon: 'i-lucide-hard-drive',
      onSelect: () => (activeTab.value = 'drive'),
      active: activeTab.value === 'drive',
    },
    {
      label: 'Telegram',
      icon: 'i-lucide-send',
      onSelect: () => (activeTab.value = 'telegram'),
      active: activeTab.value === 'telegram',
    },
    {
      label: 'WhatsApp',
      icon: 'i-lucide-message-circle',
      onSelect: () => (activeTab.value = 'whatsapp'),
      active: activeTab.value === 'whatsapp',
    },
  ],
])
</script>

<template>
  <UModal
    v-model:open="open"
    title="Settings"
    :ui="{
      content: 'w-5/6 h-220',
    }"
  >
    <template #body>
      <div class="flex h-full">
        <aside class="w-1/5">
          <UNavigationMenu
            color="neutral"
            variant="link"
            orientation="vertical"
            :items="navItems"
            :ui="{
              link: 'my-1 text-xs',
              separator: 'bg-inherit',
              linkLeadingIcon: 'size-4',
            }"
          />
        </aside>

        <div class="overflow-y-auto w-full">
          <component :is="tabs[activeTab]" />
        </div>
      </div>
    </template>
  </UModal>
</template>
