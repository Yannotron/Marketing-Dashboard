from __future__ import annotations

"""Product Hunt client placeholder using official GraphQL API."""

from typing import List

from ..models import Post
from ..utils import get_json_logger, retry_with_backoff


log = get_json_logger("reddit_pipeline.clients.producthunt")


class ProductHuntClient:
    @retry_with_backoff()
    def fetch_today(self, limit: int = 50) -> List[Post]:
        log.info("Fetching Product Hunt posts", extra={"limit": limit})
        return []


