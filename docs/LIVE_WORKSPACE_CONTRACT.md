# Live workspace contract

## Scope

This contract governs the Codex-native feature-delivery workflow. It applies
only after a learner explicitly authorizes the current workspace for the
current session.

## Guidance modes

| Mode | Read | Propose | Edit | Run commands | Explain |
| --- | --- | --- | --- | --- | --- |
| Observe | yes | no | no | no | yes |
| Guide | yes | yes | no | no | yes |
| Pair | yes | yes | no (planned) | no (planned) | yes |
| Delegate | yes | yes | no (planned) | no (planned) | yes |

The shipped foundation is local and read-only: no write, command, network, or
sync action is available in any mode. Its future action layer must bind each
approval to a visible affected-path diff, exact command, or data-category
preview; text-only instructions are not enforcement.

## Workbench snapshot

The local workbench returns structured, inspectable data rather than an
implicit model summary:

- task and active guidance mode;
- mapped entry points, symbols, imports, and a visible call-path candidate;
- adapter classification and its limitations;
- current change and test state, including when those have not been collected;
- action approval requirements and one next decision.

The first foundation snapshot reads source text and project metadata only. It
does not collect a diff, execute tests, edit a workspace, make network calls,
or sync data.

## Adapter contract

The shared workflow recognizes JavaScript/TypeScript, Python, Java, and Kotlin
source. An adapter may claim only facts it extracts from source text or project
metadata. Runtime, build, test, and deployment claims require a future
policy-enforced approved action and its observed output.

## Future archive requirements — not implemented

No archive, OAuth, encryption, retention control, export, or deletion service
exists in this foundation. Before any future archive implementation may ship,
secret scanning must block credentials and private keys; the client must encrypt
archive content with a user-held recovery phrase; and setup must offer 30 days,
one year, or until-deleted retention plus export and permanent deletion.
