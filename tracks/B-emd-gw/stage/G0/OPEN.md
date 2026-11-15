# What G0 of B-emd-gw still lacks

State 2026-11-15, after the lead's review. Items 1-3 are owed before the gate can be
tagged; the rest are open questions that G0 records and later gates close.

## Owed by the gate itself (charter 9.2, brief 13.3-13.4; CHECKLIST.md items)

1. Working note v0 (C5, C15): a REVTeX note under `tracks/B-emd-gw/note/` written with
   `/paper-writing`, carrying sections 1-8 of `REPORT.md`, with the manuscript checker
   passed with `--compile`. Not started.
2. Schematics (C6, C9, C10, C14): track architecture (exists / to be ported / new: AthenaK
   Z4c + NRPIC + `nrpic_cosmo` exist; gw_diag analysis new; Newtonian mode on core/newton
   to be merged; GW output and initial-data TT part requested) and the gate timeline
   (REPORT.md section 8), drawn with `/sleep-paper-figure-style`. Not drawn.
3. Independent verifier report (C16): `VERIFIER_REPORT.md` by a fresh agent given the
   artefacts (EVIDENCE.md), not the conclusions. The lead's own check is `REVIEW.md`;
   it is the owner's, not independent of the track.
4. `nrpic-stage verify` on the committed tip: not run (it rebuilds through `nrpic-env exec`,
   whose environment has no numpy until the worktree has a `.venv`, and `.venv` is not in
   the ignore list, so creating it dirties the worktree; outbox to orch). The lead's
   equivalent clean-export re-check is run B-emd-gw-20261115-131016-03b1119.
5. Knowledge base: the reference statements are verified at the source in
   `kb-data/raw` (REPORT.md section 5), not yet in an indexed snapshot (kb request).

## Scientific items open at G0 (closed at G1-G3)

6. GR reference solution of the plane-symmetric pancake (the brief's row cites only the
   Newtonian exactness; check 1E shows the naive form is the decaying mode only):
   planar Szekeres-class dust, to be derived and read (1708.09143) [TO VERIFY].
7. The gauge-safe pre-shell-crossing reference for the first source: the second-order
   Poisson-gauge strain carried to the code's slicing and zero shift, or a gauge-invariant
   comparison through K^TT [TO VERIFY].
8. The noise floor after shell crossing: the jittered-lattice null run (needs a jitter
   option in `cosmo/ic/make_east.py`, request to core).
9. Whether the late rise of h^TT in the existing cosmology dumps (gw_diag scouting,
   a > 600) is the second-order gauge piece of the flat projection [JUDGEMENT, TO VERIFY].
10. Covariant (York) TT decomposition with respect to the actual metric (vector elliptic
    solve): not implemented; the flat projection is exact at first order only.
11. The literature box comparison of S2: 2212.00425 and 2312.12499 not read.
12. Baseline discrepancies: the Omega prefactor of 2403.15126 line 1501 missed by a factor
    144-392; whether 2605.04487's code is model B.
13. Oblique linear-wave test (generator fix by core), gauge wave to 1000 crossings, the
    robust-stability test per gauge in a Minkowski box.
14. FLRW and growth rows: particle-number convergence in the production configuration,
    growth rate f(a), a glass or Poisson start (VERIFY.md section 7).
15. Multi-code row: the shearing-dust comparison of arXiv:2003.08014 (specified in
    VERIFY.md section 3, not run).
16. Thin periodic boxes with Z4c and particles (core to confirm) and the cost of 8 per
    cell, dump I/O and the end 3/delta.
