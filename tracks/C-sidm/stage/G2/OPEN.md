# C-sidm G2: what the gate still lacks

State at the end of the lead session of batch 32 (2026-11-27). Nineteen of twenty checklist items
pass; the one open item is C18, the fresh verifier (decision 0016 item 4; ruling 0045 item 5: it is
sent once q0057 and q0058 are read, which this session did). Failures on record that stay with the
passing items: A.4 and BA.3 (N = 1e5 controls collapse by particle noise; ruling 0045 item 5),
NS.2, D2.3 seed-pair part (2.24 M against 2 M), the failed run D2eta1 (guard stop after its
collapse), the withdrawn predictions B17.1-B17.3 (JOURNAL). Every collapse time of the package is
the alpha_min = 0.3 lapse marker of a run made without the horizon finder
(C-20261125-160207-05b6db1; ruling 0041 item 3).

## What changed in batch 32

- Closed (nrpic-run finish) and judged with registered analyses, figures read: A16b324
  C-20261126-121449-1d37e77 (6.3844 card-hours; B20.1 held: no collapse on M/16, block means
  -0.0171..+0.0107, C-20261127-084538-8e98060) and N6b324e1 C-20261126-130519-1a79a66 (2.6175
  card-hours; B20.3 second half held: no collapse, central lapse within 1.4e-5 of shift_eta 2.0,
  C-20261127-084417-79c0e4d). C1, C2, C7, C9 pass: the bracket keeps its fates on both meshes and
  in both gauges at N = 1e6.
- Note figures of G2 (C10, C11, C13, C15, C16) from run C-20261127-084828-b6ca5ce; note compiled
  and checked (C17); rerun list RERUN.md (C6).

## Item by item

| Item | State | What it waits for |
|---|---|---|
| C18 verifier | OPEN | a fresh verifier with the artefacts (this package, RERUN.md), not the conclusions |
| all others | PASS | - |

## What the verifier should recompute first

1. The fates of the eleven threshold runs (RERUN.md section 1) from the raw `cc.nrpic.hst` with a
   reader of its own that applies the restart rule (a later row replaces earlier rows from its
   time on): the marker crossings 295.78, 534.81, 252.31, 217.97, 252.41, 229.79 M and "no
   crossing by 600 M" for N6c, N6b324, A16b324, N6b324e1, A324s1i.
2. The band readings of the stable members (block means of alpha_c - alpha_c(0) within +-0.03;
   eta1 minus eta2 below 0.01) and that the 20 M windows were fixed before the runs (JOURNAL
   2026-11-25T16:02Z, B20.1-B20.3).
3. That the decks of the legs differ from N6b344/N6b324 only in the mesh (M/16) or in shift_eta
   (make_decks_b20.py) and that all N = 1e6 members share the sampler and seed of N6c.
4. That no run had the horizon finder (no horizon file in any output directory).

## Further items for the verifier (from batch 27)

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
