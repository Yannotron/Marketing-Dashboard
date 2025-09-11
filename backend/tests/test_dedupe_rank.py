from __future__ import annotations

from datetime import UTC, datetime

from reddit_pipeline.dedupe import dedupe_posts
from reddit_pipeline.models import Post
from reddit_pipeline.ranking import rank_posts


def _post(pid: str, score: int, comments: int) -> Post:
    return Post(
        id=pid,
        source="reddit",
        title="t",
        url="https://example.com",
        author="a",
        score=score,
        num_comments=comments,
        created_utc=datetime.now(UTC),
        subreddit="test",
    )


def test_dedupe_posts():
    posts = [_post("1", 1, 1), _post("1", 2, 2), _post("2", 3, 3)]
    out = dedupe_posts(posts)
    ids = {p.id for p in out}
    assert ids == {"1", "2"}


def test_rank_posts():
    posts = [_post("1", 1, 1), _post("2", 10, 0), _post("3", 5, 100)]
    ranked = rank_posts(posts)
    assert ranked[0].id == "3"
    assert ranked[-1].id == "1"
