import json

from channels.db import database_sync_to_async

from ..services import DocumentRealtimeService


class DocumentRealtimeHandler:
    """
    Handles the `document.*` realtime protocol.

    The handler is instantiated once per WebSocket connection, so its state
    is private to that connection.
    """

    prefix = "document"

    def __init__(self, consumer):
        self.consumer = consumer
        self.service = DocumentRealtimeService()

        self.subscribed_documents: set[str] = set()
        self.held_lock_document_id: str | None = None

    @property
    def user(self):
        return self.consumer.user

    async def receive(self, data: dict) -> None:
        match data.get("type"):
            case "document.subscribe":
                await self._subscribe(data)

            case "document.unsubscribe":
                await self._unsubscribe(data)

            case "document.acquire_lock":
                await self._acquire_lock(data)

            case "document.heartbeat":
                await self._heartbeat(data)

            case "document.release_lock":
                await self._release_lock_message(data)

    async def dispatch(self, message: dict) -> None:
        match message.get("type"):
            case "document.lock_state":
                await self._send(
                    type="document.lock_state",
                    document_id=message["document_id"],
                    lock=message["lock"],
                )

            case "document.changed":
                await self._send(
                    type="document.changed",
                    document_id=message["document_id"],
                )

    async def on_connect(self) -> None:
        pass

    async def on_disconnect(self) -> None:
        if self.held_lock_document_id:
            await self._release_document_lock(self.held_lock_document_id)

        for document_id in tuple(self.subscribed_documents):
            await self._leave_group(document_id)

        self.subscribed_documents.clear()

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    async def _subscribe(self, data: dict) -> None:
        document_id = data.get("document_id")

        if not document_id:
            return

        if document_id in self.subscribed_documents:
            return

        allowed = await self._can_subscribe(document_id)

        if not allowed:
            await self._send(
                type="document.subscribe_denied",
                document_id=document_id,
            )
            return

        await self._join_group(document_id)
        self.subscribed_documents.add(document_id)

        lock = await self._get_lock(document_id)

        await self._send_lock_state(
            document_id,
            lock,
        )

    async def _unsubscribe(self, data: dict) -> None:
        document_id = data.get("document_id")

        if document_id not in self.subscribed_documents:
            return

        await self._release_document_lock(document_id)
        await self._leave_group(document_id)

        self.subscribed_documents.discard(document_id)

    # ------------------------------------------------------------------
    # Lock
    # ------------------------------------------------------------------

    async def _acquire_lock(self, data: dict) -> None:
        document_id = data.get("document_id")

        if not document_id:
            return

        if document_id not in self.subscribed_documents:
            return

        lock = await self._try_acquire_lock(document_id)

        if lock is None:
            current = await self._get_lock(document_id)

            await self._send_lock_state(
                document_id,
                current,
            )
            return

        self.held_lock_document_id = document_id

        await self._broadcast_lock_state(
            document_id,
            lock,
        )

    async def _heartbeat(self, data: dict) -> None:
        document_id = data.get("document_id")

        if document_id != self.held_lock_document_id:
            return

        still_held = await self._refresh_lock(document_id)

        if still_held:
            return

        self.held_lock_document_id = None

        current = await self._get_lock(document_id)

        await self._send_lock_state(
            document_id,
            current,
        )

    async def _release_lock_message(self, data: dict) -> None:
        document_id = data.get("document_id") or self.held_lock_document_id

        await self._release_document_lock(document_id)

    async def _release_document_lock(self, document_id: str | None) -> None:
        if document_id != self.held_lock_document_id:
            return

        released = await self._release_lock(document_id)

        self.held_lock_document_id = None

        if not released:
            return

        await self._broadcast_lock_state(
            document_id,
            None,
        )

        await self._broadcast(
            type="document.changed",
            document_id=document_id,
        )

    # ------------------------------------------------------------------
    # Service
    # ------------------------------------------------------------------

    @database_sync_to_async
    def _can_subscribe(self, document_id: str) -> bool:
        return self.service.can_subscribe(
            document_id,
            self.user,
        )

    @database_sync_to_async
    def _get_lock(self, document_id: str):
        return self.service.get_lock(document_id)

    @database_sync_to_async
    def _try_acquire_lock(self, document_id: str):
        return self.service.try_acquire_lock(
            document_id,
            self.user,
        )

    @database_sync_to_async
    def _refresh_lock(self, document_id: str) -> bool:
        return self.service.refresh_lock(
            document_id,
            self.user.id,
        )

    @database_sync_to_async
    def _release_lock(self, document_id: str) -> bool:
        return self.service.release_lock(
            document_id,
            self.user.id,
        )

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------

    async def _join_group(self, document_id: str) -> None:
        await self.consumer.channel_layer.group_add(
            self.service.group_name(document_id),
            self.consumer.channel_name,
        )

    async def _leave_group(self, document_id: str) -> None:
        await self.consumer.channel_layer.group_discard(
            self.service.group_name(document_id),
            self.consumer.channel_name,
        )

    # ------------------------------------------------------------------
    # Outbound
    # ------------------------------------------------------------------

    async def _send(self, **payload) -> None:
        await self.consumer.send(text_data=json.dumps(payload))

    async def _broadcast(self, **payload) -> None:
        await self.consumer.channel_layer.group_send(
            self.service.group_name(payload["document_id"]),
            payload,
        )

    async def _send_lock_state(
        self,
        document_id: str,
        lock,
    ) -> None:
        await self._send(
            type="document.lock_state",
            document_id=document_id,
            lock=self._as_wire_dict(lock),
        )

    async def _broadcast_lock_state(
        self,
        document_id: str,
        lock,
    ) -> None:
        await self._broadcast(
            type="document.lock_state",
            document_id=document_id,
            lock=self._as_wire_dict(lock),
        )

    @staticmethod
    def _as_wire_dict(lock) -> dict | None:
        return lock.as_wire_dict() if lock else None
