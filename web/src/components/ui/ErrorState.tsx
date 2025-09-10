import React from "react";

export function ErrorState({ message }: { message?: string }) {
  return (
    <div className="text-sm text-red-600 border border-red-200 rounded-2xl p-4 bg-red-50">
      {message ?? "Something went wrong."}
    </div>
  );
}
