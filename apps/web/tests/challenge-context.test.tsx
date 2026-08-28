import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { ChallengeContext } from "../components/ChallengeContext";

describe("ChallengeContext", () => {
  it("replaces loading with a retriable error state", () => {
    const markup = renderToStaticMarkup(
      <ChallengeContext candidate={null} context={null} error="The evidence service could not load the approved challenge context." onRetry={() => undefined} />
    );

    expect(markup).toContain("Challenge context unavailable");
    expect(markup).toContain("Retry approved context");
    expect(markup).not.toContain("Loading approved public challenge context");
  });
});
