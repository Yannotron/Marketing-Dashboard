export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      posts: {
        Row: {
          id: string
          title: string
          score: number
          num_comments: number
          created_at: string
          subreddit: string
          author: string
          url: string
          text: string | null
          upvote_ratio: number | null
          is_self: boolean
          over_18: boolean
          spoiler: boolean
          locked: boolean
          stickied: boolean
          distinguished: string | null
          gilded: number
          archived: boolean
          contest_mode: boolean
          suggested_sort: string | null
          thumbnail: string | null
          thumbnail_width: number | null
          thumbnail_height: number | null
          preview: Json | null
          media: Json | null
          media_embed: Json | null
          secure_media: Json | null
          secure_media_embed: Json | null
          domain: string | null
          is_video: boolean
          post_hint: string | null
          permalink: string
          link_flair_text: string | null
          link_flair_css_class: string | null
          link_flair_background_color: string | null
          link_flair_text_color: string | null
          created_utc: number
          updated_at: string
        }
        Insert: {
          id: string
          title: string
          score: number
          num_comments: number
          created_at?: string
          subreddit: string
          author: string
          url: string
          text?: string | null
          upvote_ratio?: number | null
          is_self?: boolean
          over_18?: boolean
          spoiler?: boolean
          locked?: boolean
          stickied?: boolean
          distinguished?: string | null
          gilded?: number
          archived?: boolean
          contest_mode?: boolean
          suggested_sort?: string | null
          thumbnail?: string | null
          thumbnail_width?: number | null
          thumbnail_height?: number | null
          preview?: Json | null
          media?: Json | null
          media_embed?: Json | null
          secure_media?: Json | null
          secure_media_embed?: Json | null
          domain?: string | null
          is_video?: boolean
          post_hint?: string | null
          permalink: string
          link_flair_text?: string | null
          link_flair_css_class?: string | null
          link_flair_background_color?: string | null
          link_flair_text_color?: string | null
          created_utc: number
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          score?: number
          num_comments?: number
          created_at?: string
          subreddit?: string
          author?: string
          url?: string
          text?: string | null
          upvote_ratio?: number | null
          is_self?: boolean
          over_18?: boolean
          spoiler?: boolean
          locked?: boolean
          stickied?: boolean
          distinguished?: string | null
          gilded?: number
          archived?: boolean
          contest_mode?: boolean
          suggested_sort?: string | null
          thumbnail?: string | null
          thumbnail_width?: number | null
          thumbnail_height?: number | null
          preview?: Json | null
          media?: Json | null
          media_embed?: Json | null
          secure_media?: Json | null
          secure_media_embed?: Json | null
          domain?: string | null
          is_video?: boolean
          post_hint?: string | null
          permalink?: string
          link_flair_text?: string | null
          link_flair_css_class?: string | null
          link_flair_background_color?: string | null
          link_flair_text_color?: string | null
          created_utc?: number
          updated_at?: string
        }
        Relationships: []
      }
      comments: {
        Row: {
          id: string
          post_id: string
          body: string
          score: number
          author: string
          created_at: string
          created_utc: number
          parent_id: string | null
          is_submitter: boolean
          stickied: boolean
          distinguished: string | null
          gilded: number
          archived: boolean
          controversiality: number
          permalink: string
          updated_at: string
        }
        Insert: {
          id: string
          post_id: string
          body: string
          score: number
          author: string
          created_at?: string
          created_utc: number
          parent_id?: string | null
          is_submitter?: boolean
          stickied?: boolean
          distinguished?: string | null
          gilded?: number
          archived?: boolean
          controversiality?: number
          permalink: string
          updated_at?: string
        }
        Update: {
          id?: string
          post_id?: string
          body?: string
          score?: number
          author?: string
          created_at?: string
          created_utc?: number
          parent_id?: string | null
          is_submitter?: boolean
          stickied?: boolean
          distinguished?: string | null
          gilded?: number
          archived?: boolean
          controversiality?: number
          permalink?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "comments_post_id_fkey"
            columns: ["post_id"]
            isOneToOne: false
            referencedRelation: "posts"
            referencedColumns: ["id"]
          }
        ]
      }
      insights: {
        Row: {
          id: string
          post_id: string
          summary: string
          pain_points: string[]
          recommendations: string[]
          segments: string[]
          tools_mentioned: string[]
          contrarian_take: string
          key_metrics: string[]
          sources: string[]
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          post_id: string
          summary: string
          pain_points: string[]
          recommendations: string[]
          segments: string[]
          tools_mentioned: string[]
          contrarian_take: string
          key_metrics: string[]
          sources: string[]
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          post_id?: string
          summary?: string
          pain_points?: string[]
          recommendations?: string[]
          segments?: string[]
          tools_mentioned?: string[]
          contrarian_take?: string
          key_metrics?: string[]
          sources?: string[]
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "insights_post_id_fkey"
            columns: ["post_id"]
            isOneToOne: true
            referencedRelation: "posts"
            referencedColumns: ["id"]
          }
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

export type Tables<
  PublicTableNameOrOptions extends
    | keyof (Database["public"]["Tables"] & Database["public"]["Views"])
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof (Database[PublicTableNameOrOptions["schema"]]["Tables"] &
        Database[PublicTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? (Database[PublicTableNameOrOptions["schema"]]["Tables"] &
      Database[PublicTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : PublicTableNameOrOptions extends keyof (Database["public"]["Tables"] &
        Database["public"]["Views"])
    ? (Database["public"]["Tables"] &
        Database["public"]["Views"])[PublicTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  PublicTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? Database[PublicTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : PublicTableNameOrOptions extends keyof Database["public"]["Tables"]
    ? Database["public"]["Tables"][PublicTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  PublicTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? Database[PublicTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : PublicTableNameOrOptions extends keyof Database["public"]["Tables"]
    ? Database["public"]["Tables"][PublicTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  PublicEnumNameOrOptions extends
    | keyof Database["public"]["Enums"]
    | { schema: keyof Database },
  EnumName extends PublicEnumNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = PublicEnumNameOrOptions extends { schema: keyof Database }
  ? Database[PublicEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : PublicEnumNameOrOptions extends keyof Database["public"]["Enums"]
    ? Database["public"]["Enums"][PublicEnumNameOrOptions]
    : never

// Convenience types
export type Post = Tables<'posts'>
export type PostInsert = TablesInsert<'posts'>
export type PostUpdate = TablesUpdate<'posts'>

export type Comment = Tables<'comments'>
export type CommentInsert = TablesInsert<'comments'>
export type CommentUpdate = TablesUpdate<'comments'>

export type Insight = Tables<'insights'>
export type InsightInsert = TablesInsert<'insights'>
export type InsightUpdate = TablesUpdate<'insights'>

