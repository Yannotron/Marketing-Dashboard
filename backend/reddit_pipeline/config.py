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
    reddit_client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(..., env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field("reddit-dashboard/0.1.0", env="REDDIT_USER_AGENT")

    # Optional external sources (disabled by default until API access is configured)
    hackernews_enabled: bool = Field(False, env="HACKERNEWS_ENABLED")
    producthunt_enabled: bool = Field(False, env="PRODUCTHUNT_ENABLED")

    # LLM / embeddings
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    llm_model_summariser: str = Field("gpt-4o-mini", env="LLM_MODEL_SUMMARISER")
    llm_model_munger: str = Field("gpt-4o-mini", env="LLM_MODEL_MUNGER")
    embeddings_model: str = Field("text-embedding-3-large", env="EMBEDDINGS_MODEL")
    embeddings_dim: int = Field(3072, env="EMBEDDINGS_DIM")

    # Orchestration limits
    top_n_posts: int = Field(20, env="TOP_N_POSTS")
    top_k_comments: int = Field(5, env="TOP_K_COMMENTS")
    summariser_max_input_tokens: int = Field(4000, env="SUMMARISER_MAX_INPUT_TOKENS")
    http_timeout_seconds: int = Field(60, env="HTTP_TIMEOUT_SECONDS")

    # Reddit fetch controls
    reddit_lookback_days: int = Field(30, env="REDDIT_LOOKBACK_DAYS")
    reddit_min_comments: int = Field(5, env="REDDIT_MIN_COMMENTS")

    # Supabase
    supabase_url: AnyUrl = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
