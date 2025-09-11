"""Hacker News client placeholder using official Firebase API."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx

from ..models import Post
from ..utils import get_json_logger, retry_with_backoff

log = get_json_logger("reddit_pipeline.clients.hackernews")


class HackerNewsClient:
    @retry_with_backoff()
    def fetch_top(self, limit: int = 50) -> list[Post]:
        log.info("Fetching HN top stories", extra={"limit": limit})
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    "https://hn.algolia.com/api/v1/search?tags=front_page",
                    params={"hitsPerPage": limit},
                )
                resp.raise_for_status()
                data = resp.json()
                posts: list[Post] = []
                for hit in data.get("hits", [])[:limit]:
                    created = datetime.fromtimestamp(int(hit.get("created_at_i", 0)), tz=UTC)
                    posts.append(
                        Post(
                            id=str(hit.get("objectID", "")),
                            source="hackernews",
                            title=str(hit.get("title") or hit.get("story_title") or ""),
                            url=str(
                                hit.get("url") or hit.get("story_url") or "https://example.com"
                            ),
                            author=str(hit.get("author", "")),
                            score=int(hit.get("points", 0)),
                            num_comments=int(hit.get("num_comments", 0)),
                            created_utc=created,
                            subreddit="hn",
                            text=str(hit.get("story_text") or "") or None,
                        )
                    )
                return posts
        except Exception as exc:  # pragma: no cover
            log.error("HN fetch failed", extra={"error": str(exc)})
            return []
