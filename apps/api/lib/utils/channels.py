def channel_name(kind: str, identifier) -> str:
    """
    Builds a `<kind>-<identifier>` name — the one naming convention shared by
    every realtime transport in the project: Django Channels group names (WS,
    `apps.common.realtime`/`apps.domains.document`) and Redis pub/sub channels (SSE,
    `apps.common.streaming`). Channels group names allow only ASCII alphanumerics,
    hyphens, underscores, and periods — no colons (`channels_redis` enforces
    this; `InMemoryChannelLayer` doesn't, which is how a `:`-based name could
    stay unnoticed against it) — so every caller follows that restriction
    through here instead of each app inventing its own separator.

    `kind` identifies what's on the other side of the id — `"user"`, `"member"`,
    `"document"` — so the same `identifier` can't collide across unrelated
    concepts (a user id and a document id landing on the same channel by luck).
    """
    return f"{kind}-{identifier}"
