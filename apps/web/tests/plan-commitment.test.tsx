import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { PlanCommitment } from "../components/PlanCommitment";

const plan = { objective: "", strategy: "", representation: "", invariant: "", complexity: "", planned_tests: "" };

describe("PlanCommitment", () => {
  it("offers transparent support levels and an editable guided starter", () => {
    const markup = renderToStaticMarkup(
      <PlanCommitment complete={false} onChange={() => undefined} onSubmit={() => undefined} onSupportChange={() => undefined} onUseStarterPlan={() => undefined} plan={plan} supportLevel="guided" />
    );

    expect(markup).toContain("Choose your support level");
    expect(markup).toContain("Load an editable starter plan");
    expect(markup).toContain("This changes guidance, not the challenge, evidence, or scoring.");
  });
});
