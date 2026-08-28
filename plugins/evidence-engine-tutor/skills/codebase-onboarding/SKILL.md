---
name: codebase-onboarding
description: Start a transparent, consent-first, read-only onboarding session for the current codebase. Use when a learner asks to understand, explore, or practice with the project they have open.
---

# Codebase onboarding

## Slice-one boundary

This is the consent screen for a future read-only codebase exploration flow.
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
- If the learner answers `yes`, acknowledge consent, explain that source
  mapping will become available in the next preview slice, and do not inspect
  the workspace yet. State: "Consent recorded for this conversation only. This
  preview has not inspected files or run commands."
- Never treat an earlier message, an implied preference, or a request to
  "continue" as consent.
