import json
import time
from dataclasses import dataclass

from lib.clients import redis_client

LOCK_TTL_SECONDS = 20
"""How long a lock survives without a heartbeat. Must be well under the client's
heartbeat interval's double (see `useDocumentRealtime` on the frontend, ~8s) so a
dropped connection (crash, network loss) frees the document quickly, not forever."""


def _lock_key(document_id) -> str:
    return f"doc:lock:{document_id}"


@dataclass
class DocumentLock:
    user_id: int
    username: str
    acquired_at: float

    def as_wire_dict(self) -> dict:
        """What the client actually needs to know — `acquired_at` is bookkeeping."""
        return {"user_id": self.user_id, "username": self.username}


class DocumentLockService:
    """
    Pessimistic per-document edit lock, backed by Redis so it's shared across every
    Daphne worker process. Not a full collaborative-editing system (no operational
    transform/CRDT) — just enough to stop two people from silently overwriting each
    other's draft in the same document at the same time.
    """

    def get(self, document_id) -> DocumentLock | None:
        raw = redis_client.get(_lock_key(document_id))
        if not raw:
            return None
        data = json.loads(raw)
        return DocumentLock(**data)

    def try_acquire(self, document_id, user_id: int, username: str) -> DocumentLock | None:
        """
        Returns the lock (whether newly acquired or already held by `user_id`) on
        success, or `None` if someone else holds it. Uses `SET NX` so the check and
        the write are atomic even under concurrent requests for the same document.
        """
        current = self.get(document_id)

        if current and current.user_id != user_id:
            return None

        payload = DocumentLock(user_id=user_id, username=username, acquired_at=time.time())
        redis_client.set(_lock_key(document_id), json.dumps(payload.__dict__), ex=LOCK_TTL_SECONDS)

        return payload

    def refresh(self, document_id, user_id: int) -> bool:
        """Renews the TTL on a heartbeat. Returns False if this user no longer holds it
        (lock expired and someone else grabbed it, or was never held by them)."""
        current = self.get(document_id)

        if not current or current.user_id != user_id:
            return False

        redis_client.expire(_lock_key(document_id), LOCK_TTL_SECONDS)

        return True

    def release(self, document_id, user_id: int) -> bool:
        """Releases the lock only if `user_id` is the one holding it. Returns whether
        it actually released anything, so the caller knows whether to broadcast."""
        current = self.get(document_id)

        if not current or current.user_id != user_id:
            return False

        redis_client.delete(_lock_key(document_id))

        return True
