import type { FormEvent } from "react";
import type { Plan, SupportLevel } from "../lib/types";

const fields: { key: keyof Plan; label: string; placeholder: string; help: string }[] = [
  { key: "objective", label: "What do you want to understand?", placeholder: "Explain how BFS explores a graph", help: "Say the idea you want to practice in your own words." },
  { key: "strategy", label: "What is your first move?", placeholder: "Use a first-in, first-out queue", help: "Describe the approach before you see the result." },
  { key: "representation", label: "How is the graph shown?", placeholder: "A list of each node's neighbors", help: "Name the structure that holds the connections." },
  { key: "invariant", label: "What must stay true?", placeholder: "A node is marked before another parent can add it", help: "An invariant is a rule the algorithm should never break." },
  { key: "complexity", label: "What work do you expect?", placeholder: "Visit nodes and edges once: O(V + E)", help: "A rough explanation is enough; you can revise it later." },
  { key: "planned_tests", label: "What example will you check?", placeholder: "A graph where two paths reach the same node", help: "Choose a case that could expose a mistake." }
];

const supportOptions: { id: SupportLevel; title: string; description: string }[] = [
  { id: "guided", title: "Guided start", description: "See plain-language explanations and load an editable starter draft." },
  { id: "supported", title: "Some support", description: "Keep the prompts and short examples while you write your own plan." },
  { id: "independent", title: "Independent", description: "Use concise prompts with no starter draft." }
];

export function PlanCommitment({ plan, onChange, onSubmit, complete, supportLevel, onSupportChange, onUseStarterPlan }: { plan: Plan; onChange: (plan: Plan) => void; onSubmit: () => void; complete: boolean; supportLevel: SupportLevel; onSupportChange: (level: SupportLevel) => void; onUseStarterPlan: () => void }) {
  function submit(event: FormEvent) { event.preventDefault(); onSubmit(); }
  return <section className="panel plan-panel">
    <div className="panel-heading"><span className="step">01</span><div><h2>Start with a prediction, not a blank page</h2><p>There is no score for this plan. It captures your current thinking so you can compare it with what the graph shows next.</p></div></div>
    <section className="onramp" aria-label="Learning support">
      <div><span className="eyebrow">Choose your support level</span><strong>How much help would you like to start?</strong><p>This changes guidance, not the challenge, evidence, or scoring.</p></div>
      <div className="support-options">{supportOptions.map((option) => <button aria-pressed={supportLevel === option.id} className={supportLevel === option.id ? "selected" : ""} key={option.id} type="button" onClick={() => onSupportChange(option.id)}><strong>{option.title}</strong><span>{option.description}</span></button>)}</div>
      {supportLevel === "guided" && <button className="secondary starter-plan" type="button" onClick={onUseStarterPlan}>Load an editable starter plan</button>}
    </section>
    <form onSubmit={submit}>
      <div className="field-grid">{fields.map((field) => <label key={field.key}>{field.label}<small>{supportLevel === "independent" ? "Write your current best answer." : field.help}</small><input required minLength={3} value={plan[field.key]} placeholder={field.placeholder} onChange={(event) => onChange({ ...plan, [field.key]: event.target.value })} /></label>)}</div>
      <button className="primary" type="submit">{complete ? "Use this plan to get coaching" : "Save my current thinking"}</button>
    </form>
  </section>;
}
