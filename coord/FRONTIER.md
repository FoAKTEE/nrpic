# Frontier after the brief's survey

Owner: orchestrator (branch `main`). State on 2026-11-20 (wave 3), from the check of the brief
by the knowledge base in wave 3a (branch `kb/brief-check` at 476a1763; reports of the sessions in
`scratch/orch/wave3a_reports/kb.md`). Three parts: (1) papers that the brief's survey does not
cite, per track, with one line each on whether it changes the track's plan or overlaps with it;
(2) the verdicts of the novelty searches, with their limits; (3) the open questions of brief
sections 7 and 8 that were found answered or partly answered. Every statement is taken from
the file named with it; the corrections of the brief itself are rows of `coord/BRIEF_ERRATA.md`
(row numbers given here as "errata 1.32").

Labels. One-line summaries of papers rest on the abstract as served by INSPIRE unless a TeX
locator is given ([VERIFIED: abstract], `s39_frontier/FRONTIER.md`). The "Plan" lines are
[JUDGEMENT] of the kb packages, for the track lead to accept or reject; none of them is a
decision. No number here may enter a note: it must be taken from the paper at its locator
(CLAUDE.md rule 7).

Paths `<pkg>/<file>` are `tracks/kb/brief_check/<pkg>/<file>` on `kb/brief-check`.

## 1. Papers not cited by the survey, per track

### How they were found, and the limits

- Source: `s39_frontier/FRONTIER.md`. Forward citations (INSPIRE `refersto:recid:`) of all 32
  ids of brief lines 243-255, and topic and author queries per row, restricted to recent months
  (run kb-20261119-152359-851b963, 59 queries); Track D, which has no row in brief section 3.9,
  got its own queries, together with extra topics for A, B, C, E, F and the last weeks (run
  kb-20261119-152939-22939e5, 15 queries). The scan, run kb-20261119-153319-ad2a3a7, merged the
  74 answers: 284 distinct papers with an arXiv id, 226 of them not cited anywhere in the brief,
  47 of those dated 2026-10 or later, 11 in 2026-11. Exact dates of the November items: run
  kb-20261119-153125-0836e49.
- Only one paper found is dated after the survey (version 2 of the brief, 2026-11-15; its
  newest id is 2611.15050): 2611.23627 (2026-11-17), listed under core. Everything else below
  appeared before the survey and was not cited by it.
- Limits (same file): summaries are from INSPIRE abstracts; full texts were read only for
  2605.20320, 2609.14755 and 2604.27429, which were already in the store; INSPIRE indexes new
  arXiv papers with a delay of days, so the week 2026-11-12 to 11-19 is covered only as far as
  INSPIRE had it at 15:24-15:31Z; the fetch tool cannot search the arXiv listing; topics
  outside the directions of brief lines 243-255 and Track D were not searched (for Track B,
  "pancake" and "shell crossing" were not query terms); the new papers are not ingested in the
  knowledge-base database.
- Added from other packages: papers that a package fetched or read to answer a statement and
  that bear on a track's plan (source named in the row).

### Track A (S1, PBH formation in an early matter era)

| arXiv (date) | What is new | Plan |
|---|---|---|
| 2610.01964 (2026-10-01) | Bambague, Bezares, Clough: automatic differentiation locates a line of critical solutions in a 2D parameter space of scalar collapse with 35 runs, against 270 runs for 10 points by bisection | Overlaps in aim with A's threshold line in (ellipticity, amplitude); AthenaK is not differentiable, so no change; the run count is a benchmark for A's scan budget |
| 2607.08738 (2026-07) | Escrivà: finite-action statistics of curvature-profile dispersion around peak profiles, applied to spherical collapse thresholds | Context for the statistics of A's thresholds; no change |
| 2607.27343 (2026-07) | Redondo-Yuste, Aurrekoetxea: NR test of perturbation theory near the collapse threshold of a scalar field | Context; no change |
| 2611.05996 (2026-11-04) | Kishimoto, Joana, Suyama: full NR of a massive cosmic string in a radiation background, cylindrical symmetry | Cosmological-gauge experience only; no change |
| citations of 2609.14218 | three citing papers (2608.13206, 2610.08045, 2610.23218), all already in the brief | The direct competitor has no newer particle follow-up; A's plan (decision 0016 item 5) stands |
| 2607.09326 (2026), 2606.16879 (2026) | Einstein-de Sitter is nonlinearly stable for Einstein-Euler on T^3 with a polytropic equation of state of index n > 3 (proof), Gowdy-symmetric numerics agree; dust EdS is linearly unstable; nothing for massive Einstein-Vlasov (`2607.09326/v1/src/main.tex:141, 307, 317`; `2606.16879/v1/src/main_v2.tex:43`; s37_38 and s7_s8, errata 3.19) | Background for long periodic-box runs in an early matter era (s7_s8 request to A and B); whether particle velocity dispersion stabilises EdS is unknown; no change |

### Track B (S2, gravitational waves from early-matter-era structure)

| arXiv (date) | What is new | Plan |
|---|---|---|
| 2609.11891 (2026-09) | del-Corral, Spalding: relations mapping the characteristic frequencies of a GW background onto the mass and abundance of PBHs whose domination made an early matter era | Context for the population spectrum (B's second goal); no change |
| citations of 2605.04487 | 2605.11332, 2604.13012, 2504.20135: background phenomenology, none computes structure-formation waves | No competitor to B's full-GR pancake; no change |
| Macpherson group | no paper by Macpherson after 2026-06 in INSPIRE (author query, 0 hits) | Nothing to add to the S6 benchmark |
| 2607.28207, 2605.09004 (Adamek group) | late-universe applications (kinetic gravity braiding signatures; a separate-universe super-resolution emulator) | Weak-field late universe; no overlap with B |
| 2608.27962 (2026-08) | Bendtsen, Koksbang: learning the averaged history of an inhomogeneous universe from its present density field | Backreaction context (S6); no change |
| 2607.09326, 2606.16879 | as for Track A | Background for long periodic-box runs; no change |

### Track C (S3, relativistic collapse of an SIDM core)

| arXiv (date) | What is new | Plan |
|---|---|---|
| 2610.28890 (2026-10-20) | van den Bosch, Tokayer: spherical direct-simulation Monte Carlo without force softening; several scatterings per particle per step are harmless if implemented appropriately; the usual harmonic interpolation between long- and short-mean-free-path conductivities is inaccurate, a gentler transition fits; collapse slows once the core is optically thick | May change C's Newtonian fluid reference: if it interpolates the conductivities harmonically, check it against this calibration; also a Newtonian check of C's Monte Carlo step |
| 2610.28745 (2026-10-20) | Gurian, Gandhi, Dalal: kinetic simulations (KiSS-SIDM) of isolated halos, cross sections 50 to 250 000 cm^2/g; the collapse time is predicted by the Knudsen number at the scale radius; a hydrostatic fluid model calibrated to them | Overlaps with C's goal (collapsed mass fraction against Knudsen number) in the Newtonian regime; C's addition is the relativistic endpoint; use as the Newtonian baseline of the Kn scan |
| 2609.16122 (2026-09) | Gu, Jiang, Chen, Li et al.: the relativistic non-equilibrium (Misner-Sharp) halo model of 2601.17117 applied to little red dots | Same spherical fluid model; no 3D kinetic GR; no change |
| 2510.24565 (2025-10) | Feng, Yu, Zhong: GR instability of a self-gravitating thermal system with Fermi degeneracy | A further onset criterion beside 2108.11967 for C's threshold stage; no change |
| 2610.37852, 2606.19428, 2609.22758 | inelastic SIDM universality (fluid); dissipative SIDM (N-body); post-collapse black-hole-halo co-evolution (N-body) | Newtonian context; no change |

Abstract check (`s39_frontier/FRONTIER.md`, journal entry 4): of the 40 papers found by the C
queries and the citations of 2601.17117 and 2506.17641, only 2601.17117, 2609.16122, 2510.24565
and 2511.09311 mention a relativistic treatment, and none is a 3D kinetic calculation.

### Track D (S4, black-hole growth and dark-matter dress)

| arXiv (date) | What is new | Plan |
|---|---|---|
| 2610.33150 (2026-10-23) | Hoefken Zink, Piantadosi: a general-relativistic Eddington inversion, the distribution function in the energy at infinity from a density profile on a TOV background, applied to an NFW halo with a Gondolo-Silk spike around Sgr A* | Overlaps with D's strong-field spike: a candidate reference distribution function for sampling a relativistic spike as initial data (isotropic, static background) |
| 2611.08145 (2026-11-05) | Hassanabadi, Zare: a truncated spike as an Einstein cluster (circular orbits only) around Schwarzschild, closed-form metrics for indices 7/3 and 3/2 | A closed-form GR test configuration for D's particle initial data; not the adiabatically grown spike; no change |
| 2609.14755 (2026-09) | Pradhan, Ghaderi, Zeyauddin et al.: static, spherical, self-consistent Einstein-Vlasov black-hole environments parametrized by the occupation of orbital actions (`2609.14755/v1/src/Paper.tex:33-57`) | Equilibrium families to compare D's strong-field spike with; static only; no change |
| 2611.13170 (2026-11-09) | Sharpe, Spieksma, Ginat et al.: a massive-black-hole merger depletes the spike within about 100 Schwarzschild radii by orders of magnitude (q = 0.03; q = 0.005 too) | Bears on D's later goal, dressed binaries: the dress may not survive a merger history; a motivation caveat, no change to the first goals |
| 2610.13684 (2026-10) | Wang, Chadha-Day, Clough et al.: relativistic dynamical friction of matter on a static boosted Kerr-Schild background, first order in the matter density | Comparison for drag on a dressed binary; no change |
| 2610.15053, 2507.18934 | full NR of binaries in scalar (wave) dark matter; relativistic scalar drag | Wave dark matter, not particles; no change |
| 1903.01490 (2019, cited by the brief elsewhere) | NR lattice of spinning black holes: horizon masses constant to 0.1 per cent while lengths grow by about e^2 (`1903.01490/v2/src/spinning_BH_v2_CT.tex:640-644, 653-657, 713-715`), which bounds abs(k) <= 5.0e-4 for M proportional to a^k (run kb-20261119-154605-3ee42d2; novelty) | Changes the S4 null test: it must measure the accretion flux through the horizon separately and reach abs(k) well below 5e-4 (section 2) |

### Track E (S11, stochastic inflation)

| arXiv (date) | What is new | Plan |
|---|---|---|
| 2610.26669 (2026-10) | Braglia, Franciolini et al.: mean-field backreaction in single-field inflation (decoupling limit); Bunch-Davies UV modes distort backreaction unless adiabatically subtracted; spurious UV sensitivity in some cases | Bears on E's acceptance criteria (UV sensitivity of the noise and of backreaction); add as a check |
| 2602.11652, 2605.00476 | Kawasaki, Kuroda; Cruces, Kuroda: stochastic formalism with non-Markovian noise, UV modes evolved on the stochastic IR background | A known alternative to the Markovian noise of E's implementation; context; no change |
| 2606.28005 (2026-06) | Barnert, Iacconi, Assadullahi et al.: smooth Hubble-flow parametrisations of USR hide sharp spikes in higher derivatives of the reconstructed potential | Check E's inflection-point test potential for such features |
| 2609.21578 (2026-09) | del-Corral, Gondolo, Kumar et al.: metric fluctuations stop being negligible during preheating (linearized constraints) | Relevant to a later field-to-particle hand-over; no change |
| 2610.42044 (2026-10) | Blachier: elastic end-of-diffusion boundaries in stochastic delta N | Context; no change |
| Launay, Rigopoulos, Shellard | nothing after the thesis 2610.32592 (author query since 2026-06) | E's comparison base unchanged |

### Track F (S12, Hills mechanism)

| arXiv (date) | What is new | Plan |
|---|---|---|
| 2605.20320 (2026-05) | Cardoso, Ficarra, Redondo-Yuste et al.: full NR (Einstein Toolkit) of head-on collisions of a black-hole pair next to a companion, three holes from rest, configurations chosen to satisfy the Hills criterion so that the pair is not disrupted (`2605.20320/v2/src/main.tex:86, 169, 205-220, 274`) | Partial overlap: the first full-NR three-hole set-up with a Hills-criterion check, in the non-disruptive head-on regime; F's disruptive pericentre scan stays new; cite it |
| 2604.27429 (2026-04) | Sharma, Heger, Price et al.: a benchmark of binary-SMBH encounters with post-Newtonian schemes and a scalar perturbation of the background metric (`2604.27429/v1/src/template.tex:22, 45, 72-74`) | A baseline in the approximation ladder below F; no change |
| 2605.22525 (2026-05) | Maeda, Okawa: a binary in a local inertial frame of Kerr; adiabatic, tidally affected, chaotic and disruptive scattering regimes by semimajor axis | Regime boundaries to compare with F's pericentre scan line; no change |
| 2610.09336 (2026-10) | Qiao, Liu: head-on collisions of several black holes in BSSN from rest | Context for multi-hole data; no change |
| 2608.22735, 2607.18761 | restricted three-body plus SPH for star-white-dwarf binaries; semi-analytic binaries in the empty loss cone | Newtonian context; no change |

### core and the group of the source paper

| arXiv (date) | What is new | Plan |
|---|---|---|
| 2611.23627 (2026-11-17, the one paper after the survey) | Solod, Kim, Most: a five-point smoothness indicator as a refinement criterion, implemented in AthenaK, tested on Newtonian, special- and general-relativistic MHD benchmarks | A candidate criterion for core's refinement of periodic runs (cosmo-amr package), in the same code base; information, no change forced |
| 2611.12831 | no citing paper in INSPIRE at 2026-11-19 15:24Z | Nothing to follow yet |
| 2609.25240, 2609.25241 | frozen-in gravitational field lines and their reconnection in the electrodynamic formulation of GR | No effect on the pusher |
| 2611.15318 (2026-11-11) | Shen, Song, Wan: weak null singularities for the massive and massless Einstein-Vlasov systems without symmetry (mathematics) | No effect |

## 2. Novelty searches

Four of the six searches of brief line 1749 (section 15 item 5) are in `novelty/NOVELTY.md`
(searches 2026-11-19, 07:33-07:45 PST; 61 INSPIRE requests in `novelty/search/query_log.tsv`;
web and knowledge-base searches in `novelty/search/SEARCH_LOG.md`). S11 belongs to Track E's
specification; S12 was searched by Track F (`track/F-hills:tracks/F-hills/novelty/NOVELTY.md`)
and its key queries repeated by package s311.

| Item | Owner | Verdict | In one line | Errata |
|---|---|---|---|---|
| S5, PBH formation with a free-streaming component | no track | Not found: open | No full-GR kinetic calculation exists; the leading fluid group says in 2023 and 2025 that only a dedicated simulation with a fluid and a free-streaming component can decide whether neutrinos suppress or enhance formation in the e+e- epoch (`2303.07980/v2/src/PBHs_QCD.tex:367-368, 933-935`; `2406.11417/v1/src/chapter.tex:507-508`); add both to the key references of S5 | 3.16, 2.90 |
| S7, 3+1 numerical test of the Burnett conjecture | no track | Not found: open, but the premise of line 434 is outdated | No 3+1 comparison of a high-frequency vacuum evolution with Einstein-massless-Vlasov exists; the closest numerical work tests only the averaged radiation-like expansion (1505.02959); the conjecture is proven without symmetry in generalized wave coordinates (2403.03470), so S7 would be a first quantitative demonstration and a probe of the open reverse direction, not a test of an open 3+1 conjecture | 1.32, 3.17, 2.91 |
| S4 null test, NR test of the cosmological coupling | Track D | Partly done | No NR evolution of a black hole in an expanding matter background aimed at the coupling claim was found, but the NR lattice of 1903.01490 bounds abs(k) <= 5.0e-4 against k = 3.11 claimed by 2302.07878 (run kb-20261119-154605-3ee42d2; the bound is the package's reading, the paper does not frame it so); an NRPIC run adds the ambient collisionless medium and a separately measured accretion flux, and must reach or beat that bound; 2302.07878 itself expects k = 0 for Kerr, so a puncture tests the claim only for ordinary black holes | 2.87 |
| Binary black holes in a particle dark-matter environment, full NR | Track D (novelty statement, line 235) | Done in the broad form by 2611.12831 | The source paper evolves in full NR two black holes that form from clumps, inspiral and merge inside a collisionless envelope (`2611.12831/v1/src/main.tex:1335-1391`). Open: (i) a binary of pre-existing holes on a quasi-circular inspiral of many orbits in a dark-matter particle distribution much lighter than the binary; (ii) its waveform dephasing against vacuum; (iii) convergence in particle number and resolution of that dephasing; (iv) a comparison with the wave-dark-matter NR results and with Newtonian N-body friction | 3.14 |
| S12, Hills-type full NR of a binary passing a heavier black hole (line 273) | Track F | Not found, as of 2026-11-19 | Track F's four key INSPIRE queries return the same records (9, 8, 22, 19) four days later (run kb-20261119-153345-ed7ee04, package s311); the claim must stay narrow: full-NR binaries with a heavier third hole exist on bound orbits without separation (2406.11985, q = 4 and 9), and binaries are broken up in full NR by equal or lighter holes (0711.1165, 2505.03934); no full-GR calculation of a matter binary passing a black hole was found | 3.15 |
| S3, 3D full-GR kinetic SIDM collapse (line 234 and CHECK #39 of s37_38) | Track C | Not found | No counter-example to "a 3D full-GR kinetic SIDM calculation does not exist yet" (INSPIRE query files 3032b0f66c081770, 77f08945fdd1ef1d, 64636c015b786bf5); the abstract check of section 1 agrees | none |
| S1, S2: 3D Einstein-Vlasov particle evolution in cosmology | Tracks A, B | Not found | Headline of `s39_frontier/FRONTIER.md`; 2609.14218 is 3+1 NR with a dust fluid plus a particle-in-cell attempt in its last section (errata 2.61) | 2.61 |
| S8 sentence of line 441 (no numerical Vlasov spike study) | no track | Limited check | One INSPIRE query only (s8_k1); not a novelty search | none |

Limits common to the searches (`novelty/NOVELTY.md`, summary; `scratch/orch/wave3a_reports/kb.md`):
INSPIRE title and full-text indices, full text mostly for arXiv papers; a response holds at most
25 records sorted by date, so five broad queries (s5_k1, s5_k6, s5_c2, b_k4, b_k12) were read
only for their 25 most recent hits; theses, proceedings and papers without arXiv numbers were
seen only as titles; papers of the last days before 2026-11-19 may not be indexed; at most four
generic web searches per item; the embedding search of the knowledge base was not used (the
model is not installed in `wt/kb-brief`), only BM25 text search. A negative result means "not
found by these searches", not "does not exist". For S5, the calculation must cover the gradual
decoupling between 2 and 1 MeV, not only the fluid and free-streaming limits
([JUDGEMENT], same file). For the binary item, the authors' publication lists were read for the
two authors of 2611.12831 only; other groups with Einstein-Vlasov codes were found only through
the topic queries.

Requests that follow from the verdicts (package novelty): narrow the binary-in-dark-matter item
of line 1749 to (i)-(iv) above, and restate S7 without the premise of line 434. The brief stays
unedited (decision 0016 item 8); errata rows 1.32, 3.14 and 3.17 record both.

## 3. Open questions of brief sections 7 and 8

Source: `s7_s8/CHECK.md` parts B and C (searches up to 2026-11-19: citing papers of the cited
work on INSPIRE with `refersto:recid`, title and abstract queries, `kb search` of the store);
question 20 also `s37_38/CHECK.md` ("Answer to item 6"). Of the 26 questions none is answered,
16 are partly answered and 10 are open (Q3, Q4, Q6, Q9, Q10, Q16, Q18, Q24, Q25, Q26); of the
twelve candidates of section 8, four are partly answered, six open (U1, U4, U6, U7, U10, U12)
and two were not searched (U8, U9). Absence statements rest on INSPIRE queries and the store
and cannot prove absence (`scratch/orch/wave3a_reports/kb.md`, s7_s8). Some papers below were
read at their arXiv metadata only (locator `meta:arxiv-api/<id>`).

| Q (line) | Question, short | What answers part of it | Still open | Locator |
|---|---|---|---|---|
| Q1 (558) | a gauge that carries pressureless matter through caustics to black-hole formation | dust fluid: lapse and shift analysed, black hole not stably reached (2610.23218); particles in an early matter era evolve through crossing and form horizons, with "a big caveat" on the constraints after crossing (2609.14218); asymptotically flat prolate collapse through caustics into a black hole in moving-puncture gauge (2611.12831) | a gauge for particles in an expanding background with controlled constraints | `2610.23218/v1/src/main.tex:447-449`; `2609.14218/v1/src/MDPBH.tex:177, 1148`; `2611.12831/v1/src/main.tex:975` |
| Q2 (559) | existence and uniqueness of strong-perturbation data; physics of the branches | toy model: two branches, a maximum, horizons on the strong branch (2509.26470); an evolutionary solve of the constraints is unique by construction (2607.21308); periodic domains impose integrability conditions (2607.06441) | a general existence theory; the physics of the strong branch beyond spherical toy models | `2509.26470/v2/src/main_PRD.tex:249, 340`; `2607.21308/v2/src/cosmology.tex:76`; `2607.06441/v1/src/main.tex:66` |
| Q5 (562) | foliation-independent averages | gauge-invariant proposals (scalar-preserving perturbative; proper-time foliations) and a first quantitative study of foliation dependence (2401.09170) | an accepted nonperturbative construction | `2310.19451/v2/src/Verweg2023_ClassQuantGrav_Averaging_GaugeProblem_preprint.tex:41`; `2409.00024/v1/src/main.tex:49`; `meta:arxiv-api/2401.09170` |
| Q7 (567) | particle noise in constraint violation and spurious GWs | initial Hamiltonian and momentum violations scale as N^-1/2 at fixed mesh, controlled by particles per cell, and so do the late plateaus (2611.12831) | spurious GWs from particle noise: no quantitative study found | `2611.12831/v1/src/main.tex:1129, 1476, 1509-1511` |
| Q8 (568) | in what sense small-dispersion Vlasov approaches dust near caustics | dust is a singular case of Vlasov; Newtonian Vlasov-Poisson solutions do not form the dust singularities (2305.04360); Vlasov data close to Oppenheimer-Snyder dust form a trapped surface before any singularity (2410.06701, proof); linear Vlasov theory beyond dust in cosmology (2610.25145) | a convergence statement at caustics in GR | `2305.04360/v1/src/cc_hoop_conj.tex:99-100, 185`; `meta:arxiv-api/2410.06701`; `meta:arxiv-api/2610.25145` |
| Q11 (574) | threshold, mass spectrum and spin of black-hole formation in an early matter era | threshold for triaxial data with particles an order of magnitude below the analytic estimate, with the constraint caveat (2609.14218); spin only from analytic models | a mass spectrum from simulations | `2609.14218/v1/src/MDPBH.tex:177, 1148, 1211-1215` |
| Q12 (575) | GW spectrum of early-matter-era structure; validity of perturbation theory | Newtonian N-body plus lattice: agreement with the perturbative peak, considerable enhancement at smaller scales (2312.12499); inflaton-halo GWs from N-body (2212.00425); a fully relativistic simulation is called for above the light-crossing frequency of the largest halos | the relativistic spectrum | `2312.12499/v2/src/main.tex:109, 209, 251`; `2212.00425/v2/src/main.tex:82, 113` |
| Q13 (576) | collective collapse of several peaks; formation rate of primordial binaries | collective collapse of two peaks in the radiation era (2609.03051) | a binary formation rate; the early matter era | `2609.03051/v1/src/mainv_JJCC_final.tex:173, 803` |
| Q14 (577) | seed mass from SIDM core collapse | non-equilibrium Misner-Sharp (spherical GR) collapse gives a seed of about 3e-8 of the halo mass at horizon formation (2601.17117); population and post-collapse N-body growth (2609.13041, 2609.22758) | a 3D relativistic simulation | `2601.17117/v2/src/SIDM_MS.tex:60, 66-70`; `meta:arxiv-api/2609.13041`; `meta:arxiv-api/2609.22758` |
| Q15 (578) | relativistic dark-matter profile around black holes; backreaction on mergers | relativistic EMRI dephasing in spikes without backreaction on the metric (2505.09715); spikes depleted by EMRIs and by massive-black-hole mergers (2609.37234, 2611.13170) | a self-consistent relativistic backreaction | `2505.09715/v2/src/main_v2.tex:97, 256`; `meta:arxiv-api/2609.37234`; `meta:arxiv-api/2611.13170` |
| Q17 (580) | inhomogeneity and dark-energy inference at the DESI level | possible but rare in NR (1 of 20 observers, 2606.05479); order-of-magnitude effects in toy models; further backreaction claims in 2026 | no consensus | `2606.05479/v1/src/main.tex:50`; `2601.20633/v1/src/PRL_main_V2.tex:180`; `meta:arxiv-api/2607.20715`; `meta:arxiv-api/2609.31543` |
| Q19 (582) | Burnett conjecture without symmetry | direct direction proved under U(1) symmetry (1907.10743) and in generalized wave coordinates without symmetry (2403.03470); reverse direction without symmetry for finitely many null dusts (2402.17530) | genuine Vlasov limits without symmetry (only under U(1), 2506.21779); errata 1.32 | `1907.10743/v2/src/main.tex:87, 149`; `2403.03470/v1/src/wavecoordinate.arxiv.240305.tex:119, 143`; `2506.21779/v1/src/dustvlasov.250626.tex:124, 394`; `2402.17530/v2/src/superposition_final_AOPDES_first_revision_bis.tex:147` |
| Q20 (583) | nonlinear stability of matter-dominated FLRW under Einstein-Vlasov | the fluid analogue: EdS stable for Einstein-Euler with n > 3 on T^3 (2607.09326), Gowdy numerics (2606.16879), dust unstable; Landau damping on expanding backgrounds for repulsive Vlasov-Poisson only (2604.14911) | massive Einstein-Vlasov near EdS: nothing found; item 6 of section 15 can be closed (s37_38); errata 3.19 | `2607.09326/v1/src/main.tex:141, 307, 317`; `2606.16879/v1/src/main_v2.tex:43`; `2604.14911/v1/src/Landau-electro.tex:146, 257` |
| Q21 (587) | window, coarse-graining scale and slicing in the tail statistics, in full NR | coloured noise from non-sharp windows and non-Bunch-Davies states (2512.17070); non-Markovian simulations (2602.11652) and theory (2605.00476, 2611.15050); in NR only the window sharpness is discussed (2512.14649) | the effect on tails in NR | `2512.17070/v2/src/non-white.tex:40, 62`; `2512.14649/v2/src/PRD_v2.tex:503-507`; `2611.15050/v1/src/v5.tex:136`; `meta:arxiv-api/2602.11652` |
| Q22 (588) | NR stochastic inflation against stochastic delta N and the lattice; role of USR | a shear-free lattice bridging stochastic inflation and delta N (2604.00978); USR on the lattice with nonperturbative zeta enhances the positive tail that stochastic approaches miss (2506.11795) | the quantitative NR comparison, announced in 2512.14649, not done | `2604.00978/v3/src/main.tex:158`; `2506.11795/v2/src/main.tex:87, 114`; `2512.14649/v2/src/PRD_v2.tex:536` |
| Q23 (589) | replacing the inflaton condensate by Vlasov particles; matching across the hand-over | done in the Newtonian limit: N-body particles for the fragmenting condensate after inflation, Schrodinger-Poisson zooms (2011.13333, 2110.15109) | the relativistic hand-over with matched stress-energy and constraints | `2011.13333/v2/src/inflaton_halos_v2.tex:52, 64, 69`; `2110.15109/v2/src/inflaton_stars.tex:62, 86` |
| U2 (605) | caustic curvature spikes and GW bursts in an expanding background | asymptotically flat prolate collapse ends in black holes (2611.12831) | the expanding-background version | `2611.12831/v1/src/main.tex:975, 1373`; `meta:arxiv-api/2611.13266` |
| U3 (606) | extremal Kerr at the threshold | charged analogue proved and simulated (2402.10190, 2511.20567); gluing to extremal Kerr horizons proved in vacuum (2610.35836) | a rotating collisionless threshold study | `meta:arxiv-api/2511.20567`; `meta:arxiv-api/2610.35836`; errata 2.104 |
| U5 (608) | evolving the strong-field branch of 2509.26470 | Uehara et al. 2025 evolved "type II" data of this branch in spherical symmetry | the cosmology of the branch | `2509.26470/v2/src/main_PRD.tex:253`; errata 2.105 |
| U11 (614) | stochastic kicks and the constraints | the NR implementation satisfies the constraints to second order in the noise (errata 1.4) | where physical backreaction ends | `2512.14649/v2/src/PRD_v2.tex:536` |

Package s7_s8 addressed Q20 to Tracks A and B and Q24 (open; closest work 2605.22525 and
2604.27429) to Track F (`scratch/orch/wave3a_reports/kb.md`, s7_s8 requests). By subject
[JUDGEMENT of the clerk]: Q1 and Q11 bear on Track A, Q12 on Track B, Q14 on Track C, Q15 on
Track D, Q21-Q23 and U11 on Track E, Q26 (open) on Track F.
