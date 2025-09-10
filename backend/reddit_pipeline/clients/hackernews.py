from __future__ import annotations

"""Hacker News client placeholder using official Firebase API."""

from typing import List

from ..models import Post
from ..utils import get_json_logger, retry_with_backoff


log = get_json_logger("reddit_pipeline.clients.hackernews")


class HackerNewsClient:
    @retry_with_backoff()
    def fetch_top(self, limit: int = 50) -> List[Post]:
        log.info("Fetching HN top stories", extra={"limit": limit})
        return []


