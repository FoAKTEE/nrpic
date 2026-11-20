# JOURNAL of verifier_g1 (fresh-context verifier of Track D's G1 material, item C17)

Helper of owner D-bh-dress, wave 3, 2026-11-20. I produced none of the material. Before
the verdicts are committed I read only what the task allows: SCOPE.md, DERIVATION.md,
scripts, inputs, manifests, raw outputs, package README files (layout only), the AthenaK
source, the knowledge base, and the note at the pinned commit 78d470ca. Each entry: the
prediction and what would make the claim WRONG, written before the run; the outcome after.

## Entry 1 (2026-11-20 14:15 PST): V1, ES-1 and V-1, prediction

Script `v1_es.py` (my own readers of `traj.bin`, `trajmet.bin` with the 17-double record of
`athenak/src/particles/nrpic_io.cpp:811-814` and 926, `part.*.bin` of :941-978,
`horizon_summary_0.txt` by its header; the format-2 table of
`coord/INTERFACES/spherical_id_format2.md`). Exact curves from the data set
D-20261115-170213-d2c2131 only through its table `es.tab`/`v1.tab` and particle files
`es.nrp`/`v1.nrp` (not through `es.json`, `es_reference.csv` or the track's scripts):
R0 = psi^2 rbar at the tracer's start, Misner-Sharp mass m = (R/2)(1 - (dR/dl)^2 + R^2 KT^2),
energy per unit mass Etilde^2 = 1 - 2m/R0 + R0^2 KT^2 (a particle at rest in the slice moves
with dR/dtau = -R KT), then the closed-form radial geodesic (cycloid for Etilde < 1,
R = (R0^(3/2) + (3/2) sqrt(2m) tau)^(2/3) for Etilde = 1). Areal radius of a tracer from the
evolved 3-metric at the particle: R = r sqrt((tr gamma - n.gamma.n)/2), r the coordinate
distance from the puncture at the origin (tangential eigenvalue of a spherically symmetric
metric in Cartesian coordinates).

Predictions (what I expect if the track is right):
- P1a wall tracers (tags 56-69), max_i max_{tau<=200} |R/R_w - 1|: 2.2e-3 (ES-1), 1.6e-3
  (V-1). WRONG if my value differs from the claim by more than 15 per cent (definition of
  the areal radius could move it a little), or if it exceeds 3e-3.
- P1b exact crossing times of R = 2M from my closed form: 14.8269 M (R0 = 6 M) and
  34.4423 M (R0 = 10 M) to 1e-4 M; run crossings (proper time of the tracer interpolated to
  R = 2M) 14.826 and 34.437 M within 2e-3 M and 1e-2 M of the claims. WRONG if my exact value
  differs from the claimed exact by more than 1e-3 M, or the run value by more than 1e-2 M.
- P1c horizon mass, max |M_AH(t)/M_AH(100 M) - 1|: 100-200 M: 3.40e-4 (ES-1), 1.37e-4 (V-1);
  100-165 M: 9.3e-5 and 4.2e-5. WRONG if mine differ by more than 20 per cent (e.g. a
  different reference sample), or if ES-1 over 100-165 M exceeds 2e-4.
- P1d no dust particle inside the wall: in every snapshot (t = 0, 25, ..., 200 M), the
  smallest coordinate radius of a dust particle (tag >= 140) exceeds the largest coordinate
  radius of the wall tracers in the nearest direction; the particles removed during the run
  are tracers only (tags < 140). WRONG if any dust particle lies inside, or any dust tag
  disappears.

### Outcome of entry 1 (14:25 PST), run D-20261120-222209-871e07f

All four predictions held (`v1_results.json`, figures `v1_wall.png`, `v1_inner.png`,
`v1_horizon.png`, `v1_dust_wall.png`, all looked at).
- P1a: wall, max over tau <= 200 M: ES-1 2.196e-3 (axis tracers; diagonal 1.734e-3),
  V-1 1.594e-3. The second areal-radius definition (det gamma / n.gamma.n)^(1/4) r gives the
  same digits. Attempt to break: over the whole run (tau up to 283 M in ES-1, 250 M in V-1)
  the error grows to 1.71e-2 (ES-1, diagonal, at the end) and 7.17e-3 (V-1); tau = 200 M is
  reached at t = 137.5 M. So the claim holds only on its stated window, and the window
  ends where the curves turn (figure `v1_wall.png`).
- P1b: exact crossing times from my closed form 14.82693 M and 34.44232 M (claims 14.8269,
  34.4423). Run, mean over 14 tracers: 14.82652 (cubic interpolation in R) or 14.82634
  (linear), 34.43683 or 34.43675; spread over the 14 tracers 1.6e-4 and 4e-4 M. The claimed
  14.8263 matches my linear value. R0 = 20 M group: 244.33 M against 244.74 (ES-1 only;
  V-1 ends first).
- P1c: horizon drift 3.400e-4 (ES-1) and 1.368e-4 (V-1) over 100-200 M; 9.35e-5 and
  4.21e-5 over 100-165 M; M_AH(100 M) - M = 9.55e-4 and 9.37e-4. Exact agreement with the
  claims. Attempt to break: with the mean over 95-105 M as reference the numbers become
  3.82e-4 and 1.32e-4 (100-200 M), 9.2e-5 and 3.7e-5 (100-165 M): the single-sample
  reference moves them by up to 12 per cent, not more.
- P1d: no dust tag disappears (696688 dust particles in all nine snapshots); the 42
  removed particles are tracers 0-41 (groups R0 = 6, 10, 20 M). A naive test (dust against
  the wall tracer of the nearest of 14 directions) fails at t >= 175 M (-0.061 M at 200 M)
  because the coordinate radius of the wall differs by 0.57 M between axis and diagonal at
  t = 200 M. With the wall interpolated between the 14 directions by the angular shape of
  the innermost dust layer itself (fit a + b(r0 - 36.4) + c q4 + d q6, residual <= 0.020 M,
  rms 0.007 M) the smallest margin is 0.1356 M at t = 200 M (lowest cubic harmonic alone:
  0.1359 M); within 6 degrees of the 14 wall tracers, model-free, 0.126 M. No dust inside.
