# Diagnostics for the expanding-ball problem (A-pre-4, part 2)

Helper of A-emd-pbh, 2026-11-15. Plan for black-hole mass and spin, for invariant
comparisons with the exact solution, and for wave extraction: what exists in this
repository, what it is good for in S1, and what is missing (with the owner who would
write it: analysis code outside `athenak/src` is the track's, source is core's, decision
0010). Labels as in `GAUGE.md`; locators are files and lines of this repository unless a
paper is named (`M`, `P`, `Y` as in `GAUGE.md`).

## 1. What the deliverables need

S1 asks for the black-hole mass at formation and its growth, the spin at formation and
after accretion, the waveform against the quadrupole approximation, and, for gate G2,
turnaround and horizon-formation times of the spherical ball that converge to the exact
solution (brief lines 345-351, 721; `coord/CHARTER.md` section 9.4). Every one of these
must be read in a way that does not depend on the slicing, because the gauge itself is
still being chosen (`GAUGE.md`).

## 2. Black-hole mass and spin: the horizon finder

Exists [VERIFIED]:
- AthenaK's pseudospectral flow finder (`athenak/src/z4c/fastflow.cpp`), options in
  `<fastflow>` (lines 57-140): `num_horizons`, `ntheta`, `lmax`, `flow_iterations_N`,
  `flow_alpha_beta_const_N`, `mass_tol_N`, `find_every`, `initial_radius_N`,
  `center_x_N..z_N`, `start_time_N`, `stop_time_N`, `metric_drvts`. Output
  `horizon_summary_N.txt`: 1 iter, 2 time, 3 mass, 4-6 S_x, S_y, S_z, 7 S, 8 area,
  9 hrms, 10 hmean, 11 mean radius, 12 min radius (lines 260-261), and the shape file.
- Column 3 is the Christodoulou mass sqrt(M_irr^2 + S^2/(4 M_irr^2)) (line 821), with
  M_irr = (A/16 pi)^(1/2) (line 761). `paper/sections/method.tex:197` calls the finder's
  mass irreducible; the two agree for zero spin. For S1 read M_irr from column 8.
- The correction of this repository: `metric_drvts = interpolant` takes metric
  derivatives from the interpolant of the ghost-filled metric; the distributed setting
  reads masses 2 to 6 percent low near block faces (`docs/TESTLOG.md:334-365`). With the
  correction the finder agrees with the slice's Misner-Sharp mass to 3e-4 at the
  production settings (16 polar points, l_max 8, mass tolerance 1e-5, every 16 cycles;
  `docs/TESTLOG.md:367-385`, 81-89).
- Small horizons: the default flow constant 1 overshoots for m << 1; 0.05 for horizons of
  about 0.1 M and 0.2 for a common horizon, tolerance 1e-7 over 2000 iterations, agree
  with the Misner-Sharp mass to one percent (`method.tex:197`).
- Particle excision inside a found horizon (`ah_exc_factor`, `particles/nrpic.cpp:399-420`)
  and by lapse (`alpha_exc`, absolute, lines 117, 482-485).

Plan for S1:
1. Centre the search on the peak (spherical and triaxial cases: the origin of the
   octant-symmetric data); start radius a few times 2 M_exp and flow constant of order
   M_exp, with M_exp the mass the exact solution (spherical) or the hoop estimate of
   A-pre-2 (triaxial) assigns to the forming horizon; start time a little before the
   exact horizon-formation time. Record every `find_every` cycles from then on.
2. Mass: M_irr from the area; at formation compare with the exact mass inside the shell
   whose areal radius first equals 2 m (section 3); afterwards fit the growth (2608.13206
   uses the Zel'dovich-Novikov form and the rate Psi = dM/(H M dt), P:457-495; the matter
   era form is to be derived by the track).
3. Spin: the finder's S is (1/8 pi) closed integral of phi^a s^b K_ab dA with flat
   coordinate rotation vectors about the search centre (`fastflow.cpp:1357-1378`), the
   full K_ab. In an expanding region K_ab has the trace part (K/3) gamma_ab with
   K = -3H, and a flat rotation vector is tangent to the surface only for a sphere about
   the centre. The trace part then adds (K/(24 pi)) times the integral of D_a phi^a over
   the enclosed volume (Gauss), which vanishes for a metric axisymmetric about that axis
   and not otherwise [JUDGEMENT, derived here, not yet measured]. The analytic
   expectations for S1 range from near-extremal to very small spins (brief lines
   207-208, 349; to be read in 1707.03595, 2507.18312, 2306.11810 by A-pre-2), so the
   bias must be measured before a small spin is quoted: run G-R4 of `GAUGE.md` (a
   non-rotating collapse with the centre offset by a few cells); the fix is to project
   phi onto the surface or to use the trace-free part, a few lines in the finder
   (core).
4. Independent spin checks (missing): the angular momentum of the matter that falls in,
   sum of m_p (x - x_c) x u for the particles excised inside the horizon (the history
   records their number and rest mass only, `docs/FORMATS.md:41` columns 17-18), and the
   mesh integral of S_i phi^i sqrt(gamma) (the history has the linear integrals of S_i
   only). Offline, the particle snapshots (`<base>.part.NNNNN.bin`, x^i, u_i, m per
   particle, `docs/FORMATS.md:44`) give the first at the snapshot cadence `snap_dt`.

## 3. Comparison with the exact solution in invariants

The spherical runs (G2) compare with the exact time-reversed Oppenheimer-Snyder or
Lemaitre-Tolman-Bondi solution of A-pre-1. Invariants that need no identification of
slices [BACKGROUND for the spherical-symmetry statements]:
- per particle (dust shell of enclosed rest mass M_s): proper time tau and areal radius R.
  Before shell crossing R(tau) is the exact cycloid or parabola of that shell; its
  turnaround (dR/dtau = 0) and the moment R = 2 M_s (the shell crosses the trapping
  horizon, an invariant hypersurface in spherical symmetry because m and R are scalars)
  are the G2 times;
- the Misner-Sharp mass m = (R/2)(1 - gamma^ij d_iR d_jR + R^2 K_T^2): a scalar,
  constant on each dust shell before shell crossing, so m at a particle's R must equal
  its shell's M_s whatever the slicing;
- the Kretschmann scalar: inside a homogeneous dust region the Weyl part vanishes and
  I = (320/3) pi^2 rho^2 [JUDGEMENT, derived from R_ab = 8 pi (T_ab - T g_ab / 2) for dust],
  so the centre gives I(tau_centre) against the exact rho(tau).

Exists [VERIFIED]:
- trajectories with the metric at the particle (`<base>.traj.bin`, `<base>.trajmet.bin`,
  `docs/FORMATS.md:42-43`, `traj_ntrack`, `traj_dcycle`), and the analysis pattern that
  turns them into tau (d tau/dt = alpha/W) and R (r times the mean tangential metric
  length) against exact geodesics: `analysis/diag/tracers_exact.py` (lines 1-45);
- Misner-Sharp profiles of restart dumps on logarithmic shells, with the outermost
  2m/R = 1, its mass, a spread that measures non-sphericity, and the finder's mass at its
  mean radius for comparison: `analysis/diag/slicemass.py` (lines 1-60);
- the probe's lapse, energy density and normal-observer proper time, the smallest and
  largest lapse, the mean K and the proper volume in `<base>.nrpic.hst`
  (`docs/FORMATS.md:41`; columns 13-16, 28-30 in the cosmology runs);
- the Kretschmann scalar with matter terms (`athenak/src/particles/nrpic_curvature.cpp`,
  `method.tex:207-215`; `curv_dt`, `curv_slice`), checked against Schwarzschild to 1e-5
  at sixth order (`analysis/diag/README.md`, curvature entry).

Missing (analysis, track A unless noted):
1. Exact references per shell for the expanding ball: R(tau), turnaround tau, tau at
   R = 2 M_s, rho_centre(tau): A-pre-1 (`tracks/A-emd-pbh/expball`).
2. A shell comparison script for the ball after `tracers_exact.py`: tags chosen at known
   initial radii (`initial_radius_by_tag` in `analysis/diag/common.py`), errors of the two
   G2 times against particle number, mesh spacing and ball radius.
3. In `slicemass.py`, the sign of K_T: 2m/R > 1 holds both for trapped surfaces
   (K_T > 0, both null expansions negative) and for anti-trapped ones (K_T < 0)
   [JUDGEMENT, from Theta_pm = +-(2/R) s.dR - 2 K_T]. The ball starts with
   2m/R = (HR)^2 < 1 (brief line 355), but a periodic box larger than the Hubble radius
   (Phase 1) has anti-trapped regions.
4. The Weyl/Ricci split of I (2610.23218 uses it, M:407-425): the Ricci part is
   64 pi^2 (2 T_ab T^ab - T^2/3), T_ab T^ab = E^2 - 2 S_i S^i + S_ij S^ij; it needs S_ij on
   the mesh in an output (core) or is computed in the code (core). Low priority.
5. A centre tracker for matter peaks (two-peak data, moving clumps): the compact object
   tracker follows a puncture by -beta or a fluid velocity (`z4c/compact_object_tracker.cpp`
   lines 96-130), not a particle overdensity (core).

## 4. Wave extraction

Exists [VERIFIED]: Psi_4 on coordinate spheres (`<z4c> nrad_wave_extraction`,
`extraction_radius_N`, `extraction_nlev`, `waveform_dt`; `z4c.cpp:216-232`), projected on
spin-weighted harmonics 2 <= l <= 8 (`z4c_wave_extr.cpp:78-106`), written to
`waveforms/rpsi4_real_*`, `rpsi4_imag_*`. Psi_4 is built from the ADM variables with the
vacuum form of the electric part, R_ab + K K_ab - K_ac K^c_b, without matter terms
(`z4c_calculate_weyl_scalars.cpp:372-378`), on a tetrad started from the coordinate
radial and z directions (lines 254-320), multiplied by the coordinate radius (lines
409-410). Cauchy-characteristic dumps exist (`z4c/cce`, `<cce> num_radii`), but the
characteristic evolution is not in this repository and decision 0010 excludes an outside
code, so they are of no use here [JUDGEMENT].

What this means for S1 [JUDGEMENT]:
- Phase 0 (ball in vacuum): the exterior is Schwarzschild for the spherical part
  (Birkhoff), so any Psi_4 outside the ball comes from the deformation; the vacuum form is
  correct there as long as each extraction sphere stays outside the matter for the whole
  run. With zero shift the ball keeps its coordinate radius; with a Painleve-Gullstrand
  shift its coordinate radius grows with its areal radius: choose radii beyond the largest
  coordinate extent of the matter. Normalize with the areal radius of the sphere (offline
  from the metric), not the coordinate radius.
- Phase 1 (periodic): every sphere lies in matter; the vacuum form then carries matter
  terms (for dust R_ab mbar^a mbar^b = 8 pi rho (u.mbar)^2) and Psi_4 is not the Weyl
  scalar. Needs the matter terms in the code (core) and coordination with Track B's
  wave diagnostics (B-pre-3), which own the periodic case.
- Quadrupole comparison (brief line 350): needs the mass quadrupole of the particles,
  I^ij = sum m_p x^i x^j (or the energy-weighted form), and its rate at a cadence that
  resolves the collapse. The history has no such column; particle snapshots (`snap_dt`,
  `docs/FORMATS.md:44`) allow it offline at their cadence. A history column with
  sum m x^i x^j and sum m (x^i v^j + x^j v^i) is cheap (core).
- Amplitude: the signal of a single collapse is small against the junk radiation of the
  initial data and the gauge waves of the lapse collapse; the extraction must be tested
  on the spherical ball first, where the exact answer is zero.

## 5. Summary: exists, missing, owner

| Item | Exists | Missing | Owner |
|---|---|---|---|
| Horizon mass | flow finder, corrected derivatives, settings for small horizons | finder settings from M_exp per run | A (inputs) |
| Spin | finder S with flat rotation vectors | bias test G-R4; surface-projected rotation vectors; excised angular momentum and mesh angular momentum in the history | A (test), core (source) |
| Invariant G2 times | traj/trajmet, tracers_exact pattern, slicemass | exact per-shell references; ball shell script | A-pre-1, A |
| Trapped vs anti-trapped | | K_T sign in slicemass | A |
| Curvature | Kretschmann with matter terms | Weyl/Ricci split | core (low priority) |
| Waves, Phase 0 | Psi_4 (vacuum form), l <= 8 | areal-radius normalization; zero-signal test on the spherical ball | A |
| Waves, Phase 1 | | Psi_4 with matter terms; coordination with B-pre-3 | core, B |
| Quadrupole | particle snapshots and restart files | history column of the particle quadrupole and its rate | core |
| Peak tracking | puncture and fluid trackers | particle-overdensity tracker for finder centres | core |
