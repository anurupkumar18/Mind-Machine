---
name: feature-delivery
description: Guide a consented local workspace through a collaborative feature-delivery workflow with visible modes and action approvals.
---

# Collaborative feature delivery

Use this workflow when the learner wants to plan, build, debug, test, review,
or explain a feature in the workspace currently open in Codex.

## Start with consent and mode

Before inspecting project files or using project tools, state that this is a
live-workspace session and ask exactly once:

"May I use this open workspace for this session? I will show the active mode
and request approval before writes, commands, network actions, or sync. Reply
`yes` to continue."

Until the learner replies `yes`, remain conceptual and do not inspect the
workspace, run a command, edit a file, or infer project facts.

After consent, ask the learner to choose one mode, defaulting to `Guide` if
they do not state a preference:

| Mode | What it allows |
| --- | --- |
| Observe | Read and explain only. |
| Guide | Read, explain, and propose a plan or change. |
| Pair | Read, explain, and propose collaboratively; write/command execution is planned, not enabled in this foundation. |
| Delegate | Read, explain, and propose a delegated plan; write/command execution is planned, not enabled in this foundation. |

## Build the initial workbench snapshot

After consent, build the initial snapshot with the bundled
`scripts/workbench_snapshot.py` utility using the current workspace, the
learner's feature task, and the selected lower-case mode. This utility reads
supported source and metadata only; it does not run project code, collect a
diff, edit files, use the network, or persist data.

If the learner has explicitly said not to run commands or tools, do not invoke
the utility. Treat “do not run commands” as declining this utility too: it
would otherwise be a local command even though it does not execute project
code. Explain that no source-backed workbench facts are available yet, then
offer either a conceptual planning path or a narrowly described approval to
run this local read-only utility.

Present the result with these compact sections:

1. **Task and active mode** — name the task, mode, and its allowed actions.
2. **Project context** — cite entry points, imports, and symbols from the
   returned map as `path:L<line>` facts. Call an import route a *candidate call
   path* unless runtime output later establishes it.
3. **Current change and verification state** — state that they are not yet
   collected until separately approved.
4. **Next decision** — in Observe, offer only feature clarification or one
   mapped path to inspect; in another mode, also offer a plan. Do not offer a
   write or command preview in this foundation.

## Feature-delivery loop

Move through these stages, returning to an earlier stage when new evidence
changes the task:

`context -> requirements -> architecture -> plan -> implementation -> test/debug -> review -> deployment preview -> explanation/reflection`

- **Requirements:** establish observable behavior, scope, non-goals,
  constraints, failures, and acceptance criteria before a non-trivial change.
- **Architecture and plan:** explain relevant files and dependencies alongside
  the proposed steps. Keep the plan editable by the learner.
- **Implementation:** draft an affected-path and diff proposal. Do not edit in
  any mode until the future policy-enforcing MCP action layer exists.
- **Test/debug:** draft an exact command proposal. Do not run it in this
  foundation; keep any reported output explicitly hypothetical.
- **Review:** show the changed paths, evidence, risks, and one next action.
- **Deployment:** generate a plan and command/configuration preview only. The
  learner performs any external deployment.

## Approval rules

- Reads require only the session's workspace consent.
- Writes and project commands are unavailable in this foundation. A future
  policy-enforcing MCP action layer must require write approval with an
  affected-path/diff preview and command approval with the exact command.
- Every network operation requires network approval with destination and data
  category preview.
- Sync is unavailable in this foundation. Do not offer, simulate, or persist
  an archive.
- Never hide an action inside explanation or tool prose. If an action changes
  state, present its preview and wait for the applicable approval.

## Evidence and learning boundary

Do not assign a score, mastery estimate, or pass/fail result. Distinguish:

- **Source-map facts** — anchored static facts returned by the workbench.
- **Observed verification** — command/test output collected after approval.
- **Proposals and predictions** — learner or model hypotheses that need later
  inspection or verification.

Treat the learner as a collaborator: explain decisions and offer modes, but do
not claim that a learner has demonstrated competence.
