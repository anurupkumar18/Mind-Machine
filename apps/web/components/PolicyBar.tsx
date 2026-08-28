import type { PolicyMode } from "../lib/types";

const labels: Record<PolicyMode, string> = {
  no_code_help: "No code help",
  hints_only: "Hints only"
};

export function PolicyBar({ policyMode, onChange }: { policyMode: PolicyMode; onChange: (mode: PolicyMode) => void }) {
  return <section className="policy-bar" aria-label="Instructor policy">
    <div><span className="eyebrow">Public practice only</span><strong>Instructor AI-use policy</strong></div>
    <div className="policy-options">
      {(Object.keys(labels) as PolicyMode[]).map((mode) => <button key={mode} className={mode === policyMode ? "selected" : ""} onClick={() => onChange(mode)}>{labels[mode]}</button>)}
    </div>
  </section>;
}
