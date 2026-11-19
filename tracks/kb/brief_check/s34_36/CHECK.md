# Check of brief lines 186-195 and 217-223 (sections 3.4 and 3.6)

Owner kb, work package s34_36, 2026-11-19. Brief: `einstein_vlasov_pic_cosmology_agent_brief.en.md`
(version 2), section 3.4 "Early universe (problems dominated by scalar fields)" and section 3.6
"Structure formation and gravitational waves in the early matter-dominated era". Every statement
of these lines with a label, and every specific claim about a cited paper (also where it carries
no label: here the attribution of each listed paper to its topic), is checked at the TeX source in
the knowledge-base store; nothing here rests on an abstract page alone.

Locators: `<key>/<version>/src/<file>:<line>` are lines of the TeX sources under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/`; the version checked is the newest in the store.
`meta:arxiv-api/<id>` and `meta:inspire/<id>` are the metadata files
`kb-data/meta/arxiv-api/<id>.json` and `kb-data/meta/inspire/<id>.json` written by
`harness/bin/nrpic-fetch-arxiv`. All 60 cited papers, and the later paper 2607.06441 used in row
9, were already in the store; nothing was fetched. One INSPIRE citation query was made (row 9).
None of these lines has a row in `coord/BRIEF_ERRATA.md`; rows about 2512.14649 elsewhere in it
(row 1.4, brief line 262; section 5) are not repeated here.

Label column: the brief's label for the statement; "(unl.)" marks a specific claim about a paper
that carries no label; "[title only verified]" is the brief's own label on line 221. No statement
of these lines carries [BACKGROUND] or [TO VERIFY]. The one [JUDGEMENT]-type statement (line 188)
is listed at the end without a verdict.

Verdicts: CONFIRMED (the source says it, at the locator), CONFIRMED (precision) (right, but the
source qualifies it in a way a reader should know; what in the note), CORRECTED (the source says
something else or the statement omits what reverses its reading; what is right in the note),
NOT FOUND (what was searched). Totals: 66 rows; 45 CONFIRMED, 17 CONFIRMED (precision),
4 CORRECTED, 0 NOT FOUND.

## Line 190: initial conditions for inflation

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | 190 | "Initial conditions for inflation. arXiv:1511.05143, ..." | (unl.) | CONFIRMED | `1511.05143/v2/src/main.tex:70-80, 172` | Full Einstein equations with a scalar inflaton in 3+1 dimensions; an initially expanding, highly inhomogeneous, gradient-dominated universe can enter inflation (East, Kleban, Linde, Senatore). |
| 2 | 190 | "... arXiv:1608.04408, ..." | (unl.) | CONFIRMED | `1608.04408/v2/src/inhomoinf.tex:88, 109` | 3+1 simulations of inhomogeneous field and extrinsic-curvature initial data; small-field inflation is much less robust than large-field inflation. |
| 3 | 190 | "... arXiv:1712.07352, ..." | (unl.) | CONFIRMED | `1712.07352/v2/src/inhomoinf2.tex:73, 122-123` | Large tensor (transverse-traceless extrinsic-curvature) perturbations on top of scalar inhomogeneities, small-field models. |
| 4 | 190 | "... arXiv:1910.12547, ..." | (unl.) | CONFIRMED | `1910.12547/v3/src/ConvexConcave_Resubmit.tex:91, 111, 213` | Analytic criterion on the shape of the potential, tested with 3+1 NR; convex potentials are more robust than concave ones. |
| 5 | 190 | "... arXiv:2011.12190, ..." | (unl.) | CONFIRMED | `2011.12190/v2/src/main.tex:125, 153` | 3+1 NR; Starobinsky and Higgs inflation with inhomogeneous field, velocity or equation of state. |
| 6 | 190 | "... arXiv:2212.04479, ..." | (unl.) | CONFIRMED | `2212.04479/v2/src/main.tex:17, 44-45, 90` | Initial data with non-zero momentum density (scalar field and its time derivative inhomogeneous), single- and two-field models. |
| 7 | 190 | "... arXiv:2405.03490, ..." | (unl.) | CONFIRMED | `2405.03490/v2/src/main.tex:73, 100` | Large kinetic inhomogeneities reduce the number of e-folds; sub-Planckian models are not robust. |
| 8 | 190 | "... arXiv:2304.12150" | (unl.) | CONFIRMED (precision) | `2304.12150/v1/src/inflation_paper2.tex:103, 138, 146, 378` | A tetrad-formulation code with gauge-invariant diagnostics that reaches the opposite conclusion to rows 1-7: "inflation does not solve the homogeneity and isotropy problems ... beginning from generic initial conditions following a big bang" (L378). The list is not a consensus. |
| 9 | 190 | "Latest result: for the α-attractor T-model with order-one gradient and kinetic inhomogeneities, obtaining 60 e-folds requires a characteristic scale of about 0.02 m_P (arXiv:2512.13673)" | [VERIFIED] | CONFIRMED (precision) | `2512.13673/v1/src/main.tex:80, 112-116, 183, 273, 276, 305, 309`; `2512.13673/v1/src/main.tex:238`; `2607.06441/v1/src/main.tex:46, 61, 69`; `meta:arxiv-api/2607.06441`; `meta:inspire/2512.13673` | mu_crit ≈ 0.020 m_P (non-reduced Planck mass, L116) holds for the out-of-phase branch (theta = pi) under the stated assumption that the homogeneous solution gives 100 e-folds (L80, L114, L183, L309); in-phase perturbations need 0.025 m_P (L238, L276), gradient-only data 0.017 m_P (L305); only horizon-scale modes were simulated (L311). "Order one" means mean gradient and kinetic energies equal to V(phi_0) (L273). "Latest": at the brief's date a later NR study exists, 2607.06441 (posted 2026-07-07; spherical symmetry, asymptotically flat; cites 2512.13673 at L61), found by the INSPIRE query refersto:recid:3093098 (`kb-data/meta/inspire/query/48e651357ea82ee5.json`, 2 hits). |
| 10 | 190 | "corresponding to a tensor-to-scalar ratio of about 10⁻⁶ (arXiv:2512.13673)" | [VERIFIED] | CORRECTED | `2512.13673/v1/src/main.tex:80, 114, 135, 238, 276, 305, 309`; run kb-20261119-150703-95bba8b | 10⁻⁶ is the abstract's rounding (L80). The body gives r_crit ≈ 5.6×10⁻⁶ for mu_crit = 0.020 m_P (L114, L238, L309), 8.7×10⁻⁶ in-phase (L238), 4.0×10⁻⁶ gradient only (L305), each a lower bound for 100 homogeneous e-folds (L80, L112). Eq. (r), r = 16 pi mu²/(m_P² N*²) with N* = 60 (L135, L138), reproduces all body pairs to 1.5 per cent (run kb-20261119-150703-95bba8b); log10(5.6×10⁻⁶) = -5.25, nearer 10⁻⁵ than 10⁻⁶. Quote "r_crit ≈ 6×10⁻⁶ (≳ 5.6×10⁻⁶; ≈ 10⁻⁶ in the abstract)". Defect of the source: L276 pairs mu = 0.025, 0.020 with r = 5.6, 8.7 ×10⁻⁶ in the reverse order (same run; ERRATA_ROWS section 5). |

## Line 191: NR implementation of stochastic inflation

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 11 | 191 | "NR implementation of stochastic inflation. arXiv:2401.08530, ..." | (unl.) | CONFIRMED (precision) | `2401.08530/v2/src/Stochastic_Inflation.tex:43, 782, 836, 879, 892` | The formulation, not an implementation: Langevin sources for the ADM and BSSN equations that "enable a well-posed implementation for 3+1 numerical relativity simulations" (L43, L892). Its own example integrates long-wavelength uniform-field-gauge Langevin equations with the Stratonovich evolver of Mathematica (L836), "where we don't need a full Numerical Relativity code" (L879). |
| 12 | 191 | "... arXiv:2512.14649, ..." | (unl.) | CONFIRMED | `2512.14649/v2/src/PRD_v2.tex:74, 480, 783` | The implementation: the stochastic equations in BSSN in GRTeclyn (code ISTORIz), slow-roll and ultra-slow-roll cases. (Constraint statement and source defects of this paper: `coord/BRIEF_ERRATA.md` rows 1.4 and section 5, not repeated.) |
| 13 | 191 | "... arXiv:2610.32592" | (unl.) | CONFIRMED (precision) | `2610.32592/v1/src/conclusion.tex:8`; `2610.32592/v1/src/chap_ICNR.tex:82, 214` | A doctoral thesis (single author, "this thesis"), collecting the two papers above with constraint-solving initial data and extensions; not a separate peer-reviewed implementation. |

## Line 192: slow contraction and bounces

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 14 | 192 | "Slow contraction and bounces. arXiv:0808.0542, ..." | (unl.) | CONFIRMED | `0808.0542/v2/src/ekpaper.tex:39, 59-69, 206-208` | Ekpyrotic (w > 1) contraction from highly inhomogeneous and anisotropic data, numerical Einstein-scalar evolution with variations along a single spatial dimension (L208). |
| 15 | 192 | "... arXiv:2006.01172, ..." | (unl.) | CONFIRMED | `2006.01172/v1/src/Q0paper_v4.tex:60, 77, 110` | "Supersmoothing" by slow contraction, non-perturbative NR. |
| 16 | 192 | "... arXiv:2006.04999, ..." | (unl.) | CONFIRMED | `2006.04999/v2/src/ekp_sm_p2_pjs-ai.tex:37, 59, 76` | NR simulations of slow contraction over a wide range of initial conditions. |
| 17 | 192 | "... arXiv:2103.00584, ..." | (unl.) | CONFIRMED | `2103.00584/v1/src/paper_ultralocality_submission.tex:40, 61-64, 122` | Ultralocal stage before homogeneity in slow contraction. |
| 18 | 192 | "... arXiv:2104.12293, ..." | (unl.) | CONFIRMED | `2104.12293/v1/src/Ijjas-et-al-rapidity.tex:68, 83, 110-114` | Variations along two directions and several modes enhance the smoothing. |
| 19 | 192 | "... arXiv:2404.00867, ..." | (unl.) | CONFIRMED | `2404.00867/v2/src/CompContractionInflation.tex:44, 65-66, 87` | Slow contraction against inflation with a pair of tetrad codes; slow contraction smooths, inflation "fails these tests" (L66). |
| 20 | 192 | "... arXiv:1308.3044, ..." | (unl.) | CONFIRMED | `1308.3044/v1/src/ver6.tex:11, 30, 51` | Non-perturbative numerical study of perturbations through a non-singular bounce. |
| 21 | 192 | "... arXiv:2206.08466" | (unl.) | CONFIRMED | `2206.08466/v2/src/main.tex:16, 50-61` | Black holes evolved through a non-singular bounce (ghost plus ordinary scalar). |

## Line 193: preheating and oscillons

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 22 | 193 | "Preheating and oscillons. arXiv:1907.10601, ..." | (unl.) | CONFIRMED | `1907.10601/v3/src/GABERel.tex:65, 88, 342` | Preheating in full NR (GABERel). |
| 23 | 193 | "... arXiv:1912.09658, ..." | (unl.) | CONFIRMED | `1912.09658/v3/src/osciGRarXiv17.tex:99, 121` | Oscillon preheating in full GR against FLRW-background runs. |
| 24 | 193 | "... arXiv:2112.07626, ..." | (unl.) | CONFIRMED | `2112.07626/v2/src/gws_gr.tex:41, 88` | Gravitational waves from oscillon preheating in full GR, with the gauge question of the extraction. |
| 25 | 193 | "... arXiv:2311.01504, ..." | (unl.) | CONFIRMED (precision) | `2311.01504/v2/src/gaugepreheatBSSN_arxiv_v3.tex:76, 98, 121, 144` | Gauge preheating: a pseudoscalar inflaton coupled to a U(1) gauge field, BSSN; nearly all the energy goes into gauge-field radiation (L121), so this is not a problem dominated by scalar fields (section heading). |
| 26 | 193 | "... arXiv:2304.01673, ..." | (unl.) | CONFIRMED | `2304.01673/v2/src/main.tex:76, 90` | Oscillon formation during preheating with GR. |
| 27 | 193 | "... arXiv:2504.08939" | (unl.) | CONFIRMED | `2504.08939/v1/src/main.tex:44, 65-66` | Backreaction of preheating on the averaged expansion, NR. |

## Line 194: bubble collisions, cosmic strings

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 28 | 194 | "Bubble collisions, cosmic strings. arXiv:1112.4487, ..." | (unl.) | CONFIRMED | `1112.4487/v2/src/NRbubbles.tex:41, 60, 81, 108` | Bubble collisions in full GR, 1+1 dimensions by the SO(2,1) (hyperbolic) symmetry of the collision. |
| 29 | 194 | "... arXiv:1312.1357, ..." | (unl.) | CONFIRMED | `1312.1357/v3/src/collision_cosmo.tex:31, 57`; `1312.1357/v3/src/simulation_desc.tex:51`; `1312.1357/v3/src/summary.tex:21` | Bubble collisions to CMB observables, 1+1-dimensional NR with AMR. |
| 30 | 194 | "... arXiv:1808.06678, ..." | (unl.) | CONFIRMED | `1808.06678/v3/src/GW_CosmicRing.tex:71, 83` | Abelian-Higgs cosmic-string loop collapse in 3+1 NR. |
| 31 | 194 | "... arXiv:2002.05177" | (unl.) | CONFIRMED | `2002.05177/v2/src/GW_CosmicRing.tex:79, 95` | Gravitational waveforms and memory of collapsing string loops. |

## Line 219: physical background of the early matter era

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 32 | 219 | "Physical background. Review arXiv:2006.16182." | (unl.) | CONFIRMED | `2006.16182/v2/src/main_journal.tex:25, 118, 869` | Review of non-standard expansion histories, with a section on microhalo formation. |
| 33 | 219 | "In EMD small-scale perturbations go nonlinear early and form microhalos: arXiv:1106.0536, ..." | (unl.) | CONFIRMED | `1106.0536/v2/src/emd_final.tex:94-102, 622-623` | Enhanced perturbations of decay-produced dark matter; up to 50 per cent of the dark matter in microhalos above 0.1 Earth masses at z ≈ 100 for low reheat temperatures (linear theory with Press-Schechter); free streaming does not erase the effect in its models. |
| 34 | 219 | "... arXiv:1311.4034, ..." | (unl.) | CONFIRMED (precision) | `1311.4034/v2/src/structure-articlev3jhep.tex:124, 147, 171-174, 228` | Mini-halos form during the EMD, but survive the decay of the dominant species only if it decays into a nearly degenerate daughter with an open coannihilation channel; otherwise their density drops as (f_b)⁴. |
| 35 | 219 | "... arXiv:1405.7373, ..." | (unl.) | CORRECTED | `1405.7373/v2/src/ver2.tex:141, 441, 476, 508` | A counter-example, not support: sub-horizon dark-matter perturbations grow during the EMD (L441), but "in many non-thermal models free-streaming effects or kinetic decoupling after reheating can completely erase the enhancement" (L141); in the moduli scenario with wino or higgsino dark matter the growth is erased (L476, L508), so "enhanced structure does not provide a new probe" in these models (L141). Linear theory only. |
| 36 | 219 | "... arXiv:2107.10293." | (unl.) | CONFIRMED (precision) | `2107.10293/v2/src/main.tex:136-140, 153` | Halos that form during the EMD ("early halos") expand and eject their matter at its end, washing out structure on scales larger than expected; the microhalos then form after matter-radiation equality, earlier than in the standard cosmology (and earlier for a short EMD than for a long one). |
| 37 | 219 | "'Inflaton halos' during the oscillating phase of the inflaton condensate: arXiv:2011.13333, ..." | (unl.) | CONFIRMED | `2011.13333/v2/src/inflaton_halos_v2.tex:30, 52, 69-71` | N-body simulation of the fragmentation of the inflaton condensate into inflaton halos. |
| 38 | 219 | "... arXiv:1911.01661, ..." | (unl.) | CONFIRMED | `1911.01661/v2/src/inflaton_structure.tex:35, 66-68, 141` | "Inflaton clusters" (and inflaton stars) from Press-Schechter estimates; no simulation. |
| 39 | 219 | "... arXiv:2110.15109, ..." | (unl.) | CONFIRMED | `2110.15109/v2/src/inflaton_stars.tex:62, 88, 95` | N-body with Schrödinger-Poisson zoom-ins; inflaton stars inside inflaton halos. |
| 40 | 219 | "... arXiv:1909.11678." | (unl.) | CONFIRMED | `1909.11678/v2/src/main.tex:39, 57-58, 223` | Schrödinger-Poisson simulation of the fragmentation of the oscillating condensate into gravitationally confined overdensities (the word "halo" is not used for them). |

## Line 220: N-body simulations

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 41 | 220 | "N-body simulations (all Newtonian or semi-relativistic)" | [VERIFIED] | CONFIRMED | `2306.14961/v2/src/main.tex:214`; `2212.00425/v2/src/main.tex:204`; `2312.12499/v2/src/main.tex:157`; `2403.15126/v1/src/pII_GW_Vir_C2_Arx.tex:261, 1675`; `2605.04487/v2/src/main_v3.tex:189, 460` | GADGET-2, AxioNyx and CONCEPT (Newtonian; tensor modes in CONCEPT propagate at c), Aarseth's Nbody2 (Newtonian), and Newtonian self-gravity with special-relativistic particle kinematics (2605.04487). |
| 42 | 220 | "EMD structure formation and its evaporation at reheating (gravitational heating): arXiv:2306.14961" | [VERIFIED] | CONFIRMED | `2306.14961/v2/src/main.tex:59, 74, 99, 214` | "the first cosmological N-body simulations of the formation and evaporation of halos during and after an EMDE"; modified GADGET-2. |
| 43 | 220 | "Gravitational waves from inflaton-halo formation and tidal interactions: arXiv:2212.00425" | [VERIFIED] | CONFIRMED | `2212.00425/v2/src/main.tex:82, 113, 204, 219-230` | N-body (AxioNyx) from 14 to 23 e-folds after inflation; the GW is computed from the transverse-traceless part of the particles' stress tensor (method of Dufaux et al.), not from a quadrupole formula. |
| 44 | 220 | "Hybrid N-body + lattice simulations including decay of the metastable matter into radiation: arXiv:2312.12499" | [VERIFIED] | CONFIRMED | `2312.12499/v2/src/main.tex:111, 139, 157-159` | Modified CONCEPT: decaying matter as particles, decay radiation as a fluid, tensor modes on a lattice. |
| 45 | 220 | "finding that nonlinearity enhances the gravitational waves significantly: arXiv:2312.12499" | [VERIFIED] | CONFIRMED (precision) | `2312.12499/v2/src/main.tex:113, 209, 216, 235` | The enhancement is at frequencies above the reheat-scale peak ("we do not find significant enhancement of power at the reheat-scale peak, the power at smaller scales is considerably enhanced", L209; no substantial enhancement on linear scales, L216), established "up to frequencies at least as large as the inverse light-crossing time of the largest halos" (L113); above that the Newtonian spectrum "should be interpreted with care" (L235). |
| 46 | 220 | "Gravitational waves from pancake collapse and the violent-relaxation phase: arXiv:2403.15126" | [VERIFIED] | CONFIRMED (precision) | `2403.15126/v1/src/pII_GW_Vir_C2_Arx.tex:174-175, 240-247, 261, 305-314, 611` | Direct Newtonian N-body (Nbody2) started from Zel'dovich positions; the overdensity is treated as decoupled from the Hubble flow after turnaround (L611); a second spectral peak from violent relaxation (L311-314). The pancake-stage spectrum was the authors' earlier analytic result (L240-247). Its fitting of the quadrupole is criticised by 2605.04487 (row 48). |
| 47 | 220 | "Semi-relativistic N-body, a homogeneous ball with Zel'dovich deformation in an EdS background, with gravitational waves computed from the numerical quadrupole: arXiv:2605.04487" | [VERIFIED] | CONFIRMED (precision) | `2605.04487/v2/src/main_v3.tex:171, 189, 460, 695` | "Semirelativistic" means special-relativistic particle kinematics with Newtonian self-gravity (L189, L460); the Einstein-de Sitter background is a prescribed a(t), the surrounding universe is not represented by particles (L695). |
| 48 | 220 | "it finds that fitting formulae and the Zel'dovich estimate miss the evolution after shell crossing and misestimate the radiated power" | [VERIFIED] | CONFIRMED (precision) | `2605.04487/v2/src/main_v3.tex:171, 2512, 2620, 2708`; `2605.04487/v2/src/references.bib:275-284` | The "fitting-based procedure" is that of 2403.15126 (cite key DalianisKouvaris2024, eprint 2403.15126; L2708), the paper listed in the previous sentence of the brief; the Zel'dovich-based spectra fall short by several orders of magnitude near the peak (L2512). |
| 49 | 220 | "and that the main contribution comes from peaks of height ν≈3: arXiv:2605.04487" | [VERIFIED] | CONFIRMED (precision) | `2605.04487/v2/src/main_v3.tex:171, 2496, 2504, 2622` | nu_peak ≃ 2.85 and 2.98 for sigma = 0.01 and 0.1 in the Doroshkevich- and BBKS-weighted averages; a larger variance enhances the signal significantly (L171, L2622). |

## Line 221: perturbative calculations and their limits

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 50 | 221 | "Review of scalar-induced gravitational waves arXiv:2109.01398" | (unl.) | CONFIRMED | `2109.01398/v2/src/template_review.tex:95, 109, 132` | Review with emphasis on non-standard expansion histories. |
| 51 | 221 | "effect of the speed of the transition from EMD to radiation domination on the signal: arXiv:1904.12878, ..." | (unl.) | CONFIRMED | `1904.12878/v3/src/arXiv_v3.tex:109, 129-130` | Gradual transition (time scale comparable to the Hubble time). |
| 52 | 221 | "... arXiv:1904.12879, ..." | (unl.) | CONFIRMED | `1904.12879/v4/src/emd_enh.tex:76, 167-173` | Sudden transition. |
| 53 | 221 | "... arXiv:2311.12340, ..." | (unl.) | CONFIRMED | `2311.12340/v2/src/main.tex:13, 45-47` | Interpolates between fast and slow transitions with a time-dependent decay rate. |
| 54 | 221 | "... arXiv:2410.17291" | (unl.) | CONFIRMED (precision) | `2410.17291/v1/src/main.tex:35, 55, 137, 203, 566-569` | Treats both the onset and the end of an EMD caused by spectator (curvaton-like) fields, with matter decaying into radiation at a rate Gamma (L566-569) and without the instantaneous approximation (L203); the transition speed is not varied, so it is a "complete treatment" rather than a study of the speed. |
| 55 | 221 | "The gauge-dependence problem is sharpest in a matter-dominated era: arXiv:1704.03500, ..." | (unl.) | CONFIRMED | `1704.03500/v1/src/GW2nd_ApJ.tex:245, 347` | The induced tensor power spectrum depends on the temporal gauge; in the matter era the induced modes dominate the primordial ones for k ≳ 10⁻² h/Mpc in every gauge considered. |
| 56 | 221 | "... arXiv:1911.09689, ..." | (unl.) | CONFIRMED (precision) | `1911.09689/v3/src/Draft-v3.tex:435, 1412-1414` | Works out the radiation era (gauge dependence vanishes there) and only states that the matter era needs "further studies" (L1414). |
| 57 | 221 | "... arXiv:1912.00785, ..." | (unl.) | CONFIRMED | `1912.00785/v3/src/gw_TT.tex:105, 266-270` | "the tensor perturbation easily depends on the gauge during a MD era", even at late times; the authors add that this tensor perturbation "is not a gravitational wave" (L270). |
| 58 | 221 | "... arXiv:2012.14016, ..." | (unl.) | CONFIRMED (precision) | `2012.14016/v2/src/almostgaugeindependentarxiv_revised_2.tex:101, 332-346` | In dust domination the induced tensor can be gauged away and becomes a genuine wave only when dust domination ends; for EMD models the dominant contribution comes right after reheating, where their approximate gauge invariance applies (L345-346). |
| 59 | 221 | "... arXiv:2009.11081." | (unl.) | CONFIRMED (precision) | `2009.11081/v2/src/main.tex:36-44, 705-712` | In seven gauges the kernels differ (growing and decaying modes), but the energy density of the oscillating induced waves is the same in all seven: "SIGWs are gauge independent" (L712). Part of the problem is resolved there. |
| 60 | 221 | "Third-order induced gravitational waves in a matter-dominated era show secular growth (arXiv:2610.08045)" | [title only verified] | CONFIRMED | `2610.08045/v1/src/main.tex:32, 47-48, 80` | The MD kernels grow secularly, I⁽³⁾ ∝ x² at late times, so Omega_GW⁽³⁾ ∝ x⁶ against Omega_GW⁽²⁾ ∝ x² (x = k eta). Checked in the source: the label can become [VERIFIED]. |

## Line 222: black-hole-dominated early matter era

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 61 | 222 | "Black-hole-dominated early matter era. N-body with primordial black holes as particles: arXiv:1907.08129" | (unl.) | CORRECTED | `1907.08129/v1/src/ms.tex:30, 43-46, 173-174, 333` | Not an early (pre-nucleosynthesis) black-hole-dominated era: "Lambda-PBH cosmologies" in which PBHs are part or all of the cold dark matter, N-body (modified CUBEP3M) of PBH and particle-dark-matter particles "evolved from deep in the radiation era to redshift 99", i.e. the first structures of the standard matter era. |
| 62 | 222 | "gravitational waves from a gas of black holes: arXiv:2010.11573, ..." | (unl.) | CONFIRMED | `2010.11573/v3/src/GW_PBH_Paper.tex:73, 95, 101, 113-133` | Waves induced at second order by the Poisson density fluctuations of a PBH gas that dominates before evaporating. |
| 63 | 222 | "... arXiv:2012.08151, ..." | (unl.) | CONFIRMED | `2012.08151/v3/src/isocurvature_arxiv_erratum.tex:93-96, 122-125, 181` | Same mechanism treated as early isocurvature; most waves are made right after evaporation. |
| 64 | 222 | "... arXiv:2003.10455." | (unl.) | CONFIRMED (precision) | `2003.10455/v3/src/pbh_eva.tex:149-151, 219-226, 263` | Waves induced by the primordial (inflationary) curvature perturbations, enhanced by the sudden reheating at the end of a PBH-dominated era; not waves sourced by the black-hole gas itself. |
| 65 | 222 | "Accretion growth of primordial black holes in EMD (by about two orders of magnitude at most) ... in linear perturbation theory: arXiv:2505.21885" | [VERIFIED] | CONFIRMED | `2505.21885/v1/src/main.tex:65, 100, 253, 442, 513` | "up to two orders of magnitude" (L65), "one to two orders" depending on the onset of the EMD (L442); the EMD is kept in the linear regime (L253, L513). |
| 66 | 222 | "... and the resulting doubly peaked gravitational-wave spectrum" (under "Black-hole-dominated early matter era") | [VERIFIED] | CORRECTED | `2505.21885/v1/src/main.tex:65, 125, 147, 181, 357` | Two corrections. The EMD is "generated by some bosonic field phi" (L125) and the PBHs "must be subdominant" (L147): not a black-hole-dominated era. The double peak does not result from the accretion: the high-frequency peak is the induced wave of the enhanced curvature spectrum that formed the PBHs in the earlier radiation era (partly suppressed by the EMD), the low-frequency peak comes from the sudden EMD-to-radiation transition (L65, L181, L357). |

## Statement of the author's judgement (no verdict)

- Line 188: "This area is not a kinetic problem, but it is the main arena of the NR-cosmology
  community, and most of the experience with initial data, gauges and AMR comes from here." An
  assessment of the field, not a claim about a paper; not checked. The rows above show that the
  cited works use 1+1 (rows 14, 28, 29), spherical (2607.06441) and 3+1 codes with and without
  AMR, which is consistent with it but does not establish "most".
