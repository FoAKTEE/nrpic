# DESIGN: the threshold line in the periodic box (Track A, S1)

Work package `periodic_threshold`, wave 2, helper of A-emd-pbh, 2026-11-15. Decision 0013:
the threshold line is built in the periodic box; the expanding ball stays the spherical
verification case. This file fixes the set-up, says what the code does today (each claim
with a run id or a source line), and what core has to add. Predictions and outcomes of
every test: `JOURNAL.md`. Labels: [VERIFIED] read at a locator or measured in a registered
run, [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Run ids are `A-emd-pbh-<UTC>-<commit7>`;
outputs under `/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>/`.

Summary.
1. The set-up is that of arXiv:2609.14218 (one Gaussian curvature peak with ellipticity e
   and prolateness p, box of side 20/k = 8.16 r_m), with the peak at the box centre.
2. The repository's only tool for such data (`cosmo/ic/make_field.py`, linear
   Newtonian-gauge dictionary plus a nonlinear constraint solve) builds them for
   mu <= 0.3 at a start k/(a_i H_i) >= 1, with a first-order error of 8 per cent in the
   conformal factor at 64^3 that falls as h^2; it fails at the paper's start (k/aH = 1/5)
   and at mu = 0.5. On the constant-mean-curvature slice of the paper the same solver
   reproduces the gradient-expansion data at the paper's start to 3e-5 (mu = 0.03) and
   2.6e-8 (mu = 0.3, no filter), but diverges at mu = 0.5. The line needs core's phase-1
   generator on that slice with a variable-coefficient solve (request 1).
3. Static refinement works in the periodic cosmological box (homogeneity kept exactly);
   refined blocks start with an 8 per cent constraint violation relative to the
   perturbation (data interpolated from the root mesh). Adaptive refinement crashes
   because `nrpic_cosmo` sets no refinement function (one-line fix, request 3).
4. The horizon finder gives the same mass in a periodic mesh as in the calibrated
   outflow mesh, reports nothing in the homogeneous universe, and does not wrap
   coordinates: the peak must sit at the box centre.
5. Scouting runs: section 7.

---

## 1. Set-up, units and box

[VERIFIED, MDPBH.tex:839, 549, 709-719, 907-908; run A-emd-pbh-20261115-153520-0576e01 (P0)]

- Profile: zeta = 2 ln Psi = mu exp(-k^2 r^2/6) [1 + (k^2/6)(p(2X^2 - Y^2 - Z^2) +
  3e(Y^2 - Z^2))]; compaction radius r_m = sqrt(6)/k; horizon entry (k/aH)^2 = 6 defines
  t_H. Zel'dovich eigenvalues (2 mu/15)(k/aH)^2 (1+3e+p, 1-2p, 1-3e+p): the fastest axis
  is z (the profile is narrowest along Z for e > 0), so the first pancake is a sheet
  normal to z.
- Code units (cosmo/README.md): G = c = 1, H_i = 1 at a_i = 1, conformal time tau with
  a = (1 + tau/2)^2 in the homogeneous solution; k = eps_i = k/(a_i H_i) fixes the start.
  t/t_H = (a/a_H)^(3/2), a_H = 6/eps_i^2.
- Box: side 20/k (the paper's octant 0 <= X <= L = 10/k, MDPBH.tex:476, doubled), i.e.
  8.16 r_m. It spans 100 initial Hubble radii at the paper's start (eps_i = 0.2), 8.16 at
  horizon entry and 1.30 at 250 t_H, shrinking in Hubble units as t^(-1/3) (P0,
  `figures/fig_design_numbers.png`). The profile at the box face is e^(-100/6) = 6e-8 of
  the peak: the periodic images are 8.16 r_m apart and the box is causally connected over
  the scan (the comoving light distance to 250 t_H is tau = 152 at eps_i = 0.2, 1.5 box
  sides) [VERIFIED as arithmetic]. Size convergence: 20/k and 30/k (SCOPE.md section 5).
- Peak at the box centre, mesh [-10/k, 10/k)^3: the finder does not wrap (section 5) and
  the radius-based refinement criterion of `z4c_amr` measures from the origin
  (`athenak/src/z4c/z4c_amr.cpp`, RefineRadii) [VERIFIED by reading].
- Start epoch: the paper starts at k/aH = 1/5 (a_i = a_H/150). The existing tool cannot
  (section 2); the scouting runs start at eps_i = 1 (a_H = 6, tau(t_H) = 2.9,
  tau(250 t_H) = 28.9). Epochs of the scouting amplitudes (P0, e = 0.2):

| mu | first, second, third Zel'dovich axis (t/t_H) | top-hat collapse of the compaction shell | tau at 250 t_H (eps_i = 1) |
|---|---|---|---|
| 0.03 | 133, 269, 1063 | 508 t_H | 28.9 |
| 0.05 | 62, 125, 494 | 236 t_H | |
| 0.3 | 4.2, 8.5, 33.6 | 16.1 t_H (tau = 10.4) | |
| 0.5 | 1.95, 3.95, 15.6 | 7.5 t_H (tau = 7.6) | |

Top-hat amplitude for 250 t_H: mu = 0.048; for 1000 t_H: 0.019 (P0; SCOPE.md H1).

## 2. Initial data: what builds them, what is missing

### 2.1 Today: `cosmo/ic/make_field.py` through `scripts/make_peak_ic.py`

The driver writes zeta on the mesh, the linear growing mode delta_N = -(2/5) lap zeta /
(a_i H_i)^2 (psi_N = -(3/5) zeta [BACKGROUND]; the tool's own psi_N agrees with -(3/5) zeta
up to the mean of zeta, 1.8e-4 at mu = 0.03), and calls `make_field.build` unchanged:
Zel'dovich lattice of one particle per cell, Newtonian-gauge dictionary rho, K, alpha,
conformally flat constraint solve on the torus with the code's deposit (cloud-in-cell,
two binomial passes, compensation). Output: `particles.nrp`, `fields.bin` (NRCOSMO1),
`id.json`. What it gives (runs T1 A-emd-pbh-20261115-153527-0576e01 (sweep, in
progress at the time of writing for n = 32, 128 and nfilter = 0), T1b
A-emd-pbh-20261115-155802-9a6596f, S data A-emd-pbh-20261115-154735-69e8f8b):

| mu | eps_i | n | constraint residual of the solve | c = max|psi - psi_dict| / max|psi_dict - 1| | note |
|---|---|---|---|---|---|
| 0.03 | 0.2 | 64 | 1e-12 per inner solve | 0.38 | outer iteration not converged (change 1.3e-4 per step, ratio ~0.97) |
| 0.03 | 1 | 64 | 1.6e-12 | 0.078 | |
| 0.03 | sqrt 6 | 64 | | 0.025 | |
| 0.2 | 1 | 64 | 3.7e-12 | 0.031 | |
| 0.3 | 1 | 64 | 7.2e-12 | 0.137 | used for S1 |
| 0.5 | 0.2 | 64 | NaN | NaN | diverges |
| 0.5 | 1 | 64 | 0.06 (stagnates at the 60-iteration limit) | 0.10 | not solved data |

Findings [VERIFIED in the runs named; readings JUDGEMENT]:
1. **A first-order inconsistency at super-horizon scales.** c does not scale with mu
   (0.362 and 0.363 at mu = 0.03 and 0.003 in a 32^3 smoke test; 0.078 at 64^3, a factor
   4.6 smaller per halving of h). Reading: on the Newtonian-gauge slice the Hamiltonian
   constraint at super-horizon scales rests on the cancellation K^2/12 - 2 pi E =
   -(3/4) delta_N between two terms -2 psi_N that are (3/2)(aH/k)^2 times larger than
   delta_N; K is set exactly on the mesh, E is deposited and filtered, so the residual of
   the cancellation is a first-order error amplified by (aH/k)^2. It falls with h and
   with later starts (0.078 at eps_i = 1, 0.025 at sqrt 6). The paper's start eps_i = 0.2
   is out of reach of this tool.
2. **Linear in zeta.** The dictionary uses psi_N = -(3/5) zeta and alpha = sqrt(1 + 2
   psi_N), undefined for zeta > 0.83 and far from the exact long-wavelength data
   (Psi = e^(zeta/2)) for mu ~ 0.3-1. The solve stagnates between mu = 0.3 and 0.5.
3. **Conformally flat only.** NRCOSMO1 carries psi, K, alpha and Ahat; the
   gradient-expansion data of the paper have a conformal metric gamma-tilde_ij =
   delta_ij - (4/5) p_ij/(aH)^2 (MDPBH.tex:521-523). Evaluated on the same mesh
   (`make_peak_ic.ge_diagnostics`): max|gamma-tilde - delta| = 1.8e-4 at mu = 0.03,
   eps_i = 0.2, i.e. 1.2 per cent of Psi - 1 = 0.0149, but 4.4e-3 (30 per cent) at
   eps_i = 1; at mu = 0.5: 2.3e-3 at eps_i = 0.2 against Psi - 1 = 0.28. The
   transverse-traceless part of p_ij, which the longitudinal Ahat of the solve cannot
   represent, is 0.26 per cent (mu = 0.03) and 3.9 per cent (mu = 0.5) of p_ij in L2.
   So the gradient-expansion data are good only at small eps_i, where make_field fails,
   and make_field is good only at eps_i >= 1, where the gradient expansion is not.
4. **Root mesh only.** The solve runs on the root mesh; refined blocks get cubic
   interpolation of the fields while the clouds sit on the root level: 8 per cent
   violation relative to the perturbation at t = 0 (T2b, section 4).
5. **One equal-spaced lattice.** One particle per root cell: (4 pi/3) r_m^3 / dx^3 =
   2,000 particles inside r_m at 64^3 (k dx = 0.3125). SCOPE.md section 5 asks N >= 1e5
   inside the perturbation at deltabar_ent >= 0.04 (noise floor), i.e. a spacing
   k s <= 0.085 inside r_m; a uniform lattice that fine in the 20/k box has 235^3 =
   1.3e7 particles, a lattice nested to that spacing inside 2 r_m about 1e6 [VERIFIED as
   arithmetic; the requirement is SCOPE.md's JUDGEMENT].

### 2.2 The constant-mean-curvature route works with the existing solve, up to mu = 0.3

T4 (runs A-emd-pbh-20261115-160718-e04c0cc, A-emd-pbh-20261115-161134-f3949f8;
`scripts/t4_cmc_route.py`, feasibility only, no files for the code): the
gradient-expansion fields at the paper's start eps_i = 0.2, e = 0.2, 64^3; E from the
conformally flat Hamiltonian constraint of psi_GE with K = -3H; momenta from the momentum
constraint; one particle per cell at the cell centre (the paper's lattice); then
`cosmo_id.solve` unchanged with K = -3H [VERIFIED in those runs]:

| mu | filter | iterations | residual | c_CMC = max|psi - psi_GE| / max|psi_GE - 1| |
|---|---|---|---|---|
| 0.03 | none | 9 | 6e-12 | 7.5e-10 |
| 0.03 | 2 passes + compensation | 10 | 3e-12 | 3.4e-5 |
| 0.3 | none | 78 | 7e-12 | 2.6e-8 |
| 0.5 | none / with filter / started from psi_GE | 200 | NaN | diverges |

So the slice removes the super-horizon problem of 2.1 (c falls from 0.38, unconverged, to
3e-5 at the same start), and the remaining limit is the solver's iteration: it
preconditions with the mean of sigma = (5/12) K^2 psi^4 + 2 pi psi^4 E, and at mu = 0.5
(psi^4 = 2.7 at the peak) the local sigma exceeds the mean by more than the mean, so the
long-wavelength error grows [JUDGEMENT; the divergence from psi_GE itself shows it is the
iteration, not the start]. A variable-coefficient (Newton, multigrid or Krylov) step is
needed for mu >= 0.5, i.e. for the hoop line (0.45 at e = 0.2) and above.

### 2.3 Needed (request 1 to core)

The phase-1 generator (already requested in wave 1,
`outbox/20261115T1320Z__to-core__phase1-generator-and-gauge-options.md`), made precise by
T1 [JUDGEMENT]:
- slice of constant mean curvature, K = -3H (MDPBH.tex:515-520): no super-horizon
  cancellation, the density contrast is q/(aH)^2 = O(eps^2 zeta) directly;
- fields of the gradient expansion nonlinear in zeta (Psi = e^(zeta/2), q, p_ij of
  MDPBH.tex:536-543) at eps_i <= 0.2; particle masses m = E sqrt(gamma) dV / Gamma (the
  paper's rule, MDPBH.tex:1064-1074) and momenta from J = E V of the momentum constraint;
  then the constraint solve with that K for exact consistency with the run's deposit
  (`cosmo_id.solve` suffices to mu = 0.3, T4; above it a variable-coefficient step);
- a field-file format carrying the conformal metric (or the decision, with this
  package's numbers, that the conformally flat part suffices at eps_i = 0.2: 1.2 per cent
  of the perturbation at mu = 0.03, 0.8 per cent at mu = 0.5);
- a nested particle lattice (finer spacing inside the static levels, masses scaled) and
  the constraint solve on the refined levels (core's wave-2 item `idsolve`).
Acceptance tests (this package supplies the reference evaluator,
`scripts/make_peak_ic.py:ge_diagnostics`): (a) the solved psi equals the
gradient-expansion psi = Psi(1 - q/(6 (aH)^2)) to O(eps_i^4) at eps_i = 0.2 for mu = 0.03
and 0.5; (b) the code's Hamiltonian constraint at t = 0 below 1e-3 of 16 pi max|E - Ebar|
on the uniform mesh (make_field reaches 3.5e-5 to 1.8e-4, T2b) and below 1e-2 on refined
levels; (c) the linear growth of the central density contrast to 1e-2 until it reaches
0.1.

## 3. Gauge

What exists and what is known [VERIFIED at the locators]:
- Conformal-time lapse d_t alpha = -(1/3) alpha^2 K with zero shift (cosmo/README.md);
  plus the driver towards constant mean curvature `lapse_kdriver` (cosmo/TESTLOG.md
  563-578). The single-wavelength collapse of cosmo E1 with this gauge ended with a
  non-positive metric determinant in the finest cells before any horizon (64^3 uniform:
  a = 20.6; three static levels: a = 17.6; cosmo/TESTLOG.md 744-763); a Gamma-driver
  shift made it worse on refined blocks (809-825).
- Track B: in a periodic vacuum box with K_xx = 1.5 sin 2 pi x the conformal-time and
  volume lapses form gauge shocks near t = 2 that do not converge; harmonic, 1+log and
  the K driver survive (B's `periodic_z4c/tables/gauge.md`, runs
  B-emd-gw-20261115-114004-0ea0f74, -114143-0ea0f74).
- arXiv:2609.14218: d_t alpha = -2 alpha (K + 3H) + (3/2) alpha H_k exp(-C^2 alpha_b^2/a_k^2),
  C = 5, alpha_b the lapse at the box corner (MDPBH.tex:452-457); Gamma driver with
  damping 3H (466-469). arXiv:2610.23218: 1+log with K - K_FLRW, softplus slicing, shift
  damping that depends on the refinement level (REFERENCES.md).

Design [JUDGEMENT]: the scouting runs use the E1 gauge (the only one tried through a
collapse in this code) to see where it breaks; the candidates for the line, in order, to
be implemented by core's wave-2 item `gauge` and selected on the spherical test A3 and
on S1: (1) 1+log relative to the box-mean K, d_t alpha = -2 alpha (K - <K>) plus the
background term that keeps alpha = a (the analogue of MDPBH.tex:452-457 in conformal
time); (2) the existing K driver; (3) a Gamma driver scaled with alpha^2 and damped at a
rate ~ H, switched on only near the collapse. Selection criteria: the homogeneous and
linear checks of cosmo/ (alpha/a - 1 below 1e-6 after 12 steps; linear growth to 1e-2);
survival of the nonlinear gauge test of Track B; S1 to horizon formation with the
constraint bound of section 6.

## 4. Mesh

What the code supports today [VERIFIED by reading and in the runs named]:
- **Static refinement in the periodic cosmological box works.** `nrpic_cosmo` reads the
  root-mesh file and interpolates it (cubic) onto refined blocks (`nrpic_cosmo.cpp`
  header and lines 140-209). In the homogeneous universe with two static levels and the
  adaptive cloud level the conformal factor stays uniform to 2e-15 and H_max = H_mean
  (T2a, run A-emd-pbh-20261115-154250-527a6d1, `figures/fig_t2_mesh.png` top panels).
  Clouds on the finest level instead (one particle per root cell = one per 64 level-2
  cells) give a relative Hamiltonian constraint of 1.02 at t = 0: with a lattice of one
  particle per root cell the adaptive cloud level is required.
- **Refined blocks start inconsistent.** With the peak data, |H| / (16 pi max|E - Ebar|)
  at t = 0 is 1.8e-4 (mu = 0.5) and 3.5e-5 (mu = 0.03) on the uniform mesh, 0.085 and
  0.077 on the static mesh (T2b, run A-emd-pbh-20261115-154740-69e8f8b): an eight per
  cent violation relative to the perturbation, linear in mu. Constraint damping and the
  solve on refined levels (request 2) address it.
- **Adaptive refinement does not run with `nrpic_cosmo`.** Segmentation fault at the
  first refinement check, also in the homogeneous universe and with the trivial
  criterion: `<amr_criterion0> method = user` calls `pgen->user_ref_func`
  (`mesh_refinement.cpp:243`), which `nrpic_cf` sets (`nrpic_cf.cpp:175-177, 392`) and
  `nrpic_cosmo` does not (gdb backtrace, run A-emd-pbh-20261115-155737-8422a4a). One line
  in `nrpic_cosmo.cpp` (request 3). The z4c criteria then available: `chi`/`dchi`
  thresholds are useless in cosmology (chi = a^-2 psi^-4 falls everywhere); the Lohner
  indicator of alpha chi^(7/p) is a ratio of differences and does not refine the
  homogeneous universe; `radius_*` refines around the origin [JUDGEMENT from reading
  `z4c_amr.cpp`; untested in the periodic box until the fix].
- **Diagnostics on refined meshes:** the particle module's field dumps return on
  multilevel meshes (`nrpic_io.cpp`, NrpicWriteEnergyField: `if (pm->multilevel) return`);
  the scouting runs use AthenaK `tab` lines along the three axes through the peak.

Mesh of the scouting runs (`inputs/peak_smr4.athinput`): root 64^3 (k dx = 0.3125, r_m =
7.8 cells), four nested static levels, level l inside |x| < 5/2^(l-1) (finest k dx =
0.0195 inside |k x| < 0.625), 16^3 blocks, about 1.3e6 cells, step 0.25 of the finest
cell (AthenaK takes one step for all levels).

## 5. Horizon finder in a periodic run

Tested (T3, run A-emd-pbh-20261115-154250-527a6d1) [VERIFIED]:
- vacuum puncture of unit mass, dx = M/8 at the horizon, box [-16, 16]^3: the finder
  gives 0.9915211031 with outflow and with periodic boundaries, the calibration value
  0.991521 of docs/TESTLOG.md (initial slice, corrected finder) to all its digits;
- finder centred one period away, at (32, 0, 0): no horizon reported. **The finder does
  not map surface points into the periodic box**; a horizon crossing a box face is not
  found (request 4, low priority once the peak is centred);
- homogeneous universe: no horizon reported in three runs, no crash (outgoing expansion
  2/(aR) + 2H > 0).
Settings for the line [JUDGEMENT]: centre at the origin, `metric_drvts = interpolant`
(the original derivatives are wrong near block faces, docs/TESTLOG.md 336-366), initial
radius of the order of the coordinate radius of the compaction region at the time, the
area mass sqrt(A/16 pi) recorded with the polar and equatorial circumferences (hoop test,
as arXiv:1901.04498). Resolution: twelve cells per coordinate horizon radius (SCOPE.md
section 8); the coordinate radius in the conformal-time gauge is measured in S1.

## 6. Collapse and no collapse; scan grid and cost

Definition (SCOPE.md section 3, fixed before any run, with the periodic specifics)
[JUDGEMENT]:
- amplitude mu of the profile (deltabar_ent = 0.883 mu, central delta_c = 12 mu/5 at
  entry; SCOPE.md 10.1); time in units of t_H of the background, from the coordinate
  time through a(tau) of the homogeneous solution, checked per run by alpha/a at the box
  corner (the far field follows the homogeneous solution; S2 measures how well);
- BH: an apparent horizon found in at least three consecutive searches spanning at
  least 5 M_AH, with the L2 norm of the Hamiltonian constraint outside the horizon below
  0.1 of the L2 norm of 16 pi E over the same region;
- NO-BH: no horizon to t_end with the same bound; "halted" if the Lagrangian radius of
  the inner half of the perturbation mass has passed a minimum and grows again, "late"
  otherwise;
- UNDECIDED: the run ends or breaks the bound before t_end without a horizon (the
  outcome of every collapse attempt in this code so far, cosmo E1);
- threshold bracket (A_lo, A_hi] bisected in ln mu to a ratio 1.1; t_end = 250 t_H
  primary, continuation of the NO-BH run below A_c to 1000 t_H.
The constraint norms over a region need output the code lacks on refined meshes
(request 5); the scouting runs record `cstat` maxima and means over the whole mesh.

Scan grid (SCOPE.md section 5, unchanged): e in {0, 0.05, 0.1, 0.2, 0.3} at p = 0, then
p = +-0.1 at e = 0.2; bisection from seeds 0.03, 0.045, 0.05, 0.1, 0.45 at e = 0.2; about
five runs per e to a ratio 1.1, plus the convergence triplets (4N, dx/2, box 30/k) at
e = 0.1 and 0.2.

Cost: section 7 gives the measured cost of the scouting runs; the cost model of
SCOPE.md section 9 is revised there.

## 7. Scouting runs

(Filled in from runs A-emd-pbh-20261115-155754-8422a4a (S2) and
A-emd-pbh-20261115-160349-9d232d2 (S1); see JOURNAL.md.)

## 8. Requests

To core:
1. Phase-1 generator on a constant-mean-curvature slice (section 2.2), with its
   acceptance tests; field file with the conformal metric or a recorded decision.
2. Constraint solve on refined levels for the periodic generator (wave-2 `idsolve`),
   and a nested particle lattice.
3. `nrpic_cosmo.cpp`: set `user_ref_func` to a function calling
   `pmbp->pz4c->pamr->Refine(pmbp)`, as `nrpic_cf.cpp:175-177, 392` does; adaptive
   refinement in the periodic box crashes without it (section 4).
4. Horizon finder: wrap surface points into a periodic box (section 5).
5. Output on refined meshes: field dumps of the particle module on multilevel meshes, or
   the L2 norms of H and 16 pi E inside and outside a sphere in a history file; the
   proper-volume mean of K and the lapse at a fixed point far from the peak.
6. A lapse for collapse in an expanding box (wave-2 `gauge`): candidates in section 3.

To orch: `nrpic-run` refuses the shared worktree while other helpers hold untracked
files; runs were registered by hand (README.md).
