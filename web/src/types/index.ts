// Re-export Supabase types for convenience
export type { Post, Comment, Insight } from './supabase'

// Legacy types for backward compatibility
export type LegacyInsight = {
  id: string;
  title: string;
  brief: string | null;
  permalink?: string | null;
  rank_score?: number | null;
  created_utc?: string | null;
  topics?: string[] | null;
  source?: string | null;
};