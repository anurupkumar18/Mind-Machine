# Codex plugin foundation

`evidence-engine-tutor` began as consent-first codebase onboarding. It now has
a local collaborative feature-delivery foundation that keeps the earlier
source-map modes available while introducing explicit guidance modes and action
approvals. The full contract is in `docs/LIVE_WORKSPACE_CONTRACT.md`.

## Slice 1: consent-first entry

The installable local plugin presents what will happen, why it helps, and what
it will not do before it can access workspace content. Consent is limited to
the conversation; this initial preview does not yet inspect files, run
commands, edit a project, add persistence, or produce a score.

## Slice 2: read-only source map

After an exact `yes` in the current conversation, the bundled mapper reads
JavaScript, TypeScript, Python, Java, Kotlin, and nested
`package.json`/`pyproject.toml` files. It returns paths, symbol line anchors,
imports, entry-point candidates, and limitations.
The mapper does not import or execute project code, use project commands, or
write into the mapped workspace.

## Slice 3: learner-selected practice

The existing map supports three transparent views: Explorer asks one guided
navigation question, Builder asks for a two-step prediction, and Reviewer asks
for one boundary/trade-off note. Each view explains what is happening and why,
uses only existing map anchors, and treats the learner response as current
thinking rather than a score or verdict. Builder must never confirm a response
or claim runtime/fixture behavior from a static map.

The personal marketplace entry resolves to `~/plugins/evidence-engine-tutor`,
which is a local symlink to this repository's version-controlled plugin source.
This keeps manual preview installation separate from public distribution.

## Feature-delivery foundation

The new `feature-delivery` skill starts with the same exact session consent,
then offers four visible modes:

- **Observe:** read and explain only.
- **Guide:** read, explain, and propose.
- **Pair:** propose a shared change while the action layer remains unavailable.
- **Delegate:** propose a delegated plan while the action layer remains unavailable.

The local `workbench_snapshot.py` utility builds the initial structured
context: mapped files, candidate call path, supported adapters, approval rules,
and an explicit statement that no diff or tests have been collected. It never
executes project code, edits a workspace, calls a network service, or stores
data.

Writes, commands, network actions, and future sync are unavailable in this
foundation. Their future MCP action layer must provide a visible preview and a
mechanically bound class-level approval. Deployment remains plan-and-preview
only.

## Next slice

Connect the workbench snapshot to an MCP tool and UI, then implement the first
approved TypeScript feature-delivery path: scoped plan, diff preview, command
preview, observed test output, and review handoff.
