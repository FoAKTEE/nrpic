# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0, G1 and G2 (the last two with reservations,
coord/GATES.md). G3 (tail statistics of zeta, SCOPE 4d with amendments 4d.9 A1-A14) has its two robustness legs
passed (G3-C, G3-R) and a fast zeta reader; what it lacks is the baseline itself (246 of 256 card runs), then its reading.

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Where things are

- Scope of G3: `spec/scope/SCOPE.md` 4d and 4d.9 A1-A14 (A12: 0.0351 card-h a baseline run; A13: what "G3 met" means).
- Predictions and outcomes: `g3/JOURNAL.md` entries 2, 4 (criteria), 5-9 (pilot), 10-13 (batch 27: G3-C, G3-R, the table
  map, pilot zeta); `zeta/JOURNAL.md` (reader tests); `g3/amend/JOURNAL.md` (reference).
- Readers: `g3/read_g3c.py` (4d.4 + A6), `g3/read_g3r.py` (4d.5 + A7), `g3/read_pilot.py` (per member: R^NR, health, zeta
  with `--map table --msteps 4000`), `g3/zeta_table.py` (the table map), `g3/validate_table.py`, `g3/diag_table.py`,
  `g3/compare_readers.py`, `g3/check_lists.py` (run it on every new list before queueing).
- Review record: `stage/REVIEW-wave3.md` parts J and K; open items `stage/G3/OPEN.md`; risks R39, R42, R43 (R41 closed).

## Results of batch 27 (all registered, figures looked at)

- G3-C PASSES (E-20261126-115943-32970f2); G3-R PASSES (E-20261126-120438-9d48377).
- Zeta table: about 20 s a 128^3 member, cleared under g3/JOURNAL.md entry 12 (E-20261126-115112-43da266,
  E-20261126-115925-a2c6da5); TB-1 and P5-3 FAILED as written (bars below the ~1e-9 round-off of the double map, R43).
- Pilot zeta (E-20261126-120434-5dda273): P5-5 holds (skewness 0.0200 over ten members; reference 0.0199 +- 0.0012).

## Card jobs of this owner (shared queue; nothing running now)

| Entry | What | Read by |
|---|---|---|
| q0053, q0054 G3B00/01 | minus members of pairs 0-9 with pairs 10-18 (28 runs) | read_pilot.py --map table --msteps 4000 |
| q0061-q0065 G3B02-06 | mirrored pairs 19-73, 22 runs a job | idem; C6-1 cost check (g3 entry 6) |
| q0066 G3L00 | level-2 pairs 0-4 + k000/k001 on usr_prod_kd.athinput | C6-2 cost, C6-4 preview, A8 record |

They wait at low priority (3-4) behind other tracks' gate runs and had not moved by the end of batch 27. Close each with
`harness/bin/nrpic-run finish <run_id>` (run id: `harness/bin/nrpic-queue show <qid>`) before reading.

Processor work left running: `harness/bin/nrpic-stage verify E-stoch-inf G3` (started 04:08 PST, PID 2045896, the first
checksum pass over every run of the track, 77 GB read by 04:20; log scratch/E-stoch-inf/tmp/verify_g3.log). When it has
ended it leaves stage/G3/VERIFY_RESULTS.{md,json} modified: look at them, commit them, rerun `nrpic-stage report`.

## Next, in order

1. As baseline jobs end: close, read every member (`read_pilot.py OUT --run <run dir> --members <labels> --map table
   --msteps 4000 --procs 4`, about 1.5 min a member a core), keep the per-member json; when all 128 pairs exist, the pair
   statistics of A5 and the comparison (V), (T), A4 of A2/A4 (a pair-level script is still to write; predictions in
   g3/JOURNAL.md entry 4 stand).
2. Queue pairs 74-127 (about five lists of 22 runs; through check_lists.py; preregistered to entry 4) when the queue has
   room; level-2 pairs 5-15 after G3L00 measures the level-2 cost (into A12).
3. Coarse-graining bound of the reference (R39); then the package items (figures, ledger, note section, fresh verifier who
   also repeats the table check against the long-double map on a second member).

## Traps

- AthenaK takes command-line overrides only for lines the deck has (parameter_input.cpp line 400): check lists.
- Do not set bars below about 1e-9 against map_rk4: it carries round-off at that level (R43); compare with zv_lib.
- The member json field `table.spot_holds` uses TB-1's 1e-10 bar; the rule of entry 12 is 1e-8 (spot_max_abs).
- Card runs only through `harness/bin/nrpic-queue add`; production runs need `--preregistered <file>#entry-N`.
- zeta = -R^NR at first order; F_+ of zeta corresponds to F_- of R^NR (A2).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686, verification suite
  834-860, context protocol 957-1004.
