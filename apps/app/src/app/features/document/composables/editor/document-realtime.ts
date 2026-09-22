import type { iDocumentLock } from "@/app/features/document/types";
import { useUser } from "@/app/features/user/composables/user";
/**
 * One persistent connection to the app's single WebSocket endpoint (`/ws/`, see
 * `shared.websocket.GlobalConsumer` on the backend), used here to subscribe to one
 * document's realtime channel at a time and re-subscribe as `documentId` changes —
 * no reconnect needed just to switch documents. Two things ride on the subscription:
 *
 * - The pessimistic edit lock — whoever calls `acquireLock()` first "has the pen";
 *   everyone else subscribed to the same document is told via `lockedBy` and should
 *   render read-only, so two people can't silently overwrite each other's draft.
 * - `document.changed` notifications — pushed whenever the document (or its version)
 *   changes on the backend, so a tab that's just watching (not editing) knows to
 *   refetch instead of going stale until a manual reload.
 *
 * Not a collaborative editor: no operational transform, no content merging — just
 * enough to stop concurrent edits and keep viewers' sharing/publish state fresh.
 */
export function useDocumentRealtime(
  documentId: Ref<number | null> | ComputedRef<number | null>,
  options: { onDocumentChanged?: () => void } = {},
) {
  const { user } = useUser();

  const lockedBy = ref<iDocumentLock | null>(null);
  /** Whether *we* are trying to hold the lock right now (drives reconnect/heartbeat). */
  const wantsLock = ref(false);
  /** The document we last told the server we're subscribed to — `null` between mount
   * and the first subscribe, or after unsubscribing with nothing to replace it. */
  let subscribedId: string | null = null;

  const iHoldLock = computed(
    () => !!user.value && !!lockedBy.value && lockedBy.value.user_id === user.value.id,
  );
  const isLockedByOther = computed(() => !!lockedBy.value && !iHoldLock.value);

  let socket: WebSocket | null = null;
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let closingIntentionally = false;

  const HEARTBEAT_INTERVAL_MS = 8_000;
  const RECONNECT_DELAY_MS = 2_000;

  function send(payload: Record<string, unknown>) {
    if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify(payload));
  }

  function startHeartbeat() {
    stopHeartbeat();
    heartbeatTimer = setInterval(() => {
      if (subscribedId != null) send({ type: "document.heartbeat", document_id: subscribedId });
    }, HEARTBEAT_INTERVAL_MS);
  }

  function stopHeartbeat() {
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    heartbeatTimer = null;
  }

  function wsUrl(): string {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${location.host}/ws/`;
  }

  function connectSocket() {
    closingIntentionally = false;
    socket = new WebSocket(wsUrl());

    socket.addEventListener("open", () => {
      // Re-establish whatever this composable instance currently wants, in case this
      // is a reconnect after a dropped connection rather than the first open.
      if (subscribedId != null) send({ type: "document.subscribe", document_id: subscribedId });
      if (wantsLock.value && subscribedId != null) {
        send({ type: "document.acquire_lock", document_id: subscribedId });
      }
    });

    socket.addEventListener("message", (event) => {
      let data: { type?: string; document_id?: string; lock?: iDocumentLock | null };
      try {
        data = JSON.parse(event.data);
      } catch {
        return;
      }

      // Ignore anything about a document we've since moved away from — a message can
      // still be in flight right as `documentId` changes.
      if (data.document_id == null || data.document_id !== subscribedId) return;

      if (data.type === "document.lock_state") {
        lockedBy.value = data.lock ?? null;
      } else if (data.type === "document.changed") {
        options.onDocumentChanged?.();
      }
    });

    socket.addEventListener("close", () => {
      stopHeartbeat();
      // Only auto-reconnect on an unexpected drop — not when we closed it ourselves
      // (component unmounting).
      if (!closingIntentionally) {
        reconnectTimer = setTimeout(connectSocket, RECONNECT_DELAY_MS);
      }
    });
  }

  /** Switches which document this connection is subscribed to — no reconnect. */
  function subscribeTo(id: number | null) {
    const nextId = id != null ? String(id) : null;

    if (subscribedId != null && subscribedId !== nextId) {
      send({ type: "document.unsubscribe", document_id: subscribedId });
    }

    subscribedId = nextId;
    lockedBy.value = null;
    wantsLock.value = false;
    stopHeartbeat();

    if (nextId != null) send({ type: "document.subscribe", document_id: nextId });
  }

  function acquireLock() {
    wantsLock.value = true;
    if (subscribedId != null) send({ type: "document.acquire_lock", document_id: subscribedId });
    startHeartbeat();
  }

  function releaseLock() {
    if (wantsLock.value && subscribedId != null) {
      send({ type: "document.release_lock", document_id: subscribedId });
    }
    wantsLock.value = false;
    stopHeartbeat();
  }

  connectSocket();
  watch(documentId, subscribeTo, { immediate: true });

  onBeforeUnmount(() => {
    closingIntentionally = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    stopHeartbeat();
    if (subscribedId != null) send({ type: "document.unsubscribe", document_id: subscribedId });
    socket?.close();
    socket = null;
  });

  return {
    lockedBy,
    iHoldLock,
    isLockedByOther,
    acquireLock,
    releaseLock,
  };
}
