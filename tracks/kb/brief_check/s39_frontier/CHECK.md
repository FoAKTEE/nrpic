# Check of brief lines 239-256 (section 3.9, developments in 2025-2026 and active groups)

Owner kb, work package s39_frontier, wave 3a, 2026-11-19. Brief:
`einstein_vlasov_pic_cosmology_agent_brief.en.md` (version 2), lines 239-256 only: the heading
and a table of 13 rows that name 32 arXiv ids.

Locators. `<id>/<v>/src/<file>:<line>` are lines of the TeX sources under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/` (the newest version in the store; all 32 ids were
there before this package started, nothing was fetched for the check). `meta:<id>` is
`kb-data/meta/arxiv-api/<id>.json` (arXiv API record written by `harness/bin/nrpic-fetch-arxiv`).
The searches are in `specs/r*.txt` and run with `scripts/locate.py` (README).

Labels. No cell of lines 239-256 carries an evidence label. Every cell of the second column
("Recent representative work") is a specific claim about papers (authors, subject), checked
here as an unlabelled claim ("unl."); the third column ("Relation to this project") is the
author's [JUDGEMENT]. Where a judgement rests on a factual premise about the paper or is
affected by a decision, the premise is checked and given a verdict (rows 7, 37-44); pure
judgements are listed at the end without a verdict. None of these lines is in `coord/BRIEF_ERRATA.md` (its rows cite lines 88-134, 262,
275, 355-398, 520, 843-852 and the charter), so nothing here repeats it.

Verdicts. CONFIRMED (the source says it, at the locator; "precision" when the source says it
with a qualification worth recording), CORRECTED (the source says something else; what is
right is in the note), NOT FOUND (what was searched). Totals: 44 rows with a verdict, 37
CONFIRMED (16 of them with a precision), 7 CORRECTED (5 about papers: rows 1, 4, 7, 29, 36;
2 about the project relation: rows 37, 38), 0 NOT FOUND; 13 judgements without a verdict.
Tally and figure: run kb-20261119-HHMMSS (README, "Runs").

## Heading (line 239)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | 239 | "Developments in 2025–2026" (heading of the table) | unl. | CORRECTED | meta:2401.08530 (published 2024-01-16), meta:2402.02178 (2024-02-03), meta:2404.16270 (2024-04-25) | Three of the 32 ids are from 2024: 2401.08530 (row 250), 2402.02178 and 2404.16270 (row 252). The other 29 are dated 2025-01 to 2026-11. Harmless, but "2024-2026" is the right range. |

## Row "Black-hole formation in a matter-dominated era, full-NR particles" (line 243)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 2 | 243 | "Yoo, Escrivà, Harada, Kohri: arXiv:2609.14218" | unl. | CONFIRMED | `2609.14218/v1/src/MDPBH.tex:131-134` | Exactly these four, in this order. |
| 3 | 243 | 2609.14218 is "black-hole formation in a matter-dominated era, full-NR particles" | unl. | CONFIRMED (precision) | `2609.14218/v1/src/MDPBH.tex:168, 171, 175-177, 242, 1002-1072, 1197` | Fully nonlinear 3+1 NR in a matter-dominated era with two matter models: a dust fluid (most of the paper; triaxial initial data, L170, L1195) and, in the last section, "the attempt to perform a particle-in-cell (PIC) simulation in full numerical relativity" (L242). The particles sit on a regular lattice with per-particle masses carrying the inhomogeneity, and deposit with a cell-sized top-hat support (L1048-1072). With particles the runs do not crash and the threshold is "smaller than the previous analytic estimation by an order of magnitude" (L177). |
| 4 | 243 | "semi-relativistic gravitational waves by the same authors arXiv:2605.04487" | unl. | CORRECTED | `2605.04487/v2/src/main_v3.tex:144-148, 171, 189, 209-214` | Not the same authors: five, Escrivà, Harada, Kohri, Terada, Yoo (Takahiro Terada added). "Semi-relativistic" qualifies the N-body model, not the waves: collisionless particles in an Einstein-de Sitter background with Newtonian self-gravity and semirelativistic particle kinematics (L189, L209-214); the waves come from the numerical quadrupole (L171). It is not a full-NR calculation. |

## Row "Cosmological gauges for dust collapse" (line 244)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 5 | 244 | "Munoz, Byrnes, Bruni, Hawke: arXiv:2610.23218" | unl. | CONFIRMED | `2610.23218/v1/src/main.tex:21` | Exact. |
| 6 | 244 | subject "Cosmological gauges for dust collapse" | unl. | CONFIRMED | `2610.23218/v1/src/main.tex:41, 89, 93, 113` | 3D fully nonlinear simulations of a dust fluid (Einstein Toolkit, L89; CT_Dust and GRHydro with HRSC, L113), comparing lapse and shift evolution equations (CosmoLapse, L93). |
| 7 | 244 | premise of "The gauge scheme can be borrowed directly": the paper has a gauge scheme that carries dust collapse to black-hole formation | [JUDGEMENT] (premise unl.) | CORRECTED | `2610.23218/v1/src/main.tex:41, 294, 447, 449` | The paper's own conclusion: "The best-performing simulations reach close proximity to a black hole; however, further work on the gauge choice is required for this to be stable" (L41). It proposes a softplus lapse that switches from synchronous to puncture-like slicing (L447); the best Gamma-driver damping is resolution-dependent and spatially varying damping is needed but "further work is necessary to identify which damping to use" (L294, L449). There is no finished scheme to borrow; what transfers is the softplus lapse and the diagnosis of the shift. The matter is a fluid, so the shell-focusing failure it fights is the one particles avoid (row 3). |

## Row "3+1 black-hole formation in the radiation era" (line 245)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 8 | 245 | "3+1 black-hole formation in the radiation era: arXiv:2608.13206" | unl. | CONFIRMED | `2608.13206/v3/src/PRD.tex:14, 18-33, 39, 56` | Ning, Cai, Wang, Yoo; flux-conservative relativistic hydrodynamics in GRChombo, radiation-dominated, superhorizon curvature perturbations. Threshold mu_c ≃ 0.7958 for a spherical Gaussian profile (L440, L505). |
| 9 | 245 | "... arXiv:2609.03051" (3+1, radiation era) | unl. | CONFIRMED | `2609.03051/v1/src/mainv_JJCC_final.tex:162, 173, 279, 306, 811` | Escrivà alone; fully nonlinear 3+1 NR in a radiation-dominated universe, two neighbouring curvature peaks; run with the COSMOS code (acknowledgement, L811). |
| 10 | 245 | "Cosmological Gamma-driver" | unl. | CONFIRMED | `2608.13206/v3/src/PRD.tex:39, 56, 235, 402` | A "cosmologically scaled Gamma-driver" that allows Delta t ∝ a Delta x; about 94 times fewer coarse-level advances than the standard driver in a representative run (L402). Also a conformal-time moving-puncture gauge as a check (L39). |
| 11 | 245 | "multi-peak diagnostics" | unl. | CONFIRMED | `2609.03051/v1/src/mainv_JJCC_final.tex:173, 282, 592` | A nonspherical quasi-local compaction based on the Hawking mass, referenced to a flat-FLRW sphere of equal area; its maximum K_form indicates formation with a transition near 0.56 (L592); double-PBH outcomes identified by two disconnected apparent horizons (L173, L528). |

## Row "Late universe with NR + ray tracing" (line 246)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 12 | 246 | "Macpherson et al.: arXiv:2603.24838, arXiv:2606.05479, arXiv:2606.18437" | unl. | CONFIRMED (precision) | `2603.24838/v1/src/main.tex:30`; `2606.05479/v1/src/main.tex:37, 41`; `2606.18437/v1/src/main.tex:26-28` | 2603.24838 is by Macpherson alone; 2606.05479 by Macpherson and Valogiannis; 2606.18437 by Nguyen, Blake and Macpherson (Macpherson third). "Macpherson et al." is a group label, not an author list. |
| 13 | 246 | subject "Late universe with NR + ray tracing" (all three) | unl. | CONFIRMED | `2603.24838/v1/src/main.tex:40, 93`; `2606.05479/v1/src/main.tex:49, 78-85`; `2606.18437/v1/src/main.tex:214, 222-227` | Einstein Toolkit simulations of large-scale structure with general-relativistic ray tracing (mescaline) for 20 synthetic observers: weak-lensing convergence, apparent evolving dark energy, growth rate from magnitude fluctuations. |

## Row "Weak-field relativistic N-body" (line 247)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 14 | 247 | "Adamek et al.: arXiv:2607.17929, arXiv:2603.24179, arXiv:2508.20606" | unl. | CONFIRMED (precision) | `2607.17929/v1/src/gevolution2.tex:69, 75`; `2603.24179/v2/src/paper_framedragging.tex:167-169`; `2508.20606/v2/src/main.tex:14-15` | Adamek, Christiansen; Magi, Lepori, Adamek (Adamek last); Adamek, Boschetti. |
| 15 | 247 | subject "Weak-field relativistic N-body" (all three) | unl. | CONFIRMED (precision) | `2607.17929/v1/src/gevolution2.tex:65, 82, 94`; `2603.24179/v2/src/paper_framedragging.tex:189, 212, 1053-1056`; `2508.20606/v2/src/main.tex:21, 247` | 2607.17929: gevolution 2.0, GPU (CUDA) relativistic particle-mesh N-body. 2508.20606: curved spatial geometry as a spherical cap embedded in a flat exterior, implemented in gevolution's weak-field expansion in Poisson gauge (L247). 2603.24179 is mainly second-order perturbation theory of weak lensing (Sachs-basis rotation, frame dragging), validated against a relativistic N-body simulation (L1053-1056): a user of the code, not a code paper. |

## Row "Cosmological initial data" (line 248)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 16 | 248 | "Cosmological initial data: arXiv:2501.13046" | unl. | CONFIRMED | `2501.13046/v2/src/main.tex:66, 97, 99, 121` | GRTresna, a multigrid solver of the constraints (CTTK and CTTK-hybrid methods) for fundamental fields around black holes and inhomogeneous cosmological spacetimes; supports periodic cosmological spacetimes (L97). |
| 17 | 248 | "... arXiv:2509.26470" | unl. | CONFIRMED | `2509.26470/v2/src/main_PRD.tex:29-38, 45, 64, 249` | Baumgarte, Clough, Giblin: for a given over-density and mean curvature, solutions of the Hamiltonian constraint need not exist and are not unique (a weak-field and a strong-field branch joining at a maximum); iterative solvers may land on either branch. |
| 18 | 248 | "... arXiv:2607.21308" | unl. | CONFIRMED | `2607.21308/v2/src/cosmology.tex:67, 76, 119-127` | Csukás: parabolic-hyperbolic form of the constraints, evolved outward from regular data at the origin, so no (periodic) boundary condition and a unique solution; flat FLRW free data with a localized anisotropic perfect-fluid perturbation. |

## Row "NR of initial conditions for inflation" (line 249)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 19 | 249 | "NR of initial conditions for inflation: arXiv:2512.13673" | unl. | CONFIRMED | `2512.13673/v1/src/main.tex:61-75, 80, 114, 224` | Giannadakis, Elley, Flauger, Lim; GRChombo with CCZ4; alpha-attractor T-model, critical tensor-to-scalar ratio r_crit ≈ 1e-6 for order-unity inhomogeneities (abstract, meta:2512.13673). |
| 20 | 249 | "... arXiv:2607.06441" | unl. | CONFIRMED (precision) | `2607.06441/v1/src/main.tex:31-39, 69, 120, 205, 362` | Brady, Baumgarte, Clough. Spherically symmetric throughout (L120), BSSN in spherical polar coordinates with a reference metric (L205), asymptotically flat boundaries instead of periodic ones (L69, L362). Not 3+1 in the Cartesian sense. |

## Row "NR implementation of stochastic inflation" (line 250)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 21 | 250 | "Launay, Rigopoulos, Shellard: arXiv:2401.08530, arXiv:2512.14649" | unl. | CONFIRMED | `2401.08530/v2/src/Stochastic_Inflation.tex:26-36`; `2512.14649/v2/src/PRD_v2.tex:56-66` | Exact for both. |
| 22 | 250 | "... arXiv:2610.32592" under "Launay, Rigopoulos, Shellard" | unl. | CONFIRMED (precision) | `2610.32592/v1/src/preword.tex:18, 67-92, 107` | A PhD thesis by Launay alone, assembled from five papers, four of them with Rigopoulos and Shellard (L67-90); the fifth (Launay 2026) is single-author (L84, L92). |
| 23 | 250 | subject "NR implementation of stochastic inflation" | unl. | CONFIRMED | `2401.08530/v2/src/Stochastic_Inflation.tex:43, 892`; `2512.14649/v2/src/PRD_v2.tex:74, 86`; meta:2610.32592 | Langevin sources for the ADM and BSSN equations (2401.08530); BSSN implementation with a slow-roll and an inflection-point (USR) test (2512.14649); the thesis adds a validity criterion and analytic constraint solutions (meta abstract). The constraint statement of 2512.14649 is already corrected in BRIEF_ERRATA row 1.4 (line 262). |

## Row "Lattice inflation and super-horizon freezing" (line 251)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 24 | 251 | "arXiv:2606.14853" (super-horizon freezing) | unl. | CONFIRMED | `2606.14853/v2/src/Manuscript.tex:108-116, 122, 151-153, 213, 273` | Barker, Gladwyn, Zell: an exact FLRW background prevents freezing of superhorizon modes; R_k^2 ~ H^4 in slow roll, worse in USR; criterion with first-order metric perturbations implemented in CosmoLattice; small metric perturbations are necessary, not sufficient (L273). |
| 25 | 251 | "arXiv:2604.00978" | unl. | CONFIRMED | `2604.00978/v3/src/main.tex:133-135, 151, 157, 236` | Saha, Tada, Urakawa: nonlinear lattice on a shear-free, locally FLRW geometry with delta-N observables; the shear-free approximation weakens transiently when the inflaton velocity is very small (L157). |
| 26 | 251 | "arXiv:2506.11795" under "super-horizon freezing" | unl. | CONFIRMED (precision) | `2506.11795/v2/src/main.tex:71-79, 165, 244` | Caravano, Franciolini, Renaux-Petel: USR on the lattice with nonperturbative delta-N maps of zeta. It works in the decoupling limit with an FLRW metric (L165, L244), i.e. in the class that 2606.14853 finds does not freeze superhorizon modes; it is a lattice-USR reference, not a study of freezing. |

## Row "Relativistic Hills mechanism" (line 252)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 27 | 252 | "arXiv:2404.16270" (relativistic Hills mechanism) | unl. | CONFIRMED (precision) | `2404.16270/v1/src/article.tex:105-113, 123, 148-154`; `appendix.tex:114-117` | Manzaneda, Navarrete, Tejeda: tidal separation of stellar binaries by a Schwarzschild black hole with the hybrid relativistic-Newtonian approximation (exact black-hole acceleration, Newtonian binary self-gravity), against Newtonian and 1PN three-body runs. Relativistic in the approximate sense, not full GR. |
| 28 | 252 | "arXiv:2402.02178" | unl. | CONFIRMED (precision) | `2402.02178/v1/src/main.tex:92-97, 113-115, 136-150, 225-229, 513-523` | Zhang, Chen: a binary black hole on a parabolic orbit past a Kerr SMBH, evolved in a frame freely falling with the binary (tidal-tensor approach); tidal disruption of a fraction of the binaries is counted (L523). The paper says full NR is intractable for the problem (L225). |
| 29 | 252 | "arXiv:2610.13294" as relativistic Hills mechanism | unl. | CORRECTED | `2610.13294/v1/src/main.tex:107, 295, 313, 317-324` | Sersante et al. (seven authors): a population model of Hills EMRIs. The binary-MBH encounter is a semi-analytic three-body treatment in Newtonian dynamics (L295, L313); relativity enters only in the later EMRI inspiral (semi-relativistic fluxes L317-319, FEW trajectories L324). It is a Hills-channel rate and eccentricity study, not a relativistic treatment of the separation. |

## Row "Full-GR black-hole clusters and extremal black holes" (line 253)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 30 | 253 | "Full-GR black-hole clusters: arXiv:2505.01495" | unl. | CONFIRMED | `2505.01495/v2/src/apssamp.tex:76-96, 107-109` | Bamber, Shapiro, Ruiz, Tsokaros: a compact (R/M ~ 10) cluster of 25 equal-mass nonspinning black holes in full GR. |
| 31 | 253 | "extremal black holes: arXiv:2511.20567" | unl. | CONFIRMED (precision) | `2511.20567/v2/src/main.tex:56, 62-72, 117` | East alone: spherically symmetric Einstein-Maxwell-Vlasov (charged collisionless particles); beyond a critical point the threshold solution is an extremal black hole. Spherical, not 3D. |

## Row "The NRPIC authors' group" (line 254)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 32 | 254 | "arXiv:2611.12831" | unl. | CONFIRMED | `2611.12831/v1/src/main.tex:21-23` | Wu and Most. |
| 33 | 254 | "arXiv:2504.15978" (same group) | unl. | CONFIRMED | `2504.15978/v2/src/main.tex:52-56, 61` | Boyeneni, Wu, Most; Einstein's equations recast as nonlinear Maxwell-like equations, applied to a binary-black-hole collision. |
| 34 | 254 | "arXiv:2509.19769" (same group) | unl. | CONFIRMED | `2509.19769/v1/src/elsasser.tex:281-289, 296-297` | Krynicki, Wu, Most; Elsasser form of GR in the electrodynamic formulation, gravitational-wave turbulence. Both are the electrodynamic formulation that the NRPIC pusher uses (2611.12831 abstract). |

## Row "Relativistic SIDM collapse" (line 255)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 35 | 255 | "Relativistic SIDM collapse: arXiv:2601.17117" | unl. | CONFIRMED | `2601.17117/v2/src/SIDM_MS.tex:32-46, 60-68, 186-201` | Gu, Jiang, Chen, Li: Misner-Sharp (spherical, fluid) non-equilibrium GR treatment of gravothermal collapse to apparent-horizon formation; seed about 3e-8 of the halo mass (L68). |
| 36 | 255 | "arXiv:2506.17641" as relativistic SIDM collapse | unl. | CORRECTED | `2506.17641/v3/src/sidmacc.tex:36-46, 53, 74, 133, 147-155` | Feng, Yu, Zhong compute no relativistic collapse: they apply the GR-instability criterion of earlier work (1D central dispersion about 0.3c, L74, L133) to a gravothermal model and follow the seed by dark Bondi accretion and baryonic accretion (L147-155). A source of the onset criterion and of seed growth, not of relativistic collapse. |

## Further claims inside the third column, and author attributions as group labels

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 37 | 243 | "Direct competition" for 2605.04487 (implied: same regime as the project) | [JUDGEMENT] (premise unl.) | CORRECTED | `2605.04487/v2/src/main_v3.tex:189, 209-214` | 2605.04487 is a Newtonian-gravity N-body calculation (row 4); it competes with Track B's signal estimate, not with full-relativity particle runs. 2609.14218 is the direct competitor (row 3). |
| 38 | 246 | "potential collaborators for S6" | [JUDGEMENT] | CORRECTED (superseded) | `coord/DECISIONS/0017-delegation.md` item 3 | No session contacts anybody outside (decision 0017). Read: benchmark for S6 only. |
| 39 | 247 | "Comparison code in the weak-field regime" (gevolution) | [JUDGEMENT] | CONFIRMED (precision; superseded in part) | `coord/DECISIONS/0010-one-code-base.md`; BRIEF_ERRATA row 4.5 | Under decision 0010 gevolution is not run here; comparison is with its published results (2607.17929 is public, gevolution2.tex:82). Row 4.5 already records this for sheet B. |
| 40 | 248 | "Foundation of M1" (2501.13046 among them) | [JUDGEMENT] | CONFIRMED (precision) | `coord/DECISIONS/0010-one-code-base.md` consequence 4 | GRTresna is a GRChombo-family code; under decision 0010 its formalism (CTTK) may be used, the code is not; initial-data solves go into AthenaK. 2509.26470's non-uniqueness warning applies to any solver of the program. |
| 41 | 250 | "Starting point and direct comparison for Track E" | [JUDGEMENT] | CONFIRMED (precision) | BRIEF_ERRATA rows 1.4, 4.4; `coord/DECISIONS/0004`, `0010` | The comparison is with the published test cases (geodesic slicing, slow roll and inflection point) of 2512.14649, not with its code. |
| 42 | 252 | "Baselines and comparison for Track F" | [JUDGEMENT] | CONFIRMED (precision) | rows 27-29 | None of the three is full GR: HRNA (2404.16270), a freely falling tidal frame (2402.02178), Newtonian three-body (2610.13294). They are baselines in the approximation hierarchy below F's full-GR runs. |
| 43 | 253 | "Reference for S9 and §8" | [JUDGEMENT] | CONFIRMED (precision) | rows 30-31 | 2511.20567 is Einstein-Maxwell-Vlasov in spherical symmetry: a reference for the extremal-collapse motivation that 2611.12831 itself names (2611.12831 `main.tex:59-65`). |
| 44 | 255 | "Frontier of S3" | [JUDGEMENT] | CONFIRMED (precision) | rows 35-36 | The frontier calculation is 2601.17117 (spherical fluid with GR); 2506.17641 supplies the instability criterion and the growth after it. No 3D kinetic GR calculation of SIDM collapse was found in the forward citations of either (FRONTIER.md, Track C). |

## Judgements without a verdict

Line 243 "Direct competition" (for 2609.14218); 244 "The gauge scheme can be borrowed directly"
(its premise is row 7); 245 "Cosmological Gamma-driver, multi-peak diagnostics" as
relevant to the project; 246 "Benchmark ... for S6"; 247 "Comparison code"; 248 "Foundation
of M1"; 249 "Community focus; experience with initial data and gauges"; 250 "Starting point";
251 "Source of the acceptance criteria for Track E"; 252 "Baselines and comparison"; 253
"Reference for S9 and §8"; 254 "Source of the method; watch its follow-up directions"; 255
"Frontier of S3". Rows 37-44 above check the factual premises of eight of them.
