import type { SocraticResponse, SocraticSession } from "../lib/types";
import styles from "./SocraticCoach.module.css";

const diagnosisChoices = [
  { id: "late_frontier_recognition", label: "The traversal recognizes a discovered node too late, allowing another parent to add it first." },
  { id: "wrong_queue_order", label: "The queue processes siblings in the wrong order." },
  { id: "missing_cycle_exit", label: "The traversal needs to stop immediately when it sees a cycle." }
];

const timingChoices = [
  { id: "frontier_entry", label: "When the node enters the frontier" },
  { id: "frontier_exit", label: "When the node leaves the frontier" },
  { id: "traversal_end", label: "After the traversal finishes" }
];

type SocraticCoachProps = {
  visible: boolean;
  session: SocraticSession;
  guidance: SocraticResponse | null;
  onDiagnose: (choice: string) => void;
  onConfirm: (timing: string) => void;
};

export function SocraticCoach({ visible, session, guidance, onDiagnose, onConfirm }: SocraticCoachProps) {
  if (!visible) return null;

  return <section className="panel diagnosis-panel"><div className="panel-heading"><span className="step">03</span><div><h2>Diagnose the controlled mutation</h2><p>D can enter the frontier twice after B and C each discover it. Commit to the mechanism before seeing the canonical result.</p></div></div><div className={styles.choices}>{diagnosisChoices.map((choice) => <button className={`secondary ${styles.choice}`} key={choice.id} disabled={session.diagnosis_accepted} onClick={() => onDiagnose(choice.id)}>{choice.label}</button>)}</div>{guidance && <div className={styles.guidance}><span className="eyebrow">{guidance.stage} · scaffold {guidance.scaffold_level || "confirm"}</span><p>{guidance.observation}</p><strong>{guidance.question}</strong></div>}{session.diagnosis_accepted && <div className={styles.confirmation}><span className="eyebrow">Confirm</span><p>Choose the lifecycle event that makes your diagnosis testable.</p><div className={styles.choices}>{timingChoices.map((choice) => <button className={`secondary ${styles.choice}`} key={choice.id} disabled={session.repair_passed} onClick={() => onConfirm(choice.id)}>{choice.label}</button>)}</div>{session.repair_passed && <p className="success">Canonical traversal tests passed after your conceptual confirmation.</p>}</div>}</section>;
}
