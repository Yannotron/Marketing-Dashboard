import { describe, it, expect } from "vitest";
import React from "react";
import { createRoot } from "react-dom/client";

describe("smoke", () => {
  it("mounts root", () => {
    const div = document.createElement("div");
    expect(() => {
      const root = createRoot(div);
      // @ts-ignore
      root.render(React.createElement("div"));
      root.unmount();
    }).not.toThrow();
  });
});
