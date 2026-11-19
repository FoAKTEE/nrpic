# Check of brief lines 224-238 (sections 3.7 and 3.8), open question 20 (line 583) and item 6 of section 15 (line 1750)

Owner kb, work package s37_38, 2026-11-19. Brief: `einstein_vlasov_pic_cosmology_agent_brief.en.md`
(version 2), section 3.7 "Singularities, stability and mathematical results on Einstein-Vlasov"
(lines 224-230) and section 3.8 "Dark matter and strong gravity" (lines 232-237); open question
20 (line 583) and item 6 of section 15 (line 1750), which asks for the current status of stability
results for matter-dominated FLRW under Einstein-Vlasov. Every statement of these lines with a
label, and every specific claim about a cited paper (also where it carries no label: here the
attribution of each listed paper to its topic), is checked at the TeX source in the
knowledge-base store; nothing here rests on an abstract page alone.

Locators: `<key>/<version>/src/<file>:<line>` are lines of the TeX sources under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/` (key = arXiv id with "/" replaced by "_"); the version
checked is the newest in the store. `meta:arxiv-api/<id>` and `meta:inspire/<id>` are the
metadata files `kb-data/meta/arxiv-api/<id>.json` and `kb-data/meta/inspire/<id>.json`;
`iq:<sha16>` is a stored INSPIRE query result `kb-data/meta/inspire/query/<sha16>.json`; all are
written by `harness/bin/nrpic-fetch-arxiv`. The 52 papers cited in lines 224-237 were already in
the store; 13 papers used for rows 50, 59-61 and the answer to item 6 were fetched in this
package (2606.16879, 2607.09326, 2306.17774, 2107.00457, 2012.14241, 2604.14911, 2512.19454,
1402.7085, 1904.13290, 2402.08544, 2609.14755, 1007.0184; metadata only for 1208.4231). The
INSPIRE queries made are listed in `specs/inspire_queries.txt`.

Not repeated from `coord/BRIEF_ERRATA.md` (rows on other brief lines about papers cited here):
1.6 (2601.17117, the mean-free-path direction, line 384), 1.7 (1901.08528 and 1805.09034 on the
r^(-9/4) slope, line 398), 1.14 (1305.2619 treats Schwarzschild only, sheet D), section 5
(defects of 2108.11967, astro-ph/0110561, 2601.17117 and 1305.2619).

Label column: the brief's label for the statement; "(unl.)" marks a specific claim about a paper
or about the literature that carries no label. The one [JUDGEMENT]-type statement (line 230, last
sentence) is listed at the end without a verdict.

Verdicts: CONFIRMED (the source says it, at the locator), CONFIRMED (precision) (right, but the
source qualifies it in a way a reader should know; what in the note), CORRECTED (the source says
something else, or the statement omits what reverses its reading; what is right in the note),
NOT FOUND (what was searched). For a statement of absence ("not found", "does not exist yet")
CONFIRMED means that the searches named in the note found no counter-example. Totals: 60 rows;
23 CONFIRMED, 35 CONFIRMED (precision), 2 CORRECTED, 0 NOT FOUND.

## Line 226: introductions, reviews, variational principle

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | 226 | "Introductions and reviews. arXiv:gr-qc/9604001, ..." | (unl.) | CONFIRMED | `gr-qc_9604001/v1/src/main.tex:12, 24, 35` | Rendall's lectures "An introduction to the Einstein-Vlasov system" (global Cauchy problem, spherical symmetry). |
| 2 | 226 | "... arXiv:1106.1367, ..." | (unl.) | CONFIRMED | `1106.1367/v1/src/article.tex:75, 141` | Andréasson's Living Review, "a guide to theorems on global properties of solutions". |
| 3 | 226 | "... arXiv:2106.09235, ..." | (unl.) | CONFIRMED | `2106.09235/v2/src/boltzmann.tex:38, 47, 89` | Pedagogical introduction to relativistic kinetic theory on curved spacetimes (cotangent-bundle formulation, collision term). |
| 4 | 226 | "... arXiv:1309.2036" | (unl.) | CONFIRMED | `1309.2036/v2/src/AP_kinetic.tex:31, 41` | Geometry of the tangent bundle and kinetic theory of a collisionless gas; largely a review of the geometric structure. |
| 5 | 226 | "Variational principle: arXiv:1910.12152" | (unl.) | CONFIRMED | `1910.12152/v1/src/main.tex:105, 135-137` | Actions for Einstein-Vlasov in Lagrangian and Eulerian pictures; "no variational derivation ... appears to exist in the literature" before it. |

## Line 227: stability theorems

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 6 | 227 | "Stability theorems. Minkowski: arXiv:1707.06141, ..." | (unl.) | CONFIRMED (precision) | `1707.06141/v1/src/SEV4.tex:172, 186, 261, 265, 305` | Massive particles (L261); initial data that coincide with Schwarzschild data outside a ball (L265, L305); velocity support need not be compact (L172). |
| 7 | 227 | "... arXiv:1707.06079, ..." | (unl.) | CONFIRMED (precision) | `1707.06079/v2/src/main.tex:87, 196, 303, 398` | Massive Einstein-Vlasov in harmonic gauge; f_0 compactly supported (L196, L303, L398). |
| 8 | 227 | "... arXiv:1602.02611, ..." | (unl.) | CONFIRMED (precision) | `1602.02611/v1/src/masslessvlasov.tex:57, 64, 88` | Massless particles only (all particles have zero mass). |
| 9 | 227 | "... arXiv:2210.00512" | (unl.) | CONFIRMED (precision) | `2210.00512/v2/src/main.tex:115-116, 145` | Massive, wave coordinates, no compact-support condition on the Vlasov part. |
| 10 | 227 | "Cosmological backgrounds: nonlinear stability of the Milne model under Einstein-Vlasov (arXiv:1709.00267)" | (unl.) | CONFIRMED (precision) | `1709.00267/v1/src/main.tex:363, 373, 381, 390, 419, 500`; `meta:inspire/1709.00267` | Future asymptotic stability of every 3+1 Milne model (vacuum FLRW on a closed hyperbolic 3-manifold, L373, L381) among Einstein-Vlasov solutions with massive particles of compact momentum support (L390, L419), CMCSH gauge (L500). INSPIRE has no record of 1709.00267 (status not-found), in line with brief item 12 of section 15. |
| 11 | 227 | "cosmic no-hair under T³-Gowdy symmetry (arXiv:1306.6223)" | (unl.) | CONFIRMED (precision) | `1306.6223/v2/src/main.tex:152, 160, 167-169, 207-212` | With a positive cosmological constant (L160, L167), which the brief omits although it lists the paper under "cosmological backgrounds"; the solutions are also shown future stable in the class of all solutions (L169). |
| 12 | 227 | "For the stabilization of fluids on non-accelerating expanding backgrounds see arXiv:2002.02119" | (unl.) | CONFIRMED (precision) | `2002.02119/v1/src/fsMilne_v3.tex:97, 119, 130, 142-143` | Irrotational relativistic Euler, p = K rho with 0 < K < 1/3, on the FIXED background a = t on T^3 (L97): not coupled to the Einstein equations, not Vlasov. For dust only integrability of a^-2 is needed (L142). |

## Line 228: phenomena specific to kinetics

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 13 | 228 | "Nonlinear phase mixing near Schwarzschild, valid up to the time-scale set by the nonlinear echo mechanism (arXiv:2609.13394)" | [VERIFIED] | CONFIRMED (precision) | `2609.13394/v1/src/Phase_mixing_EV.tex:18-22, 82, 738-741, 760` | Spherical symmetry (L18, L82) and matter supported on bounded geodesics (L19); the nonlinear result holds up to s ≤ T_f = eps^-1 (log 1/eps)^-2 (L760), motivated by the echo term that cannot be controlled at eps^-1 (L739-741). |
| 14 | 228 | "Rigorous proof of the quadrupole formula (arXiv:2309.00431)" | (unl.) | CONFIRMED (precision) | `2309.00431/v2/src/main.tex:97, 130-136, 178-186` | For solutions close to Minkowski, with explicit remainder estimates under stated assumptions on boundedness, decay and no incoming radiation (L131-136, L178); the assumptions are linked to, not proven for, the global solutions of Lindblad-Taylor. |
| 15 | 228 | "Formation of trapped surfaces (arXiv:2510.12429)" | (unl.) | CONFIRMED (precision) | `2510.12429/v2/src/arma_version.tex:480, 486, 491` | Massless Vlasov only, double null gauge; large-data semi-global existence and dynamical trapped-surface formation. |

## Line 229: near singularities

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 16 | 229 | "The past asymptotics of Bianchi I Einstein-Vlasov differ from those of a perfect fluid (arXiv:gr-qc/0512031)" | [BACKGROUND] | CONFIRMED | `gr-qc_0512031/v1/src/BianchiIVlasov.tex:147-153, 191, 197-199, 929, 954`; `gr-qc_0512031/v1/src/BianchiIVlasov.tex:315-317` | "The dynamical behaviour toward the past singularity of the collisionless matter model differs considerably from the Bianchi type I perfect fluid model" (L197-199); on the past attractor a heteroclinic network (L148-149, L929). Diagonal (non-LRS) Bianchi I, massive and massless particles (L315-317). The label can become [VERIFIED]. |
| 17 | 229 | "Numerical studies of generic singularities (BKL, spikes): arXiv:gr-qc/9805063, ..." | (unl.) | CONFIRMED (precision) | `gr-qc_9805063/v1/src/grf_mpl.tex:103-107, 177, 226, 249` | Gowdy, magnetic Gowdy and U(1)-symmetric spacetimes: symmetric, vacuum except the magnetic field; no Vlasov matter. |
| 18 | 229 | "... arXiv:gr-qc/0312117, ..." | (unl.) | CONFIRMED (precision) | `gr-qc_0312117/v4/src/singular.tex:26-28, 43-44, 442` | Vacuum, no symmetry; notes that only scalar-field matter had been treated without symmetry before (L43-44). |
| 19 | 229 | "... arXiv:0904.1546, ..." | (unl.) | CONFIRMED (precision) | `0904.1546/v2/src/g2spike_prd_resub.tex:88-92, 107-115, 130-133` | Spikes in the Mixmaster regime of G_2 cosmologies, the generalisation of the vacuum Gowdy models (L113-115, L130-133); no matter field. |
| 20 | 229 | "... arXiv:2010.01399" | (unl.) | CONFIRMED | `2010.01399/v1/src/spikepaper.tex:37, 59` | Spike shapes resolved with AMR; vacuum Einstein equations in scale-invariant variables (L59). |
| 21 | 229 | "review arXiv:gr-qc/0201056" | (unl.) | CONFIRMED (precision) | `gr-qc_0201056/v1/src/lr_numsing01_rev.tex:26-27, 229-234, 568` | Berger's Living Review. Common precision for rows 17-21: none of the numerical singularity studies cited evolves Vlasov matter; the review mentions collisionless matter only for collapse of spheroids (L229-234, L568). This bears on open question 18 (line 581). |

## Line 230: Burnett conjecture

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 22 | 230 | "Burnett conjecture. Weak limits of high-frequency vacuum spacetimes satisfy the Einstein equations with massless Vlasov matter" | [BACKGROUND] | CONFIRMED (precision) | `1907.10743/v2/src/main.tex:85, 103, 116-124`; `2506.21779/v1/src/dustvlasov.250626.tex:124`; `1706.09501/v1/src/main.tex:109, 2438-2439` | A conjecture (Burnett 1989, J. Math. Phys. 30, 90; not on arXiv): a sequence of vacuum metrics converging uniformly with derivative bounds has a limit isometric to a solution of Einstein-massless Vlasov, with measure-valued Vlasov fields admitted (1907.10743 L116-121). 2506.21779 L124 states it in the "if and only if" form. The label can become [VERIFIED] for the statement of the conjecture. |
| 23 | 230 | "proofs under U(1) symmetry: arXiv:1706.09501, ..." | (unl.) | CORRECTED | `1706.09501/v1/src/main.tex:71, 75-76, 109, 112` | 1706.09501 does not prove the conjecture. Under POLARIZED U(1) symmetry it proves the reverse direction for a special class: generic local-in-time small-data Einstein-multiple null dust solutions are weak limits of vacuum solutions (L76); it calls itself "a first step towards approaching the questions of Burnett" (L112) and says both of Burnett's questions "remain open" (L109). |
| 24 | 230 | "... arXiv:1907.10743" | (unl.) | CONFIRMED (precision) | `1907.10743/v2/src/main.tex:87, 128-129, 139` | The proof (the conjecture's direction) assumes a U(1) symmetry, not necessarily polarized (L128), and an elliptic gauge in which the bounds hold (L129). |
| 25 | 230 | "The converse holds as well: under U(1) symmetry, small and localized Einstein-massless-Vlasov solutions can be approximated by high-frequency vacuum spacetimes (arXiv:2506.21779)" | [VERIFIED] | CONFIRMED (precision) | `2506.21779/v1/src/dustvlasov.250626.tex:108, 126, 161, 261` | Elliptic gauge, on R^(3+1), compactly supported small regular data (L161); proof by approximating Einstein-massless Vlasov by Einstein-multiple null dust with the number of dusts to infinity (L108, L261); "the first construction ... where the effective limiting matter field is not given by null dusts" (L126). |

## Line 234: gravothermal collapse of SIDM

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 26 | 234 | "Gravothermal collapse of self-interacting dark matter (SIDM). The classic picture: arXiv:astro-ph/0110561, ..." | (unl.) | CONFIRMED | `astro-ph_0110561/v2/src/SIDMGT_Xiv2.tex:28, 55, 192, 220` | Gravothermal fluid formalism, self-similar long-mean-free-path solution, gravothermal catastrophe. |
| 27 | 234 | "... arXiv:astro-ph/0111176" | (unl.) | CONFIRMED | `astro-ph_0111176/v3/src/SMBH_SIDM_Xiv2.tex:18, 32-36` | Black-hole formation as the consequence of relativistic core collapse in SIDM halos. |
| 28 | 234 | "As seeds of supermassive black holes: arXiv:1501.00017, ..." | (unl.) | CONFIRMED (precision) | `1501.00017/v1/src/sidm_smbh_paper.tex:46-50, 72` | A subdominant (f ≲ 0.1) ultra-strongly self-interacting component, not SIDM as all of the dark matter. |
| 29 | 234 | "... arXiv:1812.05088, ..." | (unl.) | CONFIRMED (precision) | `1812.05088/v3/src/GravothermalCollapse6c.tex:53-58, 167` | Subdominant SIDM component, elastic and dissipative scattering, N-body simulations (not fluid). |
| 30 | 234 | "... arXiv:2010.15132" | (unl.) | CONFIRMED | `2010.15132/v3/src/smbh.tex:64-65, 83` | Seed from gravothermal collapse, accelerated by baryons; conditions for the GR instability. |
| 31 | 234 | "Relativistic instability criterion: arXiv:2108.11967" | (unl.) | CONFIRMED | `2108.11967/v2/src/main.tex:66, 83, 85` | TOV equilibria of a truncated Maxwell-Boltzmann distribution; collapse at fractional binding energy 0.035 and central redshift 0.5 (L85). (Typos of its Table 1: errata section 5, not repeated.) |
| 32 | 234 | "Connection with the JWST 'little red dots' (arXiv:2506.17641)" | [VERIFIED] | CONFIRMED | `2506.17641/v3/src/sidmacc.tex:53, 74` | Store has v3 (updated 2026-09-24, `meta:arxiv-api/2506.17641`). |
| 33 | 234 | "triggering the general-relativistic instability requires a central one-dimensional velocity dispersion of about 0.3c" | [VERIFIED] | CONFIRMED | `2506.17641/v3/src/sidmacc.tex:74, 133` | "the 1D central velocity dispersion ... must reach approximately 0.3 c", citing Balberg et al. 2001 and Feng et al. (2108.11967). |
| 34 | 234 | "along the gravothermal evolution only about 10⁻¹⁰-10⁻⁸ of the halo mass can reach this condition" | [VERIFIED] | CONFIRMED (precision) | `2506.17641/v3/src/sidmacc.tex:74, 133, 145`; `2601.17117/v2/src/SIDM_MS.tex:67-68` | The range is quoted from Gad-Nasr et al. for M200 ~ 1e8-1e11 Msun (L133). The same v3 reports (L145) that the full-GR non-equilibrium fluid model of 2601.17117 gives M_GR/M_smfp ≈ 4e-6, "larger than the estimate ... by a factor of 10"; 2601.17117 itself gives a seed of about 3e-8 of the halo mass at horizon formation (L67-68), above the brief's range. |
| 35 | 234 | "a halo of 10⁹ solar masses corresponds to an initial seed of about 1 solar mass, which then grows by accretion" | [VERIFIED] | CONFIRMED (precision) | `2506.17641/v3/src/sidmacc.tex:53, 74, 133, 142, 145, 147, 150, 201` | ~1 Msun is the paper's conservative estimate (L142, L201). The body adds that the non-equilibrium full-GR model gives 200 Msun for a 6.3e9 Msun halo (L145) and that seeds of 1e2-1e3 Msun are plausible (L147); the abstract says "initial seed masses less than 10^3 Msun" (L53). Growth by dark Bondi plus baryonic Eddington accretion (L150, L198). |
| 36 | 234 | "The seed picture for dissipative SIDM: arXiv:2504.00075" | (unl.) | CONFIRMED (precision) | `2504.00075/v2/src/SMBH_GW.tex:118, 137, 144` | Semi-analytic, merger-tree based population model of dSIDM-seeded black holes (LRDs, quasars, GW background), not a collapse calculation. |
| 37 | 234 | "Latest progress (arXiv:2601.17117): the Misner-Sharp formalism is brought into SIDM, the assumption of hydrostatic equilibrium is dropped and general-relativistic effects are added; the outward heat flux is found to drive a rapid expansion of the outer envelope that carries mass away from the core and slows the collapse markedly" | [VERIFIED] | CONFIRMED | `2601.17117/v2/src/SIDM_MS.tex:58-65, 184` | All four elements at L58-65; the effect is in the late short-mean-free-path regime (L62-64). |
| 38 | 234 | "This is a spherically symmetric, fluid-type treatment" | (unl.) | CONFIRMED (precision) | `2601.17117/v2/src/SIDM_MS.tex:158, 186, 201-205, 67-68` | Spherically symmetric non-equilibrium fluid model with conduction (L186, L201-205), followed to apparent-horizon formation, seed ≈ 3e-8 of the halo mass (L67-68). |
| 39 | 234 | "a three-dimensional full-GR kinetic calculation does not exist yet" | (unl.) | CONFIRMED (precision) | `iq:3032b0f66c081770`; `iq:77f08945fdd1ef1d`; `iq:64636c015b786bf5`; `iq:4a5922f5096f3f25`; `2611.12831/v1/src/main.tex:42-44` | No counter-example in: the 14 papers citing 2601.17117 (titles; the only collapse simulations are fluid, e.g. 2607.02151, spherically symmetric), INSPIRE titles "self-interacting dark matter" with relativistic or general relativity after 2024 (1 hit, 2601.17117), abstracts "self-interacting dark matter" with "numerical relativity" (0 hits). The 3D full-GR kinetic code that exists, 2611.12831, is collisionless (no collision operator: errata row 3.1). Holds within these searches. |

## Line 235: dark matter around black holes

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 40 | 235 | "Dark matter around black holes. Spikes: arXiv:astro-ph/9906391, ..." | (unl.) | CONFIRMED | `astro-ph_9906391/v1/src/joe1-xxx.tex:31-35, 51` | Gondolo-Silk spike from adiabatic accretion around the central black hole. |
| 41 | 235 | "... arXiv:1305.2619, ..." | (unl.) | CONFIRMED | `1305.2619/v1/src/SFWpaper.tex:38, 66-67` | Relativistic adiabatic growth in Schwarzschild; density vanishes at 2 R_S, not 4 R_S. (Rows 1.14 and section 5 of the errata on this paper are not repeated.) |
| 42 | 235 | "... arXiv:2411.12007" | (unl.) | CONFIRMED (precision) | `2411.12007/v3/src/mnras_template.tex:103, 125, 155, 188` | Newtonian N-body (modified SWIFT) spike formation in Hernquist halos; the black hole is a Newtonian point mass (L155). |
| 43 | 235 | "Effect on binary-black-hole waveforms: arXiv:2002.12811, ..." | (unl.) | CONFIRMED | `2002.12811/v2/src/main.tex:156-158` | IMRIs with a dark-matter dress that evolves through dynamical-friction feedback; dephasing smaller than with a static dress. |
| 44 | 235 | "... arXiv:2211.01362, ..." | (unl.) | CONFIRMED | `2211.01362/v1/src/main.tex:129, 169` | Accretion disks, DM spikes and scalar clouds distinguished in IMRI/EMRI waveforms, Bayesian analysis. |
| 45 | 235 | "... arXiv:2402.13762" | (unl.) | CONFIRMED (precision) | `2402.13762/v1/src/main.tex:155, 180, 191` | Newtonian N-body code NbodyIMRI (L191) for binaries in spikes; dynamical friction and "stirring". |
| 46 | 235 | "a fully relativistic treatment of EMRI environments: arXiv:2505.09715" | (unl.) | CONFIRMED (precision) | `2505.09715/v2/src/main_v2.tex:70, 89, 97` | Relativistic at adiabatic order on a fixed Kerr background, neglecting the environment's backreaction (L97): relativistic perturbation theory for collisionless environments, not numerical relativity. |
| 47 | 235 | "Full NR with wave-dark-matter environments: arXiv:2210.09254, ..." | (unl.) | CONFIRMED | `2210.09254/v2/src/main.tex:73, 97, 104, 113` | NR of equal-mass binaries in a scalar-field environment; it recalls that particle-DM spikes disperse in N-body simulations of equal-mass mergers (L97). |
| 48 | 235 | "... arXiv:2311.18156, ..." | (unl.) | CONFIRMED | `2311.18156/v2/src/main.tex:95, 101-105` | 10-orbit binary in a complex massive scalar field, constraint-satisfying initial data. |
| 49 | 235 | "... arXiv:2409.01937" | (unl.) | CONFIRMED (precision) | `2409.01937/v2/src/main.tex:70, 87, 106` | Self-interacting scalar (wave) dark matter, isolated and binary black holes. |
| 50 | 235 | "Full NR with a particle-dark-matter environment was not found" | [TO VERIFY] | CORRECTED | `2611.12831/v1/src/main.tex:42-44, 1313, 1338, 1352, 1360, 1385-1390`; `meta:arxiv-api/2611.12831`; `iq:4a5922f5096f3f25`; `iq:371a146e4d145e5a`; `iq:fcf8b40e7ce8db0c`; `iq:dc16c19cdf118343`; `iq:ab3f3c961b9edab7`; `iq:2d6b06309d0b5f4c`; `iq:37c8a029e659b899`; `iq:5a6b59928d3b5674`; `iq:236f6e632a778a7c` | The target paper of the program does it: 2611.12831 (posted 2026-11-09, before the brief's version 2) simulates in full NR "the collapse of two overdensities within a common collisionless envelope, following black-hole formation, binary inspiral and merger, and subsequent mass accretion onto the remnant" (L42-44), 5e6 particles (L1338), common horizon at t ≈ 64.175 M (L1360; see errata row 2.8 for the paper's inconsistent times), strain extracted at R = 40 M (L1352). Caveats: generic collisionless matter, black holes formed in place from Jeans-unstable clumps, idealised; not a pre-existing binary in a dark-matter spike. Apart from it the searches found none: INSPIRE titles collisionless with "numerical relativity" (1 hit, 2611.12831), "dark matter" with "numerical relativity" (1 hit: 2504.20825, binary neutron stars with dark matter as a fermionic fluid), "black hole" with Vlasov since 2015 (17 hits: stationary or test-gas accretion, static equilibria such as 2609.14755), abstracts Einstein-Vlasov with black hole since 2023 (6 hits), and four more with 0-1 relevant hits; papers citing 2611.12831: none yet. A generic web search returned only the wave-DM papers of row 47 and N-body work. Proposed wording: "Full NR of a black-hole binary inside a collisionless (particle) environment: 2611.12831 (clumps that collapse, inspiral and merge inside a common envelope); a binary in a dark-matter spike or halo of particles in full NR was not found." |

## Line 236: dark-matter dress of primordial black holes

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 51 | 236 | "Dark-matter dress of primordial black holes. arXiv:1607.00612, ..." | (unl.) | CONFIRMED | `1607.00612/v2/src/paper2.tex:20, 28-33` | Spikes of DM particles around PBHs from the radiation era. |
| 52 | 236 | "... arXiv:1901.08528, ..." | (unl.) | CONFIRMED | `1901.08528/v2/src/PBH-UCMH-ArXiv-v2.tex:104-107` | Simulated halos with steep profiles around PBHs; WIMP annihilation bound. (Row 1.7 of the errata on the slope attribution is not repeated.) |
| 53 | 236 | "... arXiv:2106.07480, ..." | (unl.) | CONFIRMED (precision) | `2106.07480/v2/src/sections/abstract.tex:1`; `2106.07480/v2/src/sections/building_minispikes.tex:13` | Mini-spike profiles around PBHs; it states that 1712.06383 (listed next in the brief) underestimated the collapsed mini-spike density (L13 of building_minispikes.tex). |
| 54 | 236 | "... arXiv:1712.06383, ..." | (unl.) | CONFIRMED (precision) | `1712.06383/v3/src/PBH_WIMP_final_JCAP-revised-2.tex:9, 52` | WIMP spikes bound to PBHs and the resulting annihilation bounds; criticised by 2106.07480 (row 53). |
| 55 | 236 | "... arXiv:2002.10771" | (unl.) | CONFIRMED | `2002.10771/v2/src/main.tex:17, 37, 48-49` | Accretion of a DM halo onto PBHs and the resulting CMB bounds. |
| 56 | 236 | "effect on the merger rate: arXiv:1805.09034" | (unl.) | CONFIRMED (precision) | `1805.09034/v3/src/main.tex:27, 41, 517` | The effect on the merger rate is "rather small with respect to the case of naked black holes" (L41); the LIGO limit on f_PBH becomes a factor 2 stronger (L517). |

## Line 237: "cosmologically coupled" black holes

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 57 | 237 | "'Cosmologically coupled' black holes. Observational claim: arXiv:2302.07878" | (unl.) | CONFIRMED (precision) | `2302.07878/v1/src/paper_couple_rev.tex:25, 103, 107, 129-131` | k = 3.11 (+1.19, -1.33) at 90 per cent (L130), zero coupling excluded at 99.98 per cent (L103), black holes proposed as the source of dark energy (L107). |
| 58 | 237 | "theoretical discussion: arXiv:2306.11588" | (unl.) | CONFIRMED (precision) | `2306.11588/v2/src/main.tex:34, 67-68, 84-87` | Theory (nonsingular black holes couple with k = 1, "unlikely to be the source of dark energy", L67) plus its own data test (elliptical galaxies at z = 0.8-0.9 favour k > 1; JWST data compatible with k = 1, L68); it also cites a JWST test favouring k ≈ -1 (L86). A single, partly critical theory paper; not a survey of the theoretical discussion. |

## Line 583: open question 20

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 59 | 583 | "Nonlinear stability of matter-dominated FLRW solutions under Einstein-Vlasov. Existing results cover the Milne model (arXiv:1709.00267) and cases with symmetry or a cosmological constant" | (unl.) | CONFIRMED (precision) | `1709.00267/v1/src/main.tex:363, 381`; `2012.14241/v2/src/Milne-EVM-Final.tex:329-330`; `1306.6223/v2/src/main.tex:160, 167-169`; `1402.7085/v1/src/main.tex:50-52`; `1007.0184/v3/src/bianchiarticleV3.tex:40-48`; `1904.13290/v2/src/main.tex:333, 359`; `2306.17774/v1/src/masslessVlasovFLRW.tex:49, 64` | Right, with the list made precise: Milne (vacuum, linear expansion) with massive Vlasov (1709.00267) and with charged Vlasov-Maxwell (2012.14241); Λ > 0: Ringström's monograph (not on arXiv; cited in 1402.7085 L52), T^3-Gowdy (1306.6223), surface symmetry (1402.7085); spatially homogeneous: massive Bianchi I tends to the dust EdS behaviour (Nungesser 2010, 1007.0184 L40-48, described in 1904.13290 L359 as "the massive Einstein-deSitter model is a future attractor"), massless diagonal Bianchi I tends to the radiative EdS model (1904.13290 L333); decelerated inhomogeneous: massless Vlasov FLRW on R^3, spherically symmetric compactly supported perturbations (2306.17774 L49). The Milne model is vacuum: it is not "matter-dominated". |
| 60 | 583 | "the case of an Einstein-de Sitter-type background is [TO VERIFY]" | [TO VERIFY] | CONFIRMED (precision) | `1904.13290/v2/src/main.tex:359`; `2607.09326/v1/src/main.tex:96, 138-149, 300, 307, 311, 317`; `2606.16879/v1/src/main_v2.tex:43, 56, 59, 184, 215, 280`; `iq:2ad127a6360ac3bf`; `iq:9863399afc6fcac4`; `iq:5d79da858c8bc1b1`; `iq:5b4c67a2b9e4822b`; `iq:30f941fcf21612cc`; `iq:f9092f2c3181d6d4`; `iq:38225ca010ad309d`; `iq:36121fac85e7fc78`; `iq:9d4e8863f05b8d19` | Open for Einstein-Vlasov: no stability theorem (or numerical study) for the EdS-type solution of the massive Einstein-Vlasov system beyond spatial homogeneity was found (searches in specs/inspire_queries.txt, plus a generic web search). In 2019: "unknown except in the homogeneous context" (1904.13290 L359). New since June-July 2026, for a fluid: EdS is nonlinearly stable for Einstein-Euler on T^3 with a polytropic equation of state of index n > 3 (proof: 2607.09326, Theorem L140-149; numerical evidence in Gowdy symmetry: 2606.16879 L43, L59, L215, L280), "the first nonlinear stability result for a physically realistic matter-dominated cosmological spacetime" (2607.09326 L307); with dust EdS is unstable (2606.16879 L56, L184; 2607.09326 L138, L317), and the authors conjecture instability for 0 < n < 3 (2607.09326 L300). For kinetic matter they only suggest a Boltzmann model with a suitable collision kernel and cite the massless spherically symmetric result (L311). See "Answer to item 6" below. |

## Line 230: statement of judgement (no verdict)

- Line 230, last sentence: "This is the mathematical basis for 'representing high-frequency gravitational waves by
  massless particles' (S7 in §5)." [JUDGEMENT] of the brief's author. Note for S7: the rigorous
  results (rows 23-25) require U(1) symmetry, an elliptic gauge and small, localised data; the
  conjecture itself is open without symmetry (open question 19, line 582), and 2506.21779 says
  extending the construction without symmetry is open (`dustvlasov.250626.tex:394`).

## Answer to item 6 of section 15 (line 1750) and open question 20 (line 583)

Question: current status of stability results for matter-dominated FLRW under Einstein-Vlasov
(searched 2026-11-19; INSPIRE queries in `specs/inspire_queries.txt`; landscape figure from run
named in the README). Each entry is [VERIFIED] at the locator unless labelled otherwise.

1. The spatially flat, Λ = 0, matter-dominated FLRW solution (Einstein-de Sitter, a ∝ t^(2/3))
   is NOT known to be nonlinearly stable, or unstable, under the massive Einstein-Vlasov system
   outside spatial homogeneity: no theorem and no numerical study found. Within spatial
   homogeneity, non-diagonal Bianchi I solutions close to isotropy with bounded particle
   velocities tend to the dust behaviour and Kasner exponents 1/3 (1007.0184
   `bianchiarticleV3.tex:40-48`), i.e. EdS is a future attractor there (1904.13290 `main.tex:359`).
2. For a fluid the question was settled in 2026: Einstein-Euler with polytropic p = C rho^(1+1/n),
   n > 3, on T^3, Λ = 0: an open family of nonlinearly stable solutions with EdS leading-order
   asymptotics (2607.09326 `main.tex:140-149`), after numerical evidence in Gowdy symmetry with a
   critical index near 3.1 (2606.16879 `main_v2.tex:215`). Dust (pressureless) EdS is unstable
   (linear Sachs-Wolfe/Jeans growth; nonlinear numerics of Marshall 2025, 2502.08095, cited at
   2607.09326 `main.tex:317`); the authors conjecture instability for 0 < n < 3 (`main.tex:300`).
3. Λ = 0, linear expansion (Milne, curvature-dominated, vacuum background): stable with massive
   Vlasov (1709.00267), charged Vlasov-Maxwell (2012.14241), dust (2107.00457 `main.tex:141`: all
   FLRW models with compact negative-Einstein spatial slices are future stable for Einstein-dust,
   which includes open k = -1 dust FLRW), Euler with 0 < K < 1/3 (2301.11191, INSPIRE abstract in
   `iq:9863399afc6fcac4`, source not fetched).
4. Λ = 0, decelerated, massless Vlasov (radiation-like, a ∝ t^(1/2)): stable on R^3 for compactly
   supported spherically symmetric perturbations (2306.17774 `masslessVlasovFLRW.tex:49`); diagonal
   Bianchi I isotropizes to the radiative EdS model (1904.13290 `main.tex:333`).
5. Λ > 0: Ringström's monograph (Einstein-Vlasov with a nonlinear scalar field, not on arXiv;
   1402.7085 `main.tex:52`), T^3-Gowdy (1306.6223), surface symmetry (1402.7085).
6. Past direction: stable Big Bang formation for near-FLRW data of Einstein-scalar field-Vlasov
   (2402.08544 `VlasovSF.tex:152`).
7. Newtonian analogues: Vlasov-Poisson on an expanding torus shows Landau damping for a = t^q,
   q in (0, 1/2), for the plasma (repulsive) case only; for gravity at a ∝ t^(2/3) "one expects the
   so-called Jeans instability to lead to gravitational collapse" (2604.14911
   `Landau-electro.tex:146, 240, 246`). Euler-Poisson has a critical expansion rate at α = 2/3
   (2512.19454 `classical_stability.tex:98-99`).
8. [JUDGEMENT] A cold kinetic gas in FLRW has, for the homogeneous solution, a pressure that falls as
   rho a^-2 ∝ rho^(5/3) (velocity dispersion redshifts as 1/a), the scaling of a polytrope with
   n = 3/2, inside the range 0 < n < 3 for which 2607.09326 conjectures Einstein-Euler instability;
   and physical structure formation is the growth of perturbations of EdS. So a stability theorem
   for massive Einstein-Vlasov EdS in the sense of 2607.09326 is not to be expected, and the open
   problem is better posed as the long-time behaviour (phase mixing versus Jeans growth) of
   near-EdS Einstein-Vlasov data. This is an inference, not a result of the literature.
