# G3 of Track E: what is open (batch 19, 2026-11-25)

G3 is not ready for review. The scope is fixed (spec/scope/SCOPE.md 4d with the amendments 4d.9, written
before any production run); no G3 production run has run yet.

1. Reference proper (A1, A4, A9, A10): direct 4e6 paths for s0.01_lattice (with the state at N_f) and
   s0.1, run E-20261125-152832-c301e92 (processors, started 07:28 PST); the importance-sampled nu = 4 part
   (A9: target relative standard error 2 per cent per side) not started.
2. The zeta reader (4d.1 (ii)) and its tests Z0-Z2 on processors (A3): not written.
3. Card runs in the shared queue: q0050 G3P (pilot, re-entry of q0045 at priority 2), q0051 G3C, q0052 G3R
   (priority 2), q0053 G3B00 and q0054 G3B01 (priority 5, after G3P). The remaining 98 pairs of the
   baseline and the 16 level-2 pairs wait for the pilot's measured cost (A12).
4. Open question raised by the smoke run E-20261125-152619-d917a14 [TO VERIFY at 4e6]: the one-patch
   field at N_f already carries the delta-N skewness (0.023 at 2e4), while the box's d phi skewness is about
   8e-4 (review run E-20261125-131002-ceefa2f). If confirmed, the review's reading that the non-Gaussianity
   of zeta comes from the shared map does not hold, and A4's direct comparison carries the G3 result.
5. Reservation carried: the slicing is geodesic only (A8); U-A4'(a) of G2 stays FAILED as written and is
   answered by G3-C.
6. Package items (C9-C17): schematic of the parameter space, result figures, working-note section, fresh
   verifier: after the runs.
