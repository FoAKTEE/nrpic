# Stage report: B-emd-gw G0 (scoping)

Owner B-emd-gw (Track B, problem S2), branch `track/B-emd-gw`, 2026-11-15. Submitted for
the orchestrator's review; not self-passed. Checklist: `CHECKLIST.md` (from
`harness/bin/nrpic-stage collect`); artefacts: `EVIDENCE.md`; what the gate still lacks:
`OPEN.md`; the lead's check of the helper packages: `REVIEW.md`. Detailed scope by the
helper: `tracks/B-emd-gw/scope/SCOPE.md` (reviewed; numbers below carry their source).
Labels: [VERIFIED] read at the source or measured in a named run, [BACKGROUND],
[JUDGEMENT], [TO VERIFY]. One code base (decision 0010): every simulation here is
AthenaK of this repository; outside `athenak/src/` only references, analysis and figures.

## 1. Problem statement

Question (brief lines 366-372): how much gravitational radiation comes from the
formation, virialization and merging of structure in an early matter era, and in which
range Newtonian N-body plus the quadrupole formula can be trusted. Minimum publishable
unit (line 376): the pancake collapse of a plane-symmetric or single-mode perturbation,
full-GR waves against the Zel'dovich prediction. Why full GR (criteria N4, K1, brief
line 302): every calculation in the literature is Newtonian or semirelativistic with the
flat-space quadrupole formula [VERIFIED by scope: 2403.15126 `pII_GW_Vir_C2_Arx.tex:609-612,
898`; 2605.04487 `main_v3.tex:206-213, 1568-1590`], and the representative case of
2605.04487 (sigma = 0.1) reaches mean peculiar speeds of 0.4-0.5 c at the emission peak,
where its authors expect relativistic corrections [VERIFIED `main_v3.tex:2395-2405`,
re-read by the lead].

Two findings of this wave shape the problem:
1. An exactly plane-symmetric pancake radiates nothing at nonzero wave number (E(2)
   symmetry), and on the torus carries one global harmonic TT mode, an anisotropic mean
   expansion that is not radiation [VERIFIED symbolically twice: scope run
   B-emd-gw-20261115-113102-bc5e082; lead run B-emd-gw-20261115-131027-03b1119, checks b,
   c]. The pancake of the minimum publishable unit is the zero member of a family, not
   the source.
2. First source [JUDGEMENT, `scope/SCOPE.md` section 3]: two crossed sine waves of unequal
   amplitude (1, eps, 0) in a box of four initial Hubble radii; eps = 0 is the pancake
   (in-family null), and before shell crossing the TT strain at (k, +-k, 0) is linear in
   eps with the coefficient h_+ = -(5/6) phi_x phi_y cos(K.x) of the weak-field equation
   (Poisson gauge; arXiv:1604.06065 `compendium_arxiv.tex:294-298`) [VERIFIED twice:
   scope run B-emd-gw-20261115-113148-4e5c33b; lead run -131027-03b1119, check d].
   Second source: the three-wave data (1, 0.9, 1.1) of `cosmo/`. The isolated triaxial
   patch and a halo population follow at G3.

## 2. Parameter ranges

| Parameter | Range | Basis |
|---|---|---|
| Box L (initial Hubble radii) | 4; then 2 and 8 | relativistic depth (9/2)(H/k)^2 delta; at L = 4 the box modes sample the radiation band of the collapse (virial frequency 0.81-3.57 c k_1 for delta 0.0025-0.05), at L = 2 they stay in the near field below delta = 0.016 [run B-emd-gw-20261115-113632-2960145; model estimate, JUDGEMENT] |
| Amplitude delta | 0.0025, 0.005, 0.01, 0.02; 0.05 only until it fails | 0.05 fails at a = 17.2 in `cosmo/` [`cosmo/TESTLOG.md` 1842-1852, via scope] |
| Second-wave ratio eps | 0, 0.01, 0.03, 0.1, 0.3, 1 | linearity before shell crossing; noise bound after it (risk R1) |
| Cells per side | 64, 128, 256 (thin 256 x 256 x 16 if core confirms) | second-order convergence of the TT strain |
| Particles per cell | 8 (two per direction) in every production run; 1 only as the noise leg | one per cell under-samples the stretched lattice: pancake void H_r 1.3e-3 and M_r 0.21 at a = 15, negative energy density after crossing; two per direction about 30 times lower [VERIFIED runs B-emd-gw-20261115-115217-69ab1db, -115902-a3207d7, analysis -123852-ea4475c] |
| End | a = 1.4/delta; 3/delta for the post-collapse emission | 99 % of the emission of 2605.04487 by twice the shell-crossing time (`main_v3.tex:2277-2281`, via scope) |
| Dump cadence | conformal-time step 0.1 or finer | ten samples per period of the lowest radiating mode (period 2.8 at L = 4) |
| Gauge (third convergence leg) | conformal-time lapse (production) against harmonic slicing and 1+log | the production lapse forms gauge shocks in vacuum at K/k ~ 0.24 [VERIFIED runs B-emd-gw-20261115-114004-0ea0f74, -115139-42096b9, -115140-42096b9; reading JUDGEMENT] |

## 3. Exit criteria

Charter sheet 9.5 (`coord/CHARTER.md` line 121). G1: the two diagnostics agree on
analytic linear waves; the Newtonian baseline reproduces the scaling of the literature;
background error and constraint convergence with the stand-in matter. G2: scale-factor
error and linear growth rate of the particle FLRW run sub-percent and convergent in
particle number and mesh; agreement with gevolution in the weak-field regime. G3:
three-way convergence of the pancake GWs; a quantitative statement of when relativistic
corrections matter. Proposed rewording under decision 0010 (outbox
`20261115T1340Z__to-orch__track-b-criteria-under-0010.md`): stand-in matter struck
(superseded by the particle background); "gevolution" read as the shearing-dust
comparison of arXiv:2003.08014 against its published numbers plus the AthenaK Newtonian
mode on the same particles; the Newtonian N-body baseline run in AthenaK's Newtonian mode.

Numbers proposed for the first source [JUDGEMENT; `scope/SCOPE.md` section 6, reviewed]:
- Null (eps = 0, aligned lattice): TT strain at every nonzero wave vector below 1e-12 of
  the traceless strain at all times through shell crossing; harmonic mode reported apart.
- Noise floor (eps = 0, lattice jittered in y and z, 1 and 8 per cell): TT at least ten
  times below the eps = 0.3 signal up to a = 1.4/delta; otherwise the post-crossing part
  is descoped to what clears it.
- Before shell crossing: TT strain and K^TT at (k, k, 0) linear in eps to 1 % up to
  eps = 0.3, equal to the second-order reference carried to the code's gauge, with a
  truncation error falling at second order over 64, 128 and 256 cells.
- G3: rho_K and the TT spectrum at the box modes converged to 10 % in particle number,
  mesh and lapse condition; GR minus weak field resolved above that for one amplitude.
- Stop rules: no amplitude above 0.02 until a slicing passes black-hole formation (shared
  with Track A); if the noise floor exceeds the eps = 1 signal after crossing at 128
  cells, the claim is restricted to the pancake phase.

## 4. Test plan, mapped to the rows of brief section 10 held by B

| Row (brief line) | State | Test and criterion | Evidence so far |
|---|---|---|---|
| FLRW dust (845) | done in `cosmo/`, re-checked | lapse = scale factor to 1e-7 at a = 4 and 36, fourth-order mesh convergence (A0); missing: particle-number convergence and a run in the full production configuration (about 0.2 card-h) | `verify_cosmo/VERIFY.md` section 1; recomputed in run B-emd-gw-20261115-115414-7ffbde1 |
| Growth of linear perturbations (846) | done in part | growing-mode amplitude to 1e-5 of linear theory over a thousandfold expansion; missing: growth rate f(a), particle-number convergence in the production configuration, a glass or Poisson start | `VERIFY.md` section 2 (from `cosmo/analysis/daverio_b.json`) |
| Linear GWs in a periodic box (847) | done for axis-aligned waves | Fourier TT and Psi_4 agree with the analytic wave on AthenaK output (amplitude 3e-7, phase 1.2e-6 rad at 32^3 over two periods); oblique wave waits for the generator fix; expanding box: TT mode decays as 1/a (reference ready) | runs B-emd-gw-20261115-113218-0ea0f74, -120128-7dfaa38 |
| Plane-symmetric pancake through shell crossing (848) | first scouting done | eps = 0 member of the first source: particles continue through the multi-stream region (all kept to a = 42, plane symmetry to 1e-12); Newtonian Zel'dovich exact to crossing; GR departure converged in mesh and particle number and scaling as (H/k)^2; GR exact reference TO VERIFY (planar Szekeres class) | runs -115217-69ab1db, -115902-a3207d7, -123852-ea4475c |
| Multi-code comparison, weak field (849) | not met | under decision 0010: (i) AthenaK Newtonian mode against GR on the same particles; (ii) the weak-field tensor equation of 1604.06065 driven by the code's particles; (iii) arXiv:2003.08014 shearing dust against its published numbers | `VERIFY.md` section 3 (specification with locators) |
| Szekeres-type dust (851, A and B) | not started | non-symmetric null test of the diagnostic (Szekeres dust has no magnetic Weyl part [BACKGROUND, TO VERIFY with 1708.09143]); shared with Track A | none |

## 5. Key references: statements verified at the source

Read in `kb-data/raw/arxiv/<id>/<v>/src/`: eleven sources by the scope helper with
file:line locators (`scope/REFERENCES.md`); the lead re-read the rows marked *.

| Statement | Locator | Status |
|---|---|---|
| Omega_GW proportional to sigma^(7/2) = A_s^(7/4) (Zel'dovich + quadrupole) * | 2403.15126 v1 `pII_GW_Vir_C2_Arx.tex:1074` | [VERIFIED] |
| ZA spectrum dE/dln omega = (32/135 pi)(c^5/G) omega (GM/c^3)^2 S abs(E_1/3(i omega t_k) - alpha^-1 E_1/3(i omega t_col))^2 | 2605.04487 `main_v3.tex:2896-2918`; 2403.15126:966-970 | [VERIFIED]; rederived (baseline T1; lead check e) |
| Crossing along x at t/t_k = 22.536, along y at 29.097 * | 2605.04487 `main_v3.tex:2276-2278` | [VERIFIED]; reproduced to 1.0 % and 0.09 % only by the literal model B (baseline T5) |
| Mean peculiar speeds 0.4-0.5 c at sigma = 0.1; relativistic corrections expected * | 2605.04487 `main_v3.tex:2395-2405` | [VERIFIED] |
| rho_K = (M_pl^2/2) K^TT_ab K_TT^ab, York TT part of K, hypersurface dependent * | 2111.09163 v2 `prd_v1.tex:258-262` (also 163-175, 369-426) | [VERIFIED] |
| Weak-field tensor equation (1/2)h'' + Hc h' - (1/2) lap h = TT[8 pi G a^2 Pi - 2 dPhi dPhi - 4 Phi ddPhi], metric (1 - 2 Phi) delta + h * | 1604.06065 v2 `compendium_arxiv.tex:142, 294-298` | [VERIFIED] |
| Quasi-static h_ij is a static spin-2 field, not a free wave | 1604.06065 `compendium_arxiv.tex:1437-1444` | [VERIFIED by scope] |
| Shearing-dust comparison of gevolution, GRAMSES, Einstein Toolkit, CosmoGRaPH; all within 0.03 % of linear theory at b = 0.005 H*^2 L^2 | 2003.08014 v2 `draft.tex:142-182, 285, 348, 360, 383` | [VERIFIED by verify_cosmo] |
| N-body gauge: Newtonian N-body with Zel'dovich data contains the first-order GR effects | 1505.04756 `finalpaper.tex` (`scope/REFERENCES.md`) | [VERIFIED by scope] |
| CTTK constraint solving with periodic boundaries | 2207.03125, 2501.13046 | [VERIFIED by scope]; not used here (decision 0010, consequence 4) |
| Not read: 2212.00425 and 2312.12499 (the Newtonian box results S2 compares with), 1704.03500, 2012.14016, 1708.09143, 2610.08045 | - | [TO VERIFY] (kb request) |

## 6. Risk list (likelihood, effect, watch and response in `tracks/B-emd-gw/RISKS.md`)

R1 spurious TT from particle noise after shell crossing (the sheet's main risk; momentum
constraint 2.9e-2 at a = 40 and 0.17 at a = 100 in the `cosmo/` collapse run
[`cosmo/TESTLOG.md` 1674-1676, via scope]); R2 junk TT of conformally flat data (decays
as 1/a, 1.8 % of the static value at a = 60); R3 near field against radiation in the box;
R4 hypersurface and gauge dependence of h^TT and rho_K, with a measured example (late
rise in `gw_diag/figs/cosmo_tt.png` of the size of the second-order gauge piece); R5 gauge
shocks of the production lapse; R6 black-hole end at delta >= 0.05; R7 output volume and
float32 dumps; R8 dependence on core (generator fix, Newtonian mode on main, GW output,
jitter option); R9 the literature box comparison (2212.00425, 2312.12499) unread.

## 7. Compute estimate on this machine

Measured on one A100 (single-wavelength problem, delta = 0.01, to a = 140) [VERIFIED,
logs read by the lead]: 64^3, 1404 cycles in 63.8 s, 5.77e6 zone-cycles/s
(`runs/cosmo/east_d0.01_n64_pcs4b/athena.20261114-072656.log`); 128^3, 2773 cycles in
1302 s, 4.47e6 (`runs/cosmo/east_d0.01_n128_tsc/athena.20261114-021442.log`). Per run
[scope run B-emd-gw-20261115-113632-2960145]: 0.018 card-h at 64^3, 0.36 at 128^3, 5.8 at
256^3 (about 32 GB of 80), 0.36 for a 256 x 256 x 16 thin box; at delta = 0.0025
(a = 560): 0.037, 0.76, 12.1, 0.76. Used this wave: 0.48 card-h (six pancake runs, two
jobs).

| Block to G2 | Runs | Card-hours [JUDGEMENT] |
|---|---|---|
| Null and jittered null, 64 and 128 cells, 1 and 8 per cell | 8 | about 2 |
| eps scan (6 values) at delta 0.01 and 0.0025, 64 and 128 cells | 24 | about 7 |
| Three-wave set with dumps, 4 amplitudes, 64 and 128 cells | 8 | about 2 |
| Convergence at 256 cells for two points | 2-3 | 0.7-1.1 thin, 12-18 as full cubes |
| FLRW and growth particle-number package (`VERIFY.md` section 7) | 6-9 | about 0.5 |
| Shearing dust of 2003.08014 (small boxes) | about 10 | about 0.5 [TO VERIFY] |
| Total | | about 13 (thin) to 31 (full cubes) of the 40 of decision 0006 |

Not included: dump I/O at the GW cadence, the later end 3/delta, the cost of 8 per cell
(assumed twice). Analysis on processors: seconds to minutes per dump; the lead's re-check
of all five packages took 174 s on 8 cores (run B-emd-gw-20261115-131016-03b1119).

## 8. Stage timeline (proposed)

| Gate | Content | Depends on | Target |
|---|---|---|---|
| G0 | this package; working note v0, two schematics and the independent verifier report still owed (`OPEN.md`) | - | submitted 2026-11-15 |
| G1 | diagnostics agree on an oblique AthenaK wave and in an expanding box; Newtonian baseline in AthenaK's Newtonian mode (plane wave, ellipsoid tests N1-N3 of `baseline/BASELINE.md`); first-source scouting (null and eps scan at 64^3); criteria reworded | core: generator fix, Newtonian mode on main | weeks 3-4 |
| G2 | FLRW and growth convergence in particle number; three-leg convergence of the first source before shell crossing; shearing-dust comparison; first full-GR kinetic run through shell crossing with GW diagnostics | core-v0.2 tag, jitter option, GW output | months 3-4 |
| G3 | pre-registered eps and delta scan through shell crossing, three-way convergence, GR minus weak field; three-wave halo source | G2 | months 6-9 |
| G4 | paper | G3 | months 10-12 |

## 9. Review of the helper packages

`REVIEW.md`: every result of the five packages reproduced bit for bit from a clean export
(run B-emd-gw-20261115-131016-03b1119); key derivations confirmed independently (run
B-emd-gw-20261115-131027-03b1119); defects fixed: the normalization of the crossed-wave
coefficient, 34 manifests mislabelled production, a hard-coded path. New caveat found: the
late TT rise in the existing cosmology dumps may be a gauge artefact (R4).

## 10. Decision requested

Accept sections 1-7 as the G0 scope of Track B, with `OPEN.md` items 1-3 (working note v0,
schematics, independent verifier report) owed before the gate is tagged, and act on the
criteria proposal to orch.
