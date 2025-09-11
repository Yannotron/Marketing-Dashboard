"""Supabase storage adapter.

All writes must be idempotent (UPSERT) keyed by stable IDs.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ..models import Post, UpsertResult
from ..utils import get_json_logger, retry_with_backoff
from ..config import settings

log = get_json_logger("reddit_pipeline.storage.supabase")

try:  # import optional dependency
    from supabase import Client, create_client  # type: ignore
except Exception:  # pragma: no cover
    Client = Any  # type: ignore
    create_client = None  # type: ignore


class SupabaseStore:
    def __init__(self, url: str, key: str) -> None:
        self.url = url
        self.key = key
        self._client: Client | None = None

    def _get_client(self) -> Client:
        if self._client is None:
            if create_client is None:
                raise RuntimeError("supabase client not available")
            self._client = create_client(self.url, self.key)
        return self._client

    @retry_with_backoff()
    def upsert_posts(self, posts: Iterable[Post]) -> UpsertResult:
        items = list(posts)
        log.info("Upserting posts", extra={"count": len(items)})
        if not items or not settings.supabase_enable_writes:
            return UpsertResult(inserted=0, updated=0)
        data = [
            {
                "id": p.id,
                "title": p.title,
                "url": p.url,
                "author": p.author,
                "created_utc": p.created_utc.isoformat(),
                "score": p.score,
                "comments_count": p.num_comments,
                "subreddit_or_channel": p.subreddit,
                "source_id": None,
            }
            for p in items
        ]
        client = self._get_client()
        resp = client.table("posts").upsert(data, on_conflict="id").execute()
        inserted = len(resp.data) if getattr(resp, "data", None) else 0
        return UpsertResult(inserted=inserted, updated=0)

    @retry_with_backoff()
    def upsert_insight(self, insight: dict[str, Any]) -> None:
        if not settings.supabase_enable_writes:
            return
        client = self._get_client()
        client.table("insights").upsert(insight, on_conflict="id").execute()

    @retry_with_backoff()
    def upsert_embedding(self, entity_type: str, entity_id: str, vector: list[float]) -> None:
        if not settings.supabase_enable_writes:
            return
        client = self._get_client()
        # simple delete+insert to ensure idempotency for this demo
        client.table("embeddings").delete().eq("entity_type", entity_type).eq(
            "entity_id", entity_id
        ).execute()
        client.table("embeddings").insert(
            {"entity_type": entity_type, "entity_id": entity_id, "embedding": vector}
        ).execute()


# --- Module-level helpers used by pipeline ---

_store: SupabaseStore | None = None


def _ensure_store() -> SupabaseStore:
    global _store
    if _store is None:
        key = settings.supabase_service_role_key or settings.supabase_anon_key
        _store = SupabaseStore(settings.supabase_url, key)
    return _store


def upsert_post(post_dict: dict[str, Any]) -> None:
    """UPSERT a single post into Supabase."""
    if not post_dict:
        return
    p = Post.model_validate(post_dict)
    _ensure_store().upsert_posts([p])


def upsert_comment(comment_dict: dict[str, Any]) -> None:
    """UPSERT a single comment into Supabase (not implemented here)."""
    log.info("upsert_comment", extra={"id": comment_dict.get("id")})


def upsert_insight(insight_dict: dict[str, Any]) -> None:
    """UPSERT an insight record into Supabase."""
    _ensure_store().upsert_insight(insight_dict)


def upsert_embedding(entity_type: str, entity_id: str, vector: list[float]) -> None:
    """UPSERT an embedding vector for a post/insight."""
    _ensure_store().upsert_embedding(entity_type, entity_id, vector)
