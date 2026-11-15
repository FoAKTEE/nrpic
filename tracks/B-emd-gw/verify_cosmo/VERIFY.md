# VERIFY: what `cosmo/` already establishes for Track B, against its criteria

Helper package `verify_cosmo` of owner B-emd-gw, 2026-11-15. Charter point 2
(`coord/CHARTER.md` lines 22-25): B-pre-2, part of B-pre-5 and the rows "FLRW dust" and
"growth of linear perturbations" of brief section 10 are done in `cosmo/`; B verifies
them against its own criteria. Criteria quoted from `coord/CHARTER.md`: section 10 rows
(lines 224, 225, 228) and the Track B sheet (line 121).

Sources read: `cosmo/README.md`, `cosmo/PLAN.md` (state blocks 01:08 to 10:31 of
2026-11-14), `cosmo/TESTLOG.md` (entries cited by line), `cosmo/paper/main.tex`
(results and progress ledger, lines 129-410), stored analysis results
`cosmo/analysis/daverio_{a,b,c256_p3}.json`, run directories `runs/cosmo/*` of the main
checkout (untracked), and the paper source of arXiv:2003.08014 in
`kb-data/raw/arxiv/2003.08014/v2/src/draft.tex` (read only).

Labels: [VERIFIED] = read from the named source, with "(recomputed)" where this
package re-derived the number from the run output itself (run
`B-emd-gw-20261115-115414-7ffbde1`, `results/flrw_recheck.json`, figure
`figs/flrw_recheck.png`) and "(log)" where it is the number written in
`cosmo/TESTLOG.md` with its run directory and was not recomputed here;
[JUDGEMENT] = this package's inference; [TO VERIFY] = open.

Units of `cosmo/`: G = c = 1, initial Hubble rate 1 at a = 1, lapse condition
d_t alpha = -(1/3) alpha^2 K with zero shift, so alpha = a and t is conformal time
(`cosmo/README.md`, "Units and gauge").

---------------------------------------------------------------------------------------

## 1. Row "FLRW dust (Einstein-de Sitter)": background expansion, gauge, step scaling

| Evidence | Run directory | Numbers | Label |
|---|---|---|---|
| Homogeneous lattice at rest, 32 cells, box 4, step h/4, a = 1 to 4, densities converted per stage (C0) | `runs/cosmo/flrw_n32_cpu_sd` | largest relative error of the lapse (= scale factor) 1.9e-7, probe density 1.1e-6, mean K 3.8e-7, proper volume 1.1e-6 | [VERIFIED] (recomputed) |
| Same with the sources held fixed during a step (the published coupling) | `runs/cosmo/flrw_n32_cpu` | lapse 7.9 %, density 4.2 %, mean K 3.0 %: the first-order coupling error that `source_density` removes | [VERIFIED] (recomputed); cause in TESTLOG lines 47-59 |
| Step limited by the expansion rate, 16 cells, box 4, a = 1 to 36 | `runs/cosmo/dtexp_test/{ref,lim}` | Courant step: lapse 4.3e-5, density 7.4e-5, H_r 2.5e-5 at the end; limit 0.01: 7.0e-8, 1.5e-7, 6.0e-8 | [VERIFIED] (recomputed); TESTLOG lines 1077-1081 |
| Thousandfold expansion (test A0 of arXiv:1904.07841), 8, 16, 32 cells, step 0.1 cell | `runs/cosmo/dav_a0_n{8,16,32}` | error of chi at t = 100 Mpc/h: 3.9e-9, 2.4e-10, 1.5e-11 (ratios 16.0, 15.7: fourth order with the step tied to the cell); at t = 3000 Mpc/h: 1.0e-7, 6.4e-9, 7.0e-10 | [VERIFIED] `cosmo/analysis/daverio_a.json` |
| Same with damping per unit of conformal time | `runs/cosmo/dav_a0k_n{8,16,32}` | chi error at the end 3.9e-8, 2.6e-9, 6.2e-10 (arXiv:1904.07841: 2.6e-9, 1.6e-10, 9.8e-12; factor 15 at 8 cells only partly explained) | [VERIFIED] (log) TESTLOG lines 586-600 |
| White noise on all fields and particles (test A) | `runs/cosmo/dav_a_n{8,16,32}` | stable to a = 1001; largest H falls from 1.2e-5 (t = 100 Mpc/h) to 2.5e-10 (t = 3000) at 8 cells; chi error as without noise | [VERIFIED] `daverio_a.json`; TESTLOG lines 420-433 |
| Cosmological constant | `runs/cosmo/flrw_lambda_n32_cpu` | lapse within 1.8e-6 of a(t), largest H_r 1.7e-6 | [VERIFIED] (log) TESTLOG line 738 |

Gauge: the conformal-time condition is Bona-Masso with f = 1/3 on Khat (TESTLOG lines
14-18, 412-419: Theta enters the lapse equation and drifts the clock at 1e-8); two
alternatives were built and tested for the collapse (TESTLOG lines 339-360, 563-582).

Against G2, first half ("the scale-factor error ... of the particle FLRW run reach the
sub-percent level and converge in particle number and mesh"):
- Sub-percent: met by five orders of magnitude (1e-7 at a = 4 and a = 36, 1e-7 to 1e-9
  at a = 1001). [VERIFIED]
- Mesh: fourth-order convergence at fixed step ratio (A0). [VERIFIED]
- Particle number: NOT shown. Every homogeneous run uses one particle per cell on a
  lattice, whose deposit is exactly uniform at any particle number; no run varies the
  particles per cell, with or without position noise. [VERIFIED by reading the run list
  and the log]
- None of these runs is in the production configuration of `cosmo/README.md` (cubic
  cloud, compensation, spline, step limit and damping together); `dtexp_test/lim` has
  the step limit only. [VERIFIED by reading the logs and inputs]

## 2. Row "Growth of linear perturbations": particle noise, convergence at small amplitude

| Evidence | Run directory | Numbers | Label |
|---|---|---|---|
| C1: three-mode data of arXiv:1908.05683 at amplitude 1e-4, 32 cells, a = 1 to 100, old configuration (linear cloud, filter) | `runs/cosmo/east_d1e-4_n32_cpu` | observer density contrast within 0.5 % of linear theory to a_p = 30, +0.75 % / -0.70 % at a_p = 100; GR against Newtonian 0.3 % and 0.8 % of the contrast | [VERIFIED] (log) TESTLOG lines 163-181 |
| Test B of arXiv:1904.07841 (plane wave 1e-7, box 1.35 initial Hubble radii, a = 1 to 1001), production configuration, 32 cells, 8 particles per cell | `runs/cosmo/dav_b_n32_pcs4b` | potential constant to 2.5e-4; wave amplitude over linear theory 0.99995 at the end; density with the mean removed within 3.8e-5, 4.9e-5, 7.6e-5 at t = 100, 1000, 3000 Mpc/h | [VERIFIED] `cosmo/analysis/daverio_b.json` |
| Same, step limit 0.002 | `runs/cosmo/dav_b_n32_pcs4b_f2` | potential constant to 1.5e-5; amplitude 0.99999; mean-density error 1.8e-9 | [VERIFIED] `daverio_b.json` |
| Same, 64 cells | `runs/cosmo/dav_b_n64_pcs4b` | potential constant to 7.1e-5; amplitude 0.99999; density with the mean removed 1.1e-5 to 4.0e-5 | [VERIFIED] `daverio_b.json` |
| Old configuration 32 and 64 cells (second-order mesh convergence shown there) | `runs/cosmo/dav_b_n{32,64}` | potential drift +1.72 % and +0.44 % (ratio 3.9); density departure ratio 4.0 at all times | [VERIFIED] (log) TESTLOG lines 542-561 |
| Random field, box 704 Mpc/h (linear to z = 0), production configuration, 32, 64, 128 cells (8, 8, 1 particles per cell) | `runs/cosmo/dav_c704_n{32,64,128}_pcs4bt` | power against linear theory within 0.2 % to z = 10; 64 and 128 cells agree to 0.005 % of the power in the two long shells at every epoch | [VERIFIED] (log) TESTLOG lines 1599-1650 |
| Random field, box 256 Mpc/h (nonlinear by z = 1), production configuration, 64 and 128 cells | `runs/cosmo/dav_c256_n{64,128}_pcs4bt` | the two resolutions agree to 0.2 % of the power in every shell at every epoch | [VERIFIED] (log) TESTLOG lines 1725-1747 |
| Particle number at fixed mesh: 8 against 27 particles per cell, box 256, 64 cells, OLD configuration (quadratic cloud, no compensation) | `runs/cosmo/dav_c256_n64_{t,p3t}` | largest power departure below half the cut-off 2.56 % against 2.46 % at z = 100, 5.67 % against 5.61 % at z = 10 (set by the cloud, not by the particles) | [VERIFIED] `cosmo/analysis/daverio_c256_p3.json` |
| Newtonian reference with the same particles (random field, 704 box) | `runs/cosmo/newton_c704_n{32,64}_pcs4` | nonlinear excess over linear theory equal in both to 0.02 % of the power; GR minus Newtonian -0.01 to -0.02 % at 64 cells, not determined whether relativistic or numerical | [VERIFIED] (log) TESTLOG lines 1921-1948 |

Against G2, second half ("the linear growth rate ... sub-percent and converge in
particle number and mesh"):
- Sub-percent: met for the amplitude of the growing mode (1e-5 of linear theory over a
  thousandfold expansion, test B). The growth RATE f = d ln D / d ln a is not computed
  anywhere; it follows from the amplitude records but has not been extracted.
  [VERIFIED for the amplitude; the rate is TO VERIFY]
- Mesh: second order in the old configuration (test B); in the production
  configuration the 32- and 64-cell errors are both at 1e-5 and the remaining error is
  the background step (TESTLOG lines 1901-1903), so the production configuration has no
  clean mesh-convergence sequence for test B; the random field has 64 against 128 cells
  agreeing to 5e-5 of the power. [VERIFIED (log)]
- Particle number: only in the old configuration and only for the random field (8
  against 27 per cell, above); test B ran at 8 per cell only; the production
  configuration has no run at fixed mesh with different particle numbers. NOT shown.
- Particle noise at small amplitude (the row's "what it checks"): lattices only; a
  glass or Poisson start (the noise the row is about, item 7 of brief section 7) has
  not been run. NOT shown.

## 3. Row "Multi-code comparison (weak-field regime)": gevolution, GRAMSES, fluid NR

What exists is comparison with the published numbers of other codes and with the
in-repository Newtonian particle-mesh reference; no other code was run (and by decision
0010 none may be):
- arXiv:1908.05683 (Einstein-Vlasov code of East, Wojtak, Pretorius): collapse delays and
  luminosity distances compared with values read from its figures
  (`cosmo/notes/east_figures/SUMMARY.md`): distances agree to about a tenth of the
  plotted deviations (TESTLOG lines 641-670); the delays are 2 to 5 times smaller here
  for the three lower amplitudes, attributed to the different resolution of that
  paper's two codes (TESTLOG lines 390-395, converged here in three configurations,
  lines 1705-1721). [VERIFIED (log)]
- arXiv:1904.07841 (Daverio, Dirian, Mitsou): tests A, B, C repeated with its boxes and
  resolutions; numbers side by side in TESTLOG and `cosmo/paper/main.tex` ledger.
  [VERIFIED (log)]
- arXiv:2001.07968 (GRAMSES): its initial-condition tests only (no evolution), without
  radiation, 20 of 20 closed-form checks (TESTLOG lines 1087-1126;
  `cosmo/notes/c6_report.md`). "An evolved comparison would need its code" (line
  1126). [VERIFIED (log)]
- gevolution: nothing. Fluid numerical relativity: nothing.

Against G2, third part ("agreement with gevolution in the weak-field regime"): NOT met.
Under decision 0010 and charter point 5 the comparison is with published results and
with this repository's own Newtonian reference (to be built in AthenaK by core). The
brief's own reference for this row, arXiv:2003.08014 (Adamek, Barrera-Hinojosa, Bruni,
Li, Macpherson, Mertens, "Numerical solutions to Einstein's equations in a
shearing-dust Universe: a code comparison"), compares gevolution, GRAMSES, the Einstein
Toolkit (fluid) and CosmoGRaPH (particles) on one test, so it covers all three codes of
the row at once [VERIFIED, `draft.tex` lines 41, 285]:
- initial data in closed form: alpha = 1, beta = 0, a flat spatial metric in sheared
  coordinates and K_ij depending on y only, dust density and u^x from the constraints
  (`draft.tex` lines 142-182);
- the numerical-relativity codes use a "harmonic" slicing with zero shift whose linear
  solution has alpha = t^2/t*^2 with t conformal time and a proportional to t^2
  (lines 235-242, 321, 328), i.e. alpha = a as in this code [VERIFIED for the paper's
  statement; that its lapse equation is the one of this code (f = 1/3) is TO VERIFY];
- observable: the angle between two light rays arriving at an observer, cos(theta)
  (lines 224-229), with a closed-form linear prediction (line 262);
- grid: H*L = 2^n, n = -7 ... 2, b = {0.005, 0.05, 0.5} H*^2 L^2 (line 287);
- results: all codes within 0.03 % of linear theory for b = 0.005 H*^2 L^2 (line 348),
  within 0.1 % and 1 % for the two larger amplitudes in sub-horizon boxes (line 383);
  at H*L = 4, b = 0.5 H*^2 L^2 the departures from linear theory are -0.619
  (gevolution), -0.68 (GRAMSES), -0.8183 +- 0.0004 (CosmoGRaPH) (line 360).
[JUDGEMENT] It needs no new simulation capability here: the substitution
x' = x + (b / 2 pi H*) sin(2 pi y / L) turns the initial metric into delta_ij (psi = 1),
is periodic, and leaves K_ij to transform with the Jacobian, so `nrpic_cosmo` with
`id = file` can take it; particles carry rho0* and u^x; light rays exist (C3). Open
[TO VERIFY]: the sign conventions of K_ij, the parallel transport of the first arrival
along the observer's worldline (line 270), and whether a lattice of one particle per
cell is enough (CosmoGRaPH used N_y^2/8 particles in a one-dimensional box, line 328).

## 4. G1 criteria of the Track B sheet

- "the two diagnostics agree on analytic linear waves": B-pre-3, other packages of
  this worktree (`tracks/B-emd-gw/gw_diag/`, `tracks/B-emd-gw/periodic_z4c/`); not
  assessed here.
- "the Newtonian baseline reproduces the scaling of the literature": B-pre-4, package
  `tracks/B-emd-gw/baseline/`; not assessed here. Note: `cosmo/newton/pm.py` is a Python
  particle-mesh code that predates decision 0010; this package uses it only as the
  reference its task names (consequence 3 of decision 0010 moves Newtonian baselines into
  AthenaK's Newtonian mode once core has built it).
- "background error and constraint convergence with the stand-in matter": the
  stand-in fluid of B-pre-2 was never run; the particle background it stood in for is
  measured directly (section 1). Constraint convergence on the background: H_r of
  test A0 at t = 100 Mpc/h is 1.6e-9, 1.1e-10, 3.2e-11 at 8, 16, 32 cells
  (`daverio_a.json`) [VERIFIED]; in the production random-field runs the mean H_r at
  z = 100 is 2.5e-8, 2.3e-8, 1.0e-8 at 32, 64, 128 cells (TESTLOG lines 1648-1650)
  [VERIFIED (log)], i.e. not convergent there: a floor from the step on the
  background and the second-order terms. [JUDGEMENT] The stand-in-matter item is
  superseded and should be struck from G1 by the lead (request below).

## 5. B-pre-2 and B-pre-5 item by item

| Item | State in `cosmo/` | Missing |
|---|---|---|
| B-pre-2 cosmological gauge | conformal-time Bona-Masso slicing (f = 1/3 on Khat), zero shift; alternatives `lapse_volume`, `lapse_kdriver` built and tested for collapse (TESTLOG lines 339-360, 494-516, 563-631) | a gauge that survives collapse to a black hole in an expanding box (E1, open; not needed for S2 before G3) |
| B-pre-2 FLRW reference-metric factoring (arXiv:1704.04307 and others) | not done; the full metric is evolved, background errors 1e-7 (section 1) | [JUDGEMENT] not needed at this error level |
| B-pre-2 FLRW with stand-in fluid | not done | superseded by the particle runs |
| B-pre-5 constraint-solved periodic data | `cosmo/ic/cosmo_id.py`: Hamiltonian and momentum constraints on the torus for fixed particles and given K, Fourier solve for psi and the vector potential of Ahat; the mean of the momentum source is removed (integrability on the torus) and the Hamiltonian problem is uniquely solvable because the density scales with psi (`cosmo/PLAN.md`, Decisions). Code's own constraints at t = 0: 6e-10 and 8e-10 (TESTLOG line 119); this package's data: largest residuals 2.9e-10 (Hamiltonian) and 2.4e-8 (momentum) | CTTK scheme for a fluid source (arXiv:2207.03125, 2501.13046): not done; nonlinear horizon-scale data move into the code (decision 0010, consequence 4) |

## 6. Plane-symmetric pancake through shell crossing (part ii of this package)

See `JOURNAL.md` for predictions and outcomes and `README.md` for how to rerun. Results
are filled in below once all runs have finished.

PANCAKE_RESULTS

## 7. What is missing against the criteria (summary)

1. FLRW: a homogeneous run in the full production configuration over a thousandfold
   expansion at two or three meshes, and at 1, 8, 27 particles per cell with position
   noise (particle-number convergence of the scale-factor error). Minutes on a card.
2. Growth: the growth rate f(a) extracted from test B and the random field; test B in
   the production configuration at 1, 8, 27 particles per cell at fixed mesh and at
   32, 64, 128 cells with the step limit 0.002 (so that the background step does not
   mask the mesh error); one start from a glass or Poisson distribution for the particle
   noise the row names.
3. Multi-code: the shearing-dust test of arXiv:2003.08014 (section 3) on its grid, at
   least b = 0.005 and 0.05 H*^2 L^2 for H*L = 1/4 to 4, against the published linear
   prediction and code results; until AthenaK has a Newtonian mode, the PM reference
   of `cosmo/newton` for the Newtonian side.
4. Pancake: see section 6.
