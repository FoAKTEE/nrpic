# SCOPE of Track D (S4): black-hole growth and dark-matter dress, G0

Status: G0 scoping material, written 2026-11-15 by a helper of D-bh-dress for the lead.
Units G = c = 1, M the initial black-hole mass, eps = H_i M the initial Hubble rate in
units of the hole. Labels as in the brief: [VERIFIED] (source and locator given),
[BACKGROUND], [JUDGEMENT], [TO VERIFY]. Locators of papers are in `REFERENCES.md`; numbers
from the scoping calculation carry its run id `D-bh-dress-20261115-120304-795eee9`
(output `scratch/D-bh-dress/D-bh-dress-20261115-120304-795eee9/scoping_table.txt`,
figure `figs/scoping_estimates.png`).

## 1. Problem

Brief S4 (lines 394-405), sheet 9.7 (lines 766-783), criteria N1, N4, K1, K3 (line 304).
Three questions, in this order:

1. Growth law. How does a black hole in a matter-dominated, collisionless medium grow?
   Observable: the apparent-horizon mass M_AH against the scale factor a measured by
   distant dust, and against the matter that crosses the horizon.
2. Spike. What is the density profile of the bound (non-captured) dark matter around the
   hole in the strong field, r < 10-50 M, where the probe-limit results
   (arXiv:1305.2619, 1707.06302) and the Newtonian self-similar results
   (arXiv:1901.08528, 2106.07480) stop being valid (2106.07480 says so itself,
   `sections/conclusion.tex:20`)?
3. Null test of "cosmological coupling" (section 3): does the horizon mass of an
   ordinary black hole change with a beyond accretion?

Later (after G3, with F): dressed black-hole binaries, initial data for dressed holes
(sheet line 781).

What is new against the literature [JUDGEMENT]: the existing dress calculations are
Newtonian N-body (1901.08528 `:297`, 1805.09034 `:568`) or semi-analytic; the existing
full-NR growth calculations use fluids or scalar fields (2608.13206, 2109.04896). A
3+1 evolution with collisionless particles and a black hole in an expanding medium was
not found in what was read (the brief's own [TO VERIFY] at line 235 stands).

## 2. What exists and what Track D needs (decision 0010: all simulation in AthenaK)

| Need | State | Locator |
|---|---|---|
| Puncture data, moving-puncture gauge, corrected horizon finder (`metric_drvts = interpolant`) | on main | `athenak/src/pgen/nrpic/nrpic_cf.cpp:15`; docs/TESTLOG.md:334-365 |
| Particles on the evolved metric, deposition, removal at a lapse threshold and inside 0.8 of a found horizon | on main | docs/TESTLOG.md:1971-2053 |
| Spherical data with extrinsic curvature (table format 2, superposes with punctures) | branch `core/id-extrinsic`, not on main | interface `coord/INTERFACES/spherical_id_format2.md`; commits 408df57, c9aa6d2, 1311b8e |
| The vacuum-bubble slice (D-pre-1): table plus puncture | orchestrator's construction, to be re-derived by D | `coord/notes/derivations_to_check.md:38-53`; `coord/notes/design_wave2_initial_data.md:88` |
| Newtonian mode of the particle module (D-pre-3 baselines) | branch `core/newton`, not on main | commits 728637a, fee90ca |
| Periodic domain, conformal-time lapse (periodic version of the null test) | on main | `cosmo/README.md`; owner of the gauge: B |
| Puncture on the torus (constraint solve with a puncture in a periodic box) | does not exist | request to core (README.md, Requests) |
| Probe-limit geodesics on fixed Kerr (D-pre-2) | on main (`nrpic_geodesic`, analytic metric) | docs/results_cluster_test.md:89-113 |

One global time step for the whole mesh (no time subcycling found in `athenak/src`;
`z4c/z4c_newdt.cpp:26-58`): the finest cell at the puncture sets the step everywhere,
which is the main cost driver of long runs (section 7).

## 3. The null test, worded

### 3.1 The statement tested
For a black hole without interior matter (a moving puncture: Schwarzschild, later Kerr,
geometry with no matter inside the horizon) embedded in an expanding, pressureless,
collisionless medium and evolved with the full Einstein equations in 3+1 dimensions
without imposed symmetry, the horizon mass changes only through the matter that crosses
the horizon.

### 3.2 What is measured
- M_AH = (A_AH / 16 pi)^(1/2) (irreducible mass; with spin the Christodoulou mass), from
  the finder with the production settings (docs/TESTLOG.md:378-385: finder against slice
  3e-4 at production settings, below 1e-4 tightened).
- a(t): areal radius of comoving dust shells far from the hole against the proper time of
  their particles, compared with the exact marginally bound solution
  R = R_i (1 + (3/2) H_i tau)^(2/3) (`coord/notes/derivations_to_check.md:9-23`);
  coordinate time is not used.
- Delta M_in(t): energy that crossed the horizon, two independent definitions
  (a) the sum over removed particles of m E with E = -u_t evaluated where each particle
  crosses a sphere r_s = 6-10 M in the late, nearly stationary gauge, (b) the change of
  the Misner-Sharp mass on that sphere minus the flux through it. Their difference is
  quoted as a systematic. In the vacuum-bubble case Delta M_in = 0 by construction.
- k_eff = Delta ln[M_AH - Delta M_in] / Delta ln a over the run; reported as
  k_eff +- sigma_k (three resolutions and the noise floor of D-pre-4) and an upper limit
  |k| < k_95.

### 3.3 Expected size of the numbers
- Coupling hypotheses: k = 3 (vacuum-energy interiors, 2302.07878 `:132-133`), k = 1
  (regular black holes, 2306.11588 `:67`), k = 0 for Kerr (2302.07878 `:132`). One
  doubling of a separates k = 1 from k = 0 by Delta ln M = 0.69.
- Definitional drift of the area mass in a non-vacuum neighbourhood: McVittie gives
  d ln M_AH / d ln a = -12 (m H)^2 [JUDGEMENT, REFERENCES.md section 2], -1.2e-3 at
  eps = 0.01 and -1.1e-2 at eps = 0.03 (run D-bh-dress-20261115-120304-795eee9, Part B).
  Inside an exact vacuum bubble this term is absent.
- Numerical floor: vacuum puncture slice-mass error at t = 50 M of 3.9e-2, 1.5e-3, 1.4e-5
  at dx = M/4, M/8, M/16 (docs/TESTLOG.md:384-385; the M/4 value at the horizon is
  -3.4e-2, :1029-1031). The long-time drift with the corrected finder has not been
  measured (the 2.2e-5 per M of TESTLOG:205 came from the defective finder and is
  withdrawn, TESTLOG:363-365): that is D-pre-4. With matter the drift is larger: after a
  collapse the horizon mass moved 0.7 percent in 15 M with the adaptive cloud level and
  stayed within 0.2 percent with clouds at the finest level (TESTLOG:678-688, 732-744).
- So the test is not limited by precision against k = 1 or 3: even a 1 percent floor gives
  |k| < 0.015 over one doubling [JUDGEMENT]. Its value lies in the control of systematics.

### 3.4 What an upper limit would show
1. That the method (Z4c plus particles, puncture gauge, finder, removal) produces no
   spurious coupling above k_95: a code result, and the G2 criterion of the sheet.
2. That a vacuum black hole in an expanding particle medium, evolved without symmetry
   assumptions, behaves as the exact solutions say it must (Birkhoff inside the vacuum
   bubble; McVittie, Kottler, Kerr-de Sitter: 2308.07374 `:370-381`, `:701-704`).
3. Only in the periodic version (cosmological boundary conditions, a dust-filled torus
   with a hole), that this black-hole model does not show the growth that 2302.07878
   `:100-101` attributes to "black hole models with realistic behaviour at infinity". The
   expanding-ball version has a vacuum (Schwarzschild) exterior and is asymptotically
   flat, so it cannot speak to that boundary-condition argument.

### 3.5 What it would not show
1. Nothing about black holes with non-vacuum interiors (regular black holes,
   gravastars, vacuum-energy cores), which are the object of the hypothesis
   (2302.07878 `:157-160`, `:170-174`; 2306.11588 `:67`). A puncture has no interior
   matter, and the claim's authors themselves assign k = 0 to Kerr (2302.07878 `:132`):
   the null result is predicted by both sides and does not test the observational claim.
2. Nothing about the averaging argument that links coupling to dark energy (Croker and
   Weiner 2019; criticised in 2304.09817 `:120-121`): the test measures a local horizon,
   not the source term of the averaged Friedmann equation.
3. Nothing about observed supermassive black holes (accretion and merger histories,
   2302.07878 data; 2302.12386, 2305.01307).
4. Nothing beyond its range: eps <= 0.1, a_f/a_i <= 4 (G2) or 10 (G3), no Lambda,
   pressureless matter.

### 3.6 Sentence for notes and papers (proposed)
"For a vacuum black hole embedded in an expanding collisionless medium we find no change
of the apparent-horizon mass beyond the matter that crosses the horizon, |k| < k_95 over
a_f/a_i = X. This is what Birkhoff's theorem and the known exact solutions imply; it is a
test of the numerical method and of this black-hole model, not of the cosmological-coupling
hypothesis for black holes with non-vacuum interiors."

## 4. Parameter ranges

From run D-bh-dress-20261115-120304-795eee9 (Newtonian shells around a point mass in
Einstein-de Sitter; `scoping_table.txt`):
- The background mass that has turned around grows as M_b,ta = 0.5648 M (a/a_i) only
  asymptotically ((4/(3 pi))^(2/3); within 1 percent from a/a_i = 121.5 on); at
  a/a_i = 2, 4, 10 the coefficient is 0.263, 0.407 ((2.628 - 1)/4), 0.500. Turned
  around (hole included): 1.525 M at a/a_i = 2 and 2.63 M at 4, for every eps.
- Turnaround radius r_ta at a/a_i = 2 (4): 74.6 (187) M at eps = 0.003, 33.4 (83.9) M at
  0.01, 16.1 (40.3) M at 0.03, 7.2 (18.1) M at 0.1. Slope d ln r_ta / d ln a = 1.3331 and
  frozen-in density slope -2.2503 at a/a_i = 1000.
- Einstein-Straus wall (dust mass removed = M) R_w = (2/eps^2)^(1/3) M: 60.6, 27.1, 13.0,
  5.8 M; wall speed (2 eps)^(1/3): 0.18, 0.27, 0.39, 0.58; Hubble radius 1/eps.
- Run length per factor in a: T = (2/(3 eps)) [(a_f/a_i)^(3/2) - 1]: 122 M (a doubling) and
  467 M (a quadrupling) at eps = 0.01; 41 and 156 M at 0.03; 12 and 47 M at 0.1.

| Parameter | Range | Reason |
|---|---|---|
| eps = H_i M | 0.01-0.03 (G2); 0.003-0.1 (G3 scan) | 2109.04896 `:58`, `:99`: a black hole formed in a matter era has H M ~ 1e-2. Smaller eps costs 1/eps in run time; eps = 0.1 puts the wall at H R = 0.58 and the dust shell (1.5 R_w) at H R = 0.88, near the anti-trapped limit H R < 1 (`derivations_to_check.md:23`) |
| a_f/a_i | 2 (G2), 4 (G2 with matter, G3), 10 (G3 at eps >= 0.03) | cost (section 7) |
| Dust region | thick comoving shell R_w < R < 1.5 R_w (vacuum bubble), or filled to the hole | marginally bound shells evolve independently [JUDGEMENT from the LTB form, `derivations_to_check.md:9-23`] |
| dx at the puncture | M/16, M/32, M/64 | slice mass at 50 M: 1.5e-3 (M/8), 1.4e-5 (M/16), TESTLOG:384-385 |
| dx over the dust | 1-2 M | the ball's curvature scale is 1/H >= 33 M; core's expanding-ball test: areal-radius error 3.3e-3, 1.1e-3, 4.6e-4 at dx = 1, 1/2, 1/4 M (commit 1311b8e) |
| Particles N | 1e5-4e6 in the dust | memory: block limit 2280 per card used so far (TESTLOG:2037); particle cost 1.2e-7 s per particle-step (run, Part C) |
| Velocity dispersion sigma (tangential, at turnaround) | 0 (growth law, null test with matter); 0.03-0.1 (spike) | see the next paragraph |
| Spin a/M | 0 (G2); 0.5, 0.9 (G3, spike) | 1707.06302 |
| Lapse | conformal-time or 1+log with care | core test 2 (1311b8e): with 1+log a lapse front from a sharp ball surface reaches the centre |

Accretion against dress [JUDGEMENT, to be checked in D-pre-3]: a particle that falls
from turnaround with E close to 1 is captured if L < L_c = 4 M (1305.2619 `:120`, `:381`).
At r_ta = 16-34 M (one doubling at eps = 0.03-0.01) this needs a tangential speed above
4 M / r_ta = 0.12-0.25 at turnaround, comparable to the circular speed there
((1.5 M / r_ta)^(1/2) = 0.21-0.31). Cold dust is therefore swallowed almost entirely in the
full-NR regime: the cold runs measure the growth law, and a bound spike needs either a
relativistic dispersion (sigma ~ 0.05-0.1) or tidal torques from a non-spherical
environment. In the Newtonian self-similar regime (r_ta >> M) the same capture cone is
negligible, which is why the r^(-9/4) dress of 1901.08528 and the strong-field spike are
different regimes. Expected cold growth law, Newtonian radial infall without shell
crossing before capture: a shell is captured near 2^(2/3) times the scale factor of its
turnaround, so M_BH - M -> 0.5648 / 2^(2/3) (a/a_i) M = 0.356 (a/a_i) M at large a/a_i
[JUDGEMENT, derived here, to be computed in D-pre-3 with the transient].

## 5. Exit criteria

G0 (this package): references read with locators, wording of the null test, ranges,
criteria, test plan, risks and compute estimate written; one scoping run registered.

G1 (sheet line 779; numbers proposed here):
- D-pre-1: derivation re-derived independently (symbolic); the format-2 table plus
  puncture has Hamiltonian and momentum residuals that converge at the order of the
  differencing over three resolutions, except at the wall if it is sharp (core test 2,
  1311b8e: a sharp surface leaves a non-converging residual; a smooth wall profile is the
  fallback and its effect on the interior mass is bounded); Misner-Sharp mass at the wall
  equal to M to 1e-6; no anti-trapped surface between throat and wall.
- D-pre-2: probe-limit density from integrated geodesics (AthenaK `nrpic_geodesic` with
  the analytic metric, and an independent phase-space quadrature) vanishes at r = 4 M for
  Schwarzschild; constant distribution function: peak ratio to Gondolo-Silk 3 and the
  "8Gm -> 4Gm" curve 15 percent above (1305.2619 `:443`); Kerr qualitatively as 1707.06302
  (numbers to be extracted).
- D-pre-3: semi-analytic self-similar solution: coefficient 0.5648 and slopes 4/3, -9/4
  (turnaround part done here); post-turnaround normalisation against 1901.08528 (+53
  percent, `:468`) and Bertschinger 1985 [TO VERIFY]; capture fraction against sigma; the
  same in AthenaK's Newtonian mode when it is on main: slope -9/4 +- 0.05 between 2 dx and
  r_ta/2.
- D-pre-4: noise floor: |M_AH(t)/M_AH(t_0) - 1| for t_0 = 50 M to t_0 + 450 M at M/8 and
  M/16 (and M/32 to 250 M), production finder settings, with its convergence order;
  converted to k_floor(eps, a_f) = Delta ln M_noise / ln(a_f/a_i).

G2 (sheet line 779):
- Vacuum bubble: |Delta ln M_AH| over a_f/a_i = 2 at eps = 0.03 (and 0.01) not above the
  D-pre-4 floor for the same resolution and duration, at three resolutions, converging;
  the innermost dust shell follows the exact R(tau) to 1e-3; no particle enters the bubble.
- With matter (cold dust filling the bubble from 2-4 M outward): M_AH(t) - M_AH(t_0) equal
  to Delta M_in(t) within max(3 sigma_noise, 1 percent of Delta M_in), both definitions of
  Delta M_in; rest-mass bookkeeping (sum m + removed = initial) to 1e-12.
- Relaxation control: capture rate and spike profile unchanged between N and 4N.

G3 (sheet line 779): three-resolution convergence of the growth law M_AH(a) and of the
spike profile with an observed order; growth law compared with the Newtonian cold-infall
expectation (section 4) and a Zel'dovich-Novikov-type fit (2608.13206 `:457-471`); the
null-test upper limit k_95 with the wording of section 3.6.

## 6. Test plan against brief section 10

Rows Track D owns:

| Row (brief line) | Track D test | Reference | Runs and cost |
|---|---|---|---|
| Self-similar secondary infall (854) | D-pre-3: shells and orbits (semi-analytic, outside `athenak/src`), then AthenaK Newtonian mode, then a low-eps full-NR run | Bertschinger 1985 [TO VERIFY]; 1901.08528; run D-bh-dress-20261115-120304-795eee9 | processors; Newtonian mode on a card under 0.5 card-hour [JUDGEMENT] |
| Black hole in a vacuum bubble (855) | D-pre-1 offline, then G2 vacuum-bubble runs | exact (Birkhoff inside the bubble), `derivations_to_check.md:38-53` | 2.2 card-hours (eps = 0.03, three resolutions), section 7 |

Rows Track D depends on (owner in brackets):

| Row (line) | What Track D takes from it |
|---|---|
| Geodesics on a fixed background (840, CORE) | D-pre-2 pusher accuracy; measured invariants on mesh metric: E 1.2e-7, L_z 5e-6 median after 1000 M (docs/results_cluster_test.md:136-150) |
| Oppenheimer-Snyder and its time reverse (841, CORE, A) | expanding-ball data and gauge (core test 2, 1311b8e); the dust region of D-pre-1 is its marginally bound case |
| Lemaitre-Tolman-Bondi dust (850, A) | the shell outside the bubble is marginally bound LTB |
| Einstein-Vlasov steady states (843, CORE, C) | long-time phase-space fidelity: the measured relaxation of 1e2-1e4-particle clusters (section 8) |
| FLRW dust, growth of linear perturbations (845-846, B) | the periodic version: gauge, time step, particle noise |

## 7. Compute estimate (run D-bh-dress-20261115-120304-795eee9, Part C)

Model: card-seconds = blocks x 4096 x cycles / R + N x cycles x c_p, cycles = T / (0.25 dx_min).
Measured anchors: vacuum puncture with static refinement, 288 / 344 / 400 blocks at
dx_min = M/4 / M/8 / M/16, 2.08 / 4.71 / 11.46 s per M, R = 9.27e6 zone-cycles/s
(`runs/puncture/hcal/*/athena.log`); the two-overdensity production run with matter, AMR
and three horizons, 3.05e7 block-cycles in 19476 s, R = 6.4e6, which is 1.45 times slower
than the vacuum rate (`runs/jeans/n1e4_v19/chain/seg*.log`); particle cost
c_p = 1.2e-7 s per particle-step from the periodic run with 64^3 cells and 64^3 particles
(`runs/cosmo/east_d0.01_n64_pcs/athena.20261114-012440.log`, against the Z4c rate
2.0e7 of docs/TESTLOG.md:46; an upper estimate). The model reproduces its own anchors by
construction; its spread between vacuum and matter runs is the factor 1.45.

| Package | Configuration | Card-hours |
|---|---|---|
| D-pre-4 | vacuum puncture, 500 M at M/8 and M/16, 250 M at M/32 | 0.90 + 2.01 + 2.0 (*) = 4.9 |
| D-pre-2 | test particles, analytic Kerr: 1.1e8 particle-steps/s (results_cluster_test.md:278) | < 0.1 (or processors) |
| D-pre-1, D-pre-3 | offline, semi-analytic | 0 (processors) |
| G1 total | | about 5 |
| G2 vacuum bubble | eps = 0.03, a x 2, dx_ball = 2 M, 1e6 particles, M/16 + M/32 + M/64 | 0.27 + 0.59 + 1.29 = 2.2 |
| G2 vacuum bubble | eps = 0.01, a x 2, dx_ball = 2 M, M/16 + M/32 | 1.08 + 2.32 = 3.4 |
| G2 with matter | eps = 0.03, a x 4, dx_ball = 2 M, M/16 + M/32 | 1.33 + 2.86 = 4.2 |
| G2 relaxation control | the matter run with 4e6 particles, M/16 (mesh 1.0, particles 1.3) | 2.3 (*) |
| G2 total | | about 12 |

(*) the same model evaluated by hand for this configuration, not a row of the run's
table [JUDGEMENT].

G1 plus G2 is about 17 card-hours against the 30 GPU-hours to the next gate of decision
0006, with a model uncertainty of a factor 1.5. Out of reach for G2: eps = 0.01 with a x 4
(14-60 card-hours, and 2500 blocks, above the 2280 per card used so far, TESTLOG:2037).
Retries for failed runs are not included.

## 8. Risks

| Risk | Measured evidence | Effect on D | Response |
|---|---|---|---|
| Particle resolution near the puncture | Matter left near a puncture produced non-finite cells within two cells of it at M/64 (TESTLOG:1949-1969); removal inside 0.8 of a found horizon cured it, the lapse rule alone did not, because the lapse at cell centres next to the puncture stays at 0.02-0.05 (TESTLOG:1971-1989, 2039-2053). Density noise: relative L2 noise 0.24-0.28 at about 1.1 particles per occupied cell, falling as N^(-1/2) (results_cluster_test.md:215-235). For a r^(-9/4) dress, N(<r) = N_d (r/r_ta)^(3/4): with N_d = 1e5 and r_ta = 33 M, 4.1e4 particles inside 10 M spread over 1.7e7 cells of M/16, 2.4e-3 per cell [JUDGEMENT, arithmetic] | the source next to the hole is pure noise unless deposited on coarser cells; coarser clouds near a forming hole made the horizon mass drift by 0.7 percent in 15 M (TESTLOG:678-688, 732-744) | horizon-based removal on from the first search; clouds limited to at most one level coarser (`deposit_max_coarsen`, TESTLOG:756-763) and the limit scanned; N scan; request to core: particle splitting near the hole (G3) |
| Numerical relaxation of the dress | Self-gravitating stable cluster (period about 72 M, TESTLOG:557-558): 1e2 particles do not hold within one period (TESTLOG:690-695, 998-1001); 1e3 follow 1e4 to 190 M and then drift (TESTLOG:996-997); 1e4 stay bound for 1200 M with a bounded 2-3 percent lapse oscillation (TESTLOG:1006-1022). Test particles on a fixed mesh metric (no self-gravity): no growing error in E (median 1.2e-7 flat) and L_z levelling at 5e-6 over 1000 M (results_cluster_test.md:140-150), 20 times larger for pericentres below 4-5 M (:151-155); the mesh-metric error changed the fate of 7 of 1e4 marginal orbits in 500 M (:263-268) | loss-cone refilling by noise means spurious accretion; relaxation flattens the spike. In the dress the potential is the hole's, so the cluster numbers, where self-gravity dominates, overstate the relaxation by about M_dress(<r)/M [JUDGEMENT] | G2 relaxation control (N and 4N); the capture count compared with the exact capture condition per particle (as in results_cluster_test.md:256-259); keep N_dress >= 1e5 |
| Definition of the accreted energy | none yet | the null test with matter depends on it | two definitions, difference quoted as a systematic (section 3.2) |
| Sharp wall of the vacuum bubble | core test 2 (1311b8e): a sharp ball surface leaves a constraint residual that does not converge | constraint violation at the wall could leak inward | smooth wall over a few cells; check that the interior mass is unchanged |
| Gauge | core test 2: with 1+log a lapse front from the surface reaches the centre at t = 5.5 M for R_b = 10 M | horizon mass and finder during the transient | conformal-time lapse in the dust, puncture gauge near the hole; compare two gauges for M_AH (gauge-invariant up to the slicing of the horizon) |
| Outer boundary | core test 2: outflow condition violated by the r^(-3/2) fall-off of K_ij; boundary out of causal contact needs L >= 0.71 T (TESTLOG:2098-2100) | spurious waves reach the hole | domain sized in section 7 |
| Finder | block-face defect fixed (TESTLOG:334-365); 3e-4 against the slice at production settings | noise floor | production settings fixed in D-pre-4 and kept |
| Remnant above the total mass in the two-overdensity run, 2.5 percent, cause not determined (TESTLOG:2190-2195) | | the same unexplained excess could appear in a growth-law run | initial data that satisfy the momentum constraint (design note, section 3); watch the Misner-Sharp mass far out |
| Wording of the null result | 2302.07878 `:132` | over-claiming | section 3.5 and 3.6 wording, reviewed by a second agent |
| Physical regime of the dress | section 4 (capture cone at r_ta ~ 10-100 M) | cold runs give no spike | dispersion scan; the spike is a G3 item |

## 9. Order of work

1. G1 in parallel: D-pre-1 (derivation and table, processors), D-pre-3 (semi-analytic,
   processors), D-pre-2 (geodesics, processors or under 0.1 card-hour), D-pre-4 (about
   5 card-hours, no new code).
2. G2 needs `core/id-extrinsic` on main (or a pinned build of it) and the D-pre-1 table.
3. The periodic version needs a puncture on the torus (core) and B's gauge; it is the
   only version that speaks to the boundary-condition argument (section 3.4, item 3).
