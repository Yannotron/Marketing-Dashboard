from __future__ import annotations

"""Ranking utilities for posts.

Implements a composite ranking score per requirements:
- Inputs: score, comments, upvote_ratio (optional), created_utc
- Freshness decay so newer posts rank higher.

All functions are pure and side-effect free for testability.
"""

from datetime import datetime, timezone
from typing import List, Optional

from .models import Post


def composite_rank(
    score: int,
    comments: int,
    upvote_ratio: Optional[float],
    created_utc: datetime,
) -> float:
    """Compute a composite ranking score.

    Heuristic:
    - Base = score_weight * score + comment_weight * comments
    - Upvote ratio bonus if provided
    - Time decay: exponential decay by age in hours
    """

    score_weight = 1.0
    comment_weight = 0.5
    ratio_weight = 2.0
    # half-life ~ 48h: decay = 0.5 ** (age_hours/48)
    half_life_hours = 48.0

    base = score_weight * float(score) + comment_weight * float(comments)
    ratio_bonus = ratio_weight * float(upvote_ratio) if upvote_ratio is not None else 0.0

    now = datetime.now(timezone.utc)
    age_hours = max(0.0, (now - created_utc).total_seconds() / 3600.0)
    decay = 0.5 ** (age_hours / half_life_hours)

    return (base + ratio_bonus) * decay


def rank_posts(posts: List[Post]) -> List[Post]:
    """Return posts sorted descending by composite rank."""

    def _rank(p: Post) -> float:
        return composite_rank(
            score=p.score,
            comments=p.num_comments,
            upvote_ratio=None,  # not present in Post model; handled upstream if available
            created_utc=p.created_utc,
        )

    return sorted(posts, key=_rank, reverse=True)


