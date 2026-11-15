# Track B (S2) at G0: scope

Gravitational waves from structure formation in an early matter era, computed with the
Einstein-Vlasov particle-in-cell code of this repository (AthenaK, decision 0010).
Helper package `scope` of owner B-emd-gw, 2026-11-15. Labels as in the brief: [VERIFIED]
read at the source (file and line given), [BACKGROUND] standard result not checked here,
[JUDGEMENT] my inference or design, [TO VERIFY] open. References with locators:
`REFERENCES.md`; predictions and outcomes: `JOURNAL.md`; runs under `../runs/`.

## 1. Problem statement

Question of S2 (brief lines 366-379): how much gravitational radiation the formation,
virialization and merging of halos in an early matter era produce, and within what range
Newtonian N-body plus the quadrupole formula can be trusted. Deliverables named there: the
burst of one pancake through shell crossing, the stochastic spectrum of a halo population
in a small box, and a wavenumber comparison with the Newtonian box results of 2212.00425
and 2312.12499 (not read yet). Minimum publishable unit: pancake collapse of a
plane-symmetric or single-mode perturbation, full-GR waves against the Zel'dovich
prediction.

What the literature has, read at the source:
- Both N-body calculations use Newtonian gravity and the flat-space quadrupole formula
  for an isolated patch: 2403.15126 (N up to 1e4, started at turnaround with the Hubble
  flow dropped; `pII_GW_Vir_C2_Arx.tex:611, 667, 898-903`) and 2605.04487 (N = 3000,
  relativistic kinematics only; `main_v3.tex:206-213, 1568-1590, 2365`). [VERIFIED]
- Scaling: the emitted spectrum falls as sigma^(7/2) with omega_peak proportional to
  sigma^(3/2) (2403.15126:1007, 1031) [VERIFIED]. The paper also states Omega_GW today
  proportional to sigma^(7/2) (= A_s^(7/4), line 1074), but its eq. (result_OmZ) takes the
  emission redshift at each configuration's collapse (line 1061); with that, the
  verifier of wave 2 finds sigma^(5/2) for the peak today (`stage/G0/VERIFIER.md` C8)
  [TO VERIFY; amended in wave 2: use 7/2 only for the emitted energy]; the post-shell-crossing stage
  dominates, Zel'dovich estimates fall short by up to about three orders at the peak
  (2605.04487:2512, 2625). [VERIFIED]
- The representative 2605.04487 case (sigma = 0.1) reaches mean peculiar speeds of
  0.4 to 0.5 c at the emission peak; the authors expect an order-one correction and name
  a fully relativistic treatment as future work (`main_v3.tex:2395-2405, 1586, 2630`).
  [VERIFIED]
- [JUDGEMENT] The exponent 7/2 is (v/c)^7 with v^2/c^2 of the order of the contrast at
  horizon entry: the patches that dominate the signal are the ones whose collapsed
  compactness is not small. That, and the Zel'dovich part of the spectrum peaking at
  omega ~ 1/t_col (wavelength 2 pi t_col, larger than the Hubble radius at emission,
  2403.15126:1007), is where the full-GR calculation adds something (criteria N4 and K1
  of brief line 302).

Our setting. The single-wavelength problem of `cosmo/` (box of four initial Hubble radii,
three crossed sine waves, `cosmo/ic/make_east.py`) starts close to horizon entry
(k = 1.57 aH at a = 1) like the patches of 2403.15126 and 2605.04487, with a peak linear
potential of 1.82 delta
([VERIFIED] `runs/cosmo/east_d0.01_n64_pcs4b/id.json`: max_abs_psiN = 0.0182 at
delta = 0.01). It runs through shell crossing for delta up to 0.01 and approaches black
hole formation at 0.05, where it fails at a = 17.2 (`cosmo/TESTLOG.md` lines 1842-1852).
The relativistic infall is later than the Newtonian one by about five times the amplitude
(lines 1905-1919). So the amplitude range 0.0025 to 0.05 spans weak field to the
black-hole threshold.

## 2. Item 3 of `coord/notes/derivations_to_check.md`, checked

Claim (lines 55-65): an exactly plane-symmetric collapse radiates nothing; the pancake is
a test of the multi-stream region, not a source. Verdict: **holds, with three
amendments.** Run `B-emd-gw-20261115-113102-bc5e082` (sympy; `results/check_item3.json`)
and `B-emd-gw-20261115-113148-4e5c33b` (Fourier, `results/crossed_waves_tt.json`,
`figs/crossed_waves_tt.png`).

1. Linear (Fourier) form. Plane-symmetric fields have wave vectors along x only. The TT
   projector for khat = x leaves ((T_yy - T_zz)/2)(e_y e_y - e_z e_z) + T_yz(e_y e_z +
   e_z e_y), which vanishes exactly when T_yy = T_zz and T_yz = 0 (check 1A). Invariance
   under rotations about x is equivalent to that form (1B). So the argument needs the
   rotation part of the plane symmetry, E(2), not only the two translations: with
   translations alone, plane waves along x with h_+ = h_yy - h_zz are allowed and would be
   sourced by anisotropic transverse stress. For the cold pancake the transverse stress
   vanishes and the gravitational stress is E(2)-symmetric, so the claim holds; on the
   code's mesh the 90-degree rotation of the lattice suffices for the modes along x.
   Numerically the TT part of the plane wave is exactly 0.0 (check 2A).
2. Covariant (York) form on the torus. The TT tensors with the symmetry form one global
   mode, A = c / Y^3 diag(1, -1/2, -1/2) for the slice metric diag(X^2, Y^2, Y^2)(x)
   (check 1C). The projection of K onto it is proportional to -d/dt of the integral of
   sqrt(gamma_xx / gamma_yy) over x (1D): an anisotropic mean expansion of the box (a
   Bianchi-I-like shear), zero at first order, generically nonzero at second order and
   after shell crossing. It is not radiation; the diagnostic must report it apart from the
   modes at nonzero wave number. [JUDGEMENT on its interpretation]
3. Wording of the note. "Three equal crossed waves (the single-wavelength problem of
   `cosmo/`)" is not what `cosmo/` ran: the amplitudes are delta (1, 0.9, 1.1)
   ([VERIFIED] `cosmo/ic/make_east.py:7, 51, 211`; `id.json` of the production runs).
   And cubic symmetry does not remove the TT modes at mixed wave vectors: equal amplitudes
   carry them with the same TT fraction 0.5 (check 2C).

By-product (check 1E). With a transverse metric a(t)^2 independent of x, dust at rest and
X = a (1 + D psi'), the Hamiltonian constraint forces dD/dt = -(3/2) H D: only the decaying
mode. The growing-mode pancake in GR has an x-dependent transverse metric (a comoving
curvature perturbation). The brief's reference for the pancake row ("Zel'dovich exact in
plane symmetry", line 848) is a Newtonian statement; the GR reference solution for the
pancake test is [TO VERIFY] (plane-symmetric dust solutions of the Szekeres family are the
candidates; not read).

## 3. The first gravitational-wave source

| Candidate | TT source | Null limit in the same family | Initial data and code today | Reference before shell crossing | Literature link | Cost | Verdict |
|---|---|---|---|---|---|---|---|
| Exactly plane-symmetric pancake (1, 0, 0) | none (section 2) | is the null | `make_east.py --ratios 1,0,0` | Newtonian Zel'dovich exact; GR form TO VERIFY | multi-stream test row | 64^3: 1 min | test, not a source |
| Two crossed waves of unequal amplitude (1, eps, 0) | at (+-k, +-k, 0) only, h_+ = (5/12) phi_x phi_y (check 2B) | eps = 0 | `make_east.py --ratios 1,eps,0`; z-independent | second order exact (check 2), LPT | pancake through shell crossing (MPU) | 64^3: 1 min; thin box possible | **first source** |
| Transversely modulated pancake (potential flow with a (k, k, 0) component) | at second order, proportional to the modulation | modulation 0 | `cosmo/ic/make_field.py` from a density field | LPT | MPU | as above | alternative to the row above |
| Three crossed waves (1, 0.9, 1.1), the `cosmo/` data | 12 mixed modes, TT fraction 0.5 (check 2C) | none in the family (equal amplitudes still radiate) | runs exist, without metric dumps | second order | halo formation; black-hole end | 64^3: 1 min each | **second source**, run alongside |
| Triaxial isolated patch (2605.04487 set-up) | quadrupole of the patch | spherical patch | `make_field.py` with a smooth patch [TO VERIFY] | Zel'dovich ellipsoid | direct (2403.15126, 2605.04487) | 256^3 or more: 6 h a run | G3 |
| Small population of halos | stochastic | none | random fields exist (`cosmo/ic/random_field.py`) | linear | 2212.00425, 2312.12499 | 256^3, several h | G3/G4 |

Lead note (2026-11-15, run `B-emd-gw-20261115-131027-03b1119`, check d): the value
(5/12)|phi_x phi_y| here and in risk 2 is the magnitude of the complex Fourier coefficient
of h_+ at (k, k, 0) with numpy's `fftn/N^3` normalization; the real-space wave is
h_+ = -(5/6) phi_x phi_y cos(K.x) at K = (k, k, 0) (basis e_+ = u u - z z,
u = (1, -1, 0)/sqrt 2; the same magnitude with the opposite sign at (k, -k, 0) in its own
basis u = (1, 1, 0)/sqrt 2 [lead's hand projection]), with phi_i the amplitude of
Phi = sum_i phi_i sin(k x_i). The (k, k, 0) value is confirmed independently by a
real-space projection.

Decision [JUDGEMENT]: **the first source is the pair of crossed waves of unequal amplitude
(1, eps, 0) in the box of four initial Hubble radii**, with eps = 0 as the in-family null
(it is the plane-symmetric pancake, so the pancake row of section 10 is run in the same
set). Reasons, in order: (a) an exact null in the same code path and initial-data tool,
so particle and truncation noise are measured on the configuration itself; (b) an exact
second-order reference: before shell crossing the TT strain at (k, k, 0) is linear in eps
with a known coefficient (check 2B), so the first comparison is quantitative. Caveat: that
coefficient is the Poisson-gauge strain of the weak-field equation, and the TT part of
the metric is gauge dependent at second order (2111.09163); the gauge-safe comparison is
K^TT on the code's slicing (Newtonian at first order, risk 4), where before shell crossing
only the junk oscillation of risk 2 should appear, and the strain is compared after the
reference is carried to the code's spatial gauge [TO VERIFY, package `gw_diag`]; (c) nothing
new is needed from core to start (`make_east.py --ratios`, `nrpic_cosmo`, AthenaK's
`variable = z4c` dumps as used in `periodic_z4c/inputs/gauge.athinput:71-73`); (d) the
data do not depend on z, which allows thin boxes for the convergence study [TO VERIFY with
core]; (e) at delta = 0.01 the box modes lie in the radiation band of the collapse (check
3B). The three-wave `cosmo/` configuration is the second source, run with the same
diagnostics: it forms a three-dimensional halo, goes through violent relaxation, and its
amplitude ladder reaches the black-hole end. The isolated triaxial patch and the halo
population follow at G3.

## 4. Parameter ranges

| Parameter | Range | Why |
|---|---|---|
| Box L (initial Hubble radii) | 4; then 2 and 8 | 4 is the `cosmo/` problem; the relativistic delay of the infall is about three times the initial potential depth |psi_N| = (9/2)(H/k)^2 delta, 1.0 to 1.2, 4.6 to 5.3 and 28 to 30 percent at L = 2, 4, 8 for delta = 0.01, and at L = 8 the run ends near black-hole formation at a = 96 (`cosmo/TESTLOG.md` lines 672-695); check 3B: at L = 2 the box modes lie above the radiation band for delta below 0.016 |
| Amplitude delta | 0.0025, 0.005, 0.01, 0.02; 0.05 only to its failure | peak linear potential 1.82 delta: 0.005 to 0.09; 0.05 fails at a = 17.2 |
| Second-wave ratio eps | 0 (null), 0.01, 0.03, 0.1, 0.3, 1 | linearity in eps before shell crossing; eps >= 0.3 after shell crossing (risk 1) |
| Cells per side | 64, 128, 256 (thin 256 x 256 x 16 if it works) | second-order convergence of the TT strain |
| Particles per cell | 1 and 8 (two per direction) | noise scaling; production configuration of `cosmo/README.md` |
| End | a = 1.4 / delta as in `cosmo/` C2 (2.5 times linear collapse); 3 / delta for the post-collapse emission | 99 percent of the emission of 2605.04487 by 2 t_shell-crossing (`main_v3.tex:2277-2281`) |
| Dump cadence | conformal-time step 0.1 or finer (period of the (k, k, 0) mode: 2.8) | ten samples per period of the lowest radiating modes |

## 5. What is measured and against what

1. TT strain of the conformal metric at the box wave vectors (Fourier TT projector), and
   the covariant TT part of K with rho_K (2111.09163, `prd_v1.tex:160-187, 260`), the
   harmonic part on the torus reported separately (section 2). Weyl Psi_4 with a
   plane-wave tetrad per wave vector as the third measure. Built by package `gw_diag`.
2. Before shell crossing: the second-order reference (static part (5/12) phi_x phi_y at
   (k, k, 0) in the weak-field Poisson-gauge equation of 1604.06065, `compendium_arxiv.tex:
   294-298`, plus the junk oscillation of check 3A), then LPT (2010.12584).
3. Weak-field reference at all times: the same h_ij equation with the TT stress of the
   particles taken from AthenaK snapshots and integrated with the conformal-time Green's
   function (`compendium_arxiv.tex:1446-1452`), outside `athenak/src/` (decision 0010).
   The difference GR minus weak field, as a function of delta and L, is the "when do
   relativistic corrections matter" statement of the track sheet.
4. Quadrupole-formula reference for the lattice of sources: the box mode at G is driven
   by the Fourier component of the source, which for G R << 1 is the second time
   derivative of the quadrupole of one cell divided by the cell volume [BACKGROUND]; the
   comparison is mode by mode, not in total power.
5. The Newtonian counterpart with identical particles: AthenaK's Newtonian mode when core
   has it (decision 0010), until then `cosmo/newton/` (the existing reference of `cosmo/`).

## 6. Exit criteria

G0 (this package): the items of the gate (problem, ranges, exit criteria, test plan,
references with locators, risks, compute) exist and item 3 is checked. Done here, pending
review.

For the first source, numbers I propose for G1 to G3 [JUDGEMENT]:
- Null (eps = 0, aligned lattice): TT strain at every nonzero wave vector below 1e-12 of
  the traceless strain at all times, through shell crossing; harmonic mode reported.
  Amended in wave 2: the relative form fails at the first dumps only because the
  traceless part is then tiny (first_source P1); the criterion is absolute, TT amplitude
  of h and tilde A at the rounding of the metric (below 1e-15) at every dump.
- Noise floor (eps = 0, particles jittered in y and z, 1 and 8 per cell): TT level at
  least ten times below the eps = 0.3 signal at all times up to a = 1.4/delta. If not,
  the post-shell-crossing part is descoped to what clears it.
- Before shell crossing: TT strain and K^TT at (k, k, 0) linear in eps to 1 percent for
  eps up to 0.3; K^TT equal to the junk oscillation predicted from the second-order
  reference (risk 2), the strain equal to that reference carried to the code's gauge,
  both within a truncation error that falls at second order between 64, 128 and 256
  cells. Amended in wave 2: the reference is the full second-order solution from the
  code's own initial data, s g(tau) with the junk oscillation (verifier C3, weakest point
  1); at delta = 0.01 it holds to 0.5 percent for 2 <= a <= 10 and departs by 1-2 percent
  at a = 20 (first_source P2): the quantitative comparison window is a <= 10 at this
  amplitude, wider at smaller delta.
- After shell crossing (G3): rho_K and the TT spectrum at the box modes converge to 10
  percent in particle number, mesh spacing and lapse condition (the three legs of the
  gate); GR minus weak field resolved above that error for at least one amplitude.
- Stop rules: if the black-hole end cannot be passed (as at delta = 0.05 today), the
  amplitude range ends at 0.02 until the gauge work with Track A (2610.23218, 2608.13206)
  gives a stable slicing; if the TT noise floor exceeds the eps = 1 signal after shell
  crossing at 128 cells, the science claim is restricted to the pancake phase.

## 7. Test plan, mapped to the rows of brief section 10 that Track B holds

| Row (brief line) | Status here | Test and criterion |
|---|---|---|
| FLRW dust, Einstein-de Sitter (845) | done in `cosmo/` C0 (`cosmo/TESTLOG.md` 25-77) | package `verify_cosmo` re-checks: lapse and scale factor to 1e-6 at 32 cells (lines 65-68) |
| Growth of linear perturbations (846) | done in `cosmo/` C1, C5 test B (163-181, 538-560, 1868-1903) | `verify_cosmo`; G2 asks for sub-percent and convergence |
| Linear gravitational waves in a periodic box (847) | packages `periodic_z4c`, `gw_diag` | analytic linear wave: Fourier TT and Psi_4 agree; in the expanding box the TT mode decays as 1/a (check 3A gives the reference: envelope times a constant to 0.7 percent) |
| Plane-symmetric pancake through shell crossing (848) | this scope, first runs at G1 | eps = 0 member of the first-source set: TT null (section 6); particles continue through the multi-stream region; Newtonian Zel'dovich to shell crossing for the Newtonian counterpart; GR reference TO VERIFY (check 1E) |
| Multi-code comparison, weak field (849) | redefined by decision 0010 | no outside code is run: weak-field h_ij equation of 1604.06065 on AthenaK particle output (section 5.3); GRAMSES initial conditions already compared in `cosmo/` C6 |
| Szekeres-type dust (851, A and B) | optional for B | Szekeres dust has no magnetic Weyl part [BACKGROUND, TO VERIFY with 1708.09143]: a non-symmetric null test of the GW diagnostic, shared with Track A |

## 8. Risks

1. **Spurious TT from particle noise at small amplitude** (brief line 745). From the
   measured levels in `cosmo/TESTLOG.md`:
   - Before shell crossing a lattice start has no random noise. The deposit error of a
     compressed lattice is deterministic: 0.4 c^3 for the cubic cloud at compression c,
     capped at 3e-4 with two particles per cell and direction (lines 260-266); in plane
     symmetry it stays plane-symmetric, so it adds no TT at all (section 2).
   - After shell crossing the measured mean relative constraint violations of the
     production collapse run (delta = 0.01, 64 cells) are 2.4e-4 and 1.6e-2
     (Hamiltonian) and 2.9e-2 and 0.17 (momentum) at a = 40 and 100 (lines 1674-1676);
     in the random-field box 1.3e-4 to 6.9e-4 and 5e-2 to 0.13 (lines 1150-1152). They
     are the connection-constraint violation fed by truncation error and particle noise
     (lines 1794-1801), and 3.4 times more particles lower them by only a third, so they
     are not shot noise alone (lines 1404-1415).
   - [JUDGEMENT] Taking the momentum-constraint level eps_M as the relative error of the
     traceless curvature, at most a fraction sqrt(2/5) of it is TT (two of five traceless
     components): 0.018 at a = 40 and 0.11 at a = 100. The physical TT fraction of the
     source is min(sqrt(3) eps, 1/2), so 1.73 eps up to eps = 1/(2 sqrt 3) = 0.289 and 0.5
     above (check 2B; corrected in wave 2 from "0.18", verifier C2: 0.18 was a grid point
     of the scan). A margin of three then needs eps >= 0.032 at a = 40 and eps >= 0.19 at
     a = 100 (first written as 0.03 and 0.3). The fraction counts only the scope's terms
     of the source; with the full source it is 1.24 eps, saturating at 0.69 (verifier C2).
     Hence the scan in section 4.
   - The decisive number is measured, not estimated: the jittered-lattice null run of
     section 6. 2605.04487 makes the same point for its particle load: random sampling
     gives an initial |Q| of about 1e-1, the cleaned glass 1e-14 (`main_v3.tex:2238`).
2. **Junk TT of conformally flat initial data.** The data of `cosmo_id.py` are
   conformally flat, so the TT mode starts at zero instead of at its second-order value
   (5/12) phi_x phi_y (1.54e-5 at delta = 0.01, eps = 1). The oscillating difference
   decays as 1/a (check 3A, run `B-emd-gw-20261115-113632-2960145`: slope -0.997,
   envelope times a constant to 0.7 percent), 1.8 percent of the static value at a = 60,
   near collapse for delta = 0.01. Mitigation: subtract the computed junk, or put the
   second-order TT part into the initial conformal metric (request to core).
3. **Near field against radiation.** In the matter era the sub-horizon second-order TT
   field is static and follows its source; it oscillates only where the source changes on
   the light-crossing time of the mode (1604.06065, `compendium_arxiv.tex:1437-1444`).
   Check 3B: for L = 4 the virial frequency at collapse is 0.81 to 3.57 times c k_1 for
   delta = 0.0025 to 0.05 (1.57 and 3.27 at the measured infall of 0.01 and 0.05). So
   the box modes sample the radiation band; for delta above 0.016 the band moves to the
   harmonics |n| = 2 to 4, and at L = 2 the box modes stay in the near field for delta
   below 0.016. rho_K (K^TT) carries the propagating part, the TT strain the static
   part; both are reported.
4. **Hypersurface dependence of rho_K** (2111.09163, `prd_v1.tex:369-426`). The code's
   slicing keeps alpha / gamma^(1/6) fixed (`cosmo/TESTLOG.md` lines 341-346); with
   constant potential in the linear matter era this is the Newtonian slicing at first
   order [JUDGEMENT: alpha = a(1 + Phi), gamma^(1/6) = a(1 - Phi)], on which rho_K holds
   only propagating modes at second order (`prd_v1.tex:76, 647`). After collapse the
   slicings differ; the lapse condition is the gauge leg of the convergence test.
5. **Black-hole end.** delta = 0.05 fails at a = 17.2 with the metric determinant
   non-finite (`cosmo/TESTLOG.md` 1842-1852); three lapse and shift attempts did not pass
   collapse (494-516, 809-826). Shared with Track A.
6. **Constraint growth after collapse** (risk 1 numbers): limits how long after
   collapse the runs are trusted; the end at 1.4/delta keeps the Hamiltonian violation at
   or below 1.6e-2.
7. **Output volume.** A full Z4c dump at 64^3 is about 20 doubles per cell, 42 MB; 200
   dumps per run 8 GB, 67 GB at 128^3 [JUDGEMENT, arithmetic]. An in-situ output of the
   low-wave-number Fourier modes of gamma_ij and K_ij is the way out (request to core).
8. **Mode-by-mode comparison with the quadrupole formula** in a periodic box is not the
   textbook isolated-source comparison: images, the finite source size (G R not small)
   and the expansion all enter. The weak-field equation on the same particles (section
   5.3) is the primary reference for that reason.

## 9. Compute estimate

Measured throughput on one A100, one particle per cell, the single-wavelength problem
(delta = 0.01, to a = 140): 64^3, 1404 cycles in 63.8 s, 5.77e6 zone-cycles/s, 1.7 GB
(`runs/cosmo/east_d0.01_n64_pcs4b/athena.20261114-072656.log`; `cosmo/TESTLOG.md` line
201: 25 steps/s); 128^3, 2773 cycles in 1302 s, 4.47e6, 5.1 GB
(`runs/cosmo/east_d0.01_n128_tsc/athena.20261114-021442.log`); production configuration
at 128^3: 5.7e6 and 5.6e6, 6.1 GB (`runs/cosmo/dav_c256_n128_pcs4bt/chain/seg00{1,2}*.log`).
The cards hold 80 GB (a run reached 61.6 GB: `runs/os/mc_nocap3/athena.20261113-140154.log`).
Table from run `B-emd-gw-20261115-113632-2960145` (`results/regime_estimates.json`, step
0.25 of the cell, memory linear in the cell count between the two measured points):

| delta (a_end) | 64^3 | 128^3 | 256^3 (about 32 GB) | 256 x 256 x 16 |
|---|---|---|---|---|
| 0.01 (140) | 0.018 card-h | 0.36 | 5.8 | 0.36 |
| 0.0025 (560) | 0.037 | 0.76 | 12.1 | 0.76 |

Plan to G2 for the first and second sources [JUDGEMENT]: null and jittered null at 64 and
128 cells, 1 and 8 particles per cell (8 runs, about 2 card-hours with the 8-per-cell
runs at roughly twice the cost [TO VERIFY]); eps scan of 6 values at delta 0.01 and
0.0025 at 64 and 128 cells (24 runs, about 7 card-hours); three-wave set with dumps at
four amplitudes, 64 and 128 cells (8 runs, about 2 card-hours); convergence at 256 cells
for two points (12 to 18 card-hours as full cubes, 0.7 to 1.1 as thin boxes). Total about
12 card-hours with thin boxes, about 30 with full cubes, inside the 40 GPU-hours of
decision 0006. Dump I/O and the larger end time 3/delta are not included [TO VERIFY].
Analysis (Fourier projections, Green's-function weak-field reference) runs on processors:
seconds to minutes per dump at these sizes.

## 10. Not done in this package

- The GR reference solution for the plane-symmetric pancake (check 1E shows the naive
  form is wrong) is not derived.
- 2212.00425, 2312.12499, 1704.03500, 2012.14016, 1708.09143 not read.
- No AthenaK run was made here; every number on the code's behaviour is quoted from
  `cosmo/` with its locator.
- The noise criterion of risk 1 is an estimate; the jittered null run decides it.
