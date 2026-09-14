from django.db import transaction

from lib.bases import ServiceBase

from ..models import MediaFeedback, MediaFeedbackDecision


class MediaFeedbackService(ServiceBase):
    def __init__(self):
        super().__init__(model=MediaFeedback)

    @transaction.atomic
    def add_feedback(
        self,
        media_id: int,
        user_id: int | None,
        content: str = "",
        *,
        version_id: int | None = None,
        decision: int | None = None,
    ):
        """`user_id=None` is the public share-link path — there's no stable identity to
        dedupe repeat votes on, so it always inserts a new row instead of upserting."""
        if user_id is None:
            return MediaFeedback.objects.create(
                media_id=media_id,
                version_id=version_id,
                decision=decision or MediaFeedbackDecision.LIKE,
                notes=content or "",
            )

        obj, _ = MediaFeedback.objects.update_or_create(
            media_id=media_id,
            version_id=version_id,
            given_by_id=user_id,
            defaults={
                "decision": decision or MediaFeedbackDecision.LIKE,
                "notes": content or "",
            },
        )
        return obj
