"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { EvidenceServiceError, getApprovedChallengeCandidates, getApprovedCodeContext, getEvidence, submitCheckpoint, submitConfirmation, submitDiagnosis, submitPrediction } from "../lib/api";
import type { ChallengeCandidate, CoachingCard, CodeContext, EvidenceResponse, Plan, PolicyMode, SocraticResponse, SocraticSession, SupportLevel } from "../lib/types";
import { ChallengeContext } from "../components/ChallengeContext";
import { EvidenceMap } from "../components/EvidenceMap";
import { GraphLab } from "../components/GraphLab";
import { PlanCommitment } from "../components/PlanCommitment";
import { PolicyBar } from "../components/PolicyBar";
import { SocraticCoach } from "../components/SocraticCoach";

const emptyPlan: Plan = { objective: "", strategy: "", representation: "", invariant: "", complexity: "", planned_tests: "" };
const emptySession: SocraticSession = { phase: "read", diagnosis_attempts: 0, diagnosis_accepted: false, repair_passed: false, retry_scheduled: false };
const guidedStarterPlan: Plan = { objective: "Explain how BFS explores a graph", strategy: "Use a first-in, first-out queue", representation: "A list of each node's neighbors", invariant: "Mark a node before another parent can add it", complexity: "Visit nodes and edges once: O(V + E)", planned_tests: "A graph where two paths reach the same node" };

function readSessionValue<T>(key: string, fallback: T): T {
  const saved = window.sessionStorage.getItem(key);
  if (!saved) return fallback;
  try { return JSON.parse(saved) as T; } catch { return fallback; }
}

async function loadApprovedChallenge(): Promise<{ context: CodeContext; candidate: ChallengeCandidate }> {
  const [context, candidates] = await Promise.all([getApprovedCodeContext(), getApprovedChallengeCandidates()]);
  const candidate = candidates[0];
  if (!candidate) throw new Error("The approved fixture has no curated challenge candidate.");
  return { context, candidate };
}

export default function Home() {
  const [plan, setPlan] = useState<Plan>(emptyPlan);
  const [supportLevel, setSupportLevel] = useState<SupportLevel>("guided");
  const [policyMode, setPolicyMode] = useState<PolicyMode>("hints_only");
  const [card, setCard] = useState<CoachingCard | null>(null);
  const [predicted, setPredicted] = useState<string[]>([]);
  const [predictionCorrect, setPredictionCorrect] = useState<boolean | null>(null);
  const [session, setSession] = useState<SocraticSession>(emptySession);
  const [guidance, setGuidance] = useState<SocraticResponse | null>(null);
  const [evidence, setEvidence] = useState<EvidenceResponse | null>(null);
  const [codeContext, setCodeContext] = useState<CodeContext | null>(null);
  const [candidate, setCandidate] = useState<ChallengeCandidate | null>(null);
  const [contextError, setContextError] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [sessionHydrated, setSessionHydrated] = useState(false);
  const latestContextRequest = useRef(0);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      setPlan(readSessionValue("evidence-engine-plan", emptyPlan));
      setSession(readSessionValue("evidence-engine-socratic-session", emptySession));
      const savedSupportLevel = sessionStorage.getItem("evidence-engine-support-level");
      if (savedSupportLevel === "supported" || savedSupportLevel === "independent") setSupportLevel(savedSupportLevel);
      setSessionHydrated(true);
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);
  useEffect(() => { if (sessionHydrated) sessionStorage.setItem("evidence-engine-plan", JSON.stringify(plan)); }, [plan, sessionHydrated]);
  useEffect(() => { if (sessionHydrated) sessionStorage.setItem("evidence-engine-support-level", supportLevel); }, [supportLevel, sessionHydrated]);
  useEffect(() => { if (sessionHydrated) sessionStorage.setItem("evidence-engine-socratic-session", JSON.stringify(session)); }, [session, sessionHydrated]);
  const loadLatestChallengeContext = useCallback((requestId: number) => {
    void loadApprovedChallenge()
      .then(({ context, candidate }) => {
        if (requestId !== latestContextRequest.current) return;
        setCodeContext(context);
        setCandidate(candidate);
        setContextError(null);
      })
      .catch((caught) => {
        if (requestId !== latestContextRequest.current) return;
        setCodeContext(null);
        setCandidate(null);
        setContextError(caught instanceof Error ? caught.message : "Unable to load the approved challenge context.");
      });
  }, []);
  const retryChallengeContext = useCallback(() => {
    latestContextRequest.current += 1;
    setContextError(null);
    loadLatestChallengeContext(latestContextRequest.current);
  }, [loadLatestChallengeContext]);
  useEffect(() => {
    latestContextRequest.current += 1;
    loadLatestChallengeContext(latestContextRequest.current);
  }, [loadLatestChallengeContext]);
  const planComplete = useMemo(() => Object.values(plan).every((value) => value.trim().length >= 3), [plan]);

  async function commitPlan() {
    try {
      setError("");
      setCard(await submitCheckpoint(plan, policyMode));
      setSession((current) => ({ ...current, phase: "assess" }));
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to assess your plan."); }
  }
  async function revealPrediction() {
    try {
      setError("");
      const result = await submitPrediction(predicted);
      setPredictionCorrect(result.correct);
      setSession((current) => ({ ...current, phase: "guide" }));
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to verify your prediction."); }
  }
  async function diagnose(choice: string) {
    try {
      setError("");
      const attempt = Math.min(session.diagnosis_attempts + 1, 3);
      const result = await submitDiagnosis(choice, attempt);
      setGuidance(result);
      setSession((current) => ({ ...current, phase: result.stage, diagnosis_attempts: attempt, diagnosis_accepted: result.accepted }));
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to assess the diagnostic commitment."); }
  }
  async function confirmRepair(timing: string) {
    try {
      setError("");
      const result = await submitConfirmation(timing);
      setSession((current) => ({ ...current, phase: "confirm", repair_passed: result.tests_passed }));
    } catch (caught) { setError(caught instanceof EvidenceServiceError && caught.status === 400 ? "Choose the lifecycle event that preserves the invariant." : caught instanceof Error ? caught.message : "Unable to confirm this lifecycle event."); }
  }
  async function buildEvidence() {
    if (predictionCorrect === null) return;
    try {
      setEvidence(await getEvidence({ prediction_correct: predictionCorrect, invariant_preserved: session.diagnosis_accepted, cycle_counterexample_passed: session.repair_passed, repair_passed: session.repair_passed, retry_scheduled: session.retry_scheduled }));
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to build evidence."); }
  }

  return <main>
    <header className="hero"><div><span className="eyebrow">Evidence Engine / Traversal Lab</span><h1>Make your reasoning observable.</h1><p>Commit to a plan, model graph state, diagnose a controlled mutation, then inspect deterministic evidence.</p></div><aside><strong>Public fixture only</strong><span>No accounts. No repository uploads. No mastery score.</span></aside></header>
    <PolicyBar policyMode={policyMode} onChange={setPolicyMode} />
    {error && <p role="alert" className="alert">{error}</p>}
    <div className="workspace"><div className="primary-column">
      <ChallengeContext context={codeContext} candidate={candidate} error={contextError} onRetry={retryChallengeContext} />
      <PlanCommitment plan={plan} onChange={setPlan} onSubmit={commitPlan} complete={planComplete} supportLevel={supportLevel} onSupportChange={setSupportLevel} onUseStarterPlan={() => setPlan(guidedStarterPlan)} />
      {card && <section className="coach-card"><span className="eyebrow">Assess</span><h2>{card.title}</h2><p>{card.misconception}</p><strong>{card.corrective_question}</strong>{card.hint && <p className="hint">Hint: {card.hint}</p>}</section>}
      <GraphLab predicted={predicted} onToggle={(node) => setPredicted((current) => current.includes(node) ? current.filter((item) => item !== node) : [...current, node])} revealed={predictionCorrect !== null} correct={predictionCorrect ?? undefined} />
      {card && predictionCorrect === null && <button className="primary reveal" disabled={predicted.length === 0} onClick={revealPrediction}>Commit prediction & reveal state</button>}
      <SocraticCoach guidance={guidance} onConfirm={(timing) => void confirmRepair(timing)} onDiagnose={(choice) => void diagnose(choice)} session={session} visible={predictionCorrect !== null} />
    </div><div className="side-column"><EvidenceMap evidence={evidence} />{session.repair_passed && <label className="retry"><input type="checkbox" checked={session.retry_scheduled} onChange={(event) => setSession((current) => ({ ...current, retry_scheduled: event.target.checked }))} /> Schedule a retry with a new graph.</label>}<button className="primary" disabled={predictionCorrect === null || !session.repair_passed} onClick={buildEvidence}>Generate evidence map</button></div></div>
  </main>;
}
