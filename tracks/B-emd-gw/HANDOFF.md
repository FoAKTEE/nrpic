# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead of batch 28, wave 3, 2026-11-26
13:20-13:50 PST: q0060 and three detached analyses closed and judged; C15 done; note v3).
Rewritten at the end of every session.

State in three lines: G0 and G1 are signed (coord/GATES.md); G2 is not met (stage/G2/OPEN.md).
Nothing of B is in the card queue. One processor analysis runs (GM2, GM3); two requests wait at
the orchestrator (rulings on C1 and C3; a fresh verifier for C18).
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox && git status --short && harness/bin/nrpic-run status | grep -E "submitted|running"`

Files to read first: `STATUS.md`; `stage/G2/OPEN.md`; `stage/G2/CHECKLIST.md` (C1, C2, C3, C11,
C17, C18); `stage/REVIEW-wave3.md` section "Batch 28"; `population/JOURNAL.md` entries
2026-11-26 13:22 (how GM1-GM4 are judged) and 13:27 (outcomes).

## Running at the end of the session

| Run id | What | Then |
|---|---|---|
| B-20261126-212212-c54d979 | `analyze_gr.py --equal-mass --times 4,8,12,14,16,18,20,21 --halo-times 14,16,18,20,21` on the 256^3 Gamma-driver box (q0060 run B-20261126-105021-6343c13), 5 workers, about 30 GB each; started 13:22 PST | `nrpic-run finish` it (if its parent was killed with the session, its run.log ends with "# exit=" or not: if not and no python process of it is left, rerun the same command with fewer workers). Then register `compare_legs.py --base $S/B-20261125-115558-2ab4161/analysis_gr_gd.json --halo-base $S/B-20261126-022407-87e8803/analysis_gr_gd.json --leg m256gd:$S/B-20261126-212212-c54d979/analysis_gr_m256gd.json` and judge GM2 (band ratio within 5 per cent to a = 64, inside 0.8-1.2 before a = 100, within 20 per cent to a = 132; Omega_cor all shells at a = 121 1.0-2.0x, refuted outside 0.8-3) and GM3 (counts inside 2 sqrt(N) + 2 at a = 64-132, largest mass within 10 per cent), look at pop_legs.png |
| (closed) | q0060's run B-20261126-105021-6343c13 closed completed at 13:59 (280 GB hashed, 3.7461 card-h) | nothing |

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw`.

## Established this session (run ids in population/JOURNAL.md 2026-11-26 13:27)

- GM1 holds (256^3 shifted box to a = 143, K_max < 0); GM4 refuted (Hr 1.11x); q0060 3.75 card-h.
- M2 counts hold, largest masses fail at a = 64-72; M3 holds to a = 50, fails at a = 100 (1.214),
  high-k part holds; Q1 high-k part refuted; S2, S3 hold at the same stage.
- C15: analyze_b.py, analyze_f.py, analyze.py, analyze_gr.py now write numbers only; one script
  per figure (`flrw_conv/scripts/fig_*.py`, `population/scripts/fig_pop_*.py`); driver
  `stage/G2/scripts/c15_figs.py`; pixel-identical (B-20261126-213450-f833a78).
- Note v3: section VI rewritten, abstract and summary for G2, ledger rows g2_gm1..g2_s3, compiled
  (B-20261126-213742-dcee645). `note/main.pdf` is 1.4 MB and tracked since batch 21.

## What G2 still needs (stage/G2/OPEN.md)

- C2, C11: GM2/GM3 above; then the mesh figure in the shifted gauge is that comparison's
  pop_legs.png.
- C17: one paragraph on GM2/GM3 in note section VI (`\subsection{What the legs decided...}`), a
  ledger row from the GM comparison (add its run key to note/scripts/common.py RUNS and a row in
  ledger.py values_g2/LEDGER_G2), registered run_all.py, copy outputs, compile, checker
  (`python3 ~/.claude/skills/paper-writing/scripts/check_manuscript.py --main main.tex --compile`).
- C1, C3: FAIL as written; apply the orchestrator's ruling (outbox 20261126T213945Z).
- C18: fresh verifier (requested); then `nrpic-stage verify B-emd-gw G2 --full` once, and report.
- Not G2: strain parts of A1-A3 and GD3 with equal masses; a proper-distance halo mass (R23);
  shearing-dust amplitude without stream crossing (if the ruling asks for it at G2).

Traps:
- GR particle files carry the rest-mass weight (R25): use `--equal-mass`.
- compare_legs.py: use `--halo-base` with an equal-mass catalogue; strain bases may be older.
- FoF halo masses depend on the spatial gauge (R23): state the gauge with every mass.
- Dump times: read from headers (the chains wrote extra dumps at segment ends).
- A local `nrpic-run submit` runs in the foreground: a long analysis started from a session dies
  with the session's shell unless detached; check its process after a session ends.
- Card runs only via `harness/bin/nrpic-queue add`; commit before adding; at most 6 cores; a
  full stage verify hashes hundreds of GB.
