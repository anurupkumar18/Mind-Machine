import type { FormEvent } from "react";
import type { Plan } from "../lib/types";

const fields: { key: keyof Plan; label: string; placeholder: string }[] = [
  { key: "objective", label: "Learning objective", placeholder: "Explain BFS traversal invariants" },
  { key: "strategy", label: "Approach", placeholder: "Use a FIFO queue and process one level at a time" },
  { key: "representation", label: "Graph representation", placeholder: "Adjacency list" },
  { key: "invariant", label: "Invariant", placeholder: "Every queued node is already visited" },
  { key: "complexity", label: "Complexity", placeholder: "O(V + E)" },
  { key: "planned_tests", label: "Planned tests", placeholder: "Cycle and converging-parent graph" }
];

export function PlanCommitment({ plan, onChange, onSubmit, complete }: { plan: Plan; onChange: (plan: Plan) => void; onSubmit: () => void; complete: boolean }) {
  function submit(event: FormEvent) { event.preventDefault(); onSubmit(); }
  return <section className="panel plan-panel">
    <div className="panel-heading"><span className="step">01</span><div><h2>Commit to a plan</h2><p>Write your reasoning before the system reveals evidence.</p></div></div>
    <form onSubmit={submit}>
      <div className="field-grid">{fields.map((field) => <label key={field.key}>{field.label}<input required minLength={3} value={plan[field.key]} placeholder={field.placeholder} onChange={(event) => onChange({ ...plan, [field.key]: event.target.value })} /></label>)}</div>
      <button className="primary" type="submit">{complete ? "Refresh coaching card" : "Commit plan"}</button>
    </form>
  </section>;
}

