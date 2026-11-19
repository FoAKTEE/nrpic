# Check of brief lines 406-444 and 493-553 (problems S5 to S10; directions M1 to M12)

Owner kb, work package s5_s6, 2026-11-19. Brief: `einstein_vlasov_pic_cosmology_agent_brief.en.md`
(version 2): section 5, problems S5 (PBH formation with a free-streaming component), S6 (late-time
multi-stream regions), S7 (Burnett conjecture, "graviton PIC"), S8-S10 (exploratory), lines
406-444; section 6, directions of method innovation M1 to M12, lines 493-553. Every statement of
these lines with the label [BACKGROUND], [TO VERIFY] or [VERIFIED], and every specific claim about
a cited paper (also where it carries no label, and in section 6, which line 495 labels
[JUDGEMENT] as a whole), is checked at the TeX source in the knowledge-base store; nothing here
rests on an abstract page alone.

Locators: `<key>/<version>/src/<file>:<line>` are lines of the TeX sources (and `.bbl` files)
under `/data/haiyangw/nrpic/kb-data/raw/arxiv/` (old identifiers with `_` for `/`, e.g.
`gr-qc_0512031`); the newest version in the store is the one checked. `github:<repo>/<path>` is a
file of an upstream clone under `kb-data/raw/github/` (AthenaK at c5a0d7f9155a).
`meta:inspire/query/<sha16>` is an INSPIRE query result written by `harness/bin/nrpic-fetch-arxiv`
(the queries are listed in `specs/inspire_queries.txt`). Run ids `kb-...` have manifests under
`tracks/kb/runs/`. All 90 papers cited in these lines were in the store; two papers not cited by
the brief were fetched for row 15 (arXiv:2403.03470, arXiv:2402.17530); arXiv:2505.00286
(row 51) was already in the store. The novelty statements of S5, S7 and S8 were searched with
twelve short INSPIRE queries only; the package `tracks/kb/brief_check/novelty/` of the same
worktree does the full novelty search of lines 394-444 independently.

Label column: the brief's label; "(unl.)" marks a specific claim about a paper without a label of
its own (in section 6 under the blanket [JUDGEMENT] of line 495).

Verdicts: CONFIRMED (the source says it, at the locator), CONFIRMED (precision) (right, but the
source qualifies it in a way a reader should know; what in the note; for a statement that
something does not exist: no counterexample in the searches named), CORRECTED (the source says
something else; what is right in the note), NOT FOUND (what was searched). Totals: 69 rows;
32 CONFIRMED, 32 CONFIRMED (precision), 5 CORRECTED, 0 NOT FOUND.

Not repeated here, because `coord/BRIEF_ERRATA.md` already has them: line 426, "whether NRPIC
keeps this [single time step] is [TO VERIFY]" (row 3.7, answered for line 134: yes, one global
step); line 520, 2602.17487 as a cross-check of collisions (row 1.8); line 546, noise "generated
in Fourier space" (row 4.3); 1305.2619 is Schwarzschild only and its defects (row 1.14 and
section 5; line 550 is checked in row 69 only for what it says). Line 546 otherwise is
[JUDGEMENT] (a counter-based generator) and is not checked.

## Line 410: S5 background

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | 410 | "Neutrinos decouple at about 1 MeV" | [BACKGROUND] | CONFIRMED | `1906.08217/v4/src/main.tex:98`; `astro-ph_0306304/v2/src/main.tex:140-145` | "e+e- annihilation and neutrino decoupling at around 1 MeV" (1906.08217); neutrinos go out of equilibrium near 1e10 K, i.e. 0.86 MeV (Weinberg). Label can become [VERIFIED]. |
| 2 | 410 | "when the horizon mass is of order 10⁵ solar masses" | [BACKGROUND] | CONFIRMED | `2002.12778/v2/src/CKSY2021.tex:276-291`; `kb-20261119-154408-2b35ecd` | t = 0.738 (g*/10.75)^(-1/2) (T/1 MeV)^(-2) s and M_H = c^3 t/G = 2.03e5 (t/1 s) M_sun give M_H(1 MeV) = 1.50e5 M_sun (Friedmann recomputation 1.499e5; 3.7e4 at 2 MeV). The rougher normalisation of astro-ph/0608642 (`ms.tex:197-198`, 1 M_sun at 100 MeV) is a factor 15 lower; quote 2002.12778. Label can become [VERIFIED]. |
| 3 | 410 | "from then on neutrinos make up forty to fifty per cent of the radiation energy density" | [BACKGROUND] | CONFIRMED | `astro-ph_0306304/v2/src/main.tex:328-329`; `1906.08217/v4/src/main.tex:98`; `kb-20261119-154408-2b35ecd` | 21/4 of g* = 10.75 (0.488) before e+e- annihilation; f_nu(0) = 0.40523 after it (Weinberg; recomputed 0.40523 from (4/11)^(4/3); (3.36-2)/3.36 = 0.405 from 1906.08217). Through the annihilation, for decoupling at 1 MeV, between 0.411 and 0.491 (run). Label can become [VERIFIED]. |
| 4 | 410 | "and no longer provide a pressure response like a tightly coupled fluid" | [BACKGROUND] | CONFIRMED | `astro-ph_0306304/v2/src/main.tex:31, 140-148` | Freely streaming neutrinos carry an anisotropic stress ("anisotropic inertia") once out of equilibrium. |
| 5 | 410 | "Supermassive primordial black holes above this mass (arXiv:1609.02245, arXiv:1202.3848)" | (unl.) | CONFIRMED (precision) | `1609.02245/v2/src/main.tex:198-209, 372`; `1202.3848/v2/src/smbh.tex:75, 116, 265, 279` | Both are models of PBH seeds of supermassive black holes. 1202.3848 makes PBHs "of the order of 1e5 solar masses" (5e4 to 5e6 in its examples), so at rather than above the decoupling mass; 1609.02245 notes that PBHs with initial mass above about 1e4-1e5 M_sun are severely constrained (L372) and escapes this with patches. |
| 6 | 410 | "Relativistic particles of a hidden sector (arXiv:2209.02735) pose the same kind of problem" | (unl.) | CONFIRMED (precision) | `2209.02735/v2/src/main.tex:38, 53, 67-69` | The paper is about the cut-off of the matter power spectrum set by the relativistic pressure of the hidden-sector particle that drives an early matter era; it has no black holes (no hit). The analogy with S5 is the brief's [JUDGEMENT]. |
| 7 | 410 | "The effect of the thermal history on the threshold through the equation of state has been studied (arXiv:1906.08217), but at the fluid level" | (unl.) | CONFIRMED | `1906.08217/v4/src/main.tex:71, 100, 122-124` | delta_c is a function of the equation-of-state parameter w(T) (L124); the drop of w at e+e- annihilation gives a peak of the mass function near 1e6 M_sun (L71). |

## Lines 414-416: S5 state of the art and requirements

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 8 | 414 | "I found no full-GR kinetic calculation of this problem." | [TO VERIFY] | CONFIRMED (precision) | `meta:inspire/query/94c8632af3899bd8`; `meta:inspire/query/fce9109e54ee2379`; `meta:inspire/query/594fd55ef4b82484`; `meta:inspire/query/1ff023bcaadb927c` | No counterexample in four INSPIRE queries (PBH with neutrino, free streaming, Einstein-Vlasov, anisotropic). Closest: fluid thresholds with a softened equation of state (1906.08217) and an anisotropic perfect fluid (2110.05982, title only). A short search; the full one is the novelty package's. |
| 9 | 416 | "coupled to the dynamical-spacetime fluid module (arXiv:2409.10384)" (also line 525) | (unl.) | CONFIRMED | `2409.10384/v3/src/paper.tex:103, 230-231` | GRMHD in dynamical spacetimes in AthenaK (3+1 conservative Eulerian). |

## Lines 420-428: S6

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 10 | 426 | "AthenaK's AMR uses a single time step for all levels (main text of arXiv:2409.16053)" | [VERIFIED] | CONFIRMED | `2409.16053/v1/src/main.tex:110` | "uniform time stepping across levels", kept from Athena++. That NRPIC keeps it: errata 3.7. |
| 11 | 426 | "multiplies the number of steps by c/v ..., that is, by two to three orders of magnitude" | (unl.) | CONFIRMED (precision) | `kb-20261119-154408-2b35ecd` | Arithmetic of a [JUDGEMENT]: c/v = 1e3 at 300 km/s, 1e2 at 3000 km/s, 1.5e3 at 200 km/s. That the Newtonian step scales with 1/v is the brief's premise, not checked. |
| 12 | 422 | "Fluid NR reaches only the smoothing scales before shell crossing; weak-field codes assume an FLRW background plus small perturbations from the outset" | (unl.) | CONFIRMED (precision) | `1810.05203/v1/src/grnbody.tex:291-294`; `2403.15134/v2/src/void_statistics.tex:335`; `1706.09309/v2/src/br2_arxiv2.tex:130, 194` | A pressureless fluid matches N-body only without stream crossings (1810.05203); the Einstein Toolkit fluid runs start from smoothing scales of 40 and 120 Mpc/h (2403.15134); gevolution is a weak-field expansion whose higher orders are a 1e-4 correction (1706.09309). |
| 13 | 428 | "Key references. arXiv:1908.05683, ..., arXiv:1706.09309" (ten papers) | (unl.) | CONFIRMED (precision) | `1908.05683/v2/src/main.tex:84, 95`; `1810.05203/v1/src/grnbody.tex:19, 39`; `2209.06775/v2/src/paper.tex:65`; `2606.05479/v1/src/main.tex:49`; `2601.20633/v1/src/PRL_main_V2.tex:180`; `2403.15134/v2/src/void_statistics.tex:263-265, 588`; `2408.03049/v1/src/main.tex:38`; `2412.15143/v1/src/letter_P5+.tex:189, 202`; `2406.05048/v2/src/main.tex:85, 963`; `1706.09309/v2/src/br2_arxiv2.tex:77-80` | All relevant (relativistic simulations, ray tracing, backreaction, voids, supernova tests). Only three mention timescape: 2403.15134 (void fraction matters for it), 2412.15143 (claims Pantheon+ favours timescape), 2406.05048 (timescape one of 15 models; DES-SN5YR alone finds no strong evidence for or against any, L963). 2408.03049 finds negligible backreaction on its hypersurfaces. |

## Lines 432-437: S7

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 14 | 432 | "the backreaction of high-frequency gravitational waves is equivalent, in the limit, to massless Vlasov matter (§3.7)" | (unl.) | CONFIRMED (precision) | `2403.03470/v1/src/wavecoordinate.arxiv.240305.tex:119, 136`; `1907.10743/v2/src/main.tex:128-129` | This is Burnett's conjecture; it is proven under gauge assumptions (row 15), not in general. Section 3.7 itself is checked by package s37_38 (rows 22-25). |
| 15 | 434 | "All existing proofs assume U(1) symmetry; the 3+1 case without symmetry is open." | (unl.) | CORRECTED | `2403.03470/v1/src/wavecoordinate.arxiv.240305.tex:119, 143, 179`; `2402.17530/v2/src/superposition_final_AOPDES_first_revision_bis.tex:147`; `2506.21779/v1/src/dustvlasov.250626.tex:392-394` | Huneau and Luk (arXiv:2403.03470, 2024) prove the conjecture "without symmetry assumptions or angular regularity assumptions" for metrics in generalized wave coordinates (with bounds on second derivatives; open without them, L179); earlier proofs: U(1) in an elliptic gauge (1907.10743) and angularly regular metrics in double null gauge (Luk and Rodnianski, arXiv:2009.08968) (L143). Reverse direction without symmetry: Touati (2402.17530) for Einstein-null dust with any finite number of dusts; a genuine (non-dust) massless Vlasov limit is constructed only under U(1) (2506.21779, L392-394). |
| 16 | 435 | "gravitational-wave turbulence (arXiv:2509.19769)" | (unl.) | CONFIRMED | `2509.19769/v1/src/elsasser.tex:277, 294-296` | Elsasser form of GR for gravitational-wave turbulence (theory; refers to earlier numerical work). |
| 17 | 435 | "the Green–Wald conclusion that the effective stress is traceless (arXiv:1011.4920)" | (unl.) | CONFIRMED (precision) | `1011.4920/v2/src/inhomogeneities-paper.tex:39-43, 322-324` | Traceless and of positive energy, provided the matter satisfies the weak energy condition; framework adapted from Burnett's. |
| 18 | 435 | "For related full-NR gravitational-wave cosmology see arXiv:1505.02959, arXiv:1801.08362" | (unl.) | CONFIRMED | `1505.02959/v1/src/letter-GWuni.tex:47-66`; `1801.08362/v2/src/tensor.tex:44` | Vacuum box with nonlinear standing waves (constant-K slicing); Einstein Toolkit with primordial tensor perturbations on a scalar overdensity. |
| 19 | 437 | "State of the art. No numerical work was found." | [TO VERIFY] | CORRECTED | `1505.02959/v1/src/letter-GWuni.tex:47-66, 86-92`; `meta:inspire/query/372c8aa251508922`; `meta:inspire/query/907a8e62298d345f`; `meta:inspire/query/f540d289b8ecd442` | Partly: arXiv:1505.02959, which the brief cites on line 435, tests numerically in full NR that nonlinear standing gravitational waves in a periodic box expand like a radiation fluid (Isaacson's H ∝ L^-2 within 3 per cent, 0.1 per cent time-averaged, even at wavelengths near the Hubble scale), i.e. the homogeneous limit of the averaged backreaction. Not found (three queries): a comparison with massless Vlasov or particles, or a 3+1 test of the conjecture itself. |

## Lines 441-443: S8 to S10

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 20 | 441 | "In the homogeneous case Vlasov matter is known to behave differently from a perfect fluid (arXiv:gr-qc/0512031)" | (unl.) | CONFIRMED | `gr-qc_0512031/v1/src/BianchiIVlasov.tex:149-153, 191, 199` | Bianchi I Einstein-Vlasov: a heteroclinic network toward the past, dynamics unlike any perfect-fluid model of the same Bianchi type. |
| 21 | 441 | "the inhomogeneous case (spikes, mixmaster) with Vlasov matter has no numerical study" | (unl.) | CONFIRMED (precision) | `meta:inspire/query/937b48dae3dc1ef2`; `meta:inspire/query/b6988efd942e7525` | No counterexample in two INSPIRE queries (the full-text one returns dark-matter spikes around black holes and mathematical reviews). |
| 22 | 441 | "Reference points: arXiv:0904.1546, arXiv:2010.01399" | (unl.) | CONFIRMED (precision) | `0904.1546/v2/src/g2spike_prd_resub.tex:88-91, 107-115`; `2010.01399/v1/src/spikepaper.tex:37, 59, 455` | Both vacuum (G2 cosmologies; "no scalar field matter"); reference points for spikes, not for matter. |
| 23 | 442 | "spindle collapse (arXiv:1611.07906, arXiv:1901.04498)" | (unl.) | CONFIRMED | `1611.07906/v2/src/asymflat.tex:90-100`; `1901.04498/v2/src/main.tex:89-93` | 3D NR collapse of prolate collisionless particle systems in asymptotically flat space; East finds a black hole in all cases studied. |
| 24 | 442 | "for the charged case see arXiv:2402.10190, arXiv:2511.20567" | (unl.) | CONFIRMED (precision) | `2402.10190/v1/src/main.tex:166, 187`; `2511.20567/v2/src/main.tex:64-78` | Spherical Einstein-Maxwell-Vlasov: a proof that extremal black holes arise on the threshold (2402.10190) and a numerical study with a region where the threshold solution is extremal (2511.20567), which itself names rotating matter near extremal Kerr as a route to an extremal spinning black hole (L77-78), the question of S9. |
| 25 | 443 | "the more abrupt the transition, the stronger the induced gravitational waves (arXiv:1904.12879, arXiv:2003.10455)" | (unl.) | CONFIRMED (precision) | `1904.12879/v4/src/emd_enh.tex:97-101, 164-169, 370`; `2003.10455/v3/src/pbh_eva.tex:150-151` | Shown as two limits: a sudden transition (time scale much shorter than the Hubble time) enhances the induced waves, a gradual one (comparable to it) suppresses them (companion paper 1904.12878, L370); 2003.10455 applies the sudden case to PBH evaporation. |
| 26 | 443 | "Newtonian hybrid simulations exist (arXiv:2312.12499, arXiv:2306.14961)" | (unl.) | CONFIRMED (precision) | `2312.12499/v2/src/main.tex:111, 157-159`; `2306.14961/v2/src/main.tex:214` | 2312.12499 is a hybrid: Newtonian N-body (CONCEPT) with the matter decaying into a dark-radiation fluid, plus a lattice for the waves. 2306.14961 is GADGET-2 N-body with radiation and the decaying species only in the homogeneous expansion and a rescaled kick, not a hybrid with an inhomogeneous radiation fluid. |
| 27 | 443 | "for the relativistic treatment of decaying matter in N-body see arXiv:1904.11773" | (unl.) | CONFIRMED (precision) | `1904.11773/v1/src/paper190319.tex:86, 116` | Relativistic only at linear order: linear Einstein-Boltzmann perturbations of the other species added to a Newtonian N-body run in N-body gauge. |

## Line 499: M1 boundaries

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 28 | 499 | "For an approach to non-periodic, curved geometries see arXiv:2508.20606" | (unl.) | CORRECTED | `2508.20606/v2/src/main.tex:21, 42, 49, 54-58` | The approach keeps periodic boundaries: a spherical cap of curved FLRW is embedded in a hole cut from a flat FLRW exterior, so the cubic box stays periodic (Einstein-Straus-like). It is a route to curved geometry, not to non-periodic domains; the non-periodic scheme of the brief is 2607.21308 (line 501, row 39). |
| 29 | 499 | "the constraint equations bring global integrability conditions (arXiv:1305.5576, arXiv:2207.03125)" | (unl.) | CONFIRMED | `1305.5576/v2/src/solver.tex:146, 659, 681`; `2207.03125/v2/src/paper.tex:186-201, 249` | Periodic boundaries add an integrability condition to the Hamiltonian constraint (none to the momentum constraint in Bentivegna's set-up, L681); CTTK lists four (one Hamiltonian, three momentum) and fixes the mean K by them (L186-201). |
| 30 | 499 | "the topology of the three-torus has physical effects of its own (arXiv:astro-ph/0602159, arXiv:2210.11426)" | (unl.) | CONFIRMED (precision) | `astro-ph_0602159/v3/src/topograv-aa.tex:2070-2095`; `2210.11426/v4/src/main.tex:163, 183` | astro-ph/0602159: a weak-field residual force from topological images; in a three-torus it cancels for equal sides and leaves an anisotropic term about 1e-9 of dark energy otherwise. 2210.11426: observational (CMB) signatures of the three-torus E1 and other topologies. |

## Line 500: M1 gauge

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 31 | 500 | "factoring out an FLRW reference metric (arXiv:1704.04307)" | (unl.) | CONFIRMED | `1704.04307/v1/src/nonlinear_cosmo_reference.tex:43-48` | Evolves differences from a reference solution. |
| 32 | 500 | "the cosmologically rescaled Gamma-driver (arXiv:2608.13206)" | (unl.) | CONFIRMED | `2608.13206/v3/src/PRD.tex:39, 56` | Delta t proportional to a Delta x. |
| 33 | 500 | "the lapse equation modified for dust collapse (arXiv:2610.23218)" | (unl.) | CONFIRMED | `2610.23218/v1/src/main.tex:41, 210` | Compares proposed lapse equations in a matter era and proposes its own. |
| 34 | 500 | "slicings that avoid gauge shocks (arXiv:2207.06376, arXiv:gr-qc/0210050)" | (unl.) | CONFIRMED | `2207.06376/v1/src/main.tex:57, 78`; `gr-qc_0210050/v2/src/manuscript.tex:160` | Alcubierre's shock-avoiding Bona-Masso slicing and its tests. |
| 35 | 500 | "Comoving synchronous gauge converges poorly with particles (arXiv:1810.05203)" | (unl.) | CONFIRMED | `1810.05203/v1/src/grnbody.tex:287-294` | The particles do not move, so deposition errors accumulate secularly; the authors use a pressureless fluid in that gauge instead. |
| 36 | 500 | "For more general discussion see arXiv:1809.07010, arXiv:2001.00394" | (unl.) | CONFIRMED | `1809.07010/v1/src/stability-gauge-problem-Anna-arXiv.tex:55`; `2001.00394/v2/src/gauges12.tex:38` | 2001.00394 finds synchronous, comoving, N-body, spatially flat and uniform-density gauges unviable with nonlinear structures, the longitudinal gauge viable. |

## Line 501: M1 initial data

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 37 | 501 | "Constraint solving for particle distributions: CTTK and GRTresna (arXiv:2207.03125, arXiv:2501.13046)" | (unl.) | CONFIRMED (precision) | `2207.03125/v2/src/paper.tex:99, 121`; `2501.13046/v2/src/main.tex:97` | General solvers demonstrated with scalar fields; GRTresna: "scalar fields are the only matter sources included in the current version", other matter by copying the template. Neither treats particles. |
| 38 | 501 | "existence of solutions and branches (arXiv:2509.26470)" | (unl.) | CONFIRMED | `2509.26470/v2/src/main_PRD.tex:45, 64` | In a toy model (see package s35, row on line 203). |
| 39 | 501 | "a non-periodic scheme (arXiv:2607.21308)" | (unl.) | CONFIRMED | `2607.21308/v2/src/cosmology.tex:76` | Constraints evolved outward from the origin, no boundary conditions; perfect fluid. |
| 40 | 501 | "super-horizon long-wavelength solutions (arXiv:1503.03934)" | (unl.) | CONFIRMED | `1503.03934/v2/src/PERTURBATION_PBH_sub_v2.tex:48-50` | |
| 41 | 501 | "relativistic N-body initial conditions (arXiv:1702.03221, arXiv:2110.11249, arXiv:2001.07968)" | (unl.) | CONFIRMED | `1702.03221/v2/src/backscaling-arxiv.tex:110, 140`; `2110.11249/v1/src/main.tex:25, 47`; `2001.07968/v2/src/main.tex:20, 32` | |
| 42 | 501 | "East et al. satisfy the constraints by adjusting the particle masses (arXiv:1908.05683)" | (unl.) | CONFIRMED (precision) | `1908.05683/v2/src/main.tex:220-223, 247-256` | The constraints are solved in the conformal thin-sandwich formulation for the nonlinear corrections (L220-223); then the particle masses are adjusted (subpercent) so that the density estimated from the particles matches the input density at every particle (L247-256). |

## Lines 505-508: M2

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 43 | 505 | "High-order shape functions and filtering (arXiv:2605.15260)" | (unl.) | CONFIRMED | `2605.15260/v1/src/conclusion.tex:12-14`; `2605.15260/v1/src/intro.tex:17` | Electromagnetic PIC (Entity), shapes up to 11th order and current filtering (1/4, 1/2, 1/4 passes). |
| 44 | 506 | "deposition by tetrahedral tessellation gives a noise-free density both before and after shell crossing (arXiv:1111.3944, arXiv:1210.6652, arXiv:1501.01959, arXiv:1909.00008)" | (unl.) | CONFIRMED (precision) | `1111.3944/v3/src/method.tex:149, 170, 215-218`; `1210.6652/v2/src/tet-pm.tex:45`; `1501.01959/v2/src/paper.tex:737`; `1909.00008/v2/src/complexity.tex:183, 217` | Holds while the sheet is resolved; under strong mixing (inner haloes) a fixed tessellation fails: elements must be refined (1501.01959 L737, "the most important shortcoming of TetPM") or the scheme switches to N-body there (1909.00008). |
| 45 | 506 | "Giblin et al. have already used a sheet representation in BSSN (arXiv:1810.05203)" | (unl.) | CORRECTED | `1810.05203/v1/src/grnbody.tex:324-335, 357-370, 522-525` | The phase-space sheet is the continuum picture of the paper; it is discretised into particles deposited by cloud-in-cell or a tri-cubic spline (L357-370), and the Jacobian of the sheet map only places the initial particles (L522-525). No tessellation deposition is used. |
| 46 | 507 | "The δf method: particles represent only the departure from a known distribution (arXiv:2010.07321)" | (unl.) | CONFIRMED (precision) | `2010.07321/v1/src/main.tex:136, 142-144` | For relic neutrinos in Newtonian cosmological N-body, with an analytic background distribution. |
| 47 | 508 | "Systematic effects of discreteness: arXiv:astro-ph/0702575, arXiv:1606.02038, arXiv:1801.03906" | (unl.) | CONFIRMED (precision) | `astro-ph_0702575/v2/src/hdm1_v3.tex:155-180`; `1606.02038/v1/src/wdm_discreteness.tex:12-13, 42`; `1801.03906/v1/src/ics.tex:16, 52` | 1801.03906 reduces the shot noise of neutrino particles through their initial conditions. |

## Line 512: M3

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 48 | 512 | "Electromagnetic PIC guarantees the discrete Gauss law through charge-conserving current deposition" | [BACKGROUND] | CONFIRMED | `2605.15260/v1/src/intro.tex:11-12`; `1609.03053/v3/src/gempic.tex:280-282, 316` | Deposition schemes that satisfy the discrete continuity equation, because PIC avoids solving div E = 4 pi rho (Entity); GEMPIC conserves the discrete Gauss law as a Casimir. The originals (Villasenor-Buneman 1992, Esirkepov 2001) are not on arXiv. Label can become [VERIFIED]. |
| 49 | 512 | "the original paper points out that it suits Yee-grid and constrained-transport discretizations" | [VERIFIED] | CONFIRMED (precision) | `2111.05282/v1/src/paper.tex:134-140, 1920-1930` | "potentially suitable": a natural staggered discretisation for Yee and constrained transport; first order and flux-conservative. |
| 50 | 512 | "the energy–momentum flux equation of matter has source terms (exchange with the gravitational field), unlike charge" | [TO VERIFY] | CONFIRMED (precision) | `2111.05282/v1/src/paper.tex:980-997, 1003-1022, 1924` | In dGREM the matter energy-momentum equation has the exchange term Q_a; the sum of gravitational and matter energy-momentum obeys a flux-conservative law without source terms (L1003-1022), the closer analogue of charge for a deposition scheme [JUDGEMENT]. |
| 51 | 512 | "the hyperbolicity and numerical stability of dGREM as an evolution system have to be established first (arXiv:2211.13659)" | [TO VERIFY] | CONFIRMED (precision) | `2111.05282/v1/src/paper.tex:1966-1973`; `2211.13659/v4/src/pure_tetrad_arxiv_v4.tex:2622-2624, 2638-2657`; `2505.00286/v3/src/df-einstein.tex:954, 1878-1880` | Still open with matter. 2211.13659: its 3+1 TEGR system equals dGREM; in vacuum it can be cast in the symmetric hyperbolic ERW/Buchman-Bardeen form under gauge conditions when the Hamiltonian constraint holds; "hyperbolicity ... coupled with matter is still open". First numerical vacuum scheme: 2505.00286 (polytopal discrete de Rham), where preservation of a discrete constraint is "currently unknown". |

## Line 516: M4

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 52 | 516 | "Einstein–Vlasov has a variational principle (arXiv:1910.12152)" | (unl.) | CONFIRMED | `1910.12152/v1/src/main.tex:135-137` | Actions in Lagrangian and Eulerian pictures. |
| 53 | 516 | "geometric PIC built from an action or a Poisson bracket (arXiv:1609.03053, arXiv:1612.06734) performs very well on long-time energy and Casimir invariants" | (unl.) | CONFIRMED (precision) | `1609.03053/v3/src/gempic.tex:258-261, 316-319`; `1612.06734/v1/src/16APSrev4_arXiv.tex:410, 500` | Casimirs (discrete Gauss law, div B) are conserved exactly by construction; energy is not exact but shows "excellent long-time behaviour" (backward error analysis). 1612.06734 is a review that ends with GEMPIC. |
| 54 | 516 | "symplectic integrators in NR (arXiv:0807.0734); energy-conserving geodesic integrators (arXiv:1801.02378)" | (unl.) | CONFIRMED | `0807.0734/v2/src/grsymp.tex:79-81`; `1801.02378/v3/src/paper1_geodesics_arxiv.tex:88, 103` | |

## Lines 524-526: M6

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 55 | 524 | "null-geodesic pushing (arXiv:1801.02378, arXiv:1208.3927)" | (unl.) | CONFIRMED | `1801.02378/v3/src/paper1_geodesics_arxiv.tex:103, 178`; `1208.3927/v2/src/geod3p1.tex:40` | 3+1 null and timelike geodesics. |
| 56 | 526 | "Particles + puncture black holes: already a capability of Wu and Most" | (unl.) | CONFIRMED (precision) | `2611.12831/v1/src/main.tex:370, 678, 886, 937` | In the paper black holes form by collapse and are evolved in moving-puncture gauge with lapse-based particle excision; it has no run with puncture initial data plus self-gravitating particles (its Kerr tests use a fixed Kerr-Schild metric). In this repository the combination exists (punctures in `nrpic_cf`; several punctures in core-v0.3, CLAUDE.md). |

## Lines 530-534: M7, M8

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 57 | 530 | on-the-fly ray tracing "(arXiv:2209.06775, arXiv:2107.06306, arXiv:2110.00893)" | (unl.) | CONFIRMED (precision) | `2209.06775/v2/src/paper.tex:235-241`; `2107.06306/v1/src/ms.tex:1037, 1043`; `2110.00893/v1/src/lcmetric.tex:71, 464` | All three are post-processing tools; none integrates during an NR evolution. BiGONLight's forward method is meant to be usable on the fly but runs in post-processing (L1043); LC-Metric examines an on-the-fly prescription for the ISW signal of N-body runs. |
| 58 | 534 | "Gauge-invariant characterization of spacetime (arXiv:2211.08133, arXiv:2602.00155)" | (unl.) | CONFIRMED | `2211.08133/v2/src/Robyn_1_CQG_v1.tex:55, 78`; `2602.00155/v1/src/paper.tex:4, 100-107, 145` | EBWeyl and its successor aurel. |
| 59 | 534 | "horizon finding in expanding backgrounds (arXiv:2505.15912, arXiv:2306.11810)" | (unl.) | CONFIRMED (precision) | `2306.11810/v2/src/Spinning_PBHs.tex:107, 298`; `2505.15912/v2/src/main.tex:86, 621, 633` | 2306.11810 has an appendix on apparent horizons in FLRW. BHaHAHA (2505.15912) is a general, infrastructure-agnostic finder; no expanding or FLRW case in it. |
| 60 | 534 | "non-spherical quasi-local compaction (arXiv:2609.03051, arXiv:2304.13284)" | (unl.) | CORRECTED | `2609.03051/v1/src/mainv_JJCC_final.tex:173`; `2304.13284/v2/src/compaction.tex:132, 168, 275-277` | Only 2609.03051 is non-spherical. 2304.13284 works in spherical symmetry throughout (re-interprets the Shibata-Sasaki compaction function and its gauge dependence); cite it for the compaction function, not for the non-spherical extension. |
| 61 | 534 | "gravitational-wave extraction in non-asymptotically-flat domains (arXiv:2111.09163)" | (unl.) | CONFIRMED (precision) | `2111.09163/v2/src/prd_v1.tex:74, 154` | A covariant transverse-traceless projection of the extrinsic curvature on a hypersurface, made for secondary (scalar-induced) waves. |
| 62 | 534 | "averages and foliations (arXiv:2408.03049, arXiv:2409.00024)" | (unl.) | CONFIRMED | `2408.03049/v1/src/main.tex:38, 52`; `2409.00024/v1/src/main.tex:47-49` | |

## Line 542: M10

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 63 | 542 | "joined through the existing dictionaries (arXiv:1101.3555, arXiv:1505.04756, arXiv:1711.06681, arXiv:2404.02783)" | (unl.) | CONFIRMED (precision) | `1101.3555/v3/src/0321821.tex:427, 512`; `1505.04756/v2/src/finalpaper.tex:204, 315`; `1711.06681/v2/src/main.tex:184, 310`; `2404.02783/v3/src/main.tex:53, 79` | 1101.3555 and 1505.04756 (N-body gauge) are dictionaries; 1711.06681 uses the Green-Wald dictionary to compare GR and Newtonian runs; 2404.02783 combines gevolution and Gadget-4 outputs (a hybrid, not a dictionary). |
| 64 | 542 | "AMR engineering experience: arXiv:2112.10567, arXiv:2101.12149" | (unl.) | CONFIRMED (precision) | `2112.10567/v3/src/main.tex:182-188`; `2101.12149/v2/src/warpx.tex:85, 100, 112` | 2101.12149 is about porting WarpX (AMR through AMReX) to GPUs, not about AMR as such. |
| 65 | 542 | "The cyclic zoom built into AthenaK (arXiv:2504.16802)" | (unl.) | CONFIRMED (precision) | `2504.16802/v2/src/main.tex:82`; `github:IAS-Astrophysics__athenak/src/cyclic_zoom/cyclic_zoom.cpp` | In upstream AthenaK (c5a0d7f9155a) and in this repository (`athenak/src/cyclic_zoom/`); demonstrated for GRMHD only, no particles in the paper. |

## Line 550: M12

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 66 | 550 | "Methods and accuracy comparisons for pure multi-black-hole initial data exist (arXiv:0710.0879, arXiv:0711.1165, arXiv:1004.1353)" | (unl.) | CONFIRMED | `0710.0879/v2/src/first.tex:28, 102`; `0711.1165/v2/src/second.tex:63-65, 205`; `1004.1353/v2/src/Punc_N.tex:61-64, 177, 210` | Three- and four-hole evolutions; 1004.1353 compares solved with approximate analytic data. |
| 67 | 550 | "public AthenaK ships problem generators for one and two punctures (§2.2)" | (unl.) | CONFIRMED | `github:IAS-Astrophysics__athenak/src/pgen/z4c/z4c_one_puncture.cpp`; `github:IAS-Astrophysics__athenak/src/pgen/z4c/two_punctures/z4c_two_puncture.cpp` | Upstream clone at c5a0d7f9155a. |
| 68 | 550 | "Three things are new: conformally flat data for three or more punctures; ..." | (unl.) | CONFIRMED (precision) | `0711.1165/v2/src/second.tex:205`; `1004.1353/v2/src/Punc_N.tex:61, 210` | New for AthenaK only: three- and four-puncture conformally flat data exist in the literature (approximate in 0711.1165, solved in 1004.1353). Superseded by core-v0.3, which has several punctures with momentum and spin (`puncture_setup`, CLAUDE.md). |
| 69 | 550 | "one can start from the adiabatically grown spike distribution, arXiv:1305.2619" | (unl.) | CONFIRMED | `1305.2619/v1/src/SFWpaper.tex:64-69` | Fully relativistic adiabatic growth in Schwarzschild; Kerr and the paper's defects: errata 1.14 and section 5. |
