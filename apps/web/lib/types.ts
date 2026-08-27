export type PolicyMode = "no_code_help" | "hints_only" | "bounded_snippets";

export type Plan = {
  objective: string;
  strategy: string;
  representation: string;
  invariant: string;
  complexity: string;
  planned_tests: string;
};

export type CoachingCard = {
  id: string;
  title: string;
  misconception: string;
  corrective_question: string;
  hint?: string | null;
  snippet?: string | null;
};

export type EvidenceResponse = {
  status: string;
  items: { label: string; state: string; detail: string }[];
  next_action: string;
};

export type CodeFile = {
  path: string;
  language: string;
  symbols: string[];
  line_count: number;
};

export type CodeContext = {
  repository_id: string;
  source: string;
  files: CodeFile[];
  excluded_files: string[];
};

export type CodeReference = {
  file: string;
  start_line: number;
  end_line: number;
};

export type ChallengeCandidate = {
  objective_ref: string;
  code_refs: CodeReference[];
  template_id: string;
  evidence_plan: string[];
  rationale: string;
};
