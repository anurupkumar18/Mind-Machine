# Evidence Engine charter

## Thesis

The Evidence Engine verifies whether a learner can reason about and repair AI-assisted code. It is not a generic tutor, a grading system, or a mastery estimator.

## Evidence loop

`objective/policy -> plan commitment -> external mental model -> prediction -> controlled perturbation -> diagnosis/repair -> deterministic evidence -> targeted retry`

## MVP boundary

The hosted MVP accepts a public prompt and uses one synthetic Python graph fixture. It has no login, persistence, Canvas/GitHub integration, repository upload, arbitrary code execution, or model API.

Phase 2 exposes only an allowlisted, synthetic public-code fixture through `CodeContext`; arbitrary URLs and user repositories remain rejected in the hosted product. The private Codex V2 preview is a separate, explicit-consent local adapter: it may read only the authorized open workspace to produce a bounded source map, and may never upload it through an app-owned service, execute project code, or persist learner data.

## Architecture

- **Selection:** curated challenge templates now; a provider-neutral candidate interface later.
- **Evidence:** canonical Python variants and tests, never an LLM grade.
- **Interpretation:** qualitative, event-level evidence only.
- **Coaching:** fixture-defined Socratic runbooks may guide a learner through evidence, but never supply a repair implementation or determine pass/fail.
