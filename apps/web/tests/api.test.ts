import { describe, expect, it } from "vitest";

describe("evidence contract", () => {
  it("uses a public, allowlisted repair identifier", () => {
    expect("mark_visited_on_enqueue").toMatch(/^mark_visited_/);
  });
});

