import type { CoachingCard, EvidenceResponse, Plan, PolicyMode } from "./types";

const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) throw new Error("The evidence service could not verify this step.");
  return response.json() as Promise<T>;
}

export async function submitCheckpoint(plan: Plan, policyMode: PolicyMode): Promise<CoachingCard> {
  const response = await post<{ accepted: boolean; card: CoachingCard }>("/checkpoint", { plan, policy_mode: policyMode });
  return response.card;
}

export function submitPrediction(predictedFrontier: string[]) {
  return post<{ correct: boolean; expected_frontier: string[]; observed_visited: string[] }>("/challenge/predict", {
    predicted_frontier: predictedFrontier
  });
}

export function submitRepair() {
  return post<{ tests_passed: boolean; result: string }>("/challenge/repair", { repair_id: "mark_visited_on_enqueue" });
}

export function getEvidence(input: {
  prediction_correct: boolean;
  invariant_preserved: boolean;
  cycle_counterexample_passed: boolean;
  repair_passed: boolean;
  retry_scheduled: boolean;
}): Promise<EvidenceResponse> {
  return post<EvidenceResponse>("/evidence", input);
}

