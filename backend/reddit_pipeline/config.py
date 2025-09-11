"""Configuration module for the Reddit Dashboard pipeline.

Loads settings from environment variables. Never hard-code secrets; use a
`.env` in development and CI secrets in production. This module provides a
single `Settings` object to be used across the codebase.
"""

from __future__ import annotations

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment separation is handled by how you load the `.env` file in
    development. In production (CI/host), rely on real environment variables.
    """

    # Reddit API
    reddit_client_id: str = Field(default=..., validation_alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default=..., validation_alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(
        default="reddit-dashboard/0.1.0", validation_alias="REDDIT_USER_AGENT"
    )

    # Optional external sources (disabled by default until API access is configured)
    hackernews_enabled: bool = Field(default=False, validation_alias="HACKERNEWS_ENABLED")
    producthunt_enabled: bool = Field(default=False, validation_alias="PRODUCTHUNT_ENABLED")

    # LLM / embeddings
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    llm_model_summariser: str = Field(
        default="gpt-4o-mini", validation_alias="LLM_MODEL_SUMMARISER"
    )
    llm_model_munger: str = Field(default="gpt-4o-mini", validation_alias="LLM_MODEL_MUNGER")
    embeddings_model: str = Field(
        default="text-embedding-3-large", validation_alias="EMBEDDINGS_MODEL"
    )
    embeddings_dim: int = Field(default=3072, validation_alias="EMBEDDINGS_DIM")

    # Orchestration limits
    top_n_posts: int = Field(default=20, validation_alias="TOP_N_POSTS")
    top_k_comments: int = Field(default=5, validation_alias="TOP_K_COMMENTS")
    summariser_max_input_tokens: int = Field(
        default=4000, validation_alias="SUMMARISER_MAX_INPUT_TOKENS"
    )
    http_timeout_seconds: int = Field(default=60, validation_alias="HTTP_TIMEOUT_SECONDS")

    # Reddit fetch controls
    reddit_lookback_days: int = Field(default=30, validation_alias="REDDIT_LOOKBACK_DAYS")
    reddit_min_comments: int = Field(default=5, validation_alias="REDDIT_MIN_COMMENTS")

    # Supabase
    supabase_url: AnyUrl = Field(default=..., validation_alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default=..., validation_alias="SUPABASE_ANON_KEY")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
