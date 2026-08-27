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

