# Harness rules and commands

State on 2026-11-15: the commands of brief section 11.6 are being built (owner: orch).
Until `harness/bin/` holds them, the plain-git forms below are the protocol.

| Purpose | Command now | Harness command (when present) |
|---|---|---|
| take shared content from main | `git merge --no-edit main` | `harness/bin/nrpic-ctx sync` |
| read another owner's file | `git show <branch>:tracks/<ID>/STATUS.md` | `nrpic-ctx show <ID> [file]` |
| messages addressed to me | `git ls-tree -r --name-only <branch> -- tracks/<ID>/outbox` for every other branch, names containing `__to-<me>__` or `__to-all__` | `nrpic-ctx inbox` |
| send a message | file `tracks/<ID>/outbox/<UTC>__to-<owner>__<slug>.md` with the front matter of brief section 11.3, committed | `nrpic-ctx post` |
| register a run | `tracks/<ID>/runs/<run_id>/manifest.json`, run id `<ID short>-<YYYYMMDD-HHMMSS>-<commit7>` | `harness/bin/nrpic-run` |
| stage check | package under `tracks/<ID>/stage/G<k>/` (report, evidence list, open items) | `/stage-check <ID> G<k>` |

Branch names and owners: `CLAUDE.md`. Outputs of runs: `scratch/<ID>/<run_id>/`.
