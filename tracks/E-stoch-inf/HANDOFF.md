# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (2026-11-20) and G1
(2026-11-21, with reservations; coord/GATES.md). The reproduction of arXiv:2512.14649 and
arXiv:2401.08530 is complete (note `repro/note/manuscript/main.pdf`); G2 is open, its lacks are
`stage/G2/OPEN.md` (quarter-pair reading, G2 verifier, G2 note sections, four figures).

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Runs in flight (lead of batch 13, 2026-11-24)

| What | Id | Where its output appears | Read by |
|---|---|---|---|
| FL128h, SR 128^3 at s = 1/2 (card) | queue q0037 (run id when dispatched: `nrpic-queue show q0037`) | scratch/E-stoch-inf/<run_id>/ (sr.sf.000NN.dump, .modes) | floor/JOURNAL.md entry 1, F1-F5 |
| FL256h, SR 256^3 at s = 1/2 (card) | queue q0038 | same | same |
| quarter-pair analysis (processors, 3 cores) | E-20261124-233223-51b52c0 | scratch/E-stoch-inf/E-20261124-233223-51b52c0/ (run.log, summary JSON, fig/) | g2prod/JOURNAL.md entry 3 (Q-a..Q-c) |

Card runs are closed with `harness/bin/nrpic-run finish <run_id>` (the queue does not finish them;
it commits the manifest). If the analysis E-20261124-233223-51b52c0 is not closed (`nrpic-run
status` or its manifest), check `run.log`: if it ended, `nrpic-run finish` it; if it was killed at the
end of the batch-13 session, close it as failed and rerun the same command (its manifest
`command`), about 25 min on 3 cores.

Reading the quarter pair: the analysis writes the group summary of analyse_cards (group g2q: U256 =
s 1/2 hp, U256m = hm, U256h = s 1/4 qp, U256hm = qm). Then the halving/floor part of
`g2prod/scripts/judge_g2.py` on that summary (keys as for g2a, see entry 2.3) and judge Q-a (even
factor of M at cN 6.52 from s = 1/2 and 1/4: 3.98 +- 0.015, refuted below 3.9625; H within
4.00 +- 0.05), Q-b (common mode at N_f -2.5e-6 +- 0.4e-6), Q-c (U-A0, A1, A3; records; even/odd rms
6.33e-5 +- 5 percent). Write g2prod/JOURNAL.md entry 4 with figures looked at; update
stage/G2/CHECKLIST.md C3, C7; nrpic-stage report.

Reading the floor runs: `repro/figs/figures/dumppass.py --run <dir> --base sr --label FL128h --out
<run dir> --last --scale 0.5 --save-modes` (and FL256h), the s = 1 counterparts again with `--last
--save-modes` (C128S in E-20261123-020704-2b99463 under C128S/, CL256S's last dump in
E-20261124-130952-4be980b), statistics over the shells n^2 = 2-12 as in floor/JOURNAL.md entry 1;
one figure per shell statistic; outcome into floor/JOURNAL.md entry 2 and repro/figs RESULTS.md
Fig. 7 (TO VERIFY item).

## Stage verify

`nrpic-stage verify E-stoch-inf G2` needs one to two hours (sha256 of 270 run directories,
hundreds of GB); batch 13 stopped it at run 67 to leave the disk to the analysis. Run it when no
256^3 reader is active, then `nrpic-stage report E-stoch-inf G2`.

## Finished in batch 13

Reproduction leftovers (commit 51b52c00): conts.json, continue journal entry 13, SETUP_AUDIT item 4
(N* + 8.10), CARD_PLAN.md actual costs (8.99 card-hours over the reproduction), RESULTS.md S14.
Review: stage/REVIEW-wave3.md Part E. Stage G2: collect, checklist, OPEN, verify, report. Outbox:
orch (G2 after the reproduction: verifier session, where the note sections go), core (figstyle).

## Files to read first

STATUS.md; stage/G2/OPEN.md; g2prod/JOURNAL.md entries 2.3 and 3; floor/JOURNAL.md entry 1;
coord/DECISIONS/0030 item 2 (Track E ruling); repro/note/README.md (verdict table); RISKS.md (R25,
R26, R28, R29).

## Next, in order

1. Quarter pair: Q-a..Q-c (above), then the G2 package to independent review is possible with the
   U-A4'(a) failure on record once items 2 and 3 exist (ruling 0030 item 2; OPEN.md).
2. G2 verifier (C18): a fresh-context agent given the g2prod run directories, SCOPE 4c and entry 1
   and 3 (not the conclusions of entries 2 and 4), recomputing every SCOPE 4c number with its own
   reader. Processors only.
3. G2 note sections (C17) and figures C10 (verification-ladder schematic), C13 (slice mosaic with
   zoom boxes), USR resolution figure (C11), architecture/timeline update (C16): where, per orch's
   answer to outbox 20261124T234057Z.

## Traps

- Card runs only through `harness/bin/nrpic-queue add` (decision 0033: five jobs for the account);
  no own sequencers; give `--package` so edits elsewhere in the worktree do not hold the entry.
- `nrpic-run submit --launcher local` waits in the foreground; a tool call that times out keeps it
  in the background of the session, and it ends with the session: long analyses need a session
  that stays, or a detached start.
- Pair dumps only at equal recorded times (|dt| <= 1e-9). Cold 256^3 dumps: read sequentially;
  four 256^3 runs take 25-60 min on 3 cores (disk-bound).
- analyse_cards.py has no seed option: for seed B use `analyse_g2.py --seed 20261116`.
- The odd halving is 2 by construction of the floor (two amplitudes): only the even halving tests.
- `noise_mode_scale` scales the mode file (slice and sources); the dump pass needs `--scale` equal to
  it, or the linear reference is off by s.
- Large figure PDFs stay in run directories; commit PNGs. `nrpic-run finish` and `nrpic-ctx
  post/ack` commit by themselves (path-limited).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  verification suite 834-860, context protocol 957-1004.
