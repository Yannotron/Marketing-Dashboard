-- Extensions
create extension if not exists vector;
create extension if not exists pg_trgm;

-- Run metadata
create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text check (status in ('started','success','failed')) default 'started',
  source_counts jsonb default '{}'::jsonb,
  log_url text
);

-- Sources
create table if not exists sources (
  id serial primary key,
  name text unique not null,        -- 'reddit','hn','producthunt'
  active boolean not null default true,
  config jsonb default '{}'::jsonb
);

-- Posts
create table if not exists posts (
  id text primary key,              -- native source ID e.g. reddit id
  source_id int references sources(id) on delete restrict,
  subreddit_or_channel text,
  title text not null,
  url text not null,
  author text,
  created_utc timestamptz not null,
  score int not null default 0,
  comments_count int not null default 0,
  upvote_ratio numeric,
  raw jsonb,
  language text default 'en',
  topics text[],
  keywords text[],
  rank_score numeric default 0,
  is_duplicate boolean default false,
  ingested_at timestamptz not null default now(),
  last_seen_at timestamptz
);

create index if not exists idx_posts_created on posts (created_utc desc);
create index if not exists idx_posts_rank on posts (rank_score desc);
create index if not exists idx_posts_trgm on posts using gin (title gin_trgm_ops);

-- Comments
create table if not exists comments (
  id text primary key,
  post_id text references posts(id) on delete cascade,
  author text,
  body text not null,
  score int default 0,
  created_utc timestamptz not null,
  raw jsonb
);
create index if not exists idx_comments_post on comments(post_id);

-- Embeddings
create table if not exists embeddings (
  id bigserial primary key,
  entity_type text check (entity_type in ('post','comment','insight')) not null,
  entity_id text not null,
  embedding vector(3072),           -- adjust to your model dimension
  created_at timestamptz not null default now()
);
create index if not exists idx_embeddings_vec on embeddings using ivfflat (embedding vector_cosine_ops);

-- Insights (LLM outputs)
create table if not exists insights (
  id uuid primary key default gen_random_uuid(),
  post_id text references posts(id) on delete cascade,
  summary text,
  pain_points jsonb,
  recommendations jsonb,
  segments jsonb,
  tools_mentioned text[],
  contrarian_take text,
  key_metrics jsonb,
  evidence_links text[],
  freelancer_actions jsonb,
  client_playbook jsonb,
  measurement jsonb,
  risk_watchouts jsonb,
  draft_titles text[],
  confidence numeric,
  llm_model text,
  prompt_version text,
  created_at timestamptz not null default now()
);
create index if not exists idx_insights_post on insights(post_id);
