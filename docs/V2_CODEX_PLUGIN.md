# V2 Codex plugin preview

`evidence-engine-tutor` moves codebase onboarding into Codex while preserving
the Evidence Engine's safety boundary.

## Slice 1: consent-first entry

The installable local plugin presents what will happen, why it helps, and what
it will not do before it can access workspace content. Consent is limited to
the conversation; this initial preview does not yet inspect files, run
commands, edit a project, add persistence, or produce a score.

## Slice 2: read-only source map

After an exact `yes` in the current conversation, the bundled mapper reads only
JavaScript, TypeScript, Python, and nested `package.json`/`pyproject.toml`
files. It returns paths, symbol line anchors, imports, entry-point candidates,
and limitations.
The mapper does not import or execute project code, use project commands, or
write into the mapped workspace.

## Slice 3: learner-selected practice

The existing map supports three transparent views: Explorer asks one guided
navigation question, Builder asks for a two-step prediction, and Reviewer asks
for one boundary/trade-off note. Each view explains what is happening and why,
uses only existing map anchors, and treats the learner response as current
thinking rather than a score or verdict.

The personal marketplace entry resolves to `~/plugins/evidence-engine-tutor`,
which is a local symlink to this repository's version-controlled plugin source.
This keeps manual preview installation separate from public distribution.

## Next slice

After manual feedback, add a first source-anchored micro-exploration flow
without changing the read-only boundary.
