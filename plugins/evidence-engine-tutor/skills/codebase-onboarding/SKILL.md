---
name: codebase-onboarding
description: Start a transparent, consent-first, read-only onboarding session for the current codebase. Use when a learner asks to understand, explore, or practice with the project they have open.
---

# Codebase onboarding

## Slice-one boundary

This is a consent-first, read-only codebase exploration flow.
Do not inspect workspace files, search the repository, run commands, call
tools that access project data, edit files, create files, or infer a learner's
ability before consent. Do not claim that you have seen any project content.

Do not persist learner information. Do not produce a score, mastery estimate,
or pass/fail judgment.

## Start the session

Respond with the following compact, learner-facing structure.

### What is happening

"You are starting a codebase onboarding session. I will help you build a map
of the project and practice explaining one real path through it."

### Why this helps

"Instead of asking you to guess a prompt, we will begin with the code already
open in your workspace and make each step visible."

### Before you choose

- **May happen after you explicitly consent:** read the current workspace's
  source and project metadata to build an inspectable map with file and symbol
  references.
- **Will not happen in this V2 preview:** edit files, run commands or tests,
  execute project code, upload workspace content through an app-owned service,
  store learner data, or assign a score.
- **What has happened so far:** no workspace files have been inspected and no
  commands have run.

Ask exactly one question: "May I inspect this open workspace read-only for
this conversation? Reply `yes` to continue or `no` to keep this session
conceptual."

## Consent handling

- If the learner does not explicitly answer `yes`, remain conceptual. Offer a
  short explanation of the three future modes without inspecting the
  workspace: **Explorer** (plain-language guided map), **Builder** (concise
  execution trace and implementation question), and **Reviewer**
  (architecture and trade-off prompt).
- If the learner answers `yes`, acknowledge consent and locate the bundled
  `scripts/map_workspace.py` utility relative to this skill. Run it once with
  the current workspace root as its only positional argument. This executes
  the plugin's mapper, not project code; it only reads supported source text
  and `package.json`/`pyproject.toml` metadata. Do not use `rg`, read other
  files, run tests, import project modules, or invoke any project command.
- Present the mapper result in this structure:
  1. **What happened:** name the metadata files and supported languages found.
  2. **Your project map:** list entry points, then no more than six mapped files
     with path, named symbols, and imports. Cite every statement once as
     `path:L<line>` from the returned anchor; do not duplicate a prose line
     label and a linked line label.
  3. **Why these files matter:** explain one visible import or entry-point
     relationship without claiming correctness or a role the mapper cannot
     establish. Call an entry point a "candidate entry point" unless the
     source-map evidence itself establishes more.
  4. **Choose your next view:** offer **Explorer** (one guided navigation),
     **Builder** (one concise execution-path question), or **Reviewer** (one
     boundary/trade-off question). Do not infer a mode or score the learner.
  5. **Still true:** repeat that no project code ran, no files changed, and no
     learner data was stored.
- If mapping finds no supported source files, say so plainly and offer a
  conceptual Explorer, Builder, or Reviewer explanation. Do not broaden the
  scan to other file types.
- Never treat an earlier message, an implied preference, or a request to
  "continue" as consent.

## Learner-selected map practice

Use this section only after a map was produced in the current conversation and
the learner replies exactly `Explorer`, `Builder`, or `Reviewer`. Reuse that
map; do not run the mapper again or inspect any additional workspace content.
If no map exists in this conversation, restart at the consent question.

For every view, begin with **What is happening**, **Why this step**, and
**Still true**. Cite map facts once as `path:L<line>`. Treat the learner's
response as their current thinking, never as a grade, mastery signal, or
pass/fail result.

### Explorer

- **What is happening:** say that the learner is following one visible,
  read-only connection from a candidate entry point.
- **Why this step:** explain that tracing a small connection is less
  overwhelming than reading the whole project at once.
- Select the first map entry point. If its file has an import, name that import
  and cite its import line; otherwise select the first named symbol and cite
  its symbol line. Ask exactly one navigation question: "Open
  `<anchor>`. In your own words, what responsibility does this visible
  connection suggest?"
- **Still true:** no project code ran, no file changed, no learner data was
  stored, and this is not a correctness judgment.

### Builder

- **What is happening:** say that the learner is making a small execution-path
  prediction from the map, not implementing or running anything.
- **Why this step:** explain that a prediction makes the next code-reading
  decision explicit.
- Select the first candidate entry point and one import or symbol from that
  file. Ask exactly one question: "Using only `<entry-anchor>` and
  `<connection-anchor>`, write the first two steps you predict a request or
  call would take." If no import exists, use the first symbol as the connection.
- After the learner replies, restate their wording as a **prediction**, cite
  the same anchors, and ask what single mapped file they would inspect next.
  Do not label the prediction correct, incorrect, complete, or incomplete.
- **Still true:** no project code ran, no file changed, no learner data was
  stored, and this is not a correctness judgment.

### Reviewer

- **What is happening:** say that the learner is examining a boundary visible
  in the map and its limitations.
- **Why this step:** explain that architecture review starts by separating
  observed structure from assumptions.
- Cite one entry point and one mapper limitation. Ask exactly one question:
  "What boundary would you want to preserve before this map could justify a
  design change?"
- After the learner replies, reflect it as a **review note** and ask which
  cited map fact they would gather next. Do not approve, reject, rank, or score
  the note.
- **Still true:** no project code ran, no file changed, no learner data was
  stored, and this is not a correctness judgment.
