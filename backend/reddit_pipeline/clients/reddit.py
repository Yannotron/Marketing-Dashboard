"""Reddit client interface.

Do not scrape HTML. Use official APIs with proper auth and rate limiting.
Backed by `praw` with a strict user agent. All network calls use retry with
backoff and log structured JSON.
"""

from __future__ import annotations

from datetime import datetime

from ..models import Post
from ..utils import get_json_logger, retry_with_backoff

log = get_json_logger("reddit_pipeline.clients.reddit")


class RedditClient:
    def __init__(self, client_id: str, client_secret: str, user_agent: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

    @retry_with_backoff()
    def fetch_top_submissions(
        self, subs: list[str], since: datetime, limit_per_sub: int
    ) -> list[Post]:
        """Fetch top submissions for subreddits since a given time.

        Strictly uses official API via PRAW. Rate limits respected by PRAW; we
        also retry on transient errors via decorator.
        """

        log.info(
            "Fetching top submissions",
            extra={"subs": subs, "since": since.isoformat(), "limit_per_sub": limit_per_sub},
        )
        # TODO: Wire `praw.Reddit` and map results to Post
        return []

    @retry_with_backoff()
    def fetch_comments(self, post_id: str, limit: int) -> list[dict]:
        """Fetch comments for a given post ID (minimal placeholder).

        Returns a list of dicts with stable IDs and authors. Avoid PII beyond
        usernames.
        """

        log.info("Fetching comments", extra={"post_id": post_id, "limit": limit})
        # TODO: Implement with PRAW and respect rate limits
        return []


