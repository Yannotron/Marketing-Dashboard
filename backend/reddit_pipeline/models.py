from __future__ import annotations

"""Pydantic models for pipeline inputs/outputs.

These schemas are used across ingestion, processing, and storage layers.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Post(BaseModel):
    """A normalised representation of a social post/item."""

    id: str = Field(..., description="Stable, source-specific ID (e.g. Reddit fullname)")
    source: str = Field(..., description="Source system name, e.g. 'reddit'")
    title: str
    url: HttpUrl
    author: str
    score: int = 0
    num_comments: int = 0
    created_utc: datetime
    subreddit_or_topic: Optional[str] = None
    text: Optional[str] = Field(None, description="Raw text; avoid PII beyond usernames")


class Insight(BaseModel):
    """LLM-generated insights for a post or group of posts."""

    id: str
    post_ids: List[str] = Field(default_factory=list)
    summary: str
    topics: List[str] = Field(default_factory=list)
    created_utc: datetime = Field(default_factory=datetime.utcnow)


class UpsertResult(BaseModel):
    """Return value for storage upserts (idempotent writes)."""

    inserted: int
    updated: int


