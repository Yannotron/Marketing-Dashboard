from __future__ import annotations

"""Supabase storage adapter.

All writes must be idempotent (UPSERT) keyed by stable IDs.
"""

from collections.abc import Iterable
from typing import Any

from ..models import Post, UpsertResult
from ..utils import get_json_logger, retry_with_backoff

log = get_json_logger("reddit_pipeline.storage.supabase")


class SupabaseStore:
    def __init__(self, url: str, anon_key: str) -> None:
        self.url = url
        self.anon_key = anon_key

    @retry_with_backoff()
    def upsert_posts(self, posts: Iterable[Post]) -> UpsertResult:
        items = list(posts)
        log.info("Upserting posts", extra={"count": len(items)})
        # TODO: Implement using supabase-py client with upsert on primary key
        return UpsertResult(inserted=0, updated=0)



# --- Module-level minimal function signatures (required by spec) ---

def upsert_post(post_dict: dict[str, Any]) -> None:
    """UPSERT a single post into Supabase.

    This is a stub to satisfy the minimal interface. Implement using supabase-py
    with `upsert` on a stable primary key. Must be idempotent.
    """

    log.info("upsert_post called", extra={"id": post_dict.get("id")})


def upsert_comment(comment_dict: dict[str, Any]) -> None:
    """UPSERT a single comment into Supabase (stub)."""

    log.info("upsert_comment called", extra={"id": comment_dict.get("id")})


def upsert_insight(insight_dict: dict[str, Any]) -> None:
    """UPSERT an insight record into Supabase (stub)."""

    log.info("upsert_insight called", extra={"id": insight_dict.get("id")})


def upsert_embedding(entity_type: str, entity_id: str, vector: list[float]) -> None:
    """UPSERT an embedding vector for a post/insight (stub)."""

    log.info(
        "upsert_embedding called",
        extra={"entity_type": entity_type, "entity_id": entity_id, "dim": len(vector)},
    )

