# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0, G1 and G2 (the last two with reservations,
coord/GATES.md). G3 (tail statistics of zeta, SCOPE 4d with amendments 4d.9 A1-A14) is in production on the cards; the
zeta reader is cleared (decision 0042 item 1) but is too slow on 128^3 dumps to read the baseline (R41): that is next.

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Where things are

- Scope of G3: `spec/scope/SCOPE.md` 4d and 4d.9 A1-A14 (A12 has the measured pilot cost, 2026-11-25 batch 23).
- Predictions and outcomes: `g3/JOURNAL.md` entries 2, 4 (criteria), 5-9 (pilot, reading, next entries); `zeta/JOURNAL.md`
  entries 4-9 (reader tests; entry 9: Z1 with variational expected values passes); `g3/amend/JOURNAL.md` (reference).
- Reader scripts: `g3/read_pilot.py` (R^NR, health, cost, relation; zeta with --msteps > 0, too slow at 128^3),
  `g3/compare_readers.py` (lead's vs verifier's map on sampled and tail cells), `zeta/zeta_reader.py` (map_rk4),
  `zeta/z1_variational.py`, `g3/check_lists.py` (run it on every new list: overrides must exist in the deck).
- Independent check of the reader: `g3/zeta_verify/VERIFY.md` (verifier's library `scripts/zv_lib.py`).
- Review record: `stage/REVIEW-wave3.md` Part J; open items `stage/G3/OPEN.md`; risks R41 (map cost), R42 (lists).

## Runs in flight (shared card queue; nothing to wait for)

| Entry | What | Read by |
|---|---|---|
| q0051 G3C, job 5348, run E-20261126-030044-6933f21 | seed 0 at s = +-1, +-1/2, +-1/4, 21 dumps with constraints | three-amplitude reader with A6 (G3-C) |
| q0052 G3R (priority 2) | seed 0 at s = +-1, +-1/2 on 160^3 | Richardson reader with A7 (G3-R) |
| q0053, q0054 G3B00/01 | minus members of pairs 0-9, pairs 10-18 | read_pilot.py (R^NR now), zeta reader later |
| q0061-q0065 G3B02-06 | mirrored pairs 19-73, 22 runs a job | idem; C6-1 cost check (entry 6) |
| q0066 G3L00 | level-2 pairs 0-4 + k000/k001 on usr_prod_kd.athinput | C6-2 cost, C6-4 preview, A8 record |

Close each with `harness/bin/nrpic-run finish <run_id>` (run id: `harness/bin/nrpic-queue show <qid>`); checksums of 16 GB
take some minutes.

## Next, in order

1. zeta at 128^3 (blocking): the map costs about 1.5 core-hours a member at 1000 steps (memory-bound on 2.1e6 cells).
   Candidate: tabulate the reader's map_rk4 along the box relation (corr 0.999997, slope 0.0132252 at 128^3) on a fine
   grid in d phi, plus the first and second derivative across it (variational, zv_lib), interpolate per cell; check
   against map_rk4 on 1e5 random cells and every cell beyond 2.5 sigma_lin (bar 1e-8 in zeta); prediction first.
   Then read the pilot's zeta (P5-3 is moot; P5-5 stands) and the baseline pairs.
2. Read G3C (q0051) and G3R (q0052) when they end (A6, A7).
3. After G3L00: the measured level-2 cost into A12, then level-2 pairs 5-15 and baseline pairs 74-127 (about five
   jobs of 22 runs), at most six queue entries a session; every list through check_lists.py.
4. Coarse-graining bound of the reference (R39): paired-noise runs at sigma = 0.01, 0.05, 0.1.

## Traps

- AthenaK takes command-line overrides only for lines the deck has (parameter_input.cpp line 400): check lists.
- Level 2 needs only `scalar_field/noise_level=2` (mesh mode is its default); kdriver needs `usr_prod_kd.athinput`.
- Card runs only through `harness/bin/nrpic-queue add`; production runs need `--preregistered <file>#entry-N`; the queue
  refuses packages with uncommitted files.
- zeta = -R^NR at first order; F_+ of zeta corresponds to F_- of R^NR (A2).
- A run with noise_mode_scale = s has a .modes record that already carries s (R32).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686, verification suite
  834-860, context protocol 957-1004.
