# What G1 of B-emd-gw still lacks

State 2026-11-15, end of wave 2 (lead). Items 1-6 are owed before the lead would ask for the
gate; 7-12 are open science items that G1 records.

## Owed by the gate

1. Criterion 1, oblique wave: the track's own run of k = (1, 1, 1) with both diagnostics
   (spec `periodic_z4c/inputs/lw_3d.athinput`) once core's sign fix is on main (or with the
   scouting executable `scratch/core/exe/core_requests-b/`, decision 0013); flip `xy`, `yz`
   in `periodic_z4c/analysis/refsol.py` tt_polarization at the same time (core's note).
2. Criterion 1, expanding box: a free TT wave in the matter-era box with both diagnostics
   against the 1/a reference of check 3A.
3. Schematics of G1 (brief 13.4): updated architecture (Newtonian mode now exists; gauge
   piece G_tot exists; jitter and thin boxes exist on a core branch) and a data-flow diagram
   (initial data -> AthenaK -> dumps -> gw_diag and fslib -> figures and ledger).
4. Working note: the first-source scan and the Newtonian-mode tests in Sec. IV and V of
   `note/main.tex` (run ids in `note/scripts/common.py`), recompiled with the checker.
5. Independent verifier of the wave-2 G1 runs (first_source, newton_tests): the lead's
   recheck (`stage/REVIEW-wave2.md`) is the owner's.
6. `nrpic-stage verify` for G1 passing its runs check (see G0 OPEN item 4).

## Science items recorded at G1

7. Convergence of the first source in particle number and at 128^3 (one loading and two
   meshes so far).
8. The jittered-lattice null (noise floor; risk R1).
9. Adopt `first_source/fslib/gauge.py` gauge_piece_total into gw_diag; report raw and
   corrected strain in every scan (first_source request 1, accepted).
10. N2 (embedded ellipsoid in a periodic box): needs core's per-species history.
11. A smaller amplitude (delta = 0.0025) to widen the second-order comparison window
    (verifier weakest point 1).
12. The Newtonian mode's force error (kh)^2/12: quoted with every GR-Newton comparison unless
    core adds a fourth-order option (request in the outbox).
