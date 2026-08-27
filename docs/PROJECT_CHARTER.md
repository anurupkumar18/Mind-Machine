# Evidence Engine charter

## Thesis

The Evidence Engine verifies whether a learner can reason about and repair AI-assisted code. It is not a generic tutor, a grading system, or a mastery estimator.

## Evidence loop

`objective/policy -> plan commitment -> external mental model -> prediction -> controlled perturbation -> diagnosis/repair -> deterministic evidence -> targeted retry`

## MVP boundary

The hosted MVP accepts a public prompt and uses one synthetic Python graph fixture. It has no login, persistence, Canvas/GitHub integration, repository upload, arbitrary code execution, or model API.

Phase 2 exposes only an allowlisted, synthetic public-code fixture through `CodeContext`; arbitrary URLs and user repositories remain rejected until an explicitly approved adapter exists.

## Architecture

- **Selection:** curated challenge templates now; a provider-neutral candidate interface later.
- **Evidence:** canonical Python variants and tests, never an LLM grade.
- **Interpretation:** qualitative, event-level evidence only.
