# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 34, wave 3, 2026-11-27
15:21-15:50 PST: the two runs decision 0046 item 2 required, GM2/GM3, the G2 package).
Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md). The G2 package is complete for an
independent review in the lead's judgement: every item but C18 (fresh verifier) is PASS or NA,
with failures on record (stage/G2/OPEN.md). Nothing of B runs on cards; nothing is queued.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-run status | grep -E "submitted|running"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md` (state per item, failures on record, what the
verifier should recompute first); `stage/G2/CHECKLIST.md` C1-C3; `population/JOURNAL.md` entries
2026-11-27 15:22, 15:24, 15:28; `shear/JOURNAL.md` 2026-11-26 15:02; `coord/DECISIONS/0046` item 2.

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw`.

## Running at the end of the session

| What | How it is read |
|---|---|
| `harness/bin/nrpic-stage verify B-emd-gw G2 --full`, detached (setsid nohup, PID 2643528, log `$S/tmp/verify_full_b34.log`, which ends with `exit=`), started 16:08 PST on commit 631acef88; reads every byte of the G2 outputs (hundreds of GB, hours). The quick pass of batch 34 (`--no-checksums`) is committed: PASS, 0 failed checks, 383 runs finished | when the log ends: `git status` shows stage/G2/VERIFY_RESULTS.md/.json changed; read the checks (runs, checksums, rerun, compare); commit them, then `harness/bin/nrpic-stage report B-emd-gw G2` and commit STAGE_REPORT.md. A FAIL on `checksums` names the run: compare with its sha256sums.txt and say whether it bears on the gate |

No card job, no processor run of B is left running; q0070 (job 5524) is done and its run closed.

## What G2 still waits for

- C18: the fresh-context verifier (requested: outbox 20261127T234330Z__to-orch__g2-package-ready-verifier.md).
  When its VERIFIER.md lands (stage/G2/ or a subdirectory), answer every WRONG or NOT CONFIRMED
  item with a registered run, correct the note and ledger, rerun `note/scripts/run_all.py`
  (registered, `.venv/bin/python`), compile, checker
  (`python3 ~/.claude/skills/paper-writing/scripts/check_manuscript.py --main main.tex --compile`),
  then stage collect/verify/report.
- Ruling on GM3 (outbox 20261127T234330Z__to-orch__g2-ruling-halo-catalogue-mesh.md): if the
  orchestrator asks for a 256^3 member at eight per cell, it needs 256^3 initial data at
  `--ppc 2` (about 6 h on one core by the 128^3 data's 5.5 h; run detached with
  `nrpic-run submit --background`) and about 1.5-3 card-h (chain, priority 2); write the
  prediction into population/JOURNAL first.

## Results of this session (all registered, closed, figures looked at)

- C3: q0070 B-20261127-232258-37c6773 (64^3, eight per cell, to a = 143), judged by
  B-20261127-232628-1361e3b (`population/scripts/judge_c3.py`, c3_mesh_pair.png).
- GM2/GM3: B-20261127-232236-7ab7aa2 (`compare_legs.py` on analysis B-20261126-221911-a0531db).
- Note v4: B-20261127-232833-5891f77 (Table VIII rows g2_gm2, g2_gm3, g2_c3a, g2_c3b, g2_n7*).

Traps:
- Analyses longer than a session: `nrpic-run submit --background`.
- GR particle files carry the rest-mass weight (R25): use `--equal-mass`.
- The note's `main.pdf` is 1.4 MB (above the 1 MB guideline, below the 5 MB hook limit); it was
  1.43 MB before this session too.
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; at most 6 cores.
