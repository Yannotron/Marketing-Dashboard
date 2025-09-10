import React from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "../lib/supabase";
import { Card } from "@/components/ui/card";
import { Section } from "@/components/ui/Section";
import { ResponsiveContainer, LineChart, Line, Tooltip } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/ui/ErrorState";

async function fetchOverview() {
  // Check if we're in demo mode (no valid Supabase credentials)
  const isDemoMode = !import.meta.env.VITE_SUPABASE_URL || 
    import.meta.env.VITE_SUPABASE_URL === "your_supabase_url_here";
  
  if (isDemoMode) {
    // Return demo data
    const spark = Array.from({ length: 7 }).map((_, i) => ({ d: i, v: Math.floor(Math.random() * 10) + 1 }));
    return { 
      lastRun: { status: "completed", created_at: new Date().toISOString() }, 
      count7d: 42, 
      spark 
    };
  }

  // Real Supabase queries
  const [runs, insights] = await Promise.all([
    supabase.from("pipeline_runs").select("status,created_at").order("created_at", { ascending: false }).limit(1),
    supabase.from("insights").select("id,created_utc").gte("created_utc", new Date(Date.now() - 1000*60*60*24*7).toISOString())
  ]);
  if (runs.error) throw runs.error;
  if (insights.error) throw insights.error;
  const spark = Array.from({ length: 7 }).map((_, i) => ({ d: i, v: 0 }));
  insights.data?.forEach(() => { spark[Math.floor(Math.random()*7)].v += 1; });
  return { lastRun: runs.data?.[0], count7d: insights.data?.length ?? 0, spark };
}

export default function Overview() {
  const { data, isLoading, isError, error } = useQuery({ queryKey: ["overview"], queryFn: fetchOverview });

  if (isLoading) return <Skeleton className="h-56 w-full rounded-2xl" />;
  if (isError) return <ErrorState message={(error as any)?.message} />;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card className="p-4 rounded-2xl shadow-sm">
        <Section title="Last run status">
          <div className="text-sm">
            <div className="font-medium">{data?.lastRun?.status ?? "Unknown"}</div>
            <div className="text-muted-foreground">{data?.lastRun?.created_at}</div>
          </div>
        </Section>
        <Section title="Insights this week">
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data?.spark ?? []}>
                <Tooltip />
                <Line type="monotone" dataKey="v" stroke="#2563eb" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Section>
      </Card>
      <Card className="p-4 rounded-2xl shadow-sm">
        <Section title="Top 10 insights">
          <TopInsights />
        </Section>
      </Card>
    </div>
  );
}

function TopInsights() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["top-insights"],
    queryFn: async () => {
      // Check if we're in demo mode
      const isDemoMode = !import.meta.env.VITE_SUPABASE_URL || 
        import.meta.env.VITE_SUPABASE_URL === "your_supabase_url_here";
      
      if (isDemoMode) {
        // Return demo data
        return [
          {
            id: "1",
            title: "Reddit's New Moderation Tools Are Game-Changing",
            brief: "Community moderators are reporting significant improvements in content quality after implementing the latest moderation features.",
            permalink: "https://reddit.com/r/modnews/comments/example1",
            rank_score: 95
          },
          {
            id: "2", 
            title: "SEO Best Practices for Reddit Marketing",
            brief: "A comprehensive guide on how to effectively market your business on Reddit without violating community guidelines.",
            permalink: "https://reddit.com/r/marketing/comments/example2",
            rank_score: 88
          },
          {
            id: "3",
            title: "The Future of Content Creation on Social Platforms",
            brief: "Analysis of how Reddit's recent policy changes are shaping the landscape of user-generated content.",
            permalink: "https://reddit.com/r/technology/comments/example3",
            rank_score: 82
          }
        ];
      }

      // Real Supabase query
      const { data, error } = await supabase
        .from("insights")
        .select("id,title,brief,permalink,rank_score")
        .order("rank_score", { ascending: false })
        .limit(10);
      if (error) throw error;
      return data ?? [];
    }
  });

  if (isLoading) return <Skeleton className="h-40 w-full rounded-2xl" />;
  if (isError) return <ErrorState />;
  if (!data?.length) return <div className="text-sm text-muted-foreground">No insights found.</div>;

  return (
    <ul className="space-y-3">
      {data.map((i) => (
        <li key={i.id} className="p-3 rounded-xl border hover:bg-accent/50">
          <div className="font-medium">{i.title}</div>
          <div className="text-sm text-muted-foreground line-clamp-2">{i.brief}</div>
          <a className="text-sm text-primary underline" href={i.permalink ?? "#"} target="_blank" rel="noreferrer">Open on Reddit</a>
        </li>
      ))}
    </ul>
  );
}


