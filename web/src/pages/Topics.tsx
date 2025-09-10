import React from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "../lib/supabase";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/ui/ErrorState";

const CATEGORIES = ["SEO", "PPC", "Content", "Analytics"] as const;

export default function Topics() {
  const [sort, setSort] = React.useState<"rank_score" | "created_utc">("rank_score");

  return (
    <Tabs defaultValue="SEO">
      <div className="flex items-center justify-between mb-3">
        <TabsList>
          {CATEGORIES.map((c) => (
            <TabsTrigger key={c} value={c}>{c}</TabsTrigger>
          ))}
        </TabsList>
        <Select value={sort} onValueChange={(v) => setSort(v as any)}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Sort by" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="rank_score">Rank score</SelectItem>
            <SelectItem value="created_utc">Created</SelectItem>
          </SelectContent>
        </Select>
      </div>
      {CATEGORIES.map((c) => (
        <TabsContent key={c} value={c} className="mt-0">
          <TopicList topic={c} sort={sort} />
        </TabsContent>
      ))}
    </Tabs>
  );
}

function TopicList({ topic, sort }: { topic: string; sort: "rank_score" | "created_utc" }) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["topic", topic, sort],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("insights")
        .select("id,title,brief,rank_score,created_utc,topics")
        .contains("topics", [topic])
        .order(sort, { ascending: sort === "created_utc" })
        .limit(50);
      if (error) throw error;
      return data ?? [];
    }
  });

  if (isLoading) return <Skeleton className="h-48 w-full rounded-2xl" />;
  if (isError) return <ErrorState message={(error as any)?.message} />;

  if (!data?.length) return <div className="text-sm text-muted-foreground">No results.</div>;

  return (
    <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {data.map((i) => (
        <li key={i.id} className="p-3 rounded-xl border hover:bg-accent/50">
          <div className="font-medium">{i.title}</div>
          <div className="text-sm text-muted-foreground line-clamp-2">{i.brief}</div>
        </li>
      ))}
    </ul>
  );
}


