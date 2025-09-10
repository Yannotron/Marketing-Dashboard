from __future__ import annotations

"""Dedupe utilities for posts (placeholder)."""

from typing import Dict, List

from .models import Post


def dedupe_posts(posts: List[Post]) -> List[Post]:
    """Remove duplicates by post `id`. Keeps the first occurrence."""

    seen: Dict[str, Post] = {}
    for post in posts:
        if post.id not in seen:
            seen[post.id] = post
    return list(seen.values())


