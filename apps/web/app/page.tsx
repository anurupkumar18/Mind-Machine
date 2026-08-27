"use client";

import { useEffect, useMemo, useState } from "react";
import { getApprovedChallengeCandidates, getApprovedCodeContext, getEvidence, submitCheckpoint, submitPrediction, submitRepair } from "../lib/api";
import type { ChallengeCandidate, CoachingCard, CodeContext, EvidenceResponse, Plan, PolicyMode } from "../lib/types";
import { ChallengeContext } from "../components/ChallengeContext";
import { EvidenceMap } from "../components/EvidenceMap";
import { GraphLab } from "../components/GraphLab";
import { PlanCommitment } from "../components/PlanCommitment";
import { PolicyBar } from "../components/PolicyBar";

const emptyPlan: Plan = { objective: "", strategy: "", representation: "", invariant: "", complexity: "", planned_tests: "" };

function initialPlan(): Plan {
  if (typeof window === "undefined") return emptyPlan;
  const saved = window.sessionStorage.getItem("evidence-engine-plan");
  return saved ? JSON.parse(saved) as Plan : emptyPlan;
}

export default function Home() {
  const [plan, setPlan] = useState<Plan>(initialPlan);
  const [policyMode, setPolicyMode] = useState<PolicyMode>("bounded_snippets");
  const [card, setCard] = useState<CoachingCard | null>(null);
  const [predicted, setPredicted] = useState<string[]>([]);
  const [predictionCorrect, setPredictionCorrect] = useState<boolean | null>(null);
  const [repairPassed, setRepairPassed] = useState(false);
  const [retryScheduled, setRetryScheduled] = useState(false);
  const [evidence, setEvidence] = useState<EvidenceResponse | null>(null);
  const [codeContext, setCodeContext] = useState<CodeContext | null>(null);
  const [candidate, setCandidate] = useState<ChallengeCandidate | null>(null);
  const [error, setError] = useState("");

  useEffect(() => { sessionStorage.setItem("evidence-engine-plan", JSON.stringify(plan)); }, [plan]);
  useEffect(() => {
    let active = true;
    Promise.all([getApprovedCodeContext(), getApprovedChallengeCandidates()])
      .then(([context, candidates]) => {
        if (!active) return;
        setCodeContext(context);
        setCandidate(candidates[0] ?? null);
      })
      .catch((caught) => { if (active) setError(caught instanceof Error ? caught.message : "Unable to load the approved challenge context."); });
    return () => { active = false; };
  }, []);
  const planComplete = useMemo(() => Object.values(plan).every((value) => value.trim().length >= 3), [plan]);

  async function commitPlan() { try { setError(""); setCard(await submitCheckpoint(plan, policyMode)); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to verify your plan."); } }
  async function revealPrediction() { try { setError(""); const result = await submitPrediction(predicted); setPredictionCorrect(result.correct); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to verify your prediction."); } }
  async function repair() { try { setError(""); const result = await submitRepair(); setRepairPassed(result.tests_passed); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to verify the repair."); } }
  async function buildEvidence() { if (predictionCorrect === null) return; try { setEvidence(await getEvidence({ prediction_correct: predictionCorrect, invariant_preserved: true, cycle_counterexample_passed: repairPassed, repair_passed: repairPassed, retry_scheduled: retryScheduled })); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to build evidence."); } }

  return <main>
    <header className="hero"><div><span className="eyebrow">Evidence Engine / Traversal Lab</span><h1>Make your reasoning observable.</h1><p>Commit to a plan, model the graph state, then let deterministic evidence challenge your assumptions.</p></div><aside><strong>Public fixture only</strong><span>No accounts. No repository uploads. No mastery score.</span></aside></header>
    <PolicyBar policyMode={policyMode} onChange={setPolicyMode} />
    {error && <p role="alert" className="alert">{error}</p>}
    <div className="workspace"><div className="primary-column"><ChallengeContext context={codeContext} candidate={candidate} /><PlanCommitment plan={plan} onChange={setPlan} onSubmit={commitPlan} complete={planComplete} />{card && <section className="coach-card"><span className="eyebrow">Evidence-backed coaching</span><h2>{card.title}</h2><p>{card.misconception}</p><strong>{card.corrective_question}</strong>{card.hint && <p className="hint">Hint: {card.hint}</p>}{card.snippet && <pre><code>{card.snippet}</code></pre>}</section>}<GraphLab predicted={predicted} onToggle={(node) => setPredicted((current) => current.includes(node) ? current.filter((item) => item !== node) : [...current, node])} revealed={predictionCorrect !== null} correct={predictionCorrect ?? undefined} />{card && predictionCorrect === null && <button className="primary reveal" disabled={predicted.length === 0} onClick={revealPrediction}>Commit prediction & reveal state</button>}<section className="panel repair-panel"><div className="panel-heading"><span className="step">03</span><div><h2>Repair the controlled mutation</h2><p>The mutation marks a node when dequeued, so D can enter twice.</p></div></div><code>Move <strong>visited.add(neighbor)</strong> before <strong>frontier.append(neighbor)</strong>.</code><button className="secondary" disabled={predictionCorrect === null || repairPassed} onClick={repair}>{repairPassed ? "Canonical tests passed" : "Apply allowlisted repair & run tests"}</button></section></div><div className="side-column"><EvidenceMap evidence={evidence} /><label className="retry"><input type="checkbox" checked={retryScheduled} onChange={(event) => setRetryScheduled(event.target.checked)} /> Schedule a retry with a new graph.</label><button className="primary" disabled={predictionCorrect === null} onClick={buildEvidence}>Generate evidence map</button></div></div>
  </main>;
}
