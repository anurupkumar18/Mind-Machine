import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { SocraticCoach } from "../components/SocraticCoach";

describe("SocraticCoach", () => {
  it("offers conceptual confirmation without displaying repair code", () => {
    const markup = renderToStaticMarkup(
      <SocraticCoach
        guidance={{ accepted: true, stage: "confirm", scaffold_level: 0, observation: "A discovery is delayed.", question: "When is it recorded?" }}
        onConfirm={() => undefined}
        onDiagnose={() => undefined}
        session={{ phase: "confirm", diagnosis_attempts: 1, diagnosis_accepted: true, repair_passed: false, retry_scheduled: false }}
        visible
      />
    );

    expect(markup).toContain("When the node enters the frontier");
    expect(markup).not.toContain("visited.add");
  });
});
