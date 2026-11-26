# C-sidm G2: what the gate still lacks

State at the end of the lead session of batch 27 (2026-11-26). G2 is NOT met and the package is
not ready for an independent review: three card runs that serve C1, C2, C7 and C9 have not been
read (one, A16b344, ended during this session and is being closed). Seven items pass (C3, C4, C8,
C12, C14, C19, C20); none fails as written any more; thirteen are open. Every collapse time of the
package is the alpha_min = 0.3 lapse marker of a run made without the horizon finder
(C-20261125-160207-05b6db1).

## What changed in batch 27

- Closed (nrpic-run finish) and judged with registered analyses, figures read: N4c (NS.3 held:
  t_c 295.78 M at N = 1e4), N6b344 (B17.5 held: t_c 252.31 M), N6b324 (B17.6 held: holds 600 M
  within +-0.015), D2eta1 (B17.4 held: t_c 164.01 vs 163.41 M; the run itself FAILED on record,
  guard stop at 190.4 M after collapse), N6b344e1 (B20.3 first half held: t_c 252.41 M), D2f2s2+
  (D2.3 seed-pair part FAILED: 2.24 M against 2 M). Analyses C-20261126-114801-ea62ac3,
  -120656-f5c62bb, -121702-b6b1eda, -121836-c7a76c1, -123219-f734997.
- The threshold is bracketed at one mesh (M/8) and one N (1e6): (0.324, 0.344) contains
  y_max = 0.334032; the same fates at N = 1e5. The gauge member of the unstable side agrees.
- Closed without analysis (priority-5 continuations): A334s3c+ C-20261124-082221-7f03a8e
  (completed 600 M); A334s2c+ C-20261124-053105-2fcc8af (finish running at the end of the session).
- The working note has its G2 section (Sec. V, table VI).

## Item by item, and the queue entry each waits for

| Item | What is missing | Queue entry | Prediction |
|---|---|---|---|
| C1, C7, C9 threshold with three-way convergence | the bracket on M/16 at N = 1e6 | q0055 A16b344 (ENDED: C-20261126-043714-8ea1c35, 600 M, all particles excised; close and read with nseries.py beside N6b344), q0057 A16b324 (job 5382 pending) | B20.2, B20.1 (JOURNAL 2026-11-25T16:02Z) |
| C1, C2, C7, C9 gauge leg of the stable member | y0 0.324 kin with shift_eta 1.0 | q0058 N6b324e1 (waiting) | B20.3 second half |
| C2 seed scatter at N = 1e5 (not required for the bracket) | A334s2c+, A334s3c+ to read | none (closed or closing) | seed scatter of the control |
| C10, C11, C13, C15, C16 figures | G2 note figures by one script each (run_all), ladder schematic, slice mosaic | none (processor work) | - |
| C17 note | G2 figures in the note; final text once the legs are read | none | - |
| C18 verifier | fresh verifier (ruling 0041 item 3) after q0055, q0057, q0058 are read | none | - |
| C5, C6 report and reproducibility package | complete with the items above | none | - |

## What a G2 verifier must cover

- Recompute from the raw histories, with readers of its own: collapse times and alpha_c changes of
  the N-series (N4c, the N = 1e5 control, N6c), the bracket (N6b344, N6b324, their N = 1e5
  members, the gauge and mesh members), block A (15 runs), D2 (ctrl, f1s1, f2s1, f4s1, f2s2, m16,
  eta1), and the collision counts per particle and per M.
- That every collapse time is the lapse marker (no horizon file in any run), including the two
  t_c the batch-20 recheck did not cover: 206.64 M (M/4) and 163.41 M (D2 f2).
- That the decks of batches 17 and 20 differ from their series only where make_decks_b17.py and
  make_decks_b20.py say; that the N = 1e6 samples share the sampler and seed of N6c.
- The count test of the collision rate before t_c (z = -3.39 at f = 4; REVIEW-wave3 section 14);
  the conductivity series (1.020 +- 0.004); every failed prediction on record (JOURNAL
  2026-11-24T13:12Z, 2026-11-25T12:21Z, 2026-11-26T12:20Z).
- The reading of the D2 seed pair: whether the five M/8 variants may be pooled as realisations
  (lead's JUDGEMENT, JOURNAL 2026-11-26T12:20Z).

## Reservations of G1 and where they stand

| G1 reservation | State |
|---|---|
| 1 conductivity at the per-cent level | answered: kappa/kappa_1 = 1.020 +- 0.004 (batch 11) |
| 2 threshold from collapse times or contraction against a control, three seeds | controls hold at N = 1e6; the bracket is read from fates against N6c; one seed per bracket member at N = 1e6 |
| 3 quantities named after the data | the block A ripple window was changed after the data (labelled); the 20 M band of B17.6 was written before the run |
| 4 card tests without a second check | open: verifier above |
| 5 M/4 mesh does not hold the equilibrium | M/8 holds it at N = 1e6 (N6c); M/16 member read next |

Removed from the queue in batch 17 (they serve no G2 item once the threshold is read at
N = 1e6): q0019-q0021, q0025-q0027 (kicked N = 1e5 continuations); their partial records stay.
