# Journal of core, work package "oblate": the oblate spheroid and its collapse

Branch `core/oblate`, worktree `wt/core-oblate` (wave 3a, 2026-11-19). Units G = c = 1,
lengths and times in the ADM mass M of the data. Labels: [VERIFIED] read or measured
here (with locator or run id), [BACKGROUND] standard result not re-derived here,
[JUDGEMENT] inference or design, [TO VERIFY] open. Run ids `core-<date>-<time>-<commit7>`
(UTC); manifests in `tracks/core/runs/`, outputs in `scratch/core/<run_id>/` of the main
checkout. Times of entries are UTC from the `date` command.

## 2026-11-19 14:35Z, entry 1: what was read, the design, the predictions

Read: `CLAUDE.md`; `coord/CHARTER.md` to the end of "Owners"; decisions 0010, 0016,
0017; brief lines 493-553, 688-706, 834-860; `athenak/src/pgen/nrpic/nrpic_cf.cpp`,
`python/nrpic/spheroid.py`, `python/nrpic/sampling.py` (`sample_spheroid`),
`problems/ic/make_ic.py`, `problems/prolate/prolate_amr.athinput`; of branch
`core/nrpic`: `tracks/core/verify/README.md`, `LADDER.md` (row 3),
`oblate/oblate_reference.py`; `docs/TESTLOG.md` 1527-1616 (prolate collapse).

### What the two papers of row 3 say about oblate collapse [VERIFIED by reading the sources]

Sources fetched with `nrpic-fetch-arxiv`: `kb-data/raw/arxiv/1611.07906/v2/src/asymflat.tex`
(Yoo, Harada, Okawa) and `kb-data/raw/arxiv/1901.04498/v2/src/main.tex` (East).

- Neither paper evolves an oblate configuration. In `asymflat.tex` the word "oblate"
  does not occur (grep); the data are "randomly distributed inside a prolate spheroid"
  (line 1009), and the potential is given "For a prolate (a < b) spheroid" only (lines
  496-503). In `main.tex` of 1901.04498 "oblate" occurs once, for the shape of the
  horizon during ring-down ("damped oscillations between being prolate and oblate",
  lines 258-259); the family is "a prolate spheroidal distribution" (lines 183-188),
  "we focus on very prolate cases" (line 194), e = 0.9 with 2 <= b/M <= 20 and one case
  e = 0.95 (lines 195-199). So row 3 of the ladder (brief line 842) names two references
  for "Oblate and prolate collapse" that contain the prolate half only. There is no
  published number for the oblate collapse in these two sources; the comparison below
  is in kind.
- The construction that carries over (1611.07906, `asymflat.tex` 445-550): conformally
  flat, momentarily static; reference density (1/2) Ebar Psibar^5 = E_N = 3 M_N/(4 pi
  a^2 b) inside the spheroid (lines 473-483), Psibar = 1 - Phi, Laplacian Phi = 4 pi E_N
  (487-495), total mass M = 2 M_N (526-533), particle number per volume proportional to
  2 E_N Psibar (539-544), rest mass M_0 = 2 M_N + (6/5)(M_N^2/(b e)) ln((1+e)/(1-e)) for
  the prolate spheroid (547-549). Note: Yoo et al. then solve the Hamiltonian constraint
  numerically for the sampled particles (lines 454-463, 551-552); the code here, as for
  the prolate case, keeps the continuum Psibar (paper of the method, `main.tex` 961-967).
- What they report for the prolate case, to compare in kind: a caustic in the matter
  before any horizon, with a curvature maximum that grows with resolution (1611.07906
  abstract lines 101-106; 1901.04498 lines 337-344); the calculation continues past the
  caustic and "a short time later an apparent horizon is found which envelops all the
  matter" (1901.04498 lines 363-368); "the final state in all cases studied is a black
  hole plus gravitational radiation" (abstract, lines 97-98), "All the matter ends up in
  the black hole" (279-280), "M - E_GW matches the measured mass of the black hole at
  late times to better than 0.2 %" (294-295), E_GW about 0.015 M at most for e = 0.9
  (292); horizon found "at around t/M = 30" for b/M = 10, e = 0.9 (caption, 353). In
  1611.07906 a horizon appears only for the more compact case b/M = 13/4 (lines 862-866,
  at t = 10.2 M, 915), not for b/M = 10 (603-606).

### Design [JUDGEMENT]

- Potential. For a > b the integrals I, J_a, J_b of the homogeneous spheroid are those
  of the prolate case with atanh -> atan and c^2 -> -c^2 (c the focal distance; for the
  oblate spheroid the radius of the focal ring): with w = sqrt(b^2 + lam), q = c/w,
  I = (2/c) atan q, J_a = atan(q)/c^3 - w/(c^2 (w^2 + c^2)), J_b = (2/c^2)(1/w -
  atan(q)/c). This is the closed form of `verify/oblate/oblate_reference.py` (core/nrpic),
  which that package checked against quadrature to 4e-12 (run
  core-20261115-154359-d74357f). For q < 0.3 the differences cancel; the three functions
  are then summed as series in -q^2 (the prolate series of `spheroid.py` with the sign
  of q^2 changed), which also gives the sphere a = b.
- Source: one new function `CFOblateExcess` in `nrpic_cf.cpp`, a new component type
  `kCFOblate` chosen by the parser when `compN_a >= compN_b`, one `else if` in
  `CFExcess`. The prolate branch is not touched (same statements, same order), so
  existing inputs must give the same bytes; an input with a >= b was a fatal error
  before, so no existing run changes meaning.
- Sampler: class `OblateSpheroid(e, a, M)` in `python/nrpic/spheroid.py`, a subclass of
  `ProlateSpheroid` that replaces the constructor and the potential; the density, the
  closed-form mass integrals and `sampling.sample_spheroid` hold for any a, b (psibar is
  quadratic inside). `make_ic.py oblate --e --a`. New closed form for the rest mass, from
  the potential energy of the homogeneous spheroid [BACKGROUND]: M_rest = M + (3 M^2/(5 a
  e)) asin e (prolate: M + (3 M^2/(10 b e)) ln((1+e)/(1-e)), which is line 549 of
  `asymflat.tex` with M_N = M/2).
- Case of the collapse: e = 0.9 and a = 10 M, the prolate case of the ladder with the
  axes exchanged: b = 4.3589 M, rho_N = 2.738e-4, psibar_c = 1.0933, M_rest = 1.074651
  (`make_ic.py oblate`, this entry; the prolate case has psibar_c = 1.1227, M_rest =
  1.098148).

### Semi-analytic reference for the collapse: Newtonian homogeneous spheroid

`tracks/core/analysis/oblate/newton_spheroid.py` [BACKGROUND: a cold homogeneous
spheroid stays a homogeneous spheroid, linear force law]: d^2a/dt^2 = -(3M/2) J_a a,
d^2b/dt^2 = -(3M/2) J_b b. For collisionless matter the solution continues through b = 0
with b -> -b (every particle crosses the equatorial plane at the same instant, and the
mirror image is again a homogeneous spheroid). Numbers for M = 1 and the coordinate
semi-axes (scratch run of the script, figure `figs/newton_spheroid.png`; registered
below as part of T3's reference):

| event | Newtonian time |
|---|---|
| oblate: pancake (b = 0); then a = 6.21 M, da/dt = -0.48, db/dt = -0.56 | 20.46 M |
| oblate: a = 5, 3, 2, 1 M (|b| = 1.05, 1.70, 1.67, 1.43 M after the bounce through the plane) | 22.68, 25.38, 26.40, 27.20 M |
| oblate: a -> 0 | 27.71 M |
| prolate (calibration): a -> 0, the spindle; b = 6.82 M then | 14.61 M |

Calibration of the relativistic stretch on the prolate case: the paper of the method
gives "onset of strong axial focusing at t = 20.5 M" and the "narrow axial spindle at
t = 27.75 M" (`refs/arxiv_2611.12831/src/main.tex` line 971), our run `e09_v8` has the
largest curvature at 27.75 M and the first horizon at 32.0 M (`docs/TESTLOG.md`
1531-1537). Against the Newtonian 14.61 M these are factors 1.40 (ends of the spindle)
and 1.90 (centre). The cube of the conformal factor (proper lengths psi^2, t ~ L^(3/2);
exact for the proper time of a dust ball with psi at its surface [BACKGROUND]) is 1.42
at the centre and 1.20 at the pole of the prolate spheroid: the code's coordinate time
is stretched beyond psi^3 by the 1+log lapse, more where the matter is deeper. The
oblate spheroid is less compact: psi^3 = 1.31 (centre), 1.24 (mean), 1.18 (equator).

### Predictions, written before any run (14:35Z)

T1, conformal factor on processors (`analysis/oblate/cf_check.py`,
`problems/tests/oblate_cf.athinput`, no particles, no step):

- P1a. psi^4 of the `adm` dump (single precision) equals (1 - Phi_N)^4 of the reference
  at every cell, to the rounding of the dump: largest |difference| <= half a float32
  unit in the last place (+1e-12), for three shapes: e = 0.9, a = 10 M (mesh half-width
  48 M, so that inside, near field and the series region q < 0.3 are all sampled);
  e = 0.3, a = 2 M (series reached right outside the surface); the sphere a = b = 3 M
  (closed form (M/2)(3 - r^2/a^2)/(2a) inside, M/(2r) outside). Reference: the function
  `phi_N` of `verify/oblate/oblate_reference.py` read from branch `core/nrpic` (not my
  code) for e > 0, and independently the defining integrals by adaptive quadrature at
  200 points; my Python twin `OblateSpheroid.psibar` must agree with both to 1e-11
  relative. Refuted by: any cell beyond the rounding bound (a formula error of the
  component shows at 1e-3 or more), or a twin off by more than 1e-11.
- P1b. Without matter the Hamiltonian monitor is the Ricci scalar, which for
  psi = 1 - Phi_N is 32 pi rho_N psi^-5 inside the spheroid and zero outside. Away from
  the surface (more than four cells; the second derivative of psi jumps there and the
  seven-point stencils reach three cells) the monitor of the `con` dump agrees with
  that to better than 1e-5 of the inside value (sixth-order differences on a field that
  is quadratic inside and harmonic outside; float32 dump), on a mesh of half-width 16 M
  with dx = M/4. The prolate component (existing code) gives the same picture on the
  same mesh. Refuted by: a relative difference above 1e-4 inside, or |H| above 1e-4 of
  the inside value outside.
- P1c (restated 14:37Z, before any run of T1: the first wording asked for a core mean of
  H within 0.03, which is 1.5 standard deviations of the count noise of a sample with
  four-fold symmetry, 2 per cent; the sharp statements are the integrals). With the 10^4
  sampled particles (`make_ic.py oblate`, seed 1; `problems/tests/oblate_id.athinput`,
  static mesh with dx = M/4 over the spheroid, four filter passes with compensation):
  (i) particle level, no code: S = sum m_p/psibar(x_p) = M within 1e-3 (the continuum
  identity int 2 rho_N d^3x = M sampled with density 2 rho_N psibar; expected scatter
  2e-4, psibar varies by 2 per cent over the spheroid); (ii) code: the mesh integral of
  E psi^5 equals S within 1e-3, the integral of E psi^6 equals sum m to 1e-6 (deposition
  conserves it; single-precision dump), and the integral of H psi^5/(16 pi) over the
  mesh is zero within 2e-3 M (R psi^5 = -8 Laplacian psi integrates to 16 pi M up to
  the outer faces, where psi - 1 = M/2r is cut at r = 32 M: the missing flux is known,
  see the outcome); (iii) reported, not sharp: the mean of H over the core s < 0.8 is
  within 0.06 of 16 pi <E> (three standard deviations), and the rms of H there, relative
  to 16 pi <E> and multiplied by the square root of the particles per cell, is the same
  for the two shapes within a factor 1.5 (the oblate spheroid has 2.29 times the
  volume). Prolate control (existing code) on the mirrored mesh. Refuted by: S or the
  integral of E psi^5 off by more than 1e-3, or a core mean beyond 0.08 for the oblate
  data while the prolate data stay inside 0.06 (a mismatch of particle masses and psi).

T2, regression on processors against the release executable
`.work/build_cpu_v03/src/athena` (the release was built from main after core-v0.3):

- P2. Every output file of `problems/tests/regress_cf.athinput` (table, Gaussian,
  prolate spheroid, puncture; two steps) and of `problems/tests/cf_table_regress.athinput`
  (table with 10^4 lattice particles, twelve steps) is byte-identical between the
  release executable and the executable of this branch (36 never-set bytes of restart
  headers left out, as in `analysis/id/regress_format1.py`), and so is a prolate start
  (`prolate_amr.athinput` with num_levels = 5, 16 steps, 10^4 particles). `make_ic.py`
  prolate, os, st: files identical to those of the main checkout (already seen for four
  cases while writing the model: `diff -r` empty, prolate particle file sha256
  dcc80b8d..., the file of run `e09_v8`). Refuted by: any differing byte.

T3, collapse on a card: `problems/oblate/oblate_amr.athinput` (the prolate input with
the axes exchanged), 10^4 particles (seed 1, symmetrized), four filter passes with
compensation, finest cells M/4 (num_levels = 5) and M/8 (num_levels = 6), to t = 55 M.
Budget rule fixed now: both runs in one Slurm job; a third run at M/16 only if the M/8
run shows that it fits in what is left of the card-hour with a 20 per cent margin
(memory: the prolate M/16 run peaked at 62 GB with 1352 blocks, `runs/prolate/e09_v8`
log footer).

- P3a, the pancake forms. The rms height z_rms of the particles falls to a minimum below
  0.25 of its initial value while the rms cylindrical radius is still above 0.5 of its
  initial value (Newtonian: 0 and 0.62), at t_p between 24.5 and 30.5 M (Newtonian 20.46
  M times 1.2 to 1.5; the lower factor is psi^3 of the mean, the upper one the prolate
  calibration of the ends scaled down for the weaker field). The largest energy density
  and the constraint norm peak near t_p. The flattening is not perfect: the centre lags
  the rim (deeper potential, smaller lapse), so the crossing is spread over a few M
  [JUDGEMENT]. Refuted by: t_p outside 23 to 32 M, or a minimum of z_rms above 0.4 of
  the initial value.
- P3b, the run passes the caustic. After t_p the fraction of particles on the other
  side of the equatorial plane from where they started rises above 0.9 (Newtonian: all
  at once), z_rms grows again to between 0.2 and 0.5 of its initial value (Newtonian
  |b| reaches 1.7 M, 0.39 of b_0) while R_rms keeps falling; the pusher converges
  (history column push_unconverged zero), no particle escapes, the run does not stop.
  The two resolutions give t_p within 0.5 M of each other (the caustic is a sheet of
  finite surface density, 4 pi Sigma a of order one but no divergence of the potential,
  unlike the spindle). Refuted by: a stop or non-finite fields at the caustic, fewer than
  0.9 of the particles crossing, or t_p differing by more than 1 M between resolutions.
- P3c, a horizon is found, later than the pancake: first apparent horizon at t_AH
  between t_p + 5 M and t_p + 13 M (Newtonian a = 2 M comes 5.9 M after the pancake;
  stretch 1.2 to 1.9 in the strong-field phase), so between 31 and 43 M, at both
  resolutions (M/4 within 1.5 M of M/8; the prolate pair M/8, M/16 differs by 0.25 M).
  No horizon at the pancake itself. Refuted by: no horizon by 55 M, or a horizon before
  t_p + 3 M.
- P3d, horizon mass against the mass of the data (M_ADM = 1). The largest irreducible
  mass at M/8 is 0.955 +- 0.025 (the prolate run at M/8 has 0.957, at M/16 0.967,
  `verify/README.md` on core/nrpic; the true end state should be M minus the radiated
  energy, which for the prolate case is 0.01 to 0.015 M, 1901.04498 line 292, and is
  probably smaller for the oblate one [JUDGEMENT]). At M/4 the deficit is larger than at
  M/8 (first-order error of the horizon reading on a coarser mesh): 0.90 to 0.96. All
  particles end inside: at least 0.95 of the rest mass 1.0747 removed by the lapse
  excision by the end, none escaped. Refuted by: a horizon mass above 1.00 or below
  0.90 at M/8, or M/4 closer to 1 than M/8 by more than 0.005.

## 2026-11-19 14:50Z, entry 2: T1 run, T2 started, the card job is in the queue

Source change (commit 1d19e13): `nrpic_cf.cpp` +70 lines (function `CFOblateExcess`,
type `kCFOblate`, the `else if` in `CFExcess`, the parser accepts `compN_a >= compN_b`);
`python/nrpic/spheroid.py` (`_IJ_oblate`, `OblateSpheroid`); `problems/ic/make_ic.py`
(model `oblate`, option `--a`). Builds in `.work/build_cpu`, `.work/build_gpu` of this
worktree; the changed file was recompiled after the last edit (touch, 14:36Z).

### T1, run core-20261119-143758-09c669d (processors, 31 s of AthenaK in all)

(The first attempt, core-20261119-143744-e7e1c6e, failed on a relative path of the
executable before any case ran; it stays on record.)
Figures: `analysis/oblate/figs/cf_check_psi.png`, `cf_check_ham.png`,
`cf_check_id.png` (all three looked at).

P1a HOLDS. psi^4 of the single-precision dump against the reference at every cell:

| shape | cells (inside / closed form outside / series) | largest difference in float32 units | cells beyond the rounding bound | twin against reference, against quadrature (relative, in u) |
|---|---|---|---|---|
| e = 0.9, a = 10 M, half-width 48 M | 884736 (1824 / 121400 / 761512) | 0.49997 | 0 | 3.6e-14, 4.8e-14 |
| e = 0.3, a = 2 M, half-width 8 M | 262144 (2040 / 304 / 259800) | 0.49997 | 0 | 8.9e-14, 3.1e-14 |
| sphere a = b = 3 M | 262144 (7208 / 0 / all series) | 0.49975 | 0 | 5.6e-15 (closed form of the sphere) |

The reference is `phi_N` of `verify/oblate/oblate_reference.py` at blob
(`cf_check.json`, key reference) of branch core/nrpic for the two spheroids. Every cell
of the dump is the correctly rounded reference value, so the component is right to the
resolution of the dump, 6e-8 in psi^4, 1.5e-8 in psi; the double-precision statement
(1e-13) holds for the Python twin, which has the same formulas. Limit of the test: the
C++ arithmetic itself is seen only through single precision; a term of the series
smaller than 1e-7 of u would not show (terms beyond the fifth at q = 0.3). They are
generated by one loop from the coefficient formulas, so a wrong high term without a
wrong low one is not possible in this code [JUDGEMENT].

P1b HOLDS. Monitor without matter against 32 pi rho_N psi^-5 (dx = M/4, half-width
16 M): inside, largest relative difference 5.2e-8 (oblate, 67576 cells) and 5.2e-8
(prolate control, 24328 cells), which is the rounding of the dump; outside, largest |H|
7.3e-7 (oblate) and 1.8e-6 (prolate) of the central value. In the three cells on either
side of the surface the monitor differs by order one, as it must (figure): the second
derivative of psi jumps there. The mesh integral of H psi^5/(16 pi), which is the mass
by Gauss's theorem, is 0.9999995 (oblate) and 0.9999986 (prolate), surface layer
included (0.42 and 0.52 of the integral come from the layer cells): looked at after
the run, to understand (ii) below.

P1c: (i) HOLDS, (ii) HOLDS in one part and FAILS in two as worded, (iii) HOLDS.

| quantity | oblate | prolate control |
|---|---|---|
| sum m (continuum M_rest) | 1.074651301 (1.074651301) | 1.098147966 (1.098147966) |
| (i) sum m/psibar(x_p) - M | +8.9e-5 | -6.9e-6 |
| (ii) mesh integral of E psi^5 minus (i)'s sum | +1.6e-7 | -1.0e-5 |
| (ii) mesh integral of E psi^6 minus sum m | -2.1e-5 | -6.3e-5 |
| (ii) mesh integral of H psi^5/(16 pi) | +0.0251 | +0.0307 |
| ... of which on the finest level (holds all the matter) | -9.0e-5 | +1.5e-5 |
| (iii) core mean of H / (16 pi <E>), s < 0.8 | -0.0041 | -0.0038 |
| (iii) core rms of H / (16 pi <E>); times sqrt(particles per cell) | 0.557; 0.163 | 0.348; 0.154 |

- The integral of E psi^6 is not conserved to 1e-6: the field of the `tmunu` dump is
  the filtered source (four passes and compensation), and its integral is 2.1e-5 and
  6.3e-5 below sum m. The prolate number is the one the release run shows at t = 0:
  `runs/prolate/e09_v8/prol.nrpic.hst`, first record, int_E_filtered - sum_mW =
  1.098085068 - 1.098147966 = -6.29e-5 [VERIFIED]. So this belongs to the filter of the
  release (the unfiltered deposit, column int_E, equals sum_mW to the last digit), not
  to this change. My prediction took the dumped field for the unfiltered one: wrong.
- The integral of H psi^5 over the whole mesh is 0.025 M, not zero within 2e-3. Where
  it sits (looked at after the run, with the files of this run): none of it on the
  finest level (there the integral of R psi^5/(16 pi) is 0.9999992 and the result is
  M - S, -9.0e-5, as predicted); all of it on the two coarser levels, which hold no
  matter, and there in the outermost three cells along the outer faces of the domain
  (level 0: +0.0181, -0.0019, +0.0002 in the first, second, third cell layer, nothing
  beyond; largest |H| 2.3e-4). In the run without particles (P1b) the same cells have
  |H| < 2e-9 of the central value. The two runs differ in who evaluates the monitor at
  t = 0: the generator, on ghost cells it filled analytically, or the particle module
  after the boundary conditions were applied; with the outflow copy in the ghost cells
  the second derivatives in the outer three cells are wrong. This is the face effect
  that READY of core/id-solver already describes ("the largest |H| of solved data sits
  in the outermost cells"); it is the same for the prolate control (0.0307) and has
  nothing to do with the spheroid. Named as the cause on the strength of the location
  only (three cell layers = reach of the seven-point stencil); no run was made in which
  it could have failed. The script now reports the integral without the outer four
  cell layers (rerun below).
- Reading of T1 as a whole: the oblate component is the reference potential; its
  curvature is that of the density 2 rho_N psi^-5 inside and zero outside; the sampled
  particles carry that density (mass sum to 9e-5 of M, core mean of the monitor 0.4 per
  cent of the source, noise as for the prolate data).

### T2, first attempt core-20261119-144337-5c02abf (stopped by me)

`regress_cf`: IDENTICAL, 16 files (release executable against this branch; the case
has the prolate spheroid, the table, the Gaussian and the puncture). I then stopped the
run: on the machine as loaded today (load 125) a step of 64^3 cells takes 28 s and a
step of the table case with particles 100 s, so the prolate start (2.1e6 cells, 16
steps) would have taken hours. Second attempt with 3 and 2 steps for the two cases with
particles, the two executables side by side: below.

### T3: the card job

Initial data: run core-20261119-144859-fbf3438 (`analysis/oblate/make_runs.py`;
particle file sha256 6dae810c...). Card job: run core-20261119-144923-1a7c274, Slurm
job 4647, submitted 14:49Z: `cf_card` (the conformal factor on the card, no step),
`oblate_m4`, `oblate_m8` (wall limits 10 and 32 min, Slurm limit 45 min). The queue
held fifteen jobs of other sessions and users at that time, the last with an estimated
start 8.5 hours later; nothing of T3 can be run on processors (a step of the M/4 mesh
would take about four minutes there). Not waiting: the rest of the package first.
Registration note: `nrpic-run submit` refused local runs for some minutes ("16 cores
busy in live local runs of core": the allotment is per owner, and about ten core
packages run at once); I retried instead of registering by hand.

## 2026-11-19 14:56Z, entry 3: expectation for T3 revised before the card job has run

State: Slurm job 4647 pending (squeue at 14:55Z: PD, estimated start 16:17 local time,
nine hours away); no oblate evolution exists yet. While testing
`analysis/oblate/collapse_analysis.py` on the two existing prolate runs
(`runs/prolate/e09_v8`, finest cells M/16, and
`scratch/core/core-20261115-152845-5728b1d/prolate_m8`, M/8; option `--basename prol`,
figures into scratch, not kept) I looked at the particle moments of those runs for the
first time, and they contradict the calibration I used for P3a:

| R_rms / initial (prolate runs, both resolutions the same) | 0.75 | 0.5 | 0.25 | 0.1 |
|---|---|---|---|---|
| time in the code | 12.5 M | 17.5 M | 21.5 M | 24.0 M |
| Newtonian a/a_0 of the prolate spheroid | 8.36 M | 11.40 M | 13.38 M | 14.24 M |
| ratio | 1.50 | 1.54 | 1.61 | 1.69 |

(read from the snapshots with a few lines of Python, not a registered run; the numbers
serve only this expectation). The bulk of the prolate spheroid contracts 1.5 to 1.7
times more slowly in coordinate time than the Newtonian spheroid, not 1.2 to 1.4: the
"onset of strong axial focusing at 20.5 M" of the paper, which I took as the spindle
time of the ends, is not the time at which the bulk reaches the axis. A formula that
gives these factors [JUDGEMENT]: psi^3/alpha with the lapse the 1+log slicing relaxes
to, (2 - psi)/psi: 1.61 with the mean psi of the prolate spheroid, 1.81 with the
central one. For the oblate spheroid the same formula gives 1.44 (mean) and 1.58
(centre), 0.89 of the prolate values.

Revised expectation (the predictions of entry 1 stay on record and are judged as
written; this is what I now expect and why):

- P3a': z_rms/initial passes 0.75, 0.5, 0.25, 0.1 at about 15, 21, 26, 30 M (Newtonian
  11.1, 15.3, 18.2, 19.7 M times 0.89 of the prolate ratios), and the pancake is at
  t_p = 31.5 +- 1.5 M. The band of P3a (24.5 to 30.5 M, refuted outside 23 to 32 M) is
  then likely to fail at its upper edge. Refuted (P3a') by t_p outside 29 to 34 M.
- P3c': the first horizon at t_p + 10 to 13 M (Newtonian 5.9 M after the pancake,
  stretched by 1.7 to 2.2 once the lapse has fallen), about 41 to 45 M. P3c as written
  (t_p + 5 to 13 M) covers it. The runs end at 55 M, which leaves at least 9 M after
  the horizon for the mass to settle and the particles to be removed.
- P3b and P3d unchanged.

## 2026-11-19 15:17Z, entry 4: T2 holds; a fourth part of T1 predicted

### T2, second attempt core-20261119-144947-fb1ccae (processors, 18 min)

P2 HOLDS, with fewer steps than I had written for two of the cases: release executable
`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` against `.work/build_cpu` of this
branch (sha256 43d9d9bf...), every output file compared byte by byte
(`analysis/id/regress_format1.py`):

| case | steps | files | result |
|---|---|---|---|
| `regress_cf` (table, Gaussian, prolate spheroid, puncture; all fields, restart) | 2 | 16 | IDENTICAL (also in the first attempt) |
| `cf_table_regress` (table, 10^4 lattice particles, one refined level) | 3 (written: 12) | 8 | IDENTICAL |
| prolate start (`prolate_amr.athinput`, options of the ladder runs, finest cells M/4, 10^4 particles) | 2 (written: 16) | 16 | IDENTICAL |

The step counts were cut because of the machine (entry 2). The change touches the
problem generator only, so the state at t = 0 is where a difference would arise; it is
identical in all three, and so are the first steps.
`python/tests/test_oblate_spheroid.py`: 5 of 5 pass; `python/tests/test_initial_data.py`
(the existing 29 tests, prolate sampler among them): 29 of 29 pass with this branch.

### T1, part d: prediction (15:17Z, before the run)

The interface text lists "an oblate component off the origin or together with other
components" as not tested. Test: `problems/tests/oblate_super.athinput`, an oblate
spheroid (M = 0.8, a = 6 M, b = 2.5 M, e = 0.909) centred at (3, -2, 1.5) M, a Gaussian
(m = 0.3, sigma = 1.5 M) at (-6, 4, 2) M and a puncture (m = 0.4) at (-5.1, -7.3, -6.2)
M, mesh of half-width 16 M with 64^3 cells.

- P1d. psi^4 of the dump equals (1 + u_oblate(x - x_0) + u_Gaussian + u_puncture)^4 at
  every cell within half a float32 unit (+1e-12), u_oblate from `oblate_reference.py`
  of core/nrpic at the shifted coordinates, the other two from their closed forms
  (`nrpic_cf.cpp` header). Refuted by any cell beyond the bound: the Gaussian and the
  puncture are existing code (`regress_cf` covers them), so a failure would be the
  centre or the superposition of the oblate component.

The rerun of T1 (parts a to c with the integral without the outer-face cells) and part d
are one registered run, as soon as `nrpic-run` has room (it has refused for five
minutes: sixteen cores of owner core busy).

## 2026-11-19 15:21Z, entry 5: executables published; the card part of T1 predicted

Published at 15:18Z: `/data/haiyangw/nrpic/scratch/core/exe/core_oblate/` with
`athena_cpu` (sha256 43d9d9bf...), `athena_gpu` (8b5f7275..., the same bytes as the copy
the card job 4647 will run), COMMIT (source: tree `athenak/` of 1d19e13), SHA256SUMS,
READY. READY says in STATUS that the processor executable is tested (T1, T2) and that
the card executable is built and not yet run on a card.

T1, part e (`analysis/oblate/card_cf.py`, run `cf_card` of the card job): prediction,
written while the job is pending.

- P1e. The psi^4 dump of the card run equals the reference at every cell within half a
  float32 unit (+1e-12), as on the processor, and the monitor without matter has the
  same largest value relative to 32 pi rho_N (1.18: the surface cells). Against the
  processor dump of the same input (P1a, e09) at most three of the 884736 cells differ
  (the card may round atan, sqrt or a fused multiply-add differently in the last bit of
  the double; that changes the float32 value only within 1e-16 of a rounding boundary).
  Refuted by: any cell beyond the rounding bound against the reference, or more than a
  handful of cells differing from the processor dump.

## 2026-11-19 15:35Z, entry 6: T1 rerun and part d hold; the card job still waits

### T1 a-d, run core-20261119-152206-4d292b9 (processors, 288 s, branch executable)

Figures looked at (15:31Z): `analysis/oblate/figs/cf_check_super.png` (new),
`cf_check_ham.png`, `cf_check_id.png` (redrawn from this run; same picture as in
entry 2), `cf_check_psi.png` (bytes of the PNG unchanged).

- P1a HOLDS again, same numbers as entry 2 (the code did not change): largest
  differences 0.49997, 0.49997, 0.49975 float32 units for e = 0.9, 0.3 and the sphere,
  no cell beyond the bound (`cf_check.json` of the run, key P1a).
- P1b HOLDS again: inside 5.2e-8 relative (oblate and prolate), outside 7.3e-7 and
  1.8e-6 of the central value; in the cells along the outer faces of the run without
  matter |H| < 2.5e-9 of the central value (new column `max_abs_H_edge_over_H_centre`).
- P1c, the integral of H psi^5/(16 pi) without the four outermost cell layers of the
  domain: -9.0e-5 (oblate) and +1.4e-5 (prolate), which is M - sum m/psi(x_p) within
  1.5e-7 and 2.1e-5; the integral of R psi^5/(16 pi) over the same cells is 0.9999987
  and 0.9999966. So the 0.025 M of entry 2 sits entirely in the outer four cell layers
  (0.02518 of 0.02509 there; largest |H| 2.6e-4), as located in entry 2. Restated part
  of (ii), judged now: "the integral of H psi^5/(16 pi) over the mesh without the outer
  face cells equals M - S within 2e-3": HOLDS (1.5e-7). This was formulated after the
  location was known; it is a check of the bookkeeping, not an independent prediction.
- P1d HOLDS. The oblate component at (3, -2, 1.5) M with M = 0.8, a = 6 M, b = 2.5 M,
  superposed with a Gaussian (m = 0.3 at (-6, 4, 2) M) and a puncture (m = 0.4): psi^4
  of the dump equals (1 + u_oblate + u_Gaussian + u_puncture)^4 at all 262144 cells
  within 0.49999 float32 units (3016 cells inside the spheroid; psi up to 2.25 near the
  puncture), u_oblate from `oblate_reference.py` of core/nrpic at the shifted
  coordinates; twin against reference 1.3e-14. The histogram of the differences is flat
  between -0.5 and +0.5 units (figure): correct rounding, no bias. So the offset and the
  superposition of the new component work as for the other components.

### Card job

Slurm job 4647 (run core-20261119-144923-1a7c274) still pending at 15:32Z, reason
Priority, estimated start 16:17 local time (00:17Z on 2026-11-20): fifteen jobs ahead of
it on two cards. Measured cost of the processor alternative (T2 run, prolate start at
M/4, 512 MeshBlocks): 6.5e3 zone-cycles per second on one core of the Serial build. The
prolate M/8 card run took 1.24e6 MeshBlock-cycles to 45 M (`athena.log` of
`scratch/core/core-20261115-152845-5728b1d/prolate_m8`); a quarter of that at M/4 would
be about 50 hours on one processor. T3 stays on the card.

## 2026-11-19 15:40Z, entry 7: T4, the Newtonian reference in AthenaK, predicted

Purpose: separate in T3 what is gravity from what is the particle set and the deposit.
The same 10^4 particles (run core-20261119-144859-fbf3438, sha256 6dae810c...) move in
the Newtonian potential of their own rest mass, AthenaK's Newtonian mode of release
core-v0.3 (`pusher = newton`, multigrid with multipole faces; interface text
`coord/INTERFACES/newtonian_mode.md`), with the cloud and filter of the card runs (CIC,
four binomial passes, compensation). Input `problems/oblate/oblate_newton.athinput`:
box of half-width 16 M, 64^3 (cells M/2) and 128^3 (cells M/4), step 0.02 M, to
t = 24 M, snapshots every 0.25 M. Processors, release executable
`.work/build_cpu_v03/src/athena`. Analysis `analysis/oblate/newton_mode.py`.

Reference [BACKGROUND, homogeneous spheroid, `newton_spheroid.py`]: with the total rest
mass M_0 = 1.074651 as the Newtonian mass every time scales by M_0^(-1/2) = 0.96465:
pancake at t_N = 19.738 M, a = 6.213 M there (R_rms/R_rms,0 = 0.621), polar speed
0.583; a = 5 M at 21.88 M; a = 3 M at 24.49 M (after the end of the run).

The sample is not homogeneous: number density proportional to psibar, 3.4 per cent
higher at the centre than at the rim, 1.7 per cent higher than at the pole
(`ic/*.json`, psibar coefficients). Columns of different R then reach the plane at
different times; for a time spread of 1.5 per cent of t_N (half the density contrast)
and the polar speed 0.58, the crossing is spread over 0.3 M in time and 0.17 M in
height [JUDGEMENT].

- P4a. The pancake: the minimum of z_rms over the snapshots is at t_p = 19.74 +- 0.3 M
  at both resolutions, and z_rms there is below 0.12 of its initial value (finite N,
  the density contrast above, the cloud of one to two cells). Refuted by: t_p outside
  19.2 to 20.3 M, or a minimum above 0.2.
- P4b. R_rms(t_p)/R_rms(0) = 0.62 +- 0.02.
- P4c. At t_p + 1 M at least 0.95 of the particles are on the other side of the plane
  from where they started; afterwards z_rms grows again (Newtonian |b| at t = 24 M:
  1.6 M, 0.37 of b_0) while R_rms keeps falling.
- P4d. Energy (columns 5 + 6 of `obl.newton.hst`, the particle sum of W) changes by
  less than 5e-3 of |W(0)| up to t_p - 1 M at 64^3 and by less than that at 128^3;
  across the caustic the force in the sheet is not resolved, the change there is
  reported, not predicted. The two resolutions give t_p within 0.25 M (one snapshot).
- Use for T3: the ratio t_p(GR, card)/t_p(T4) is the relativistic stretch of the
  pancake time with the particle set and deposit held fixed (entry 3 expects about
  31.5/19.7 = 1.6 against T4; the factor 1.44 to 1.58 of entry 3 was against the
  Newtonian clock with M = 1, 20.46 M).

## 2026-11-19 16:16Z, entry 8: T4 at cells M/2 holds; the crossing is wider than I wrote

Run core-20261119-153609-754c44d (processors, release executable, 64^3 and 128^3 side
by side; the 64^3 run ended at 16:07Z after 1834 s, the 128^3 run is at t = 4 M and
needs about three more hours). Analysis core-20261119-161400-72ec4a0 (the first
analysis core-20261119-161116-cb95558 has the same numbers without the crossing
diagnostics). Figures looked at: `analysis/oblate/figs/oblate_newton.png`,
`oblate_newton_particles.png`.

| quantity (64^3, cells M/2) | prediction | measured | verdict |
|---|---|---|---|
| t_p, smallest z_rms over the snapshots (every 0.25 M) | 19.74 +- 0.3 M | 20.00 M (from the second moment of the history, every 0.1 M: 19.90 M) | P4a holds, near the upper edge |
| z_rms at t_p / initial | < 0.12 (refuted above 0.2) | 0.059 | P4a holds |
| R_rms at t_p / initial | 0.62 +- 0.02 | 0.613 | P4b holds |
| across the plane at t_p + 1 M | >= 0.95 | 0.966 | P4c holds |
| z_rms, R_rms at 24 M / initial | z grows again to about 0.37, R keeps falling | 0.367, 0.364 (homogeneous: 0.37, 0.38 from the figure) | P4c holds |
| energy change before t_p - 1 M | < 5e-3 of W(0) | 4.0e-4 | P4d holds |
| energy change to t_p + 2 M | reported | 1.7e-3, at the caustic; afterwards oscillating within 8e-4 | |
| t_p of the two resolutions within 0.25 M | | 128^3 not finished | open |

The initial rms values of the sample are z_rms = 1.9399 M, R_rms = 6.3371 M against
1.9494 and 6.3246 for the homogeneous spheroid (the weight psibar concentrates the
sample slightly in z and not in R). W(0) of the particle sum is -0.086182; the
homogeneous spheroid has -(3/5) M_0^2 asin(e)/(a e) = -0.08622 [computed by hand from
the closed form; 0.05 per cent].

Failed sub-statement of entry 7: I wrote that the crossing would be spread over about
0.3 M. The 10, 50 and 90 per cent crossing times are 18.76, 20.00, 20.76 M: two M
from 10 to 90 per cent. How the spread is distributed (crossing time of every particle,
10/50/90 per cent, in bins of the starting values; `newton_mode.json`, keys
`crossing_by_*`):

| bin of the starting height / local half-thickness | < 0.10 | 0.10-0.25 | 0.25-0.50 | 0.50-0.73 | 0.73-0.90 | > 0.90 |
|---|---|---|---|---|---|---|
| 10, 50, 90 per cent of t_cross [M] | 18.26, 19.76, 20.76 | 18.26, 20.00, 20.76 | 18.76, 20.00, 20.76 | 19.00, 20.00, 20.50 | 19.50, 20.00, 20.76 | 20.00, 20.50, 21.00 |

| bin of the starting radius R_0 [M] | < 2.59 | 2.59-4.21 | 4.21-6.12 | 6.12-7.80 | 7.80-8.78 | > 8.78 |
|---|---|---|---|---|---|---|
| 10, 50, 90 per cent of t_cross [M] | 20.00, 20.26, 20.76 | 19.50, 20.00, 20.50 | 18.76, 19.76, 20.50 | 18.50, 19.76, 20.50 | 18.50, 20.00, 20.76 | 19.00, 20.76, 21.76 |

Reading [JUDGEMENT; no run has yet been made in which it could fail]: the medians move
by at most 1 M across the bins, so most of the 2 M spread is scatter inside a bin,
largest for the particles that start closest to the plane (2.5 M between 10 and 90 per
cent) and smallest for those that start farthest (1.0 M). That is the signature of the
force noise of 10^4 particles on cells of M/2 (0.7 particles per cell in the spheroid):
the ordered displacement of a particle is proportional to its starting height, the
noise is not. The medians themselves vary coherently with radius: the rim (R_0 > 8.8 M,
where the sample is 3.4 per cent less dense) crosses 0.8 M later than the middle, and
the innermost decile 0.5 M later than the middle (not predicted; the figure at 20 M
shows a ring at R of about 3 to 4 M that has already crossed while the centre has
not). The 128^3 run is the test: noise scatter and the cloud are both resolution
dependent, the coherent part from the density contrast is not.

Consequence for T3: the GR pancake time is to be compared with t_p = 20.0 M of the
same particles (snapshot grid; 19.9 M from the history), not with 19.74 M; and the
crossing fraction rises over about 2 M even without relativity, so P3b's "above 0.9"
is to be read at t_p + 1 M or later.
