import React from "react";

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="text-center text-sm text-muted-foreground border rounded-2xl p-10">
      <div className="font-medium text-foreground mb-1">{title}</div>
      {description && <p>{description}</p>}
    </div>
  );
}
