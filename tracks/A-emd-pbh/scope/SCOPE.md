# S1 scoping: primordial black holes from collisionless collapse in an early matter era

Track A (owner A-emd-pbh), gate G0, helper "scope", 2026-11-15. Status: draft for the
lead. Evidence labels: [VERIFIED] read at a locator or computed in a registered run,
[BACKGROUND] standard result not checked here, [JUDGEMENT] our design or inference,
[TO VERIFY] open. Reference statements and their locators: `REFERENCES.md`. Numbers
computed here come from run `A-emd-pbh-20261115-112625-e854f12` (script `scope_calc.py`,
outputs in `results/`, predictions and outcomes in `JOURNAL.md`, tests T1-T5).

One code base (decision 0010): every run below is an AthenaK run of this repository.
Outside `athenak/src/` this track writes only the exact and semi-analytic references,
the analysis and the specifications; capabilities that do not exist yet are requested
from core (README.md, Requests).

## 1. Problem statement

Pressureless, collisionless matter in an expanding background: when does an overdensity
of given amplitude, shape and velocity dispersion form a black hole, with what mass and
spin, and what does it radiate? In the matter era there is no Jeans length: a uniform
spherical overdensity collapses to a black hole for any amplitude (arXiv:2507.18312,
Main.tex L310) [VERIFIED as statement], so a threshold exists only because something
halts the collapse before the matter is inside 2M: non-sphericity (pancake, hoop
conjecture), inhomogeneity of the profile (shell crossing), velocity dispersion, angular
momentum, or the end of the matter era. The analytic estimates disagree with each other
and with the one full-relativity particle calculation (REFERENCES.md, last section).
S1 asks for the answer from converged full-GR Einstein-Vlasov runs:

1. the threshold line A_c(e) in amplitude against ellipticity (p = 0, no dispersion),
   then its dependence on prolateness p and on the initial dispersion s;
2. the black-hole mass at formation and its growth; direct against accretion-driven
   formation (arXiv:2109.04896);
3. the spin at formation and after accretion (predictions from near-extremal,
   arXiv:1707.03595 L81-86, to ~sigma^(1/2), arXiv:2508.10070 L680);
4. the waveform from the metric against the quadrupole estimate (arXiv:2605.04487);
5. later: two neighbouring peaks.

Minimum publishable unit (brief S1): items 1 and 3 with the mass and one waveform, and
the comparison with arXiv:2609.14218 and arXiv:1609.01588.

## 2. Position against arXiv:2609.14218

What it did [VERIFIED, REFERENCES.md]: BSSN, long-wavelength growing-mode data for a
Gaussian curvature peak with ellipticity, one octant at 80 points per direction with
scale-up coordinates; dust fluid scan in e at p = 0; particle runs (lattice, unequal
masses, cubic cloud) at e = 0.2 only, giving horizons for mu >= 0.05 and none for
mu <= 0.045, against the Zel'dovich-hoop value mu > 0.45 at e = 0.2 (our reproduction:
h-hat(0.2, 0) = 0.452, T1). Not done there: horizon mass, spin, waves, any convergence
study, p != 0, dispersion, anything after formation; the particle runs violate the
Hamiltonian constraint strongly where particles cross (MDPBH.tex L1148-1186).

What we add [JUDGEMENT]: convergence in particle number, mesh spacing and box (or ball)
size; a constraint-damped formulation (Z4c) and an apparent-horizon finder with mass and
spin; evolution through formation and accretion; p and dispersion axes; waveforms; the
threshold definition of section 3, fixed before the runs.

Four hypotheses for their low particle threshold, each with the run that decides it:

- H1 (run length). Their plotted particle runs end at 250 t_H, and the collapse time
  grows as mu^(-3/2): the read-off lapse-collapse times sit at 0.80-1.01 of the top-hat
  collapse time of the compaction shell for mu <= 0.15 (slope -1.31), and the amplitude
  whose collapse time is 250 t_H is mu_fd = 0.048 (0.044 with the measured ratio), inside
  their bracket (0.045, 0.05] (T2) [VERIFIED as arithmetic; the reading is JUDGEMENT].
  If H1 holds, mu = 0.045 forms a horizon near 0.86 t_c(r_m) = 239 t_H and mu = 0.04 near
  285 t_H; if it fails (a halted halo), no horizon by 400 t_H and the central density and
  lapse return. Decided by the same data run to 400 t_H (phase 1, two runs).
- H2 (constraint violation). The black holes below the hoop line are produced by the
  constraint violation at particle crossings. Decided by the same runs at two mesh
  spacings with constraint damping on and off: a physical outcome does not depend on it.
- H3 (resolution). One cell per particle and a cell-sized cloud smooth the pancake; a
  halted pancake needs its thickness resolved. Decided by the three-way convergence of the
  outcome at mu = 0.1, e = 0.2.
- H4 (shell crossing). arXiv:2507.18312 (L234-242) says a typical spherical peak does not
  form a black hole after its centre shell-crosses unless delta ~ 1; arXiv:2609.14218 has
  mu_c = 0.33 from the LTB nakedness argument at e = 0 (L766-768) but particle black holes
  at mu = 0.05 for e = 0.2. Decided by spherical particle runs (e = 0) at mu = 0.2, 0.3,
  0.35, 0.5 continued well past the central shell crossing.

Overlap risk: the authors announce work on the high-density regime (MDPBH.tex L1218).

## 3. Definition of the threshold (pressureless case), fixed before any run

Amplitude. For the profile of arXiv:2609.14218: mu. In general: deltabar_ent, the
linear-theory mean density contrast inside the comoving compaction radius r_m,
extrapolated in the growing mode to the epoch r_m a H = 1 (the paper's horizon entry,
L709-714). For that profile deltabar_ent = (12/(5 e_E)) mu = 0.883 mu, e_E Euler's
number (T2, checked to 2e-4). Equivalent invariant: compactness at turnaround of the
top-hat shell, 2M/R_ta = (5/3) deltabar_ent (arXiv:2507.18312 L304-316).

Time. Cosmic time of the background in units of t_H, the time at r_m a H = 1 (for the
ball: the proper time of comoving particles in its unperturbed outer layers; for the
periodic box: the background time integrated from the volume-averaged expansion,
H = -<K>/3, along the box-averaged lapse).

Outcome of one run at amplitude A with end time t_end:
- BH: an apparent horizon is found at t_AH <= t_end in at least three consecutive searches
  spanning at least 5 M_AH, with the L2 norm of the Hamiltonian constraint outside the
  horizon below 0.1 of the L2 norm of 16 pi E over the same region at t_AH;
- NO-BH: no horizon to t_end and the same constraint bound holds to t_end; sub-labels
  "halted" (the Lagrangian radius of the inner half of the perturbation mass has passed a
  minimum and grows again) and "late" (still contracting at t_end);
- UNDECIDED: the run ends or breaks the constraint bound before t_end without a horizon.
  It does not enter a bracket and is reported (unlike the "crash w/o HF" class of
  arXiv:2609.14218).

Threshold. A_c(e, p, s; t_end) lies in (A_lo, A_hi]: A_lo the largest NO-BH, A_hi the
smallest BH, bisected in ln A to A_hi/A_lo <= 1.1. If outcomes are not monotone in A the
set is reported and no threshold is quoted. Primary t_end = 250 t_H (the length of the
particle runs of arXiv:2609.14218, for the comparison); every BH run records t_AH, so
A_c(t_end') for t_end' < t_end follows from the same runs; the NO-BH run just below A_c
is continued to 1000 t_H or to the halt plus 0.3 t_c. The finite-duration part is the
known cutoff delta_fd = (t_H/t_end)^(2/3) (arXiv:1707.03595 L925); the result is stated
as A_c(t_end) together with this cutoff, and only the part above the cutoff is attributed
to the halting physics.

Converged. A_c is quoted when its bracket at (N, dx, size) overlaps the brackets at 4N
(lattice), dx/2 and 4/3 of the ball radius or box size.

## 4. Set-ups

Phase 1, periodic box: the initial data of arXiv:2609.14218 (analytic long-wavelength
geometry, E and J from the constraints, MDPBH.tex L509-547), in a periodic box of side
2L, L = 10/k, H_i = 5k, start at a = a_H/150 (L549, L709-719), particles on a lattice with
the paper's mass rule and, as the alternative, equal masses displaced by the growing-mode
field. This is the direct comparison set and holds every amplitude of the paper. Needs:
a problem generator on top of `nrpic_cosmo` (core), a slicing that survives collapse in a
periodic box (A-pre-4 with B), the horizon finder in a cosmological box.

Phase 0, expanding ball in vacuum (brief S1, A-pre-1): a piece of Einstein-de Sitter of
radius R_b = q r_m around the perturbation, Schwarzschild outside, data of format 2
(`coord/INTERFACES/spherical_id_format2.md`) and, beyond spherical symmetry, the
projection solver of `coord/notes/design_wave2_initial_data.md` item 2. The ball has to
be inside its Hubble radius, R_b H_i < 1 (2M/R = (H R)^2 for the flat ball,
derivations_to_check.md item 1 [to be re-derived by expball]), so it starts at
a_i/a_H = (q/(R_b H_i))^2 (T3). With the mean contrast in r_m at most 0.3 at the start,
the ball holds mu <= 0.031 (q = 3) or mu <= 0.069 (q = 2) at R_b H_i = 0.9; with the
central contrast at most 0.3, 2.7 times less (T3, `results/fig_design.png` left). So the
ball covers the exact-solution tests and the small-amplitude end, not the comparison
amplitudes [VERIFIED as arithmetic]. Recommendation to the lead [JUDGEMENT]: build the
threshold line in phase 1 and use phase 0 for the section-10 tests, the small-amplitude
end (mu <= 0.03) and the dispersion axis; this reverses the order of the brief.

## 5. Parameter ranges of the first scan

| Parameter | Range | Why |
|---|---|---|
| ball radius / compaction radius q (phase 0) | 2, 3; 4 for the size convergence | profile at the edge e^(-q^2): 1.8e-2, 1.2e-4, 1e-7 of the centre (T3) |
| ball radius / Hubble radius R_b H_i (phase 0) | 0.7, 0.9 | < 1 required; the start a_i/a_H = (q/R_bH_i)^2 = 4.9-36 (T3) |
| box side (phase 1) | 2L and 3L, L = 10/k | 2L is the paper's octant doubled; 3L for the size convergence |
| amplitude mu (phase 1) | bisection in [0.02, 1.0]; seeds at e = 0.2: 0.03, 0.045, 0.05, 0.1, 0.45 | spans mu_fd(1000 t_H) = 0.019 to the fluid-run amplitudes (T2) |
| amplitude mu (phase 0) | 0.005, 0.01, 0.02, 0.03 | what the ball holds (T3) |
| ellipticity e | 0, 0.05, 0.1, 0.2, 0.3 at p = 0 | the paper's e-range; h-hat rises from 0.22 to 0.48 over it (T1) |
| prolateness p | -0.1, +0.1 at e = 0.2 | allowed region |p| <= e (T1 figure) |
| dispersion s = sigma_v R/(2M) | 0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0 at e = 0 and 0.2 | critical s between 0.55 (virial, 5/3) and 1.5 (arXiv:2211.13950 L358), amplitude independent (T4) |
| particles per perturbation | lattice, N >= 1e5 at deltabar_ent >= 0.04, >= 2e6 at 0.01 | noise floor 0.1 of b_BH (T4b); random sampling needs 75 to 200 times more and is not used |

s is conserved once the dispersion is shared (Liouville, arXiv:2211.13950 L330-334), so
it is set on the initial slice by isotropic momenta of per-component dispersion
s (2M/R_i)/sqrt(3) about the growing-mode velocity [JUDGEMENT; needs initial data with
dispersion, README Requests].

Order of the scan: (1) spherical tests (section 7); (2) H1 runs; (3) e-line at p = 0,
s = 0 with the convergence triplets at e = 0.1 and 0.2; (4) p; (5) s.

## 6. Diagnostics

Apparent horizon (finder of the source paper with the calibration in docs/TESTLOG.md;
area mass, spin from the isolated-horizon formula as in arXiv:2306.11810 L209-217), its
polar and equatorial circumferences against 4 pi M (hoop test, as arXiv:1901.04498);
Hamiltonian and momentum constraints outside the horizon; central lapse; Lagrangian radii
of mass fractions of the perturbation and the virial ratio of its particles (halted or
late); Misner-Sharp compactness along the three axes (as arXiv:2610.23218); psi_4 at
several radii against the quadrupole formula of the particles (arXiv:2605.04487); mass
growth after formation against the accretion laws of arXiv:2109.04896.

## 7. Exit criteria and test plan

Rows of brief section 10 that Track A holds, as Track A will run them:

| Section-10 row | Owner | Track A test | Pass |
|---|---|---|---|
| Oppenheimer-Snyder and its time reverse | CORE (collapse), A (time reverse) | A1: marginally bound ball expanding in vacuum: shell areal radius against proper time R ~ tau^(2/3), exterior mass constant; then a bound top-hat core inside the ball: turnaround and horizon time against the cycloid | errors converge in N, dx and R_b (G2 criterion of the charter) |
| Oblate and prolate collapse | CORE, A | A2: the oblate counterpart of the prolate test core has, and the Zel'dovich pancake of a deformed core inside the ball: time of the first caustic against b/a = 1/alpha (arXiv:1609.01588 L537) at small amplitude | first-caustic time within the second-order Zel'dovich correction; horizon circumference within ~25 % of 4 pi M as in arXiv:1901.04498 L249-253 |
| Lemaitre-Tolman-Bondi dust | A | A3: the spherical profile of arXiv:2609.14218 (e = 0) against LTB: areal radius against proper length on slices of equal K for mu = 1.3 (its Appendix, L1473-1503); horizon for mu = 0.33, shell crossing without horizon for mu = 0.32 before the crossing (L766-768) | R(l) within the convergence error; horizon outcome as LTB until the first crossing |
| Szekeres dust without symmetry | A, B | A4: quasi-spherical Szekeres data (arXiv:1708.09143 [TO VERIFY: not yet read]) until shell crossing | density and expansion at the centre converge to the exact values |

Track-specific tests:
- A5 hoop line (done analytically, T1); numerically the first-caustic time of A2.
- A6 halting references for core's Newtonian mode (`core/newton`): top hat at rest,
  b_min against N for random (1.2 N^(-1/3)) and lattice (N^(-4/9)) positions and against
  s (arXiv:2507.18312 L483-542); these are the specification tests of that capability.
- A7 hypotheses H1-H4 of section 2.

Gate criteria (charter 9.4, made concrete):
- G0: this file, REFERENCES.md, the risk list and the compute estimate; lead's note v0.
- G1: offline constraint residuals of the ball data converge at the order of the checker's
  differences (+-0.2); the prediction table of A-pre-2 at one parameter set (hoop,
  Kerr-bound spin, dispersion, peak statistics); the scan design of section 5 confirmed
  by the Newtonian-mode runs of A6 once core/newton exists, otherwise by T1-T4.
- G2: A1 and A3 pass with three-way convergence; horizon mass error in A1 of the same
  order as the source paper's Oppenheimer-Snyder test [TO VERIFY: number from
  refs/arxiv_2611.12831]; one triaxial particle run of phase 1 to horizon formation with
  the constraint bound of section 3.
- G3: A_c(e) at five e with converged brackets, H1-H4 decided, mass and spin at formation
  and after 5 t_AH of accretion for at least three amplitudes, one waveform against the
  quadrupole estimate; null results and failed runs on record.

## 8. Risks

| Risk | Where it bites | Mitigation |
|---|---|---|
| Gauge fails in cosmological collapse (arXiv:2610.23218: lapse, shift damping by level) | phase 1 | A-pre-4 picks the slicing on the spherical tests A3 before any scan; the periodic conformal-time lapse of `cosmo/` is a Bona-Masso slicing with f = 1/3, weaker than harmonic [JUDGEMENT], to be tested |
| Constraint violation at particle crossings (arXiv:2609.14218 L1176) | every triaxial run | Z4c damping; bound of section 3; H2 runs |
| Curvature at caustics not convergent (arXiv:1611.07906 L97-112) | diagnostics | outcomes from horizons and constraints, not from peak curvature |
| Particle noise halts or seeds collapse near threshold | low amplitudes | lattice loading and N from T4b; N-convergence of every bracket |
| Threshold depends on the run length | all | definition of section 3; A_c(t_end) with the cutoff stated |
| Ball cannot hold comparison amplitudes | phase 0 | phase 1 for the line (T3) |
| Ball edge and outer shells leaving the domain | phase 0 | q and box convergence; spherical outer layers do not act on the interior [BACKGROUND] |
| Small horizon in a large box (M_BH ~ 1e-2 of the Hubble mass in arXiv:2109.04896 L241) | resolution, cost | dx_AH = 0.06 M_BH (twelve cells per coordinate horizon radius, docs/TESTLOG.md M/128 chain) in the cost model; refinement by trackers |
| Initial data with dispersion not available | s axis | request to core; s axis last |
| Newtonian precursor waits for core/newton (decision 0010) | G1 | T1-T4 references meanwhile; A6 specifies the tests |
| Budget: first scan ~155 card-hours against 60 to the next gate | G3 | G1 needs no cards; ask for the raise when G2 passes |
| Overlap with the authors of arXiv:2609.14218 | publication | H1 and the converged line first; watch arXiv |

## 9. Compute estimate (T5, `results/fig_cost.png`)

Measured: the two-overdensity run `jeans/n1e4_v19` (10^4 particles, eight levels,
100 M, 25600 cycles) took 5.41 card-hours, 0.761 s per cycle, 3.4e6-8.0e6 zone-cycles
per second (its 13 chain logs) [VERIFIED]; uniform Z4c 2.0e7 zone-cycles per second
(docs/TESTLOG.md L46); a periodic 128^3 run with 2,097,152 particles 11,600 steps in about
an hour (cosmo/TESTLOG.md L913-915), giving 1.0e-7 s per particle and step.

Model [JUDGEMENT]: per step the v19 cost plus 1.0e-7 s per particle; finest cell the
larger of R/32 (R the top-hat radius of the compaction shell on its cycloid) and 0.06 M_BH
with M_BH = 0.3 M_p; step 0.25 of the finest cell; black-hole runs end 30 M_p after the
horizon, halo runs 0.3 t_c after the halt. Result: 1.1 to 3.5 card-hours per run, median
2.4 at 10^6 particles; the first scan (5 e x 5 bisection runs, 2 x 3 x 3 convergence,
2 x 5 for p, 3 x 4 for s: 65 runs) about 155 card-hours, uncertain by a factor 3
(50-470). Phase-1 runs are estimated at the same cost per run (most steps come from the
collapse, which is the same in proper time), with a larger uncertainty; H1 needs two such
runs to 400 t_H (~5-10 card-hours). G2 tests about 20-30 card-hours. Processor-only work
(references, A6 once core/newton exists) is within the 16-core limit.

The model is untested on a PBH run; the first scouting runs check it (JOURNAL.md T5).

## 10. Lead's decisions and corrections at G0 (2026-11-15, after the independent re-check)

Added by the lead of A-emd-pbh; sections 1-9 above are the helper's text, unchanged. The
re-check (predictions L1-L8 in `../JOURNAL.md`, entry 2026-11-15T12:57Z) and the gate items
are in `../stage/G0/` (`CHECKLIST.md`, `EVIDENCE.md`, `OPEN.md`).

**10.1 Amplitude convention (correction).** Section 3 uses deltabar_ent = (12/(5e)) mu =
0.883 mu (mean linear contrast inside r_m at r_m aH = 1); the criteria package
(`../criteria/README.md`, "Parameters") uses the central linear contrast at the same epoch,
delta_c = 12 mu/5 (MDPBH.tex:907-908 at aH = k/sqrt6). They differ by Euler's number e for
the Gaussian profile. Both are kept; every table names its measure; delta_c = e deltabar_ent
converts [VERIFIED as arithmetic from the two definitions; JUDGEMENT to keep both]. Ratios
of thresholds do not depend on the choice.

**10.2 Order of the set-ups** [JUDGEMENT]. G2 is passed on the spherical ball, as the
charter's sheet requires. The threshold line for the comparison with arXiv:2609.14218 is
built in phase 1 (periodic box, that paper's initial data on top of `nrpic_cosmo`), with
ball runs at mu <= 0.03 as the boundary cross-check (T3, section 4). Proposed to the
orchestrator: `../outbox/20261115T1320Z__to-orch__threshold-line-in-periodic-box.md`.

**10.3 No sharp edges in evolution runs.** A sharp ball surface leaves a constraint residual
that does not fall with resolution (core's test 2, `tracks/core/JOURNAL-id.md` entry 5 on
branch `core/id-extrinsic`) and an O(1/h) momentum band offline (expball G1); the C^4 edge
taper converges (momentum orders 1.99 and 3.90 over all cells, run
A-emd-pbh-20261115-122121-aa1c84d, rerun A-emd-pbh-20261115-130402-f5566fb with identical
numbers) [VERIFIED]. Expball tables of sharp balls carry no `breaks` line, so a cubic
through the KL jump smears it over two rows with ~10 % overshoot (run
A-20261115-130257-a7374a4, `fig_crosscheck.png`); sharp tables are for offline tests only.

**10.4 G2 horizon-mass target, now verified.** The source paper's Oppenheimer-Snyder test
gives Delta M/M_ADM <~ 1e-3 for its fiducial run (refs/arxiv_2611.12831/src/main.tex:945) and
RMS errors 2.061e-3, 9.362e-4, 7.347e-4 over its AMR particle sequence A1-A3 (main.tex:1484)
[VERIFIED]. This replaces the [TO VERIFY] of section 7 (G2).

**10.5 Reference locators re-read by the lead** [VERIFIED, each found as stated]:
MDPBH.tex:766-768, 907-908, 1101-1103, 1141-1145; Main.tex (2507.18312):310, 314-316, 483-489;
Spin_PBH.tex:919-927; main_v3.tex (2605.04487):2277, 2279. The statements are in the raw store
only, not yet knowledge-base entries (kb request in the outbox).

**10.6 First full-relativity scouting runs** (to start when `core/id-extrinsic` is merged):
SR-1 and SR-2 on data set 2t (run A-emd-pbh-20261115-130609-947c898), specified with their
predicted times in `../stage/G1/STATUS.md` section 3 (predictions run
A-20261115-130948-5a2b58a).

**10.7 Compute to G2** (unit cost 8.1e-8 card-seconds per cell and step, measured by core,
run core-20261115-040406-1311b8e): SR-1 0.15 and SR-2 0.16 card-hours (256^3, dx = M/2);
spherical convergence 10-25 card-hours (uniform mesh at M/4, static refinement at M/8);
G-R1 0.3; Newtonian-mode scan <= 11 (`../newton/SCAN.md` section 6); H1 runs 5-10. About
25-50 card-hours to G2, inside the 60 of decision 0006. The G3 scan (~155, band 50-470) needs
a raise, asked when G2 passes.

**10.8 Stage timeline** [JUDGEMENT]: G0 complete with the note v0 and the two schematics
(next session); G1 with G0 (two of three criteria met, the scan design waits for
`core/newton`); G2 after the merge of `core/id-extrinsic` and `core/newton` (months 2-4); G3
needs the phase-1 generator, Track B's slicing for a periodic box and the card-hour raise
(month 9).
