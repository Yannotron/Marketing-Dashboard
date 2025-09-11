"""Pipeline orchestration entrypoint.

Respects rate limits and retries transient failures with backoff. This file is
safe to be executed by CI (weekly schedule) and locally for development.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from .clients.reddit import RedditClient
from .config import settings
from .llm.embeddings import embed_texts
from .llm.insights import generate_insights_from_summaries
from .llm.summariser import summarise_posts_with_comments
from .models import Post
from .ranking import rank_posts
from .storage.supabase import upsert_embedding, upsert_insight
from .utils import get_json_logger

log = get_json_logger("reddit_pipeline.run")


def fetch_sources() -> list[Post]:
    """Fetch items from enabled sources.

    Currently enables Reddit only (HN/PH disabled by default via settings).
    """

    log.info("Fetching sources...")

    posts: list[Post] = []

    # Reddit fetch (enabled by default via required secrets)
    try:
        reddit = RedditClient(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )
        # Fetch last N days (configurable) for a small curated list of subs
        since = datetime.now(UTC) - timedelta(days=max(1, settings.reddit_lookback_days))
        subs = [
            "technology",
            "programming",
        ]
        per_sub = max(1, min(10, settings.top_n_posts))
        fetched = reddit.fetch_top_submissions(subs, since, per_sub)
        # Filter to window and minimum comments (configurable)
        posts.extend(
            [
                p
                for p in fetched
                if p.created_utc >= since and p.num_comments > max(0, settings.reddit_min_comments)
            ]
        )
    except Exception as exc:  # pragma: no cover
        log.error("Reddit fetch failed", extra={"error": str(exc)})

    return posts


def process(posts: list[Post]) -> list[Post]:
    """Run dedupe/ranking/LLM pipelines with top-N selection.

    Note: fetching comments is not implemented here; provide top-K per post via
    external fetch in a real client. For now, pass empty comments.
    """

    log.info("Processing %d posts...", len(posts))
    if not posts:
        return posts

    ranked = rank_posts(posts)
    top_n = settings.top_n_posts
    selected = ranked[:top_n]

    # Placeholder comments map: in a real integration, supply top-K comments
    comments_by_post: dict[str, list[dict[str, Any]]] = {p.id: [] for p in selected}

    summaries = summarise_posts_with_comments(selected, comments_by_post)
    insights = generate_insights_from_summaries(summaries)

    # Embeddings: post.title, summariser.summary, and each insight record
    texts: list[str] = []
    embedding_targets: list[tuple[str, str]] = []  # (entity_type, entity_id)
    for p in selected:
        texts.append(p.title)
        embedding_targets.append(("post", p.id))
        summ = summaries.get(p.id, {}).get("summary", "")
        texts.append(str(summ))
        embedding_targets.append(("post", f"{p.id}#summary"))

    for post_id, insight_json in insights.items():
        texts.append(str(insight_json))
        embedding_targets.append(("insight", post_id))

    vectors = embed_texts(texts)
    for (entity_type, entity_id), vec in zip(embedding_targets, vectors):
        if vec:
            upsert_embedding(entity_type, entity_id, vec)

    # Persist insights JSON per-post
    for post_id, data in insights.items():
        upsert_insight(
            {
                "id": post_id,  # using post_id as temporary stable key; real impl should use UUID
                "post_id": post_id,
                "summary": summaries.get(post_id, {}).get("summary"),
                "pain_points": summaries.get(post_id, {}).get("pain_points"),
                "recommendations": summaries.get(post_id, {}).get("recommendations"),
                "segments": summaries.get(post_id, {}).get("segments"),
                "tools_mentioned": summaries.get(post_id, {}).get("tools_mentioned"),
                "contrarian_take": summaries.get(post_id, {}).get("contrarian_take"),
                "key_metrics": summaries.get(post_id, {}).get("key_metrics"),
                "evidence_links": summaries.get(post_id, {}).get("sources"),
                "freelancer_actions": data.get("freelancer_actions"),
                "client_playbook": data.get("client_playbook"),
                "measurement": data.get("measurement"),
                "risk_watchouts": data.get("risk_watchouts"),
                "draft_titles": data.get("draft_titles"),
                "confidence": data.get("confidence"),
                "llm_model": settings.llm_model_munger,
                "prompt_version": "v1",
            }
        )

    return selected


def persist(posts: list[Post]) -> None:
    """Persist outputs to Supabase using UPSERT semantics. Placeholder for now."""

    log.info("Persisting %d posts...", len(posts))


def main() -> None:
    log.info("Starting pipeline with settings loaded")
    _ = settings  # ensure settings is initialised
    posts = fetch_sources()
    processed = process(posts)
    persist(processed)
    log.info("Pipeline finished")


if __name__ == "__main__":
    main()
