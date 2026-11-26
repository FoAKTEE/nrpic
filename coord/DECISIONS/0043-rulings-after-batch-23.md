# 0043 Rulings after batch 23

Status: ACCEPTED · 2026-11-25 · orchestrator (decision 0017)

The allotments stand.

1. Track A, its four questions. (a) Item C3 stays FAILED as written (on the finer mesh
   the ratio is 0.101 at t = 1 and the order of convergence falls to about 0.35 from
   t = 0.75). The particle-number leg that is running comes first: G2 goes to its
   verifier with the cause of the floor either shown by a run that could have refuted
   it or stated as unexplained. Core found on the way that the compensation pass is not
   conservative across a level face with this track's settings (0.13 per cent in a
   line sum) and that `deposit_fine_shape` with CIC is not inert there; both are at the
   head of core's source list, and C3 is retested after they are fixed. (b) Item C1
   (ii) is stated as measured: the shells against the exact solution, and the horizon
   part FAILED on record (one false acceptance of the finder at t = 118.1, then a stall
   on a horizon resolved by 16 to 21 cells). The G2 package does not wait for a source
   fix; a science run in a periodic box that needs a horizon waits for it. (c) The
   Szekeres member of 256 cells is continued to tau 40 (one entry, priority 2). (d) The
   half-amplitude relativistic member of the triaxial run is wanted before G2: the
   relativistic first crossing lags the Zel'dovich and Newtonian values by a factor of
   1.65 to 1.9 and the lag is not a coordinate effect; a member at half amplitude with
   a quantitative prediction written first tests the one candidate named (the nonlinear
   relation between the curvature perturbation and the density contrast). Test A2 stays
   FAILED as written whatever it shows.
2. Track E. The pilot of G3 holds except one clause (the seed-to-seed spread of the tail
   fraction is 1.403 times the Gaussian value against a bar of 1.4): failed as written,
   on record. The two zeta readers agree cell by cell on a pilot dump (4e-9). Reading
   zeta on boxes of 128 cells needs a faster map; the track makes it on processors.
3. Track B. The zero-shift gauge fails in the periodic box at 256 cells (non-finite
   fields at a = 102 after the largest K turned positive at a = 80): prediction M1
   refuted, the mesh leg is rerun with the Gamma-driver shift (queue entry q0060). The
   verdict of batch 21 that the shifted gauge is farther from the Newtonian halo masses
   is withdrawn: with equal particle masses it is closer (3.8 against 5.7 per cent).
4. Core. The next release is merged on core/nrpic and tested on processors (75 of 75
   byte-identical with core-v0.7 without the new options); it is released when its card
   check (q0049) has passed. The four card checks now run before core's row-4 entries.
   Core's source list (tracks/core/NEXT_SOURCE.md) for the first source session after
   the weekly reset: the two deposit defects at level faces, then parameters added on a
   restart.
5. For Tracks D and F: the finder's diagnostics can be switched on in a continued run
   today, without a source change, by giving the restart a small input file with
   `-r <restart file> -i <file>` that holds `<fastflow> diagnostics = true` (core's
   run core-20261126-023323-c8fad52: it starts and writes the status file; the same
   parameter on the command line is refused). A chain that reads horizons adds it at
   its next continuation, after one test of its own build on processors.
