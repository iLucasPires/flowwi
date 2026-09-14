import { API_GOOGLE_DRIVE_URLS, apiFetch } from '@/app/core/clients/api'
import { computed } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'

// ─── Types ───────────────────────────────────────────────────────────────────

interface DriveConnection {
  id: string
  is_active: boolean
  workplace: string
  connected_by: string
  folder_id: string
  created_at: string
}

// ─── Query Keys ──────────────────────────────────────────────────────────────

export const driveKeys = {
  root: () => ['google-drive'] as const,
  list: () => ['google-drive', 'list'] as const,
}

// ─── Shared Query ─────────────────────────────────────────────────────────────

function useDriveListQuery() {
  const {
    data,
    refetch: refresh,
    isLoading,
  } = useQuery({
    queryKey: driveKeys.list(),
    staleTime: 30_000,
    queryFn: () => apiFetch<{ results: DriveConnection[] }>(API_GOOGLE_DRIVE_URLS.LIST),
  })

  return { data, refresh, isLoading }
}

// ─── Composable ───────────────────────────────────────────────────────────────

export const useGoogleDrive = () => {
  const toast = useToast()
  const queryClient = useQueryClient()
  const { data, isLoading } = useDriveListQuery()

  // ── Derived state ──────────────────────────────────────────────────────────

  const activeConnection = computed(() => data.value?.results?.find((c) => c.is_active))

  const connected = computed(() => !!activeConnection.value)

  // ── OAuth Popup Flow ───────────────────────────────────────────────────────

  const connecting = ref(false)
  let popup: Window | null = null
  let pollInterval: ReturnType<typeof setInterval> | null = null

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
    popup = null
  }

  function startPolling(state: string) {
    const checkCompleted = async (): Promise<boolean> => {
      try {
        const { completed } = await apiFetch<{ completed: boolean }>(
          `${API_GOOGLE_DRIVE_URLS.LIST}/auth-status?state=${state}`,
        )
        return completed
      } catch {
        return false
      }
    }

    const onCompleted = () => {
      stopPolling()
      popup?.close()
      connecting.value = false
      queryClient.invalidateQueries({ queryKey: driveKeys.root() })
    }

    pollInterval = setInterval(async () => {
      if (await checkCompleted()) {
        onCompleted()
        return
      }

      // Popup closed — one last check before giving up
      if (popup?.closed) {
        stopPolling()
        // Wait a moment for the backend to finish processing
        setTimeout(async () => {
          if (await checkCompleted()) {
            onCompleted()
          } else {
            connecting.value = false
          }
        }, 1500)
      }
    }, 2000)
  }

  async function connect() {
    if (popup && !popup.closed) {
      popup.focus()
      return
    }

    connecting.value = true

    try {
      const width = 600
      const height = 700
      const left = window.screenX + (window.outerWidth - width) / 2
      const top = window.screenY + (window.outerHeight - height) / 2

      const { url, state } = await apiFetch<{ url: string; state: string }>(
        `${API_GOOGLE_DRIVE_URLS.LIST}/auth-url`,
      )

      popup = window.open(
        url,
        'google-drive-auth',
        `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`,
      )

      if (!popup) {
        toast.add({ title: 'Popup bloqueado. Permita popups para este site.', color: 'warning' })
        connecting.value = false
        return
      }

      startPolling(state)
    } catch {
      toast.add({ title: 'Erro ao iniciar conexão com Google Drive', color: 'error' })
      connecting.value = false
    }
  }

  // ── Disconnect ─────────────────────────────────────────────────────────────

  const { mutateAsync: disconnect } = useMutation({
    mutationFn: async () => {
      const connection = activeConnection.value
      if (!connection) return
      await apiFetch(`${API_GOOGLE_DRIVE_URLS.DETAIL(connection.id)}/disconnect`, {
        method: 'POST',
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: driveKeys.root() })
      toast.add({ title: 'Google Drive desconectado', color: 'success' })
    },
    onError: () => {
      toast.add({ title: 'Erro ao desconectar Google Drive', color: 'error' })
    },
  })

  // ── Cleanup ────────────────────────────────────────────────────────────────

  onUnmounted(() => stopPolling())

  return {
    connected,
    connecting,
    isLoading,
    connect,
    disconnect,
  }
}
