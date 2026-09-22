import { API_SYNC_URLS } from '@/app/core/clients/api'
import { documentKeys } from '@/app/features/document/composables/data/document'
import { stickyKeys } from '@/app/features/sticky/composables/sticky'
import { taskKeys } from '@/app/features/task/composables/task'
import { useWorkplace } from '@/app/features/workplace/composables/workplace'
import { useQueryClient } from '@tanstack/vue-query'

/**
 * Global EventSource instance, one per session — mirrors `useNotification`'s
 * pattern (see `composables/inbox/notification.ts`).
 */
let eventSource: EventSource | null = null

interface iResourceChangedPayload {
  id: string
  action: 'created' | 'updated' | 'deleted'
  workplace_id: string
}

/**
 * Live sync for Task/Document/Sticky lists via the existing generic per-user SSE
 * stream (`apps.common.streaming.views.stream_view`) — a signal on each model fans
 * `<resource>.changed` out to every workplace member (see
 * `apps.common.streaming.publisher.publish_resource_changed`), so create/update/
 * delete elsewhere shows up here without a manual refresh.
 *
 * Payload never carries the changed object, only `{id, action, workplace_id}` — the
 * client just invalidates the matching query root and lets the normal, permission-
 * scoped endpoint refetch. `workplace_id` lets a change in a workplace you're not
 * currently viewing skip the refetch entirely.
 */
export const useWorkplaceSync = () => {
  const queryClient = useQueryClient()
  const { workplace } = useWorkplace()

  function invalidate(rootKey: readonly unknown[], event: MessageEvent) {
    let payload: iResourceChangedPayload
    try {
      payload = JSON.parse(event.data)
    } catch {
      return
    }

    if (String(payload.workplace_id) !== String(workplace.value?.id)) return

    queryClient.invalidateQueries({ queryKey: rootKey })
  }

  function connect() {
    if (eventSource && eventSource.readyState !== EventSource.CLOSED) return

    eventSource = new EventSource(API_SYNC_URLS.EVENT, { withCredentials: true })

    eventSource.addEventListener('task.changed', (e: MessageEvent) => invalidate(taskKeys.root(), e))
    eventSource.addEventListener('document.changed', (e: MessageEvent) =>
      invalidate(documentKeys.root(), e),
    )
    eventSource.addEventListener('sticky.changed', (e: MessageEvent) =>
      invalidate(stickyKeys.root(), e),
    )

    eventSource.onerror = () => {
      disconnect()
      setTimeout(connect, 5000)
    }
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  return { connect, disconnect }
}
