# What G1 of B-emd-gw still lacks

State 2026-11-21, batch 5 (lead). Nothing owed by the gate remains: item C18 is met (the
second verifier, stage/G1/VERIFIER-C18b.md, recomputed the last ledger rows; line 59 and lines
34, 56, 63 are reworded as it asks), and the note v3 corrections are made (CHECKLIST C17,
C18). What follows is recorded at G1 and blocks no criterion.

## Small additions not made (not corrections)

1. Ledger: a row for verifier3's direct zero-shift-to-driven map of the gauge rows 118-119
   (residual 2.3e-5 to 2.7e-3 in stage/REVIEW-wave3.md) and the driven-shift value 0.018 of
   row 101; both are numbers of the verifier's runs, to be read into ledger.py with their run
   ids when the note is next rebuilt.
2. The verifier_c18b qualifications 3b (the second digit of the two-per-cell value at a = 10 is
   not robust; the ratios are) and 3e (the window a <= 64 excludes the dump at a = 64.07) are
   recorded here; the reworded rows state what was measured.

## Recorded at G1 (open, not blocking)

3. waves: the small-step spectral-Weyl vs TT residual of X (6e-11, spikes 2.8e-10 at t = 2 and
   6) is not explained; an x10 run of F2 at N = 64 would test the Gamma floor of F2-4.
4. first_source: whether the extra grid-scale TT that the wave adds by a = 12 is leakage of a
   wave-modulated noise field or a response (P16' cannot separate them); particle
   convergence at 128^3 (8 per cell not run, decision accepted by the lead).
5. N2 (embedded ellipsoid in a periodic box): core ran it with the group moments of
   core-v0.6 (+2.56, +1.09, +0.42, -0.14 per cent at 64^3-256^3 against the ODE crossing;
   the short axes sit 0.02 R_L below the ODE before the crossing at every resolution). The
   track's own check and the reading of that offset are G2 work.
6. The Newtonian mode's force error: the spectral symbol of core-v0.6 removes the (kh)^2/12
   of the seven-point Laplacian; new GR-Newton comparisons use it or quote the error.
7. G0 reservation still [TO VERIFY]: Omega today sigma^(7/2) (2403.15126:1074) against
   sigma^(5/2) from its eq. (result_OmZ); criterion 2 is judged on the emitted energy. The
   factor 3 between lines 324 and 581 of 2312.12499 waits for kb's claims package.
