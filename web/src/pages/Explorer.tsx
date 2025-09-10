import React from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "../lib/supabase";
import { Input } from "@/components/ui/input";
import { Section } from "@/components/ui/Section";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/ui/ErrorState";

export default function Explorer() {
  const [q, setQ] = React.useState("");
  const [source, setSource] = React.useState<string | undefined>(undefined);
  const [open, setOpen] = React.useState(false);
  const [selected, setSelected] = React.useState<any>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["explorer", q, source],
    queryFn: async () => {
      // SQL ilike fallback if RPC not available
      let query = supabase.from("insights").select("*").order("created_utc", { ascending: false }).limit(100);
      if (q) query = query.ilike("title", `%${q}%`);
      if (source) query = query.eq("source", source);
      const { data, error } = await query;
      if (error) throw error;
      return data ?? [];
    }
  });

  return (
    <div className="space-y-4">
      <Section
        title="Explorer"
        right={<button className="text-sm underline" onClick={() => refetch()}>Refresh</button>}
      >
        <div className="grid gap-3 md:grid-cols-3">
          <Input placeholder="Search (ilike)" value={q} onChange={(e) => setQ(e.target.value)} />
          <Input placeholder="Source filter (e.g. reddit, hn)" value={source ?? ""} onChange={(e) => setSource(e.target.value || undefined)} />
        </div>
      </Section>

      {isLoading ? (
        <Skeleton className="h-48 w-full rounded-2xl" />
      ) : isError ? (
        <ErrorState />
      ) : !data?.length ? (
        <div className="text-sm text-muted-foreground">No results.</div>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((i) => (
            <li key={i.id} className="p-3 rounded-xl border hover:bg-accent/50 cursor-pointer" onClick={() => { setSelected(i); setOpen(true); }}>
              <div className="font-medium">{i.title}</div>
              <div className="text-sm text-muted-foreground line-clamp-2">{i.brief}</div>
            </li>
          ))}
        </ul>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{selected?.title}</DialogTitle>
          </DialogHeader>
          <pre className="text-xs overflow-auto max-h-[60vh] bg-muted p-3 rounded-xl">
{JSON.stringify(selected, null, 2)}
          </pre>
        </DialogContent>
      </Dialog>
    </div>
  );
}


