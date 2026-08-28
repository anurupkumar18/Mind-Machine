import type { ChallengeCandidate, CoachingCard, CodeContext, EvidenceResponse, Plan, PolicyMode, SocraticResponse } from "./types";

const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const approvedRepositoryId = "public-graph-traversal";

export class EvidenceServiceError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = "EvidenceServiceError";
  }
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`);
  if (!response.ok) throw new EvidenceServiceError("The evidence service could not load the approved challenge context.", response.status);
  return response.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) throw new EvidenceServiceError("The evidence service could not verify this step.", response.status);
  return response.json() as Promise<T>;
}

export async function submitCheckpoint(plan: Plan, policyMode: PolicyMode): Promise<CoachingCard> {
  const response = await post<{ accepted: boolean; card: CoachingCard }>("/checkpoint", { plan, policy_mode: policyMode });
  return response.card;
}

export function getApprovedCodeContext(): Promise<CodeContext> {
  return get<CodeContext>(`/code-context/${approvedRepositoryId}`);
}

export function getApprovedChallengeCandidates(): Promise<ChallengeCandidate[]> {
  return get<ChallengeCandidate[]>(`/challenge-candidates/${approvedRepositoryId}`);
}

export function submitPrediction(predictedFrontier: string[]) {
  return post<{ correct: boolean; expected_frontier: string[]; observed_visited: string[] }>("/challenge/predict", {
    predicted_frontier: predictedFrontier
  });
}

export function submitDiagnosis(diagnosis: string, attempt: number): Promise<SocraticResponse> {
  return post<SocraticResponse>("/challenge/diagnose", { diagnosis, attempt });
}

export function submitConfirmation(repairTiming: string) {
  return post<{ tests_passed: boolean; result: string }>("/challenge/repair", { repair_timing: repairTiming });
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
