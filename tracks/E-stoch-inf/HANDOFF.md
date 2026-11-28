# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0, G1 and G2 (the last two with reservations,
coord/GATES.md). G3 (tail statistics of zeta, SCOPE 4d with amendments 4d.9 A1-A14) was read on 71 of 128 mirrored pairs
(tail shape agrees with one-patch delta N; variance +0.28 +- 0.07 per cent, (V) failed as written); 102 pairs now ran.

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Card jobs of this owner (shared queue, priority 2; all on .work/build_gpu_v07 as SCOPE 4d fixes)

Batch 36 (2026-11-27 18:20-18:45 PST) entered the missing members again after the queue audit (g3/JOURNAL.md entry 19).
Each entry is a batch job of about 25 minutes. A preempted batch entry now goes back to waiting by itself, at most twice
(harness/RULES.md "Automatic retry"; every attempt is a new run, the old run stays "submitted" until you close it).

| Entry | Label | List | Holds | State at 18:38 PST |
|---|---|---|---|---|
| q0088 | G3L02b | g3/inputs/l2_02.list | level-2 pairs 11-15 + baseline pairs 126-127 (14 runs) | waiting (auto-retry 1 of 2 after job 5561 was preempted) |
| q0101 | G3B12 | base12.list | baseline m077, pairs 78-81, 105 (11) | waiting |
| q0102 | G3B13 | base13.list | baseline pairs 106-111 (12) | waiting |
| q0103 | G3B14 | base14.list | baseline pairs 112-114, 117-119 (12) | waiting |
| q0104 | G3B15 | base15.list | baseline pairs 120-125 (12) | waiting |
| q0105 | G3L03 | l2_00.list | level-2 pairs 0-4 + kdriver k000, k001 (12) | waiting |
| q0106 | G3L04 | l2_04.list | level-2 lm005 + pairs 6-10 (11) | waiting |

When all seven have completed: 128 of 128 baseline pairs and 16 of 16 level-2 pairs, with the two kdriver records (A8).

Already complete (all runs closed, nothing missing): baseline pairs 0-76, 82-104, 115-116 = 102 pairs. Where each member
lies (scratch/E-stoch-inf/<run>/<label>/):
- pairs 0-70 and p071: G3P pilot + G3B00-G3B06 (read in g3 entry 17; readings listed there).
- m071, pairs 72-76, p077: E-20261127-233720-922a7ab (job 5537, preempted, closed stopped; m077 there is cut: unused).
- pairs 82-92: E-20261127-233721-5a83c08; pairs 93-103: E-20261128-000123-7ea62cc (both completed).
- pair 104: E-20261128-000127-f4fbf9f (p105 cut); pairs 115-116: E-20261128-011609-ea3b9f3 (p117 cut).
- level 2 lp005: E-20261128-014814-dbef4a2 (lm005 cut). Nothing usable in -012413-7ca1bf1, -015422-3b47d95.
Pair 71 = p071 of job 5419 (E-20261127-011021-d486e1b) with m071 of job 5537: same seed, sign rule, deck and build.

## Next, in order

1. As each entry ends: `harness/bin/nrpic-queue list --owner E-stoch-inf`; `nrpic-run finish <run_id>` for every
   attempt (preempted ones `--status stopped`; finish hashes 34 GB a full run: run it in the background); check
   `batch.list.status` per member. An entry left `incomplete` after a third preemption: close its runs, then
   `nrpic-queue retry <id>`, or re-list only its missing members with `g3/inputs/pick_lists.py` (copy by label).
2. Read every new member: `nrpic-run submit --kind production --gate G3 --preregistered
   tracks/E-stoch-inf/g3/JOURNAL.md#entry-15 --package tracks/E-stoch-inf/g3 --launcher local --cores 3 -- python3
   tracks/E-stoch-inf/g3/read_pilot.py '$NRPIC_RUN_DIR' --run <card run dir> --deck tracks/E-stoch-inf/g2prod/inputs/
   usr_prod.athinput --lead-json <scratch>/E-20261125-161456-8d3f43c/zeta_tests.json --members <labels> --procs 3 --map
   table --msteps 4000 --save-fields`; then `pairs_g3.py` with every reading run and `--pairs 0-127` (prediction entry
   first; entry 4 stands). Pairs split over two runs (71, 77, 105, 117, level-2 5) need both readings passed.
3. Level 2 against level 0 on the same pairs; A4 from the saved fields; the variance difference (sigma-paired reference
   R39, a 160^3 subset if cards allow); fresh verifier; `harness/bin/nrpic-stage verify E-stoch-inf G3 --full`.

## Where things are

- Scope of G3: `spec/scope/SCOPE.md` 4d and 4d.9 (A13: what "G3 met" means: 128 pairs, (V), (T), A4, level 2 reported,
  fresh verifier). Predictions and outcomes: `g3/JOURNAL.md` entries 2, 4, 6 (criteria, cost), 14-19.
- Readers: `g3/read_pilot.py`, `g3/pairs_g3.py`, `g3/check_lists.py` (run on every list), lists by `g3/inputs/gen_lists.py`
  (base07-11, l2_01-02) and `g3/inputs/pick_lists.py` (base12-15, l2_04: lines copied by label).
- Note: `repro/note/manuscript/main.tex` section V (G3); review `stage/REVIEW-wave3.md` part L; `stage/G3/OPEN.md`,
  `stage/G3/CHECKLIST.md`.

## Traps

- AthenaK takes command-line overrides only for lines the deck has: run check_lists.py on every list.
- Bars below about 1e-9 against map_rk4 fail on round-off (R43); P5-3 fails that way on every box.
- `nrpic-run submit` refuses a dirty package: commit before a registered run (the note build uses --package repro/note).
- The note PDF is near the 5 MB hook limit; pass it through ghostscript (/prepress) after a rebuild.
- zeta = -R^NR at first order; F_+ of zeta corresponds to F_- of R^NR (A2).
- Before reading a card run, check its job COMPLETED (sacct, or `nrpic-queue audit`); a preempted batch leaves
  batch.list.status short and its last member directory without usr.sf.00001.dump.
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686, verification suite
  834-860, context protocol 957-1004.
