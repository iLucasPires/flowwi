# app/utils/cache.py

import hashlib
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response


def get_cache_version() -> int:
    """Versão global do cache. Incrementar invalida tudo automaticamente."""
    return getattr(settings, "API_CACHE_VERSION", 1)


def resolve_cache_ttl(view: Any) -> int | None:
    """
    Resolve TTL do cache para a view.

    Prioridade:
    1. view.api_cache_timeout
    2. settings.API_VIEW_CACHE_TIMEOUT

    Retorna None se cache estiver desativado (valor <= 0 ou ausente).
    """
    if hasattr(view, "api_cache_timeout"):
        ttl = view.api_cache_timeout
        return int(ttl) if ttl > 0 else None

    global_ttl = getattr(settings, "API_VIEW_CACHE_TIMEOUT", 0)
    return int(global_ttl) if global_ttl > 0 else None


def build_view_cache_key(view: Any, action: str) -> str:
    """
    Gera chave única de cache por view, action, usuário, workplace, path e kwargs.
    """
    request = view.request
    view_cls = view.__class__
    user = request.user

    user_segment = f"u:{user.pk}" if getattr(user, "is_authenticated", False) else "anon"
    workplace_id = (request.COOKIES.get("workplace_id") or "").strip()
    kwargs = getattr(view, "kwargs", {}) or {}
    kwargs_segment = "|".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

    raw = "|".join(
        [
            f"v:{get_cache_version()}",
            f"{view_cls.__module__}.{view_cls.__name__}",
            action,
            user_segment,
            workplace_id,
            request.get_full_path(),
            kwargs_segment,
        ]
    )

    return f"api:{hashlib.sha256(raw.encode()).hexdigest()}"


def get_or_set_view_cache(
    view: Any,
    action: str,
    builder: Callable[[], Response],
    *,
    timeout: int,
) -> Response:
    """
    Busca resposta no cache ou executa o builder e armazena o resultado.
    Só cacheia respostas HTTP 200.
    """
    key = build_view_cache_key(view, action)

    cached = cache.get(key)
    if cached is not None:
        return Response(cached)

    response = builder()

    if response.status_code == status.HTTP_200_OK:
        cache.set(key, response.data, timeout)

    return response


def invalidate_view_cache(view: Any, action: str) -> None:
    """Invalida o cache da request atual."""
    key = build_view_cache_key(view, action)
    cache.delete(key)
