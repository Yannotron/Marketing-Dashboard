"""Dedupe utilities for posts (placeholder)."""

from __future__ import annotations

from .models import Post


def dedupe_posts(posts: list[Post]) -> list[Post]:
    """Remove duplicates by post `id`. Keeps the first occurrence."""

    seen: dict[str, Post] = {}
    for post in posts:
        if post.id not in seen:
            seen[post.id] = post
    return list(seen.values())
