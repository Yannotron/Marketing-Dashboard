"""Product Hunt client placeholder using official GraphQL API."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from ..models import Post
from ..utils import get_json_logger, retry_with_backoff

log = get_json_logger("reddit_pipeline.clients.producthunt")


class ProductHuntClient:
    @retry_with_backoff()
    def fetch_today(self, limit: int = 50) -> list[Post]:
        log.info("Fetching Product Hunt posts", extra={"limit": limit})
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get("https://api.producthunt.com/v1/posts")
                resp.raise_for_status()
                data = resp.json()
                posts: list[Post] = []
                for item in data.get("posts", [])[:limit]:
                    created_raw = str(item.get("created_at", "1970-01-01T00:00:00Z")).replace(
                        "Z", "+00:00"
                    )
                    created = datetime.fromisoformat(created_raw)
                    posts.append(
                        Post(
                            id=str(item.get("id", "")),
                            source="producthunt",
                            title=str(item.get("name", "")),
                            url=str(item.get("redirect_url", "https://example.com")),
                            author=str((item.get("user") or {}).get("name", "")),
                            score=int(item.get("votes_count", 0)),
                            num_comments=int(item.get("comments_count", 0)),
                            created_utc=created.astimezone(UTC),
                            subreddit="producthunt",
                            text=str(item.get("tagline") or "") or None,
                        )
                    )
                return posts
        except Exception as exc:  # pragma: no cover
            log.error("PH fetch failed", extra={"error": str(exc)})
            return []
