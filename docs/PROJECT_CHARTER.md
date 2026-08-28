# Evidence Engine charter

## Thesis

Evidence Engine is a collaborative AI-coding environment. It helps a learner
and an agent understand project context, define a feature, make and verify
changes, and explain the evidence behind those changes. It is not a grading
system or a mastery estimator.

## Product surfaces

- **Codex plugin:** the primary live-workspace surface. The shipped foundation
  presents consented, local, read-only context and planning; its future MCP
  workbench will add policy-enforced actions.
- **Hosted portal:** the future opt-in archive and dashboard surface. It must
  never become an unconsented project-indexing service.
- **Fixture lab:** a deterministic public/synthetic evaluation testbed that
  remains separate from a learner's live workspace.

## Live-workspace boundary

Workspace access is explicit and scoped to the current Codex session. The
shipped foundation reads selected local source after consent and excludes
detected sensitive content; it cannot write, execute project commands, use the
network, or sync. A future MCP policy layer must bind every write, command,
network, and sync action to a visible class-level approval with a diff,
command, or data preview. The plugin must say which guidance mode is active
and what that mode currently allows before it takes an action.

The first local workflow may map and explain TypeScript, Python, Java, and
Kotlin source. Unsupported languages remain generic read-only context until a
tested adapter exists. Deployment stays plan-and-preview only: the learner
executes external deployment themselves.

## Privacy and learning records

Sync is absent by default. A future opted-in archive requires GitHub OAuth,
client-side end-to-end encryption, a user-held recovery phrase, secret
scanning that blocks unsafe uploads, retention chosen by the learner, export,
and permanent deletion. The service must not be able to recover archive keys.

## Architecture

- **Context:** local adapters build inspectable symbol, import, and entry-point
  facts for the authorized workspace.
- **Workflow:** skills route a feature through requirements, planning,
  implementation, tests, review, deployment preview, and reflection.
- **Approvals:** the current skills describe action boundaries; a future local
  policy layer must mechanically gate read, write, command, network, and sync
  action classes.
- **Evidence:** canonical fixture evidence and live-workspace verification
  evidence remain provenance-labelled and separate from interpretation.
- **Interpretation:** may organize observations and next actions, but never
  determine learner pass/fail or mastery.
