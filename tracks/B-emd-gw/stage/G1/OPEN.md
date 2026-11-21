# What G1 of B-emd-gw still lacks

State 2026-11-20, batch 2a (lead). Items 1-2 are owed before the lead would call the
package complete; 3-10 are open science and wording items that G1 records (none blocks a
criterion). The items 1-6 of the wave-2 version are done: criterion 1 (oblique and
expanding-box waves, both diagnostics, independent verifier), the G1 schematics, the note's
G1 sections, the verifier of the wave-2 runs (verifier2); item 6 (runs check) is in
VERIFY_RESULTS.md.

## Owed by the gate

1. C18, ledger recomputed by an independent agent: rows not yet recomputed by verifier2,
   verifier3 or the G0 verifier: the second-round table of `note/tables/ledger.tex`
   (jittered nulls, delta = 0.0025, rerun floor, parity; checked only by the note helper's
   own second reading, note/JOURNAL.md N13-N15), gauge rows 120-125, eps = 0.1 and 0.3 of
   rows 116-117, and the wave-1 rows outside the G0 claims. One verifier package, fresh
   context, artefacts only, processors only; it writes `stage/G1/verifier4/VERIFIER.md` with
   a verdict per row.
2. Note v3 wording from the verifiers (C17 stays PASS; these are corrections): ledger row 168
   "forward combination"; row 101 0.0088 over all dumps (or "at the restart cadence") with the
   driven-shift value 0.018; rows 118-119 define s and add the direct zero-shift-to-driven map;
   then `nrpic-stage report` again.

## Recorded at G1 (open, not blocking)

3. waves/README.md wordings (verifier3 F5, X1, F2/F4/X2/X3): spectral Weyl vs TT holds for the
   forward combination (<= 6.4e-11); X plus amplitudes at N >= 48 are moduli that include a
   rounding share of 1.3e-8 to 1.6e-8 in the spatial quadrature (stage/REVIEW-wave3.md); state
   the construction of the sixth-order curvature. Owed by the waves session that closes
   round 1.
4. first_source/README.md wordings (verifier2): "linear in eps to 0.05 percent" holds for
   eps 0.1 against 0.3 (eps = 1: 0.2 percent, fourth order); "32^3 and 64^3 agree to 0.5 percent
   up to a = 80" is not a bound for eps = 1 (1.02 percent at a = 75.8) or the driven shift
   (1.9 percent). Owed by the first_source session.
5. waves round 1: F2 (k = 2 pi (1,2,0), nonzero discrete divergence) and the step test XS have
   run (B-20261120-222841-acfe21d, -222849-3b921b7, -222849-e5673dc), predictions in
   waves/JOURNAL.md 2026-11-20 22:30; not analysed.
6. Convergence of the first source in particle number (1, 8, 27 per cell) and at 128^3: runs
   done (B-20261119-153655-2deca0a), scan analyses done unattended (B-20261120-223236-e213594,
   -223241-f1efd4f), outcomes of P12, P13 and the (1 + eps^2) test not written.
7. The grid-scale TT field of a jittered lattice: the jitter-without-wave run (P16 follow-up)
   is not made.
8. Adopt G_tot into gw_diag (`gw_diag/gwdiag/gauge.py`, tests, written in round 1 and
   uncommitted; waves step 4).
9. N2 (embedded ellipsoid in a periodic box) needs core's per-species history.
10. The Newtonian mode's force error (kh)^2/12 is quoted with every GR-Newton comparison
    unless core adds a fourth-order option. G0 reservation still [TO VERIFY]: Omega today
    sigma^(7/2) (2403.15126:1074) against sigma^(5/2) from its eq. (result_OmZ); criterion 2 is
    judged on the emitted energy.
