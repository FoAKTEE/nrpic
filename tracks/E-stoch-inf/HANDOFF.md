# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (2026-11-20) and G1
(2026-11-21, with reservations; coord/GATES.md). The G2 production ladder on the release card
build has run and is judged (`g2prod/JOURNAL.md` entry 2); the G2 package still lacks the items
listed in `stage/G2/OPEN.md` (verifier, note sections, figures C10-C13, gauge leg of C2).

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show

## Other sessions in this worktree (decision 0028, started 2026-11-22)

Packages `repro/scope`, `repro/langevin`, `repro/equations` (reproduction of arXiv:2512.14649
and arXiv:2401.08530 with a working note) run in their own sessions in this worktree and
commit on this branch. Commit path-limited only (`git commit -m ... -- <paths>`), never
`git add -A`, never touch `repro/`. Their card jobs (Slurm 4929, 4931 at 18:20 PST, runs
E-20261123-020704-2b99463 and E-20261123-021204-2f573ec) count as E's two card jobs: read and
closed by `repro/scope`, not by the G2 lead.

## Card runs of g2prod: all finished and closed

The sequencer ended by itself at 13:49 PST 2026-11-22 ("queue empty and every run closed";
`/data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/seq.log`); nothing to restart. Run ids
(outputs in /data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/; dumps usr.sf.000NN.dump,
records usr.sf.hst, usr.sf.con.hst):

| Label | Run | Card-h |
|---|---|---|
| T (timing) | E-20261121-202929-43dcc9c | 0.11 |
| P256v6 (SR 256^3) | E-20261121-202935-31520bc | 0.51 |
| U256ap / am (seed A, s = +-1) | E-20261121-211214-0377aab / E-20261121-214629-da64fb7 | 0.62 / 0.62 |
| U320ap / am | E-20261122-023427-0ac3f0b / E-20261122-110042-ffcb4b3 | 1.47 / 1.48 |
| U256bp / bm (seed B) | E-20261122-033244-564627b / E-20261122-071038-d9f933b | 0.62 / 0.62 |
| U256hp / hm (s = +-1/2) | E-20261122-113320-9bbb52b / E-20261122-152116-0542096 | 0.62 / 0.62 |
| U256nc (sign-flip control to t = 3.75) | E-20261122-190341-0419be6 | 0.22 |

Analyses (processors, registered, package g2prod): T + P256v6 E-20261123-015014-b4ecd4e; seed A
group (ap, am, hp, hm; all 21 dumps) E-20261123-014858-8e72d4c; seed B E-20261123-021730-a421438
(the earlier E-20261123-014905-2bf3570 used the wrong realisation: per-mode numbers invalid);
U320 E-20261123-020751-0baf597 (E-20261123-015650-493cff5 failed); SCOPE 4c judge: see
`g2prod/JOURNAL.md` 2.3. Scripts: `g2prod/scripts/analyse_g2.py` (wraps usr/scripts/
analyse_cards.py; --seed, --last), `judge_g2.py` (SCOPE 4c), `judge_tp.py` (T, P256v6).

## Files to read first

`STATUS.md`; `g2prod/JOURNAL.md` entries 1 and 2; `spec/scope/SCOPE.md` 4c; `stage/G2/OPEN.md`,
`stage/G2/CHECKLIST.md`, `stage/G2/STAGE_REPORT.md`; `stage/REVIEW-wave3.md` Part D; `RISKS.md`
(R13, R17, R21, R24, R25).

## Next, in order

1. G2 verifier (C18): a fresh-context agent given the g2prod run directories, SCOPE 4c and
   entry 1 (not the conclusions of entry 2), recomputing every SCOPE 4c number with its own
   reader. One session, processors only.
2. Working-note G2 sections and figures C10-C13 (verification-ladder schematic, convergence
   figure, constraint norms against time, slice mosaic with zoom boxes), one script per
   figure; the repro/note package of decision 0028 may carry them - coordinate through the
   plan, do not write into repro/.
3. C2 gauge leg: geodesic slicing only (RISKS R6). Either a ruling that a gauge variant is not
   required for the USR reproduction at G2, or a design (lapse option for the scalar-field
   set-up) - asked of orch in this session's outbox.

## Traps

- `nrpic-stage verify` fails on `runs` while card jobs of E are submitted (repro's jobs count).
- Pair dumps only at equal recorded times (|dt| <= 1e-9). Cold 256^3 dumps: read sequentially;
  four 256^3 runs take about 45 min on 3 cores (disk-bound, about 100 MB/s per reader).
- analyse_cards.py has no seed option: for seed B use `analyse_g2.py --seed 20261116`.
- The odd halving is 2 by construction of the floor (two amplitudes): only the even halving is a
  test (SCOPE 4c, U-A4'(b)).
- Large figure PDFs stay in run directories; commit PNGs. `nrpic-run finish` and `nrpic-ctx
  post/ack` commit by themselves (path-limited).
- `$NRPIC_RUN_DIR` in a command: inside `bash -c '...'`; do not redirect into run.log (the
  wrapper writes it).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  verification suite 834-860, context protocol 957-1004, M11 544-547.
