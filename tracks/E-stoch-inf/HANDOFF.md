# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (2026-11-20) and G1
(2026-11-21, with reservations; coord/GATES.md). The G2 package (ultra-slow-roll case against the
criteria of `spec/scope/SCOPE.md` 4c) is complete and waits for its independent review; one
criterion, U-A4'(a), is FAILED on record by rulings 0030 item 2 and 0036 item 2.

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Where things are

- G2 package: `stage/G2/` (CHECKLIST.md: every item PASS, NA by ruling, or FAIL on record; EVIDENCE.md;
  OPEN.md; STAGE_REPORT.md; VERIFIER.md = fresh verifier of batch 14 with `verifier/`). Lead's recheck:
  `stage/REVIEW-wave3.md` Part F.
- Ladder and judgement: `g2prod/` (README with run ids and the rerun recipe; JOURNAL entries 1-4:
  predictions, the SCOPE 4c judgement, the quarter pair). Entry 4: Q-a refuted (M factor 4.1275 from
  s = 1/2, 1/4), Q-b and Q-c hold; entry 4.2: the three-amplitude reading, a finding after the data.
- Note: `repro/note/manuscript/main.pdf` (32 pages; Sec. IV = the G2 sections, Appendix F =
  architecture and timeline, ledger Table XVI). Rebuild: `repro/note/README.md` "How to rerun and
  rebuild" (registered run_all; last R16 E-20261125-035757-340bd1e; copy figures PDF and tables,
  latexmk, checker with the forbid list of the README plus `U256|U320|g2prod|judge_`). The compiled
  PDF is 5.05 MB, just under the hook's 5 MiB: do not add raster figures without shrinking it (R31).
  The G1 note `note/` points to it and stays at its G1 state.

## Runs in flight

| What | Id | Output | Read by |
|---|---|---|---|
| FL128h, SR 128^3 at s = 1/2 (card) | queue q0037 (waiting, priority 2) | scratch/E-stoch-inf/<run_id>/ (`nrpic-queue show q0037` gives the run id once dispatched) | floor/JOURNAL.md entry 2 (predictions F1-F5 in entry 1) |
| FL256h, SR 256^3 at s = 1/2 (card) | queue q0038 (waiting, priority 2) | same | same |

Card runs are closed with `harness/bin/nrpic-run finish <run_id>` (the queue does not finish them).
Reading the floor runs: `repro/figs/figures/dumppass.py --run <dir> --base sr --label FL128h --out
<run dir> --last --scale 0.5 --save-modes` (and FL256h), the s = 1 counterparts again with `--last
--save-modes` (C128S in E-20261123-020704-2b99463 under C128S/, CL256S's last dump in
E-20261124-130952-4be980b), statistics over the shells n^2 = 2-12 as in floor/JOURNAL.md entry 1; one
figure per shell statistic; outcome into floor/JOURNAL.md entry 2 and repro/figs RESULTS.md Fig. 7.

## Stage verify and report (batch 15)

`nrpic-stage verify E-stoch-inf G2 --no-checksums` (log scratch/E-stoch-inf/tmp/b15/verify.log; the
full checksum pass over about 280 run directories, hundreds of GB, takes one to two hours: run it
without `--no-checksums` in a session with that time and no 256^3 reader active, if the reviewer
asks), then `nrpic-stage report E-stoch-inf G2`. Result on tip 81e736ac: harness verdict FAIL on
C3, C7 (failures on record by rulings) and on `runs` only: 7 ablation runs of the reproduction name
core's noise-level2 card executable, republished after core's review (request to core in the outbox;
stage/G2/OPEN.md item 7). Every rerun, regeneration and comparison check PASS.

## Next, in order

1. The G2 independent review (orch; outbox 20261125T0*__to-orch__g2-ready-for-review): answer its
   findings in the package; do not reword 4c.
2. Floor runs q0037/q0038 when they have run (above). Not part of G2.
3. After orch's G3 ruling: recompute the three-amplitude statistics D1, D2 with the track's own
   reader (R30) before any later criterion relies on them; plan G3 (tail statistics; level 2 of
   core-v0.7 as a sensitivity; budget from orch).

## Traps

- Card runs only through `harness/bin/nrpic-queue add` (decision 0033: five jobs for the account); no
  own sequencers; give `--package` so edits elsewhere do not hold the entry.
- `nrpic-run submit` refuses when its `--package` has uncommitted files (main.pdf after a compile:
  `git checkout -- .../main.pdf` or commit first); production runs need `--preregistered <file#anchor>`.
- The pre-commit hook refuses files above 5 MiB (the note PDF is at 5.05 MB); `git add <dir>` picks up
  main.pdf: reset it if it grew.
- In the note the noise amplitude is lambda; s is the window steepness. The program's records call
  the amplitude s.
- Pair dumps only at equal recorded times; the odd halving is 2 by construction of the 4c floor, only
  the even halving tests. analyse_cards.py has no seed option (seed B: analyse_g2.py --seed 20261116).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  verification suite 834-860, context protocol 957-1004.
