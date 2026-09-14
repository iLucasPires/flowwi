<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const open = ref(false)

const mainItems = computed<NavigationMenuItem[][]>(() => [
  [
    {
      label: 'Home',
      icon: 'i-lucide-house',
      to: '/dashboard',
      exact: true,
    },
    {
      label: 'Inbox',
      icon: 'i-lucide-inbox',
      to: '/dashboard/inbox',
    },
  ],
  [
    {
      label: 'Ferramenta',
      type: 'label',
    },
    {
      label: 'Media',
      icon: 'i-lucide-folder',
      to: '/dashboard/media',
    },
    {
      label: 'Documentos',
      icon: 'i-lucide-file-edit',
      to: '/dashboard/documents',
    },
    {
      label: 'Stickies',
      icon: 'i-lucide-squares-unite',
      to: '/dashboard/stickies',
    },
    {
      label: 'Tarefas',
      icon: 'i-lucide-kanban',
      to: '/dashboard/tasks',
    },
    {
      label: 'Formulários',
      icon: 'i-lucide-file-text',
      to: '/dashboard/forms',
    },
  ],
])
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      v-model:open="open"
      id="default"
      mode="drawer"
      class="border-none py-2"
      toggle-side="right"
      collapsible
      resizable
    >
      <template #default="{ collapsed }">
        <CUserMenu :collapsed="collapsed" />
        <UNavigationMenu
          :collapsed="collapsed"
          :items="mainItems"
          color="neutral"
          variant="link"
          orientation="vertical"
          tooltip
          popover
          :ui="{
            link: 'my-1 text-xs',
            separator: 'bg-inherit',
            linkLeadingIcon: 'size-4',
            childList: 'border-none ms-2',
          }"
        />
      </template>
    </UDashboardSidebar>

    <UDashboardPanel id="dashboard" class="p-4 ps-0">
      <RouterView />
    </UDashboardPanel>
  </UDashboardGroup>
</template>
