# G3 of Track E: what is open (batch 19, 2026-11-25)

G3 is not ready for review. The scope is fixed (spec/scope/SCOPE.md 4d with the amendments 4d.9, written
before any production run); no G3 production run has run yet.

1. Reference proper (A1, A4, A9, A10): direct 4e6 paths done (E-20261125-152832-c301e92: gate 0.99865 +-
   0.00058, skewness 0.0199 +- 0.0012, state at N_f); the importance-sampled nu = 4 part (A9: 2 per cent per
   side) not started; a lattice variant at sigma = 0.1 of the same size would bound the coarse-graining.
2. The zeta reader (4d.1 (ii)) and its tests Z0-Z2 (A3): not written; their 32^3 mirrored pairs exist
   (E-20261125-153148-cfad424; health and mirror checked, E-20261125-155027-a9037d9).
3. Card runs in the shared queue: q0050 G3P (pilot, re-entry of q0045 at priority 2), q0051 G3C, q0052 G3R
   (priority 2), q0053 G3B00 and q0054 G3B01 (priority 5, after G3P). The remaining 98 pairs of the
   baseline and the 16 level-2 pairs wait for the pilot's measured cost (A12).
4. Resolved in the same session: the 4e6 run E-20261125-152832-c301e92 gives a skewness of the one-patch
   field at N_f of 0.0007 +- 0.0012 (delta N: 0.020); the smoke run's 0.023 was noise. The non-Gaussianity
   comes from the map, as the review said; A4 tests the NR evolution at +-0.0012 in skewness.
5. Reservation carried: the slicing is geodesic only (A8); U-A4'(a) of G2 stays FAILED as written and is
   answered by G3-C.
6. Package items (C9-C17): schematic of the parameter space, result figures, working-note section, fresh
   verifier: after the runs.
