# Check of brief lines 394-444 (problems S4 to S10) and 1749 (novelty searches)

Owner kb, work package "novelty", wave 3a, 2026-11-19. Brief:
`einstein_vlasov_pic_cosmology_agent_brief.en.md` (version 2), section 5 problems S4 (black-hole
growth and dark-matter dress, lines 394-404), S5 (formation with a free-streaming component,
406-416), S6 (late-time multi-stream regions, 418-428), S7 (Burnett conjecture and "graviton PIC",
430-437), S8-S10 (439-443), and section 15 item 5 (line 1749, novelty searches). Every statement
with a label, and every specific claim about a cited paper (also where it carries no label), is
checked at the TeX source in the knowledge-base store; the four novelty searches of line 1749 that
belong to this package are in `NOVELTY.md`.

Locators: `<key>/<version>/src/<file>:<line>` are lines of the TeX sources under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/` (gr-qc/0512031 as `gr-qc_0512031`); a short form
`<file>:<line>` or `:<line>` refers to the paper of the locator before it. `meta:arxiv-api/<id>`
is the metadata record `kb-data/meta/arxiv-api/<id>.json`; `inspire-query:<label>` is the INSPIRE
response that `search/query_log.tsv` lists under that label (a record under
`kb-data/meta/inspire/query/`). Run `kb-20261119-154605-3ee42d2` (R1, `scripts/check_numbers.py`)
recomputes the numbers of rows 8, 9 and 32.

Not repeated (already in `coord/BRIEF_ERRATA.md`): line 398 "Newtonian self-similar secondary
infall gives an r^(-9/4) density profile [BACKGROUND]" (row 1.7) and line 426 "whether NRPIC keeps
this is [TO VERIFY]" (row 3.7, answered there for line 134; it holds for line 426 as well). The
unlabelled cost estimate of line 426 ("c/v ... two to three orders of magnitude") and the
judgements of lines 402, 412, 422-424 are not literature claims and are not rated.

Overlap: lines 406-444 are also checked by the sibling package `s5_s6` of this worktree (begun at
the same time, independently); the lead reconciles the two.

Label column: the brief's label; "(unl.)" marks a specific claim about a paper without a label;
line 1749 is an item of section 15, "Items for the agents to verify or complete", rated as
[TO VERIFY].

Verdicts: CONFIRMED (the source says it, at the locator), CONFIRMED (precision) (right, but the
source qualifies it in a way a reader should know; what in the note), CORRECTED (the source says
something else; what is right in the note), NOT FOUND (what was searched). Totals: 33 rows; 15
CONFIRMED, 16 CONFIRMED (precision), 2 CORRECTED, 0 NOT FOUND.

## Lines 398-404: S4, black-hole growth and the dark-matter dress

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 1 | 398 | "The corresponding radiation-era fluid result is the Zel'dovich–Novikov law (arXiv:2608.13206)" | (unl.) | CONFIRMED (precision) | `2608.13206/v3/src/PRD.tex:39, 457-466, 505` | 2608.13206 fits the late-time apparent-horizon mass of its 3+1 radiation-fluid runs to the Zel'dovich-Novikov prescription dM/dt = 4 pi F R^2 rho_b with a fitted efficiency F; the law is Zel'dovich and Novikov 1967 (cited there), valid "only at sufficiently late times", and the fitted F is foliation-dependent (:505). A fit, not a derived result |
| 2 | 398 | "for the matter-era scalar-field result see arXiv:2109.04896" | (unl.) | CONFIRMED | `2109.04896/v3/src/PBH_formation.tex:58, 89, 103, 267` | 3+1 NR; the matter background is an oscillating massive scalar field, the perturbation a massless one; mass growth beyond the self-similar rate after formation |
| 3 | 398 | "The effect of the dress on the merger rate of primordial-black-hole binaries is currently estimated in Newtonian terms (arXiv:1805.09034)" | (unl.) | CONFIRMED | `1805.09034/v3/src/main.tex:61, 286`; `2402.13762/v1/src/main.tex:191, 238` | Gadget, gravity-only N-body. The later particle work on binaries in spikes (NbodyIMRI, 2402.13762) is Newtonian as well, without post-Newtonian terms |
| 4 | 400 | "the 'cosmological coupling' claim (arXiv:2302.07878)" | (unl.) | CONFIRMED | `2302.07878/v1/src/paper_couple_rev.tex:101, 130-132` | Mass growth "independently of accretion or mergers"; k = 3.11 (+1.19, -1.33) at 90 per cent; k = 0 expected for Kerr, k = 3 for vacuum-energy interiors |
| 5 | 400 | "This is a direct numerical test, for an ordinary black hole, of the 'cosmological coupling' claim ...; a null result is expected" | (unl.) | CONFIRMED (precision) | `1903.01490/v2/src/spinning_BH_v2_CT.tex:640-644, 653-657, 713-715`; `kb-20261119-154605-3ee42d2` | Right for an ordinary black hole, and 2302.07878 itself expects k = 0 there (row 4). But an NR lattice of vacuum black holes already shows horizon masses constant to 0.1 per cent while lengths grow by about e^2, i.e. abs(k) <= 5.0e-4 (R1); an NRPIC run adds the ambient matter and the accretion to subtract (NOVELTY.md section 3) |
| 6 | 404 | Key references "arXiv:1901.08528, arXiv:1607.00612, arXiv:2106.07480, arXiv:1805.09034, arXiv:2109.04896, arXiv:2608.13206, arXiv:2302.07878" | (unl.) | CONFIRMED | `meta:arxiv-api/1901.08528`, `/1607.00612`, `/2106.07480`, `/1805.09034`, `/2109.04896`, `/2608.13206`, `/2302.07878` | All seven exist with matching subjects: halos around PBHs (steep r^(-9/4), 1901.08528), spikes around PBHs (1607.00612, 2106.07480), dressed binaries (1805.09034), matter-era NR (2109.04896), radiation-era 3+1 accretion (2608.13206), the coupling claim (2302.07878) |

## Lines 410-416: S5, formation with a free-streaming component

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 7 | 410 | "Neutrinos decouple at about 1 MeV" | [BACKGROUND] | CONFIRMED (precision) | `2303.07980/v2/src/PBHs_QCD.tex:346`; `2006.16182/v2/src/main_journal.tex:1048`; `1704.03500/v1/src/GW2nd_ApJ.tex:1270`; `1906.08217/v4/src/main.tex:98` | The sources give 1-2 MeV, about 2 MeV, about 1.5 MeV and "around 1 MeV": quote 1-2 MeV. Can become [VERIFIED] with these locators |
| 8 | 410 | "when the horizon mass is of order 10^5 solar masses" | [BACKGROUND] | CONFIRMED | `kb-20261119-154605-3ee42d2`; `1607.00612/v2/src/paper2.tex:205-218`; `2303.07980/v2/src/PBHs_QCD.tex:343` | M_H = (4 pi/3) rho H^-3 = 1.50e5 M_sun at 1 MeV and 3.7e4 at 2 MeV (g_* = 10.75, R1); the scaling of 1607.00612 gives 1.46e5 at 1 MeV (2.5 per cent apart); 2303.07980 names the 1e5 M_sun scale of the e+e- epoch |
| 9 | 410 | "from then on neutrinos make up forty to fifty per cent of the radiation energy density" | [BACKGROUND] | CONFIRMED | `2303.07980/v2/src/PBHs_QCD.tex:357`; `2006.16182/v2/src/main_journal.tex:1046-1048`; `kb-20261119-154605-3ee42d2` | 5.25/10.75 = 0.488 before e+e- annihilation; 0.409 after it with N_eff = 3.045 (R1). "Nearly half of the radiation is collisionless" (same line) holds before annihilation |
| 10 | 410 | "and no longer provide a pressure response like a tightly coupled fluid" | [BACKGROUND] | CONFIRMED | `2303.07980/v2/src/PBHs_QCD.tex:347-349, 362-364` | Neutrinos free-stream out of overdense regions and "do not even exert pressure" |
| 11 | 410 | "Supermassive primordial black holes above this mass (arXiv:1609.02245, arXiv:1202.3848)" | (unl.) | CONFIRMED (precision) | `1609.02245/v2/src/main.tex:399, 1032`; `1202.3848/v2/src/smbh.tex:75, 265` | 1609.02245: 2e4 to 2e13 M_sun allowed, ~1e10 targeted, i.e. above. 1202.3848: "of the order of 10^5 solar masses", examples 5e4, 5e5, 5e6, i.e. around rather than above this mass |
| 12 | 410 | "Relativistic particles of a hidden sector (arXiv:2209.02735) pose the same kind of problem" | (unl.) | CONFIRMED (precision) | `2209.02735/v2/src/main.tex:53, 69, 149, 210` | 2209.02735 studies how the relativistic pressure of the dominant hidden-sector particle suppresses perturbations in an early matter era, with a sound speed (fluid-like, linear); whether the particle free-streams depends on hidden-sector scattering (:210). The analogy is the brief's [JUDGEMENT] |
| 13 | 410 | "The effect of the thermal history on the threshold through the equation of state has been studied (arXiv:1906.08217), but at the fluid level" | (unl.) | CONFIRMED (precision) | `1906.08217/v4/src/main.tex:122-124`; `2303.07980/v2/src/PBHs_QCD.tex:196-206, 355-368`; `2406.11417/v1/src/chapter.tex:485-508` | 1906.08217 takes delta_c(w(T)) from fluid results without a simulation. The fluid simulations with the realistic equation of state, including the e+e- epoch, are 2303.07980 and 2406.11417, and both state that the neutrino free-streaming question is open: they belong among the key references of S5 |
| 14 | 414 | "I found no full-GR kinetic calculation of this problem" | [TO VERIFY] | CONFIRMED | `2303.07980/v2/src/PBHs_QCD.tex:367-368, 933-935`; `2406.11417/v1/src/chapter.tex:507-508`; `inspire-query:s5_k2`, `inspire-query:s5_k4`, `inspire-query:s5_c1` | None found by 16 INSPIRE queries, two web and two knowledge-base searches (NOVELTY.md section 1); the field states in 2023 and 2025 that only a dedicated simulation with a fluid and a free-streaming component can settle it |
| 15 | 416 | "the dynamical-spacetime fluid module (arXiv:2409.10384)" | (unl.) | CONFIRMED | `2409.10384/v3/src/paper.tex:103, 230-231` | GRMHD in dynamical spacetimes in AthenaK |

## Line 426: S6, cost

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 16 | 426 | "AthenaK's AMR uses a single time step for all levels (main text of arXiv:2409.16053)" | [VERIFIED] | CONFIRMED | `2409.16053/v1/src/main.tex:110` | "uniform time stepping across levels", inherited from Athena++ (same line). That NRPIC keeps it: errata row 3.7 |

## Lines 432-437: S7, Burnett conjecture and "graviton PIC"

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 17 | 432 | "the backreaction of high-frequency gravitational waves is equivalent, in the limit, to massless Vlasov matter (§3.7)" | (unl.) | CONFIRMED (precision) | `2403.03470/v1/src/wavecoordinate.arxiv.240305.tex:119`; `1907.10743/v2/src/main.tex:87`; `2404.07659/v1/src/Burnett.survey.240411.tex:183-191` | This is Burnett's conjecture: the forward direction is a theorem in generalized wave coordinates (2403.03470) and under U(1) symmetry (1907.10743); the converse ("every solution arises as a limit") is proven only in special cases (row 18) |
| 18 | 434 | "All existing proofs assume U(1) symmetry; the 3+1 case without symmetry is open." | (unl.) | CORRECTED | `2403.03470/v1/src/wavecoordinate.arxiv.240305.tex:119, 143`; `2009.08968/v1/src/HFlimit.200918.tex:101-103`; `2404.07659/v1/src/Burnett.survey.240411.tex:1505, 1571, 1595-1599`; `inspire-query:s7_k1` | Huneau and Luk (2403.03470, 2024) prove the conjecture in generalized wave coordinates in any dimension d >= 3, "the first proof ... without symmetry assumptions or angular regularity assumptions"; Luk and Rodnianski (2009.08968) treat it without symmetry in double-null gauge with angular regularity (null-dust limits); Touati constructs reverse (null-dust) limits without symmetry (2206.12318, 2402.17530, abstracts in inspire-query:s7_k1). Open: the reverse conjecture for a general Vlasov field without symmetry, gauge independence, global and large data (survey :1571-1599) |
| 19 | 435 | "gravitational-wave turbulence (arXiv:2509.19769)" | (unl.) | CONFIRMED (precision) | `2509.19769/v1/src/elsasser.tex:294-297, 308` | An analytic paper (Elsasser form of GR); the numerical evidence it cites is 2508.13294 (Ma et al.) and Galtier et al. (2108.09158, symmetry-reduced) |
| 20 | 435 | "the Green–Wald conclusion that the effective stress is traceless (arXiv:1011.4920)" | (unl.) | CONFIRMED (precision) | `1011.4920/v2/src/inhomogeneities-paper.tex:38-45, 322-328` | Traceless and with positive energy density, provided the matter satisfies the weak energy condition and the metric stays close to a background |
| 21 | 435 | "For related full-NR gravitational-wave cosmology see arXiv:1505.02959, arXiv:1801.08362" | (unl.) | CONFIRMED (precision) | `1505.02959/v1/src/letter-GWuni.tex:46-64, 98-132`; `1801.08362/v2/src/tensor.tex:61` | 1505.02959 is a full 3+1 NR test of Isaacson's radiation-fluid average for a vacuum universe of nonlinear GWs (3 per cent, 0.1 per cent averaged): the closest existing work to S7 and more than "related". 1801.08362 evolves a matter FLRW with scalar and primordial tensor perturbations, not a GW-dominated spacetime |
| 22 | 437 | "No numerical work was found." | [TO VERIFY] | CONFIRMED (precision) | `1505.02959/v1/src/letter-GWuni.tex:46-64`; `2409.01939/v2/src/main.tex:1072`; `inspire-query:s7_k5`, `inspire-query:s7_k8`, `inspire-query:s7_k11` | No 3+1 numerical comparison of a high-frequency vacuum evolution with Einstein-massless-Vlasov was found (13 INSPIRE queries, three web searches; NOVELTY.md section 2). Numerical work on the averaged (trace) part exists: 1505.02959 |

## Lines 441-443: S8 to S10

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 23 | 441 | "In the homogeneous case Vlasov matter is known to behave differently from a perfect fluid (arXiv:gr-qc/0512031)" | (unl.) | CONFIRMED | `gr-qc_0512031/v1/src/BianchiIVlasov.tex:189-199` | Bianchi I with Vlasov matter differs from any perfect-fluid model of the same type |
| 24 | 441 | "the inhomogeneous case (spikes, mixmaster) with Vlasov matter has no numerical study. Reference points: arXiv:0904.1546, arXiv:2010.01399" | (unl.) | CONFIRMED (precision) | `0904.1546/v2/src/g2spike_prd_resub.tex:88, 107-115`; `2010.01399/v1/src/spikepaper.tex:37, 70, 455`; `inspire-query:s8_k1` | Both reference points are vacuum simulations. One INSPIRE title query found only an analytic Cauchy-problem paper (gr-qc/9903018): a limited search, not a full novelty search |
| 25 | 442 | "spindle collapse (arXiv:1611.07906, arXiv:1901.04498)" | (unl.) | CONFIRMED | `1611.07906/v2/src/asymflat.tex:90-100`; `1901.04498/v2/src/main.tex:91, 125-128` | 3D spindle collapse of collisionless particles; prolate collapse with censorship upheld |
| 26 | 442 | "for the charged case see arXiv:2402.10190, arXiv:2511.20567" | (unl.) | CONFIRMED | `2402.10190/v1/src/main.tex:166, 189-192`; `2511.20567/v2/src/main.tex:65, 77, 133, 148` | Extremal Reissner-Nordstrom as critical solution of Einstein-Maxwell-Vlasov (proof); numerical construction near the extremal critical point, which names the rotating extension as open |
| 27 | 443 | "the more abrupt the transition, the stronger the induced gravitational waves (arXiv:1904.12879, arXiv:2003.10455)" | (unl.) | CONFIRMED | `1904.12879/v4/src/emd_enh.tex:164-169`; `2003.10455/v3/src/pbh_eva.tex:150-151` | Sudden transition enhances, gradual suppresses; PBH evaporation as a sudden reheating |
| 28 | 443 | "Newtonian hybrid simulations exist (arXiv:2312.12499, arXiv:2306.14961)" | (unl.) | CONFIRMED (precision) | `2312.12499/v2/src/main.tex:139, 157-159`; `2306.14961/v2/src/main.tex:74, 99, 115` | 2312.12499: Newtonian N-body (CONCEPT) of decaying matter with a decay-radiation fluid, tensor modes evolved alongside. 2306.14961: N-body formation and evaporation of halos with decaying particles; radiation enters its background only |
| 29 | 443 | "for the relativistic treatment of decaying matter in N-body see arXiv:1904.11773" | (unl.) | CONFIRMED (precision) | `1904.11773/v1/src/paper190319.tex:86` | GR and radiation effects included "at the level of linear perturbation theory" |

## Line 1749: novelty searches (this package's four items)

| # | Brief line | Quotation | Label | Verdict | Locator | Note |
|---|---|---|---|---|---|---|
| 30 | 1749 | "S5 (black-hole formation with a free-streaming component)" | [TO VERIFY] | CONFIRMED | `2303.07980/v2/src/PBHs_QCD.tex:367-368`; `2406.11417/v1/src/chapter.tex:507-508`; `inspire-query:s5_k4` | Open (NOVELTY.md section 1); recommended references 2303.07980, 2406.11417 |
| 31 | 1749 | "S7 (numerical test of the Burnett conjecture)" | [TO VERIFY] | CONFIRMED (precision) | `1505.02959/v1/src/letter-GWuni.tex:46-64`; `2403.03470/v1/src/wavecoordinate.arxiv.240305.tex:143` | Open as a numerical test; the closest numerical work tests the averaged trace only (1505.02959); the conjecture is no longer open without symmetry (row 18), so S7 is a quantitative demonstration, not a test of an open 3+1 problem (NOVELTY.md section 2) |
| 32 | 1749 | "the null test of S4 (an NR test of cosmological coupling)" | [TO VERIFY] | CONFIRMED (precision) | `1903.01490/v2/src/spinning_BH_v2_CT.tex:653-657, 713-715`; `kb-20261119-154605-3ee42d2`; `inspire-query:s4_c1`, `inspire-query:s4_c5` | No NR test framed against the claim; but vacuum lattices already bound abs(k) <= 5e-4 (row 5). New only with ambient matter and accretion subtracted (NOVELTY.md section 3) |
| 33 | 1749 | "full-NR simulations of binary black holes in a particle-dark-matter environment" | [TO VERIFY] | CORRECTED | `2611.12831/v1/src/main.tex:1335-1340, 1358, 1362, 1384-1391`; `inspire-query:b_k1`, `inspire-query:b_k4` | Done in the broad form by the target paper itself: two clumps collapse to black holes inside a collisionless envelope, inspiral and merge (t_m = 64.15625 M; 27.3 per cent of the orbital angular momentum to the envelope; no inspiral in the waveform). Open: a quasi-circular binary of pre-existing holes in a light dark-matter particle distribution, its dephasing against vacuum, and convergence (NOVELTY.md section 4) |
