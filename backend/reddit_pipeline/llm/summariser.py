from __future__ import annotations

"""Summarisation utilities (LLM-backed).

Strict-JSON output per spec. Uses OpenAI SDK with retries and truncation.
"""

from typing import Any

import orjson
from openai import OpenAI

from ..config import settings
from ..models import Post
from ..utils import get_json_logger, retry_with_backoff

log = get_json_logger("reddit_pipeline.llm.summariser")

SYSTEM_PROMPT = (
    "You are a rigorous marketing analyst. Be concise, factual, and specific. UK English."
)


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)] + "…"


def _build_user_content(post: Post, top_comments: list[dict[str, Any]]) -> str:
    title = post.title
    body = post.text or ""
    comments_str = "\n\n".join(
        f"- [score {c.get('score', 0)}] {c.get('body','')}" for c in top_comments
    )
    return (
        f"Post title:\n{title}\n\nPost selftext:\n{body}\n\nTop comments (truncated):\n{comments_str}"
    )


def _response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "summariser_schema",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "summary": {"type": "string"},
                    "pain_points": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                    "segments": {"type": "array", "items": {"type": "string"}},
                    "tools_mentioned": {"type": "array", "items": {"type": "string"}},
                    "contrarian_take": {"type": "string"},
                    "key_metrics": {"type": "array", "items": {"type": "string"}},
                    "sources": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "summary",
                    "pain_points",
                    "recommendations",
                    "segments",
                    "tools_mentioned",
                    "contrarian_take",
                    "key_metrics",
                    "sources",
                ],
            },
            "strict": True,
        },
    }


@retry_with_backoff()
def _call_openai(messages: list[dict[str, str]]) -> dict[str, Any]:
    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.chat.completions.create(
        model=settings.llm_model_summariser,
        messages=messages,
        response_format=_response_format(),
        temperature=0.2,
    )
    content = resp.choices[0].message.content or "{}"
    try:
        return orjson.loads(content)
    except Exception:
        # As a fallback, wrap as string to maintain strictness for storage.
        return {"summary": content, "pain_points": [], "recommendations": [], "segments": [], "tools_mentioned": [], "contrarian_take": "", "key_metrics": [], "sources": []}


def summarise_posts_with_comments(
    posts: list[Post],
    comments_by_post: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """Summarise each post with its top-K comments using strict JSON.

    Returns a mapping of post_id -> summariser JSON dict.
    """

    log.info("Summarising posts", extra={"count": len(posts)})
    results: dict[str, dict[str, Any]] = {}
    max_chars_per_section = 2000  # coarse truncation guard before tokenisation
    top_k = settings.top_k_comments

    for post in posts:
        comments = (comments_by_post.get(post.id) or [])[:top_k]
        # truncate long comment bodies
        trimmed_comments = []
        for c in comments:
            body = _truncate_text(str(c.get("body", "")), 800)
            trimmed_comments.append({"score": c.get("score", 0), "body": body})

        user_content = _build_user_content(
            post,
            trimmed_comments,
        )
        user_content = _truncate_text(user_content, max_chars_per_section)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Provide post title + selftext + top comments (with scores).\n"
                    "Return strict JSON with keys: summary, pain_points[], recommendations[], segments[], "
                    "tools_mentioned[], contrarian_take, key_metrics[], sources[].\n\n"
                    + user_content
                ),
            },
        ]

        payload = _call_openai(messages)
        results[post.id] = payload

    return results


