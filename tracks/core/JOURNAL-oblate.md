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
- P1c (restated 14:58Z, before any run of T1: the first wording asked for a core mean of
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
