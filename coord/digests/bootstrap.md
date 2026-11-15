# Bootstrap of the context-sharing harness (2026-11-15T11:45Z)

Written by `harness/tests/acceptance_ctx.py` from the main checkout at `b0aeec2`. It covers the acceptance tests of brief section 11.7 that concern `nrpic-ctx`, `nrpic-wt` and `nrpic-doctor`; tests 4 and 6 (run registration, stage-check rehearsal) and the guard and hook rows of test 1 and test 5 belong to the commands of the runs-and-configuration helper (`nrpic-run`, `nrpic-env`, `nrpic-stage`, `harness/hooks/`) and are reported there. The round trips run in a scratch repository with five owners, never on the live branches.

## Result

| Test (brief 11.7) | Where | Result |
|---|---|---|
| 1 `nrpic-doctor` passes in all eight worktrees | live, read-only | rows of these commands (`wt`, `build`, `ctx`) PASS in all nine worktrees; `gpu` PASS; `venv`, `env`, `scratch`, `guard`, `main`, `kb`, `git`, `stop` MISSING where their component is not built, not installed or not yet synced (table below) |
| 2 context round trip (A to B, B's brief, B's ack, A's board; nothing written across worktrees) | scratch | PASS (20 checks) |
| 3 proposal round trip (A to orch, DECISIONS on main, every track syncs and reads it) | scratch | PASS (9 checks) |
| 5 destructive test | scratch (refusals of `nrpic-ctx`); guard not built | `nrpic-ctx` refusals PASS (6 checks); the guard part (edit main, edit B, write B's scratch, force-push) is MISSING until `harness/hooks/pre_tool_guard.py` exists |
| 7 cold start from HANDOFF.md and the brief | scratch and live | scratch PASS (3 checks); live PASS: 8 of 8 owner briefs show the gate and the `Run next:` line of HANDOFF.md, at most 15 lines |

Further checks of the self-test (each message exactly once, read commands write nothing, conflict, audit, nrpic-wt):

| Section of `harness/tests/test_ctx.py` | Passed | Failed |
|---|---|---|
| Set-up: a scratch repository with five owners, worktrees by nrpic-wt | 10 | 0 |
| Messages: each post writes only the poster's worktree and branch | 13 | 0 |
| Exactly once, before any merge | 5 | 0 |
| Read commands write nothing and merge nothing | 1 | 0 |
| Copies of outboxes travel through main: still exactly once | 8 | 0 |
| Acceptance test 2: context round trip A -> B | 7 | 0 |
| Acceptance test 3: proposal round trip A -> orch -> DECISIONS -> every track | 9 | 0 |
| A boundary crossing: sync refuses to merge, audit names the commit | 2 | 0 |
| Audit: foreign paths, large file, tracked file under an ignored root, read-only | 10 | 0 |
| Acceptance test 7: cold start from HANDOFF.md and the brief | 3 | 0 |
| Refusals | 6 | 0 |
| nrpic-wt retire: checks, never removes | 3 | 0 |
| The orchestrator's generated files | 3 | 0 |
| nrpic-doctor rows of this harness, inside the scratch repository | 1 | 0 |

Total: 81 checks passed, 0 failed (scratch repository `scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo`, removed after the passing run).

## Findings on the live repository (from the audit below)

Commits outside the owner's paths (section 1):

**`core/id-extrinsic`** (owner core):
- `408df5770` 2026-11-15 11:36Z Add initial data with extrinsic curvature (table format 2) to nrpic_c…: `docs/FORMATS.md`

- the ignore rule `.gitignore:12: runs/` hides `tracks/<ID>/runs/X-20260101-000000-abcdef0/manifest.json`, which owners must commit (9 owner(s)); it is tracked only when added with -f. Anchor the pattern on main.

Findings: 1 (section 1: 1, section 2: 0, section 3: 0); notes: 11.

## Commands

Run `harness/tests/test_ctx.py` (self-test, about 20 s) and `harness/tests/acceptance_ctx.py` (this file) from the main checkout. Usage: `harness/RULES.md`.

## Acceptance test 1: `nrpic-doctor --all` (read-only in the eight owner worktrees and the main checkout)

```
$ harness/bin/nrpic-doctor --all
nrpic-doctor --all (2026-11-15T11:45Z), read-only; rows: wt, build, venv, env, scratch, guard, main, kb, gpu, ctx, git, stop
owner        wt      build   venv    env     scratch guard   main    kb      gpu     ctx     git     stop   
orch         PASS    PASS    MISSING PASS    SKIP    SKIP    SKIP    MISSING PASS    PASS    MISSING MISSING
core         PASS    PASS    MISSING MISSING MISSING MISSING MISSING MISSING PASS    PASS    MISSING MISSING
kb           PASS    PASS    MISSING MISSING MISSING MISSING MISSING PASS    PASS    PASS    MISSING MISSING
A-emd-pbh    PASS    PASS    MISSING MISSING MISSING MISSING MISSING MISSING PASS    PASS    MISSING MISSING
B-emd-gw     PASS    PASS    MISSING PASS    MISSING MISSING MISSING MISSING PASS    PASS    MISSING MISSING
C-sidm       PASS    PASS    MISSING PASS    MISSING MISSING MISSING MISSING PASS    PASS    MISSING MISSING
D-bh-dress   PASS    PASS    MISSING MISSING MISSING MISSING MISSING MISSING PASS    PASS    MISSING MISSING
E-stoch-inf  PASS    PASS    MISSING MISSING MISSING MISSING MISSING MISSING PASS    PASS    MISSING MISSING
F-hills      PASS    PASS    MISSING MISSING MISSING MISSING MISSING MISSING PASS    PASS    MISSING MISSING

orch         [venv] MISSING: no .venv in this worktree yet (harness/bin/nrpic-env create)
orch         [kb] MISSING: kb/bin/kb is not in this worktree (it arrives when kb/main is merged into main and the owner syncs)
orch         [git] MISSING: tree 8 uncommitted change(s); no pre-commit hook is installed or present under harness/
orch         [stop] MISSING: harness/hooks/stop_gate.sh does not exist
core         [venv] MISSING: this worktree has no harness/env/machines/anta.sh yet (nrpic-ctx sync brings it from main)
core         [env] MISSING: this worktree has no harness/env/machines/anta.sh yet (nrpic-ctx sync brings it from main)
core         [scratch] MISSING: own-scratch write not tried (read-only: another worktree or --all); the refusal needs harness/hooks/pre_tool_guard.py
core         [guard] MISSING: harness/hooks/pre_tool_guard.py does not exist
core         [main] MISSING: harness/hooks/pre_tool_guard.py does not exist (Claude Code's own worktree isolation is the first barrier; it is exercised in a session, acceptance test 5)
core         [kb] MISSING: kb/bin/kb is not in this worktree (it arrives when kb/main is merged into main and the owner syncs)
core         [git] MISSING: tree clean; no pre-commit hook is installed or present under harness/
core         [stop] MISSING: harness/hooks/stop_gate.sh does not exist
kb           [venv] MISSING: this worktree has no harness/env/machines/anta.sh yet (nrpic-ctx sync brings it from main)
kb           [env] MISSING: this worktree has no harness/env/machines/anta.sh yet (nrpic-ctx sync brings it from main)
kb           [scratch] MISSING: own-scratch write not tried (read-only: another worktree or --all); the refusal needs harness/hooks/pre_tool_guard.py
kb           [guard] MISSING: harness/hooks/pre_tool_guard.py does not exist
kb           [main] MISSING: harness/hooks/pre_tool_guard.py does not exist (Claude Code's own worktree isolation is the first barrier; it is exercised in a session, acceptance test 5)
kb           [git] MISSING: tree clean; no pre-commit hook is installed or present under harness/
kb           [stop] MISSING: harness/hooks/stop_gate.sh does not exist
A-emd-pbh    [venv] MISSING: this worktree has no harness/env/machines/anta.sh yet (nrpic-ctx sync brings it from main)
A-emd-pbh    [env] MISSING: this worktree has no harness/env/machines/anta.sh yet (nrpic-ctx sync brings it from main)
A-emd-pbh    [scratch] MISSING: own-scratch write not tried (read-only: another worktree or --all); the refusal needs harness/hooks/pre_tool_guard.py
A-emd-pbh    [guard] MISSING: harness/hooks/pre_tool_guard.py does not exist
A-emd-pbh    [main] MISSING: harness/hooks/pre_tool_guard.py does not exist (Claude Code's own worktree isolation is the first barrier; it is exercised in a session, acceptance test 5)
A-emd-pbh    [kb] MISSING: kb/bin/kb is not in this worktree (it arrives when kb/main is merged into main and the owner syncs)
A-emd-pbh    [git] MISSING: tree 3 uncommitted change(s); no pre-commit hook is installed or present under harness/
A-emd-pbh    [stop] MISSING: harness/hooks/stop_gate.sh does not exist
B-emd-gw     [venv] MISSING: no .venv in this worktree yet (harness/bin/nrpic-env create)
... (37 more lines)
(exit 1)
```

## Worktrees (`nrpic-wt list`)

```
$ harness/bin/nrpic-wt list
worktree             branch                 owner        head     tree      main b/a  remote
.                    main                   orch         b0aeec2  8 dirty   —         pushed
wt/A-emd-pbh         track/A-emd-pbh        A-emd-pbh    f6b7169  3 dirty   6/21      not on origin
wt/B-emd-gw          track/B-emd-gw         B-emd-gw     edd77fa  11 dirty  4/9       not on origin
wt/C-sidm            track/C-sidm           C-sidm       91cd222  clean     1/0       not on origin
wt/D-bh-dress        track/D-bh-dress       D-bh-dress   52c44eb  clean     12/0      not on origin
wt/E-stoch-inf       track/E-stoch-inf      E-stoch-inf  52c44eb  clean     12/0      not on origin
wt/F-hills           track/F-hills          F-hills      52c44eb  clean     12/0      not on origin
wt/core              core/nrpic             core         c37eeca  clean     7/11      not on origin
wt/core-coll         core/collisions        core         a9fec22  clean     8/0       not on origin
wt/core-id           core/id-extrinsic      core         c9aa6d2  18 dirty  7/2       pushed
wt/core-mp           core/multi-puncture    core         c89b6e3  8 dirty   7/3       not on origin
wt/core-newton       core/newton            core         728637a  1 dirty   7/3       1 to push
wt/core-rng          core/rng               core         b7b431d  14 dirty  7/0       not on origin
wt/core-scalar       core/scalar-field      core         a9fec22  clean     8/0       not on origin
wt/kb                kb/main                kb           d939d5d  clean     7/3       not on origin
(exit 0)
```

## Acceptance test 7 on the live worktrees: the start-up brief of every owner (`nrpic-ctx -C wt/<ID> brief`, read-only)

```
$ harness/bin/nrpic-ctx -C wt/core brief
nrpic brief 2026-11-15T11:45Z: you are core, branch core/nrpic, worktree wt/core
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. Document the interfaces from the existing code, re-verify the ladder of brief section 10 (rows CORE), prepare the tags core-v0.1 …
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        7 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 11 commit(s) not on main
remote:      no upstream; push with git push -u origin core/nrpic
tree:        clean
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: Document the interfaces from the existing code, re-verif…
read first:  tracks/core/HANDOFF.md, tracks/core/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
```
$ harness/bin/nrpic-ctx -C wt/kb brief
nrpic brief 2026-11-15T11:45Z: you are kb, branch kb/main, worktree wt/kb
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. K0 to K3 of brief section 12.
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        7 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 3 commit(s) not on main
remote:      no upstream; push with git push -u origin kb/main
tree:        clean
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: K0 to K3 of brief section 12.
read first:  tracks/kb/HANDOFF.md, tracks/kb/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
```
$ harness/bin/nrpic-ctx -C wt/A-emd-pbh brief
nrpic brief 2026-11-15T11:45Z: you are A-emd-pbh, branch track/A-emd-pbh, worktree wt/A-emd-pbh
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. A-pre-1: derivation of the expanding-ball initial data and the offline constraint check.
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        6 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 21 commit(s) not on main
remote:      no upstream; push with git push -u origin track/A-emd-pbh
tree:        3 uncommitted change(s): tracks/A-emd-pbh/expball/, tracks/A-emd-pbh/gauge/DIAGNOSTICS.md, tracks/A-emd-pbh/gauge/GAUGE.md
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: A-pre-1: derivation of the expanding-ball initial data a…
read first:  tracks/A-emd-pbh/HANDOFF.md, tracks/A-emd-pbh/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
```
$ harness/bin/nrpic-ctx -C wt/B-emd-gw brief
nrpic brief 2026-11-15T11:45Z: you are B-emd-gw, branch track/B-emd-gw, worktree wt/B-emd-gw
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. B-pre-1 and B-pre-3.
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        4 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 9 commit(s) not on main
remote:      no upstream; push with git push -u origin track/B-emd-gw
tree:        11 uncommitted change(s): tracks/B-emd-gw/gw_diag/, tracks/B-emd-gw/periodic_z4c/analysis/ana_awa.py, tracks/B-emd-gw/periodic_z4c/analysis/ana_check3d.py, tracks/B-emd-gw/periodic_z4c/analysis/ana_dump.py
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: B-pre-1 and B-pre-3.
read first:  tracks/B-emd-gw/HANDOFF.md, tracks/B-emd-gw/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
```
$ harness/bin/nrpic-ctx -C wt/C-sidm brief
nrpic brief 2026-11-15T11:45Z: you are C-sidm, branch track/C-sidm, worktree wt/C-sidm
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. C-pre-1.
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        1 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 0 commit(s) not on main
remote:      no upstream; push with git push -u origin track/C-sidm
tree:        clean
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: C-pre-1.
read first:  tracks/C-sidm/HANDOFF.md, tracks/C-sidm/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
```
$ harness/bin/nrpic-ctx -C wt/D-bh-dress brief
nrpic brief 2026-11-15T11:45Z: you are D-bh-dress, branch track/D-bh-dress, worktree wt/D-bh-dress
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. The derivation of D-pre-1.
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        12 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 0 commit(s) not on main
remote:      no upstream; push with git push -u origin track/D-bh-dress
tree:        clean
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: The derivation of D-pre-1.
read first:  tracks/D-bh-dress/HANDOFF.md, tracks/D-bh-dress/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
```
$ harness/bin/nrpic-ctx -C wt/E-stoch-inf brief
nrpic brief 2026-11-15T11:45Z: you are E-stoch-inf, branch track/E-stoch-inf, worktree wt/E-stoch-inf
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. E-pre-1, then E-pre-2.
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        12 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 0 commit(s) not on main
remote:      no upstream; push with git push -u origin track/E-stoch-inf
tree:        clean
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: E-pre-1, then E-pre-2.
read first:  tracks/E-stoch-inf/HANDOFF.md, tracks/E-stoch-inf/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
```
$ harness/bin/nrpic-ctx -C wt/F-hills brief
nrpic brief 2026-11-15T11:45Z: you are F-hills, branch track/F-hills, worktree wt/F-hills
gate:        G0 not started
headline:    seeded by the orchestrator on 2026-11-15; no session yet
last-result: none
next:        1. The novelty search F-pre-5, then F-pre-1.
blockers:    none
needs:       none
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       0 unacknowledged
main:        12 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 0 commit(s) not on main
remote:      no upstream; push with git push -u origin track/F-hills
tree:        clean
handoff:     Run next: read `CLAUDE.md`, `coord/CHARTER.md` (your sheet), then start with: The novelty search F-pre-5, then F-pre-1.
read first:  tracks/F-hills/HANDOFF.md, tracks/F-hills/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```

## The orchestrator's brief

```
$ harness/bin/nrpic-ctx brief
nrpic brief 2026-11-15T11:45Z: you are orch, branch main, worktree main checkout
role: orchestrator (harness, coord/, integration, review); board: nrpic-ctx board
  core         G0 not started             inbox 0  ahead 11  seeded by the orchestrator on 2026-11-15; no session yet
  kb           G0 not started             inbox 0  ahead 3   seeded by the orchestrator on 2026-11-15; no session yet
  A-emd-pbh    G0 not started             inbox 0  ahead 21  seeded by the orchestrator on 2026-11-15; no session yet
  B-emd-gw     G0 not started             inbox 0  ahead 9   seeded by the orchestrator on 2026-11-15; no session yet
  C-sidm       G0 not started             inbox 0  ahead 0   seeded by the orchestrator on 2026-11-15; no session yet
  D-bh-dress   G0 not started             inbox 0  ahead 0   seeded by the orchestrator on 2026-11-15; no session yet
  E-stoch-inf  G0 not started             inbox 0  ahead 0   seeded by the orchestrator on 2026-11-15; no session yet
  F-hills      G0 not started             inbox 0  ahead 0   seeded by the orchestrator on 2026-11-15; no session yet
inbox:       0 unacknowledged
remote:      origin/main: 0 to push, 0 to pull
tree:        8 uncommitted change(s): harness/bin/nrpic-run, harness/lib/nrpic_harness.py, harness/tests/rc_fixture.py, coord/BOARD.md
read first:  coord/BOARD.md (nrpic-ctx board --write), coord/CHARTER.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```

## `nrpic-ctx audit` on the live branches (read-only)

```
$ harness/bin/nrpic-ctx audit
# Audit (2026-11-15T11:45Z, `nrpic-ctx audit`, read-only)

## 1. Commits touching paths outside the owner's directory and OWNERSHIP

Range per branch: `main..<branch>`. OWNERSHIP is taken from main (the accepted version). Merge commits count only for what they change against every parent (conflict resolutions), and a merge of a branch that is neither on main nor the owner's own is reported.

**`core/id-extrinsic`** (owner core):
- `408df5770` 2026-11-15 11:36Z Add initial data with extrinsic curvature (table format 2) to nrpic_c…: `docs/FORMATS.md`

## 2. Files above 1 MB

Added or changed on a branch (not on main): none.

Tracked on main (known; listed, not counted):

- `athenak/tst/inputs/tables/SFHo_reduced.athtab` 1.86 MB
- `athenak/tst/inputs/tables/SFHo_reduced_NQT.athtab` 1.86 MB
- `paper/data/overdensities.npz` 1.84 MB
- `paper/main.pdf` 1.56 MB
- `problems/schwarzschild/results/schw_histories.npz` 1.13 MB

## 3. Tracked files under ignored roots

Every tracked path at the tip of every branch, tested against the ignore rules of the main checkout (`git check-ignore --no-index`). A root is a directory of the first or second level (`scratch/`, `wt/`, `refs/arxiv_<id>/`, ...).

None.

Tracked files below the roots that an ignore pattern also matches (listed, not counted: usually a pattern that is not anchored, which then also hides new files of the same kind):

- rule `.gitignore:12: runs/` matches 47 tracked file(s), e.g. `tracks/B-emd-gw/runs/B-emd-gw-20261115-112946-b7b431d/manifest.json` (on `core/id-extrinsic`, `core/newton`, `kb/main`, `track/B-emd-gw`)

## Notes (not counted)

- the ignore rule `.gitignore:12: runs/` hides `tracks/<ID>/runs/X-20260101-000000-abcdef0/manifest.json`, which owners must commit (9 owner(s)); it is tracked only when added with -f. Anchor the pattern on main.
- 129 run directories in scratch/core/ without a committed tracks/core/runs/<run_id>/manifest.json on core's branches (e.g. core-20261115-032614-45e1779, core-20261115-032615-45e1779, core-20261115-032617-45e1779 ...)
- 17 run directories in scratch/A-emd-pbh/ without a committed tracks/A-emd-pbh/runs/<run_id>/manifest.json on A-emd-pbh's branches (e.g. A-emd-pbh-20261115-112500-61acbec, A-emd-pbh-20261115-112505-61acbec, A-emd-pbh-20261115-112625-e854f12 ...)
- 36 run directories in scratch/B-emd-gw/ without a committed tracks/B-emd-gw/runs/<run_id>/manifest.json on B-emd-gw's branches (e.g. B-emd-gw-20261115-113212-0ea0f74, B-emd-gw-20261115-113213-0ea0f74, B-emd-gw-20261115-113214-0ea0f74 ...)
- worktree `.` (`main`) has 8 uncommitted change(s) now
- worktree `wt/A-emd-pbh` (`track/A-emd-pbh`) has 3 uncommitted change(s) now
- worktree `wt/B-emd-gw` (`track/B-emd-gw`) has 11 uncommitted change(s) now
- worktree `wt/core-id` (`core/id-extrinsic`) has 18 uncommitted change(s) now
- worktree `wt/core-mp` (`core/multi-puncture`) has 8 uncommitted change(s) now
- worktree `wt/core-newton` (`core/newton`) has 1 uncommitted change(s) now
- worktree `wt/core-rng` (`core/rng`) has 14 uncommitted change(s) now

Not checked by this command: numbers in notes without a run id (read at the stage check).

Findings: 1 (section 1: 1, section 2: 0, section 3: 0); notes: 11.
(exit 1)
```

## Transcript of the self-test

Self-test `harness/tests/test_ctx.py`, 2026-11-15T11:45Z, scratch repository `scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo`: **81 checks passed, 0 failed**.

### Set-up: a scratch repository with five owners, worktrees by nrpic-wt

```
[.]$ harness/bin/nrpic-ctx template HANDOFF --id A-emd-pbh
# HANDOFF of A-emd-pbh

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State: (three lines at most: what is established, what is in progress, what failed)
Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `wt/A-emd-pbh`.
Run next: `the exact command to run first`
Files to read first: `tracks/A-emd-pbh/STATUS.md`, then the files the next action needs.
Decisions pending: what waits for the orchestrator, another owner or the user (with the outbox file).
Traps: what went wrong before and how to avoid it.
(exit 0)
```
- PASS: the scratch repository is its own toplevel
```
[.]$ harness/bin/nrpic-wt new core
created wt/core on the new branch core/nrpic from main
  [wt] PASS  toplevel /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo/wt/core, branch core/nrpic
  [build] PASS  build dirs: none yet; no symbolic link into another worktree or the main checkout
  [copy] PASS  harness/wt_copy.list names no file
  [kokkos] PASS  submodule not initialised (only needed to build: nrpic-wt new --kokkos, or CLAUDE.md 'Machine')
next: cd wt/core && harness/bin/nrpic-ctx brief
(exit 0)
```
- PASS: nrpic-wt new core: created, [wt] and [build] PASS
```
[.]$ harness/bin/nrpic-wt new kb
created wt/kb on the new branch kb/main from main
  [wt] PASS  toplevel /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo/wt/kb, branch kb/main
  [build] PASS  build dirs: none yet; no symbolic link into another worktree or the main checkout
  [copy] PASS  harness/wt_copy.list names no file
  [kokkos] PASS  submodule not initialised (only needed to build: nrpic-wt new --kokkos, or CLAUDE.md 'Machine')
next: cd wt/kb && harness/bin/nrpic-ctx brief
(exit 0)
```
- PASS: nrpic-wt new kb: created, [wt] and [build] PASS
```
[.]$ harness/bin/nrpic-wt new A-emd-pbh
created wt/A-emd-pbh on the new branch track/A-emd-pbh from main
  [wt] PASS  toplevel /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo/wt/A-emd-pbh, branch track/A-emd-pbh
  [build] PASS  build dirs: none yet; no symbolic link into another worktree or the main checkout
  [copy] PASS  harness/wt_copy.list names no file
  [kokkos] PASS  submodule not initialised (only needed to build: nrpic-wt new --kokkos, or CLAUDE.md 'Machine')
next: cd wt/A-emd-pbh && harness/bin/nrpic-ctx brief
(exit 0)
```
- PASS: nrpic-wt new A-emd-pbh: created, [wt] and [build] PASS
```
[.]$ harness/bin/nrpic-wt new B-emd-gw
created wt/B-emd-gw on the new branch track/B-emd-gw from main
  [wt] PASS  toplevel /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo/wt/B-emd-gw, branch track/B-emd-gw
  [build] PASS  build dirs: none yet; no symbolic link into another worktree or the main checkout
  [copy] PASS  harness/wt_copy.list names no file
  [kokkos] PASS  submodule not initialised (only needed to build: nrpic-wt new --kokkos, or CLAUDE.md 'Machine')
next: cd wt/B-emd-gw && harness/bin/nrpic-ctx brief
(exit 0)
```
- PASS: nrpic-wt new B-emd-gw: created, [wt] and [build] PASS
```
[.]$ harness/bin/nrpic-wt new core --name core-rng --branch core/rng
created wt/core-rng on the new branch core/rng from main
  [wt] PASS  temporary worktree of core: toplevel /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo/wt/core-rng, branch core/rng
  [build] PASS  build dirs: none yet; no symbolic link into another worktree or the main checkout
  [copy] PASS  harness/wt_copy.list names no file
  [kokkos] PASS  submodule not initialised (only needed to build: nrpic-wt new --kokkos, or CLAUDE.md 'Machine')
next: cd wt/core-rng && harness/bin/nrpic-ctx brief
(exit 0)
```
- PASS: nrpic-wt new core --name core-rng --branch core/rng
```
[.]$ harness/bin/nrpic-wt new A-emd-pbh --branch track/B-emd-gw
nrpic-wt new: branch track/B-emd-gw does not belong to owner A-emd-pbh (owners and branches: CLAUDE.md)
(exit 2)
```
- PASS: nrpic-wt new refuses a branch of another owner
```
[wt/A-emd-pbh]$ harness/bin/nrpic-wt new kb --name kb-x --branch kb/x
nrpic-wt new: worktrees are created by the orchestrator from the main checkout on main (brief 11.2)
(exit 2)
```
- PASS: nrpic-wt new refuses to run outside the main checkout
```
[.]$ harness/bin/nrpic-wt list
worktree             branch                 owner        head     tree      main b/a  remote
.                    main                   orch         7bedaf7  clean     —         pushed
wt/A-emd-pbh         track/A-emd-pbh        A-emd-pbh    7bedaf7  clean     0/0       not on origin
wt/B-emd-gw          track/B-emd-gw         B-emd-gw     7bedaf7  clean     0/0       not on origin
wt/core              core/nrpic             core         7bedaf7  clean     0/0       not on origin
wt/core-rng          core/rng               core         7bedaf7  clean     0/0       not on origin
wt/kb                kb/main                kb           7bedaf7  clean     0/0       not on origin
(exit 0)
```
- PASS: nrpic-wt list: six worktrees, every owner has one
```
[.]$ harness/bin/nrpic-ctx owners
owner        branch               worktree               state
orch         main                 .                      ok
core         core/nrpic           wt/core                ok  (+ core/rng)
kb           kb/main              wt/kb                  ok
A-emd-pbh    track/A-emd-pbh      wt/A-emd-pbh           ok
B-emd-gw     track/B-emd-gw       wt/B-emd-gw            ok
(exit 0)
```
- PASS: nrpic-ctx owners: five owners from CLAUDE.md, core/rng as core's temporary branch

### Messages: each post writes only the poster's worktree and branch

```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx post --to B-emd-gw --type request --slug deposit-order --body request from A-emd-pbh: deposit-order. --reply-by 2026-11-27 --refs arXiv:2611.12831,run:A-test
wrote tracks/A-emd-pbh/outbox/20261115T114508Z__to-B-emd-gw__deposit-order.md
committed 573e3fa on track/A-emd-pbh; the recipients see it now (push at the end of the session)
(exit 0)
```
- PASS: A-emd-pbh posts request to B-emd-gw: deposit-order
- PASS: only wt/A-emd-pbh and refs/heads/track/A-emd-pbh changed (changed: ['A-emd-pbh'], ['refs/heads/track/A-emd-pbh'])
```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx post --to all --type info --slug hello-all --body info from A-emd-pbh: hello-all.
wrote tracks/A-emd-pbh/outbox/20261115T114508Z__to-all__hello-all.md
committed 8482b8f on track/A-emd-pbh; the recipients see it now (push at the end of the session)
(exit 0)
```
- PASS: A-emd-pbh posts info to all: hello-all
- PASS: only wt/A-emd-pbh and refs/heads/track/A-emd-pbh changed (changed: ['A-emd-pbh'], ['refs/heads/track/A-emd-pbh'])
```
[wt/core-rng]$ harness/bin/nrpic-ctx post --to A --type info --slug rng-draft --body info from core-rng: rng-draft.
wrote tracks/core/outbox/20261115T114508Z__to-A-emd-pbh__rng-draft.md
committed 7f322c5 on core/rng; the recipients see it now (push at the end of the session)
(exit 0)
```
- PASS: core-rng posts info to A: rng-draft
- PASS: only wt/core-rng and refs/heads/core/rng changed (changed: ['core-rng'], ['refs/heads/core/rng'])
```
[wt/core]$ harness/bin/nrpic-ctx post --to all --type interface-change --slug deposit-api --body interface-change from core: deposit-api.
wrote tracks/core/outbox/20261115T114508Z__to-all__deposit-api.md
committed 2d270a7 on core/nrpic; the recipients see it now (push at the end of the session)
(exit 0)
```
- PASS: core posts interface-change to all: deposit-api
- PASS: only wt/core and refs/heads/core/nrpic changed (changed: ['core'], ['refs/heads/core/nrpic'])
```
[.]$ harness/bin/nrpic-ctx post --to all --type info --slug wave-start --body info from orch: wave-start.
wrote tracks/orch/outbox/20261115T114508Z__to-all__wave-start.md
committed a663830 on main; the recipients see it now (push at the end of the session)
(exit 0)
```
- PASS: orch posts info to all: wave-start
- PASS: only the main checkout and refs/heads/main changed (changed: ['orch'], ['refs/heads/main'])
```
[wt/kb]$ harness/bin/nrpic-ctx post --to orch --type kb-request --slug snapshot --body kb-request from kb: snapshot.
wrote tracks/kb/outbox/20261115T114508Z__to-orch__snapshot.md
committed ae1d7ae on kb/main; the recipients see it now (push at the end of the session)
(exit 0)
```
- PASS: kb posts kb-request to orch: snapshot
- PASS: only wt/kb and refs/heads/kb/main changed (changed: ['kb'], ['refs/heads/kb/main'])
```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx show A-emd-pbh outbox/20261115T114508Z__to-B-emd-gw__deposit-order.md
---
from: A-emd-pbh
to: B-emd-gw
type: request
needs_reply_by: 2026-11-27
refs: [arXiv:2611.12831, run:A-test]
---
request from A-emd-pbh: deposit-order.
(exit 0)
```
- PASS: the message file has the front matter of brief 11.3 (from harness/templates/outbox_message.md)

### Exactly once, before any merge

- PASS: no merge yet: inbox of orch lists 3 message(s), each exactly once (expected 3)
- PASS: no merge yet: inbox of core lists 2 message(s), each exactly once (expected 2)
- PASS: no merge yet: inbox of kb lists 3 message(s), each exactly once (expected 3)
- PASS: no merge yet: inbox of A-emd-pbh lists 3 message(s), each exactly once (expected 3)
```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx inbox
inbox of B-emd-gw (track/B-emd-gw): 4 unacknowledged
   [1] 2026-11-15 11:45Z  from A-emd-pbh   to B-emd-gw    request          deposit-order  reply by 2026-11-27
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-B-emd-gw__deposit-order.md
   [2] 2026-11-15 11:45Z  from A-emd-pbh   to all         info             hello-all
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-all__hello-all.md
   [3] 2026-11-15 11:45Z  from core        to all         interface-change deposit-api
       core/nrpic:tracks/core/outbox/20261115T114508Z__to-all__deposit-api.md
   [4] 2026-11-15 11:45Z  from orch        to all         info             wave-start
       main:tracks/orch/outbox/20261115T114508Z__to-all__wave-start.md
read one: nrpic-ctx show <from> outbox/<file>   all bodies: nrpic-ctx inbox --show   acknowledge: nrpic-ctx ack <n|file> ...
(exit 0)
```
- PASS: no merge yet: inbox of B-emd-gw lists 4 message(s), each exactly once (expected 4)

### Read commands write nothing and merge nothing

- PASS: 55 read commands in six worktrees (inbox, board, brief, show, owners, audit, digest; brief as a hook): no worktree file, index, HEAD or ref changed; no merge commit

### Copies of outboxes travel through main: still exactly once

```
[.]$ git merge --no-edit -q track/A-emd-pbh

(exit 0)
```
```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx sync
merged 4 commit(s) of main into track/B-emd-gw (8c61cd3); 3 file(s) changed
  areas: tracks/A-emd-pbh, tracks/orch
(exit 0)
```
- PASS: B syncs main (which now holds A's outbox and orch's outbox)
- PASS: B's branch now carries a copy of A's message
```
[wt/core]$ git merge --no-edit -q core/rng

(exit 0)
```
- PASS: after the gate merge, two syncs and core merging core/rng: inbox of orch lists 3 message(s), each exactly once (expected 3)
- PASS: after the gate merge, two syncs and core merging core/rng: inbox of core lists 2 message(s), each exactly once (expected 2)
- PASS: after the gate merge, two syncs and core merging core/rng: inbox of kb lists 3 message(s), each exactly once (expected 3)
- PASS: after the gate merge, two syncs and core merging core/rng: inbox of A-emd-pbh lists 3 message(s), each exactly once (expected 3)
```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx inbox
inbox of B-emd-gw (track/B-emd-gw): 4 unacknowledged
   [1] 2026-11-15 11:45Z  from A-emd-pbh   to B-emd-gw    request          deposit-order  reply by 2026-11-27
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-B-emd-gw__deposit-order.md
   [2] 2026-11-15 11:45Z  from A-emd-pbh   to all         info             hello-all
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-all__hello-all.md
   [3] 2026-11-15 11:45Z  from core        to all         interface-change deposit-api
       core/nrpic:tracks/core/outbox/20261115T114508Z__to-all__deposit-api.md
   [4] 2026-11-15 11:45Z  from orch        to all         info             wave-start
       main:tracks/orch/outbox/20261115T114508Z__to-all__wave-start.md
read one: nrpic-ctx show <from> outbox/<file>   all bodies: nrpic-ctx inbox --show   acknowledge: nrpic-ctx ack <n|file> ...
(exit 0)
```
- PASS: after the gate merge, two syncs and core merging core/rng: inbox of B-emd-gw lists 4 message(s), each exactly once (expected 4)
```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx inbox
inbox of B-emd-gw (track/B-emd-gw): 4 unacknowledged
   [1] 2026-11-15 11:45Z  from A-emd-pbh   to B-emd-gw    request          deposit-order  reply by 2026-11-27
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-B-emd-gw__deposit-order.md
   [2] 2026-11-15 11:45Z  from A-emd-pbh   to all         info             hello-all
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-all__hello-all.md
   [3] 2026-11-15 11:45Z  from core        to all         interface-change deposit-api
       core/nrpic:tracks/core/outbox/20261115T114508Z__to-all__deposit-api.md
   [4] 2026-11-15 11:45Z  from orch        to all         info             wave-start
       main:tracks/orch/outbox/20261115T114508Z__to-all__wave-start.md
read one: nrpic-ctx show <from> outbox/<file>   all bodies: nrpic-ctx inbox --show   acknowledge: nrpic-ctx ack <n|file> ...
(exit 0)
```
- PASS: B reads A's message from A's branch, not from its own copy

### Acceptance test 2: context round trip A -> B

```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx brief
nrpic brief 2026-11-15T11:45Z: you are B-emd-gw, branch track/B-emd-gw, worktree wt/B-emd-gw
gate:        G0 in progress
headline:    one sentence on the current state of knowledge
last-result: what was established last, with run ids or KB locators
next:        1. the most important next action
             2. the second
             3. the third
blockers:    none (or: what stops progress, and who can remove it)
needs:       none (or: requests to other owners; each one also exists as an outbox file)
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       4 unacknowledged -> nrpic-ctx inbox --show, then nrpic-ctx ack
  - interface-change from core: deposit-api (2026-11-15 11:45Z)
  - request from A-emd-pbh: deposit-order (2026-11-15 11:45Z, reply by 2026-11-27)
  - info from A-emd-pbh: hello-all (2026-11-15 11:45Z)
  - info from orch: wave-start (2026-11-15 11:45Z)
main:        0 commit(s) ahead of this branch (up to date); this branch has 0 commit(s) not on main
remote:      no upstream; push with git push -u origin track/B-emd-gw
tree:        clean
handoff:     Run next: `the exact command to run first`
read first:  tracks/B-emd-gw/HANDOFF.md, tracks/B-emd-gw/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
- PASS: B's start-up brief shows the request from A
- PASS: the brief has at most 40 lines (21)
```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx ack 20261115T114508Z__to-B-emd-gw__deposit-order.md --note will answer by 2026-11-20
acknowledged tracks/A-emd-pbh/outbox/20261115T114508Z__to-B-emd-gw__deposit-order.md (from A-emd-pbh, request)
committed 15cabb3 on track/B-emd-gw
(exit 0)
```
- PASS: B's acknowledgement is committed on track/B-emd-gw only (changed: ['B-emd-gw'], ['refs/heads/track/B-emd-gw'])
```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx inbox
inbox of B-emd-gw (track/B-emd-gw): 3 unacknowledged
   [1] 2026-11-15 11:45Z  from A-emd-pbh   to all         info             hello-all
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-all__hello-all.md
   [2] 2026-11-15 11:45Z  from core        to all         interface-change deposit-api
       core/nrpic:tracks/core/outbox/20261115T114508Z__to-all__deposit-api.md
   [3] 2026-11-15 11:45Z  from orch        to all         info             wave-start
       main:tracks/orch/outbox/20261115T114508Z__to-all__wave-start.md
read one: nrpic-ctx show <from> outbox/<file>   all bodies: nrpic-ctx inbox --show   acknowledge: nrpic-ctx ack <n|file> ...
(exit 0)
```
- PASS: the request has left B's inbox
- PASS: inbox --all still lists it, as acknowledged
```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx board
# Board of the NRPIC-cosmology program

Generated by `harness/bin/nrpic-ctx board` at 2026-11-15T11:45Z from the tips of the owners' branches (read through git only). Do not edit by hand: regenerate.

## Owners

| Owner | Branch @ tip | Behind / ahead of main | Gate | Headline | Next | Blockers | Inbox | Budget |
|---|---|---|---|---|---|---|---|---|
| orch | `main` @ `8c61cd3` 2026-11-15 11:45Z | (main) | — | — | — | — | 3 | — |
| core | `core/nrpic` @ `ec39955` 2026-11-15 11:45Z | 0 / 4 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 2 | 0 GPU-hours used of the allotment in coord/DECISI… |
| kb | `kb/main` @ `ea95723` 2026-11-15 11:45Z | 0 / 2 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 3 | 0 GPU-hours used of the allotment in coord/DECISI… |
| A-emd-pbh | `track/A-emd-pbh` @ `8482b8f` 2026-11-15 11:45Z | 2 / 0 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 3 | 0 GPU-hours used of the allotment in coord/DECISI… |
| B-emd-gw | `track/B-emd-gw` @ `15cabb3` 2026-11-15 11:45Z | 0 / 1 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 3 | 0 GPU-hours used of the allotment in coord/DECISI… |

Behind / ahead: commits of main not yet merged into the branch, commits of the branch not yet on main. Inbox: messages addressed to the owner or to all and not yet acknowledged.

## Other branches

| Branch | Owner | Kind | Tip | Behind / ahead of main | Last commit |
|---|---|---|---|---|---|
| `core/rng` | core | temporary | `7f322c5` 2026-11-15 11:45Z | 4 / 1 | core(ctx): info to A-emd-pbh: rng-draft |

## Messages

| Sent | From | To | Type | Subject | Reply by | Acknowledged by | Waiting for |
|---|---|---|---|---|---|---|---|
... (8 more lines)
(exit 0)
```
- PASS: A's board shows the acknowledgement by B: | 2026-11-15 11:45Z | A-emd-pbh | B-emd-gw | request | [deposit-order](tracks/A-emd-pbh/outbox/20261115T114508Z__to-B-emd-gw__deposit-order.md) | 2026
- PASS: A acknowledges by number

### Acceptance test 3: proposal round trip A -> orch -> DECISIONS -> every track

```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx post --to orch --type interface-change --slug pusher-order --body interface-change from A-emd-pbh: pusher-order. --reply-by 2026-11-30
wrote tracks/A-emd-pbh/outbox/20261115T114516Z__to-orch__pusher-order.md
committed 965c15f on track/A-emd-pbh; the recipients see it now (push at the end of the session)
(exit 0)
```
- PASS: A-emd-pbh posts interface-change to orch: pusher-order
- PASS: only wt/A-emd-pbh and refs/heads/track/A-emd-pbh changed (changed: ['A-emd-pbh'], ['refs/heads/track/A-emd-pbh'])
A also opens `proposal/A-emd-pbh/pusher-order` with the code of the proposal (`coord/INTERFACES/pusher.md`).
```
[.]$ harness/bin/nrpic-ctx inbox
inbox of orch (main): 4 unacknowledged
   [1] 2026-11-15 11:45Z  from A-emd-pbh   to all         info             hello-all
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114508Z__to-all__hello-all.md
   [2] 2026-11-15 11:45Z  from core        to all         interface-change deposit-api
       core/nrpic:tracks/core/outbox/20261115T114508Z__to-all__deposit-api.md
   [3] 2026-11-15 11:45Z  from kb          to orch        kb-request       snapshot
       kb/main:tracks/kb/outbox/20261115T114508Z__to-orch__snapshot.md
   [4] 2026-11-15 11:45Z  from A-emd-pbh   to orch        interface-change pusher-order  reply by 2026-11-30
       track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T114516Z__to-orch__pusher-order.md
read one: nrpic-ctx show <from> outbox/<file>   all bodies: nrpic-ctx inbox --show   acknowledge: nrpic-ctx ack <n|file> ...
(exit 0)
```
- PASS: the proposal appears once in the orchestrator's inbox
```
[.]$ git commit -q -m Decision 0002: pusher order -- coord/DECISIONS/0002-pusher-order.md

(exit 0)
```
```
[.]$ harness/bin/nrpic-ctx ack 20261115T114516Z__to-orch__pusher-order.md --note accepted as decision 0002
acknowledged tracks/A-emd-pbh/outbox/20261115T114516Z__to-orch__pusher-order.md (from A-emd-pbh, interface-change)
committed 94a47c6 on main
(exit 0)
```
- PASS: the orchestrator acknowledges the proposal on main
```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx sync
merged 4 commit(s) of main into track/A-emd-pbh (f5a19f4); 3 file(s) changed
  decision: coord/DECISIONS/0002-pusher-order.md
  areas: tracks/orch
(exit 0)
```
- PASS: after sync A-emd-pbh reads decision 0002 in its own worktree
- PASS: after sync B-emd-gw reads decision 0002 in its own worktree
- PASS: after sync core reads decision 0002 in its own worktree
- PASS: after sync kb reads decision 0002 in its own worktree
- PASS: A's board shows the proposal acknowledged by orch

### A boundary crossing: sync refuses to merge, audit names the commit

```
[wt/B-emd-gw]$ git commit -q -am B edits a shared file

(exit 0)
```
```
[.]$ git commit -q -m orch edits the charter -- coord/CHARTER.md

(exit 0)
```
```
[wt/B-emd-gw]$ harness/bin/nrpic-ctx sync
sync FAILED: merging main into track/B-emd-gw conflicts in:
  coord/CHARTER.md
Auto-merging coord/CHARTER.md
CONFLICT (content): Merge conflict in coord/CHARTER.md
Automatic merge failed; fix conflicts and then commit the result.
The merge was aborted; the branch is as before. A conflict means a shared path was edited on this branch (or main wrote into this owner's directory). Tell the orchestrator: nrpic-ctx post --to orch --type blocker --slug sync-conflict --body '...'
(exit 1)
```
- PASS: sync fails and names coord/CHARTER.md
- PASS: the merge was aborted: B's branch and tree are as before

### Audit: foreign paths, large file, tracked file under an ignored root, read-only

```
[wt/A-emd-pbh]$ git commit -q -m A commits a 1.5 MB file and force-adds scratch output

(exit 0)
```
```
[.]$ harness/bin/nrpic-ctx audit
# Audit (2026-11-15T11:45Z, `nrpic-ctx audit`, read-only)

## 1. Commits touching paths outside the owner's directory and OWNERSHIP

Range per branch: `main..<branch>`. OWNERSHIP is taken from main (the accepted version). Merge commits count only for what they change against every parent (conflict resolutions), and a merge of a branch that is neither on main nor the owner's own is reported.

**`track/A-emd-pbh`** (owner A-emd-pbh):
- `22d1d1d4c` 2026-11-15 11:45Z A commits a 1.5 MB file and force-adds scratch output: `scratch/A-emd-pbh/leak.txt`

**`track/B-emd-gw`** (owner B-emd-gw):
- `37961d573` 2026-11-15 11:45Z B edits a shared file: `coord/CHARTER.md`

**`proposal/A-emd-pbh/pusher-order`** (owner A-emd-pbh) (proposal branch: foreign paths are its purpose; reviewed at acceptance):
- `5f9c20463` 2026-11-15 11:45Z A(proposal): pusher interface: `coord/INTERFACES/pusher.md`

## 2. Files above 1 MB

Added or changed on a branch (not on main):

- `track/A-emd-pbh` `22d1d1d4c` `tracks/A-emd-pbh/analysis/big.bin` 1.50 MB, still at the tip

## 3. Tracked files under ignored roots

Every tracked path at the tip of every branch, tested against the ignore rules of the main checkout (`git check-ignore --no-index`). A root is a directory of the first or second level (`scratch/`, `wt/`, `refs/arxiv_<id>/`, ...).

- `scratch/A-emd-pbh/leak.txt` (root `scratch/`, rule `.gitignore:2: scratch/`) on `track/A-emd-pbh`
... (8 more lines)
(exit 1)
```
- PASS: audit exits 1 when it has findings
- PASS: section 1 names B's commit touching coord/CHARTER.md
- PASS: section 1 lists the proposal branch as a proposal
- PASS: section 2 lists the 1.5 MB file
- PASS: section 3 lists the tracked file under scratch/
- PASS: section 1 names A's commit of scratch/A-emd-pbh/leak.txt, and none of A's own paths
- PASS: no false positives: core (with its merge of core/rng) and kb pass
- PASS: findings counted: Findings: 4 (section 1: 2, section 2: 1, section 3: 1)
- PASS: audit changed nothing
- PASS: audit --branch core/nrpic: no findings on core

### Acceptance test 7: cold start from HANDOFF.md and the brief

```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx brief
nrpic brief 2026-11-15T11:45Z: you are A-emd-pbh, branch track/A-emd-pbh, worktree wt/A-emd-pbh
gate:        G0 in progress
headline:    one sentence on the current state of knowledge
last-result: what was established last, with run ids or KB locators
next:        1. the most important next action
             2. the second
             3. the third
blockers:    none (or: what stops progress, and who can remove it)
needs:       none (or: requests to other owners; each one also exists as an outbox file)
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       2 unacknowledged -> nrpic-ctx inbox --show, then nrpic-ctx ack
  - interface-change from core: deposit-api (2026-11-15 11:45Z)
  - info from orch: wave-start (2026-11-15 11:45Z)
main:        1 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 4 commit(s) not on main
remote:      no upstream; push with git push -u origin track/A-emd-pbh
tree:        clean
handoff:     Run next: `python3 tracks/A-emd-pbh/analysis/expball.py --check`
read first:  tracks/A-emd-pbh/HANDOFF.md, tracks/A-emd-pbh/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
- PASS: A's brief carries the gate and the exact next command of HANDOFF.md
```
[/data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0]$ harness/bin/nrpic-ctx brief --hook
nrpic brief 2026-11-15T11:45Z: you are A-emd-pbh, branch track/A-emd-pbh, worktree wt/A-emd-pbh
gate:        G0 in progress
headline:    one sentence on the current state of knowledge
last-result: what was established last, with run ids or KB locators
next:        1. the most important next action
             2. the second
             3. the third
blockers:    none (or: what stops progress, and who can remove it)
needs:       none (or: requests to other owners; each one also exists as an outbox file)
budget:      0 GPU-hours used of the allotment in coord/DECISIONS/0006
inbox:       2 unacknowledged -> nrpic-ctx inbox --show, then nrpic-ctx ack
  - interface-change from core: deposit-api (2026-11-15 11:45Z)
  - info from orch: wave-start (2026-11-15 11:45Z)
main:        1 commit(s) ahead of this branch -> nrpic-ctx sync; this branch has 4 commit(s) not on main
remote:      no upstream; push with git push -u origin track/A-emd-pbh
tree:        clean
handoff:     Run next: `python3 tracks/A-emd-pbh/analysis/expball.py --check`
read first:  tracks/A-emd-pbh/HANDOFF.md, tracks/A-emd-pbh/STATUS.md, CLAUDE.md, harness/RULES.md
end of session: rewrite STATUS.md and HANDOFF.md, append JOURNAL.md, commit, push your branch
(exit 0)
```
- PASS: as a SessionStart hook (cwd from the JSON on stdin) it briefs A
```
[/data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0]$ harness/bin/nrpic-ctx brief --hook
nrpic brief unavailable: /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0 lies in the data root scratch/ of the main checkout, not in a worktree; run the command from your worktree (or pass -C <worktree>)
(exit 0)
```
- PASS: a hook call outside any worktree exits 0 with a one-line notice

### Refusals

```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx -C wt/B-emd-gw post --to core --type info --slug x --body x
nrpic-ctx post: write commands act only on the worktree you are in; run them there without -C
(exit 2)
```
- PASS: post with -C naming another worktree is refused
```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx post --to A --type info --slug self --body x
nrpic-ctx post: a message to yourself is a note, not a message
(exit 2)
```
- PASS: a message to oneself is refused
```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx post --to core --type gossip --slug x --body x
nrpic-ctx post: --type must be one of info, request, proposal, interface-change, blocker, kb-request
(exit 2)
```
- PASS: an unknown message type is refused
```
[wt/A-emd-pbh]$ harness/bin/nrpic-ctx board --write
nrpic-ctx board: board --write is for the orchestrator in the main checkout (coord/ changes only on main)
(exit 2)
```
- PASS: board --write outside the main checkout is refused
- PASS: the refused commands wrote nothing
```
[wt/kb]$ harness/bin/nrpic-ctx sync
nrpic-ctx sync: tracked files have uncommitted changes; commit them first (nrpic-ctx sync merges into a clean tree):
   M tracks/kb/STATUS.md
(exit 2)
```
- PASS: sync refuses a worktree with uncommitted tracked changes

### nrpic-wt retire: checks, never removes

```
[.]$ harness/bin/nrpic-wt retire A-emd-pbh
wt/A-emd-pbh (track/A-emd-pbh) may NOT be retired yet:
  - the tip 22d1d1d4c of track/A-emd-pbh is neither on a remote branch, nor tagged, nor on main
(exit 1)
```
- PASS: retire refuses while A's tip is neither pushed, tagged nor on main
```
[wt/A-emd-pbh]$ git push -q origin track/A-emd-pbh

(exit 0)
```
```
[.]$ harness/bin/nrpic-wt retire A-emd-pbh
wt/A-emd-pbh (track/A-emd-pbh) is clean and its tip 22d1d1d4c is safe (remote origin/track/A-emd-pbh).
Retiring is the orchestrator's housekeeping after asking the user (brief 11.2); nothing was removed.
The command, for a person to run from the main checkout (the branch and its tags stay):
  git worktree remove wt/A-emd-pbh
(exit 0)
```
- PASS: after the push it prints the command for a person; the worktree is still there
```
[.]$ harness/bin/nrpic-wt check A-emd-pbh
  [wt] PASS  toplevel /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo/wt/A-emd-pbh, branch track/A-emd-pbh
  [build] PASS  build dirs: none yet; no symbolic link into another worktree or the main checkout
  [copy] PASS  harness/wt_copy.list names no file
  [kokkos] PASS  submodule not initialised (only needed to build: nrpic-wt new --kokkos, or CLAUDE.md 'Machine')
(exit 0)
```
- PASS: nrpic-wt check A-emd-pbh passes

### The orchestrator's generated files

```
[.]$ harness/bin/nrpic-ctx board --write
wrote coord/BOARD.md (not committed)
(exit 0)
```
- PASS: board --write in the main checkout writes coord/BOARD.md with every owner
```
[.]$ harness/bin/nrpic-ctx digest --write --week 2026-W46
wrote coord/digests/2026-W46.md (not committed)
(exit 0)
```
- PASS: digest --write writes coord/digests/2026-W46.md with the requests and the audit
```
[wt/kb]$ harness/bin/nrpic-ctx ack 20261115T114508Z__to-B-emd-gw__deposit-order.md
nrpic-ctx ack: '20261115T114508Z__to-B-emd-gw__deposit-order.md' matches 0 messages addressed to kb
(exit 2)
```
- PASS: kb cannot acknowledge a message addressed to B

### nrpic-doctor rows of this harness, inside the scratch repository

```
[wt/A-emd-pbh]$ harness/bin/nrpic-doctor --rows wt,build,ctx
nrpic-doctor: wt/A-emd-pbh (branch track/A-emd-pbh, owner A-emd-pbh) 2026-11-15T11:45Z
  [wt]      PASS     toplevel /data/haiyangw/nrpic/scratch/harness/ctx-20261115T114506Z-eqe9bfv0/repo/wt/A-emd-pbh, branch track/A-emd-pbh
  [build]   PASS     build dirs: none yet; no symbolic link into another worktree or the main checkout
  [ctx]     PASS     the board lists all 5 owners; a message committed on one branch appears exactly once in the other's inbox, nothing written there (throwaway repository)
summary: 3 PASS, 0 FAIL, 0 MISSING, 0 SKIP -> every row passes
(exit 0)
```
- PASS: nrpic-doctor --rows wt,build,ctx passes in wt/A-emd-pbh
```
[.]$ harness/bin/nrpic-ctx board
# Board of the NRPIC-cosmology program

Generated by `harness/bin/nrpic-ctx board` at 2026-11-15T11:45Z from the tips of the owners' branches (read through git only). Do not edit by hand: regenerate.

## Owners

| Owner | Branch @ tip | Behind / ahead of main | Gate | Headline | Next | Blockers | Inbox | Budget |
|---|---|---|---|---|---|---|---|---|
| orch | `main` @ `e7eb680` 2026-11-15 11:45Z | (main) | — | — | — | — | 3 | — |
| core | `core/nrpic` @ `03df4b7` 2026-11-15 11:45Z | 1 / 5 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 2 | 0 GPU-hours used of the allotment in coord/DECISI… |
| kb | `kb/main` @ `7b8c31b` 2026-11-15 11:45Z | 1 / 3 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 3 | 0 GPU-hours used of the allotment in coord/DECISI… |
| A-emd-pbh | `track/A-emd-pbh` @ `22d1d1d` 2026-11-15 11:45Z | 1 / 4 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 2 | 0 GPU-hours used of the allotment in coord/DECISI… |
| B-emd-gw | `track/B-emd-gw` @ `37961d5` 2026-11-15 11:45Z | 1 / 3 | G0 in progress | one sentence on the current state of knowledge | the most important next action | none (or: what stops progress, and who can remove it) | 3 | 0 GPU-hours used of the allotment in coord/DECISI… |

Behind / ahead: commits of main not yet merged into the branch, commits of the branch not yet on main. Inbox: messages addressed to the owner or to all and not yet acknowledged.

## Other branches

| Branch | Owner | Kind | Tip | Behind / ahead of main | Last commit |
|---|---|---|---|---|---|
| `core/rng` | core | temporary | `7f322c5` 2026-11-15 11:45Z | 7 / 1 | core(ctx): info to A-emd-pbh: rng-draft |
| `proposal/A-emd-pbh/pusher-order` | A-emd-pbh | proposal | `5f9c204` 2026-11-15 11:45Z | 5 / 3 | A(proposal): pusher interface |

## Messages

| Sent | From | To | Type | Subject | Reply by | Acknowledged by | Waiting for |
... (10 more lines)
(exit 0)
```
