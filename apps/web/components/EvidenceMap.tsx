import type { EvidenceResponse } from "../lib/types";

export function EvidenceMap({ evidence }: { evidence: EvidenceResponse | null }) {
  return <section className="panel evidence-panel">
    <div className="panel-heading"><span className="step">04</span><div><h2>Evidence map</h2><p>Observed actions, not a mastery score.</p></div></div>
    {!evidence ? <p className="muted">Complete the prediction and controlled repair to generate evidence.</p> : <><h3>Graph traversal — {evidence.status}</h3><ul>{evidence.items.map((item) => <li key={item.label} className={item.state === "demonstrated" ? "pass" : "pending"}><strong>{item.state === "demonstrated" ? "✓" : "○"}</strong><span>{item.label}<small>{item.detail}</small></span></li>)}</ul><div className="next-action"><span className="eyebrow">Next targeted retry</span>{evidence.next_action}</div></>}
  </section>;
}

