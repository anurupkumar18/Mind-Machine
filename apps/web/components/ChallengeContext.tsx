import type { ChallengeCandidate, CodeContext } from "../lib/types";
import styles from "./ChallengeContext.module.css";

type ChallengeContextProps = {
  context: CodeContext | null;
  candidate: ChallengeCandidate | null;
  error: string | null;
  onRetry: () => void;
};

export function ChallengeContext({ context, candidate, error, onRetry }: ChallengeContextProps) {
  if (error) {
    return <section className={`panel ${styles.panel} ${styles.error}`} role="alert">
      <h2>Challenge context unavailable</h2>
      <p>{error}</p>
      <button className="secondary" onClick={onRetry}>Retry approved context</button>
    </section>;
  }

  if (!context || !candidate) {
    return <section className={`panel ${styles.panel}`} aria-busy="true"><p className="muted">Loading approved public challenge context…</p></section>;
  }

  return <section className={`panel ${styles.panel}`} aria-labelledby="challenge-context-title">
    <div className="panel-heading"><span className="step">00</span><div><h2 id="challenge-context-title">Challenge context</h2><p>Why this traversal challenge was selected before you commit a plan.</p></div></div>
    <div className={styles.source}><strong>{context.repository_id}</strong><span>{context.source.replaceAll("-", " ")}</span></div>
    <div className={styles.grid}>
      <div><h3>Approved code</h3>{context.files.map((file) => <div className={styles.file} key={file.path}><strong>{file.path}</strong><span>{file.language} · {file.line_count} lines</span><div className={styles.tags}>{file.symbols.map((symbol) => <span className={styles.tag} key={symbol}>{symbol}</span>)}</div></div>)}</div>
      <div><h3>Curated candidate</h3><p><strong>{candidate.template_id}</strong> — {candidate.objective_ref}</p><div className={styles.tags}>{candidate.evidence_plan.map((item) => <span className={styles.tag} key={item}>{item.replaceAll("_", " ")}</span>)}</div></div>
    </div>
    <p className={styles.rationale}>{candidate.rationale}</p>
    <p className={styles.references}>Selected reference: {candidate.code_refs.map((reference) => `${reference.file}, lines ${reference.start_line}–${reference.end_line}`).join("; ")}</p>
    <div className={styles.boundary}><strong>Public-fixture boundary</strong><span>Excluded: {context.excluded_files.join(", ")}.</span></div>
  </section>;
}
