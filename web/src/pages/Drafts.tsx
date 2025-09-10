import React from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "../lib/supabase";
import { Button } from "@/components/ui/button";
import { Section } from "@/components/ui/Section";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/ui/ErrorState";

function toMarkdown(item: any) {
  const fm = [
    "---",
    `title: "${item.title?.replace(/"/g, '\\"') ?? ""}"`,
    `date: ${item.created_utc ?? new Date().toISOString()}`,
    `source: ${item.source ?? "reddit"}`,
    "---",
    "",
    item.brief ?? "",
  ].join("\n");
  return fm + "\n";
}

function download(name: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export default function Drafts() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["drafts"],
    queryFn: async () => {
      const { data, error } = await supabase.from("drafts").select("id,draft_title,created_utc,source,brief").order("created_utc", { ascending: false }).limit(100);
      if (error) throw error;
      return data ?? [];
    }
  });

  if (isLoading) return <Skeleton className="h-48 w-full rounded-2xl" />;
  if (isError) return <ErrorState message={(error as any)?.message} />;

  if (!data?.length) return <div className="text-sm text-muted-foreground">No drafts yet.</div>;

  return (
    <Section title="Drafts">
      <ul className="space-y-3">
        {data.map((d) => (
          <li key={d.id} className="p-3 rounded-xl border flex items-center justify-between">
            <div>
              <div className="font-medium">{d.draft_title}</div>
              <div className="text-xs text-muted-foreground">{d.created_utc}</div>
            </div>
            <Button variant="default" onClick={() => download(`${(d.draft_title ?? "draft").replace(/\s+/g, "-").toLowerCase()}.md`, toMarkdown(d))}>Export Markdown</Button>
          </li>
        ))}
      </ul>
    </Section>
  );
}


