import { API_NOTIFICATION_URLS } from '@/app/core/clients/api'
import type { iInbox } from '@/app/features/inbox/types'
import { useQueryClient } from '@tanstack/vue-query'

/**
 * Global EventSource instance to ensure only one connection exists
 * across different components using this composable.
 */
let eventSource: EventSource | null = null

/**
 * Composable to handle real-time notifications via Server-Sent Events (SSE).
 */
export const useNotification = () => {
  const toast = useToast()
  const queryClient = useQueryClient()

  /**
   * Establishes a connection to the SSE endpoint.
   */
  function connect() {
    if (eventSource && eventSource.readyState !== EventSource.CLOSED) return

    eventSource = new EventSource(API_NOTIFICATION_URLS.EVENT, {
      withCredentials: true,
    })

    // The backend always sets a named `event:` field (`inbox-notification`), which the
    // SSE spec dispatches as that custom event type, never as the default `message` —
    // `onmessage` never fires for these frames, only `addEventListener` does.
    eventSource.addEventListener('inbox-notification', (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as iInbox

        // Invalidate inbox queries to refresh the list
        queryClient.invalidateQueries({ queryKey: ['inbox'] })

        // Show a visual notification
        toast.add({
          title: data.title,
          description: data.message,
          color: 'primary',
          icon: 'i-lucide-bell',
        })
      } catch (err) {
        console.error('Failed to parse notification message:', err)
      }
    })

    eventSource.onerror = () => {
      disconnect()
      setTimeout(connect, 5000)
    }
  }

  /**
   * Closes the existing SSE connection.
   */
  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  return { connect, disconnect }
}
