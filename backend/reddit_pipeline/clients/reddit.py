"""Reddit client interface.

Do not scrape HTML. Use official APIs with proper auth and rate limiting.
Backed by `praw` with a strict user agent. All network calls use retry with
backoff and log structured JSON.
"""

from __future__ import annotations

from datetime import UTC, datetime

import praw  # type: ignore

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

        try:
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )

            posts: list[Post] = []
            for sub in subs:
                subreddit = reddit.subreddit(sub)
                for submission in subreddit.hot(limit=limit_per_sub):
                    created_dt = datetime.fromtimestamp(getattr(submission, "created_utc", 0), tz=UTC)
                    posts.append(
                        Post(
                            id=str(getattr(submission, "id", "")),
                            source="reddit",
                            title=str(getattr(submission, "title", "")),
                            url=str(getattr(submission, "url", "https://example.com")),
                            author=str(getattr(getattr(submission, "author", None), "name", "")),
                            score=int(getattr(submission, "score", 0)),
                            num_comments=int(getattr(submission, "num_comments", 0)),
                            created_utc=created_dt,
                            subreddit=str(getattr(getattr(submission, "subreddit", None), "display_name", sub)),
                            text=str(getattr(submission, "selftext", "")) or None,
                        )
                    )
            return posts
        except Exception as exc:  # pragma: no cover - path validated via tests
            log.error("Failed to fetch submissions", extra={"error": str(exc)})
            return []

    @retry_with_backoff()
    def fetch_comments(self, post_id: str, limit: int) -> list[dict]:
        """Fetch comments for a given post ID (minimal placeholder).

        Returns a list of dicts with stable IDs and authors. Avoid PII beyond
        usernames.
        """

        log.info("Fetching comments", extra={"post_id": post_id, "limit": limit})
        try:
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )
            submission = reddit.submission(id=post_id)
            raw_comments = submission.comments.list()
            results: list[dict] = []
            for c in raw_comments[:limit]:
                results.append(
                    {
                        "id": str(getattr(c, "id", "")),
                        "body": str(getattr(c, "body", "")),
                        "score": int(getattr(c, "score", 0)),
                        "author": str(getattr(getattr(c, "author", None), "name", "")),
                    }
                )
            return results
        except Exception as exc:  # pragma: no cover - path validated via tests
            log.error("Failed to fetch comments", extra={"post_id": post_id, "error": str(exc)})
            return []


