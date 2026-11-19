# Novelty searches of brief line 1749 (section 15, item 5): S5, S7, the null test of S4, binary black holes in a particle dark-matter environment

Owner kb (helper "novelty", wave 3a), 2026-11-19, searches made between 07:33 and 07:45 PST.
S11 (covered by Track E's specification) and S12 (done by Track F,
`track/F-hills:tracks/F-hills/novelty/NOVELTY.md`) are not repeated. What was searched and how is
in `search/SEARCH_LOG.md`; the INSPIRE requests are listed with their labels in
`search/query_log.tsv`, and each response is the record
`kb-data/meta/inspire/query/<sha16>.json` written by `harness/bin/nrpic-fetch-arxiv`
(cited below as `inspire-query:<label>`). Paper locators `<id>/<v>/src/<file>:<line>` are lines of
the TeX sources under `kb-data/raw/arxiv/`; seven sources were fetched for this package (2403.03470,
2009.08968, 2404.07659, 2406.11417, 2606.26532, 2607.09285, 2508.13294); every other paper cited
here was already in the store. Labels as in the brief: [VERIFIED] read in the source at the locator, [JUDGEMENT] our
reading, [TO VERIFY] not settled here.

## Summary

| Item | Verdict | In one line |
|---|---|---|
| S5, black-hole formation with a free-streaming component | **Not found: open** | No full-GR kinetic calculation exists; the authors of the leading fluid study say in 2023 and again in 2025 that only a dedicated simulation with a fluid and a free-streaming component can settle whether neutrinos suppress or enhance formation in the e+e- epoch |
| S7, 3+1 numerical test of the Burnett conjecture | **Not found: open, but the premise is outdated** | No 3+1 comparison of a high-frequency vacuum evolution with Einstein-massless-Vlasov exists; the closest numerical work tests only the averaged radiation-like expansion (1505.02959). The conjecture itself is no longer open without symmetry (2403.03470), so S7 cannot be pitched as the first test of an open 3+1 problem |
| S4 null test, NR test of cosmological coupling | **Partly done** | No NR evolution of a black hole in an expanding matter background aimed at the coupling claim was found, but an NR lattice of vacuum black holes already shows horizon masses constant to 0.1 per cent while the scale factor grows by e^2 (1903.01490), i.e. abs(k) of 5e-4 at most |
| Binary black holes in a particle dark-matter environment, full NR | **Done in the broad form by 2611.12831** | The target paper itself evolves, in full NR, two black holes that form from clumps, inspiral and merge inside a collisionless envelope (§4 of 2611.12831). Open: a quasi-circular binary of pre-existing holes in a dark-matter particle distribution, with the dephasing measured against vacuum and convergence in particle number |

Common limits of all four searches: INSPIRE title and full-text indices (full text covers mostly
arXiv papers); a response holds at most 25 records sorted by date, so six broad queries (s5_k1,
s5_k6, s5_c2, s7_k5, b_k4, b_k12) were read only for their 25 most recent hits; theses,
proceedings and papers without arXiv numbers were seen only as titles; papers of the last days
before 2026-11-19 may not be indexed; four generic web searches per item at most. A negative
result means "not found by these searches", not "does not exist".

## 1. S5: primordial-black-hole formation with a free-streaming component

Queries: s5_k1 to s5_k12, s5_c1, s5_c2 (INSPIRE: PBH with neutrino(s), with free streaming,
collisionless, kinetic, Vlasov or Boltzmann; with anisotropic, imperfect, two- or multi-fluid or
viscous matter; full text "Einstein-Vlasov" or "massless Vlasov" with PBH; NR PBH papers after
2023; papers citing 2303.07980 that mention free streaming; papers citing the anisotropic-fluid
threshold paper 2110.05982), two web searches, two knowledge-base searches.

Closest papers:

- **arXiv:2303.07980** (Musco, Jedamzik, Young 2023; PBH formation in the QCD and e+e- epochs with
  a fluid equation of state). The decisive statement [VERIFIED]: at T of about 1-2 MeV neutrinos
  decouple (`2303.07980/v2/src/PBHs_QCD.tex:346`), free-stream out of overdensities, and with
  rho_nu/rho_tot = 5.25/10.75 about half of an adiabatic overdensity is lost (`:355-358`); the
  opposite effect (neutrinos attracted into the photon-e+e- overdensity, which lowers w) is also
  named (`:361-365`); the authors lean to suppression and state "only a dedicated simulation of
  PBH formation with a fluid and free-streaming component could definitely answer this question.
  Such a study is beyond the scope of the current paper" (`:367-368`, again `:933-935`). The
  abstract repeats it (`:204-205`).
- **arXiv:2406.11417** (Jedamzik 2025, review chapter). Same argument (`2406.11417/v1/src/chapter.tex:485-507`)
  and "The formation of PBHs during the e+e- annihilation is therefore an open question"
  (`:507-508`). [VERIFIED] This is the most recent statement by the field that S5 is open.
- **arXiv:2110.05982** (Musco, Papanikolaou 2022): radiation fluid with anisotropic pressure,
  initial conditions and a threshold estimate (`2110.05982/v4/src/PBH_aniso.tex:88-93`); fluid
  level, no kinetic species.
- **arXiv:2606.26532** (2026): spherical BSSN with a bulk-viscous fluid; threshold rises about
  linearly with the viscosity (`2606.26532/v3/src/arXiv.tex:52-53, 64, 78`). Dissipative fluid,
  not free streaming.
- **arXiv:2607.09285** (Gonin 2026): kinetic (semi-classical) absorption of neutrinos by PBHs that
  already exist, mass growth from 1e-3 to 1e9 M_sun (`2607.09285/v4/src/apssamp.tex:79-87`). Kinetic,
  but accretion after formation and on a fixed background.
- **arXiv:2608.13206** (2026): 3+1 GRChombo, radiation fluid, threshold and Zel'dovich-Novikov
  growth (`2608.13206/v3/src/PRD.tex:39, 457-466`); fluid only.
- **arXiv:2609.14218** and **arXiv:2109.04896**: full NR in a matter era with collisionless
  particles (`2609.14218/v1/src/MDPBH.tex:165-170`) or a massive scalar field
  (`2109.04896/v3/src/PBH_formation.tex:89, 103`); non-relativistic matter, no radiation.
- Einstein-Vlasov collapse with massless or charged particles exists only in asymptotically flat
  spherical symmetry (critical collapse gr-qc/0107076, `inspire-query:s5_k4`; extremal charged
  threshold 2402.10190, 2511.20567).

Verdict [JUDGEMENT]: no full-GR calculation of PBH formation with a free-streaming relativistic
component was found, and two papers by the leading group name exactly this calculation as the
missing one. S5 is open and its motivation is stronger than the brief states: the sign of the
effect (suppression or enhancement of the ~1e5 M_sun peak of the thermal-history scenario) is
disputed. Physics the brief should carry (run kb-20261119-154605-3ee42d2): the horizon mass is
1.50e5 M_sun at T = 1 MeV and 3.7e4 M_sun at 2 MeV (g_* = 10.75), and the neutrino share of the
radiation is 0.488 before and 0.409 after e+e- annihilation. Limits: decoupling is gradual
(the mean free path passes the Hubble length across 1-2 MeV [JUDGEMENT]), so a calculation must
cover the transitional regime, not only the two limits; the kinetic species and the fluid must be
coupled in one evolution (decision 0010: in AthenaK, massless particles plus the dynamical-spacetime
fluid of 2409.10384). Recommendation: add 2303.07980 and 2406.11417 to the key references of S5.

## 2. S7: a 3+1 numerical test of the Burnett conjecture with massless Vlasov particles

Queries: s7_k1 to s7_k13 (INSPIRE: Burnett or high-frequency Einstein in the title;
high-frequency or short-wavelength GW backreaction; GW with null dust, massless Vlasov, kinetic
theory, geometric optics or graviton gas and numerical; citations of Green-Wald 1011.4920 with
numerical titles; all citations of Huneau-Luk 1706.09501 and 2403.03470; citations of
Luk-Rodnianski 2009.08968 with numerical relativity; GW turbulence; citations of 1505.02959; full
text Burnett + numerical relativity + Vlasov), three web searches, one knowledge-base search.

Closest numerical papers:

- **arXiv:1505.02959** (Ikeda, Yoo, Nambu 2015). Full 3+1 NR of a vacuum universe filled with
  nonlinear standing gravitational waves in a periodic box, slicing with spatially uniform K,
  testing Isaacson's statement that high-frequency waves behave as a radiation fluid on average:
  H proportional to L^-2 holds to 3 per cent without and 0.1 per cent with a temporal average,
  even for wavelengths comparable to the Hubble length (`1505.02959/v1/src/letter-GWuni.tex:47-64,
  98-132`). [VERIFIED] The review 2409.01939 lists it as the NR confirmation of Isaacson's formula
  (`2409.01939/v2/src/main.tex:1072`). This tests the trace part of the Green-Wald and Burnett
  statements (radiation-like, traceless effective stress), not the Vlasov structure (momentum
  distribution, transport along null geodesics, anisotropic stress), and there is no matter
  evolution to compare with.
- **arXiv:2108.09158** (Galtier et al. 2021): first direct numerical simulation of GW turbulence,
  diagonal metric depending on two coordinates, weak waves, dissipation (`inspire-query:s7_k6`,
  abstract). Symmetry-reduced; no Vlasov comparison.
- **arXiv:1803.10719** (Clough et al. 2018): GW-turbulence initial data expand or collapse faster
  than a cascade develops (`inspire-query:s7_k6`, abstract).
- **arXiv:2508.13294** (Ma et al. 2025): nonlinear mode interactions and turbulence of black-hole
  perturbations in full GR (`2508.13294/v2/src/PRL_B.tex:125-131`); not high-frequency backreaction.
- **arXiv:1801.08362** (Wang 2018): Einstein Toolkit, FLRW with scalar curvature and primordial
  tensor perturbations (`1801.08362/v2/src/tensor.tex:61`); matter-dominated, not a high-frequency
  limit.

Mathematical state (for the premise of brief line 434) [VERIFIED]:

- Forward conjecture proven in generalized wave coordinates in any dimension d >= 3, "the first
  proof ... without symmetry assumptions or angular regularity assumptions"
  (`2403.03470/v1/src/wavecoordinate.arxiv.240305.tex:119, 143`); earlier under U(1) symmetry
  with an elliptic gauge (1907.10743, `meta:arxiv-api/1907.10743`) and in double-null gauge
  without symmetry but with angular regularity, limit Einstein-null dust
  (`2009.08968/v1/src/HFlimit.200918.tex:101-103`).
- Reverse conjecture: under polarized U(1) for multiple null dusts (1706.09501), under U(1) for
  Einstein-massless-Vlasov (2506.21779, `meta:arxiv-api/2506.21779`), without symmetry for
  finitely many null dusts in generalized wave gauge (Touati 2402.17530, `inspire-query:s7_k1`
  abstract; also 2206.12318). Open, by the survey 2404.07659: infinitely many phases without
  symmetry (i.e. a general Vlasov field), gauge independence, global and large-data
  constructions (`2404.07659/v1/src/Burnett.survey.240411.tex:1571, 1578-1580, 1588-1590,
  1595-1599`).

Verdict [JUDGEMENT]: no 3+1 numerical test of Burnett's correspondence (a high-frequency vacuum
evolution set against an Einstein-massless-Vlasov evolution of the corresponding particle
distribution) was found; the test is new. Its pitch must change: it no longer probes an open
3+1 conjecture (the forward direction is a theorem in generalized wave coordinates); it would be
the first quantitative, finite-frequency demonstration, with rates and gauge dependence, and a
numerical probe of the reverse direction where the mathematics is open (general Vlasov field
without symmetry). The application (sub-grid GW transport by massless particles) was not found
either. Limits: mathematics papers are indexed by INSPIRE only when they are on gr-qc; the
citation lists of 1706.09501 (25) and 2403.03470 (8) were read completely.

## 3. Null test of S4: a numerical-relativity test of the cosmological coupling of black holes

Queries: s4_c1 to s4_c5 (papers citing 2302.07878, INSPIRE record 2633033, with numerical
relativity, apparent horizon, horizon, GR or exact-solution titles), s4_k1 to s4_k12 (titles with
cosmologically coupled; black hole with expanding, FLRW, Einstein-de Sitter, dust, McVittie,
Swiss cheese; black-hole lattices; apparent-horizon or horizon-mass growth), three web searches,
one knowledge-base search. 2302.07878 has 120 citing records (citation count in
`inspire-query:pre_k2`); 3 of them mention numerical relativity in the full text (`inspire-query:s4_c1`), none
is an NR evolution.

Closest papers:

- **arXiv:1903.01490** (Giblin, Mertens, Starkman, Tian 2019; NR lattice of spinning black holes,
  periodic, CTT initial data). [VERIFIED] The horizon area stays the same while the coordinate
  size shrinks with the expansion (`1903.01490/v2/src/spinning_BH_v2_CT.tex:640-641`); lengths
  grow by about e^2 before the run stops (`:642-644`); "the relative fluctuation in their values
  is as small as 0.1%", consistent with the area theorem (`:653-657`); M_H "is conserved,
  implying matter-domination-like expansion" (`:713-715`; also `:733-734`). For M proportional
  to a^k this bounds abs(k) <= 5.0e-4 (run kb-20261119-154605-3ee42d2) [JUDGEMENT: the paper
  does not frame it so], against k = 3.11 (+1.19, -1.33) claimed by 2302.07878
  (`2302.07878/v1/src/paper_couple_rev.tex:130`).
- **arXiv:1306.4055**, **1204.3568**, **1404.1435** (Bentivegna, Korzynski and others; vacuum
  black-hole lattices in NR, `inspire-query:s4_k9`): expansion close to FLRW; horizon masses
  not the target.
- **arXiv:2109.04896** (de Jong et al. 2022): full NR in a scalar-field matter era; the black
  hole grows beyond the self-similar rate by accretion (`2109.04896/v3/src/PBH_formation.tex:58,
  267`). Growth by accretion, not by coupling, and not separated.
- The rebuttals and models of the coupling are analytic or observational
  (`inspire-query:s4_k1`, `s4_c3`, `s4_c4`, `s4_c5`): 2304.09817 (comment), 2302.12386, 2305.01307,
  2312.12344, 2307.02474 (observational limits), 2306.11588, 2309.16444, 2601.03296, 2410.10459,
  2407.14549, 2608.21222, 2609.38303 (models, apparent and event horizons, linearized GR).

Verdict [JUDGEMENT]: the coupling has not been tested by an NR evolution of a black hole in an
expanding matter background, but the brief's null test is partly done already: in vacuum
lattices, where the expansion is driven by the black holes themselves, horizon masses are
constant to 1e-3 over a growth of e^2 in the scale factor. What an NRPIC run would add is an
ambient expanding collisionless medium, so that accretion (the flux through the horizon) is
measured and subtracted, as the brief proposes. Two caveats for the write-up: 2302.07878 itself
expects k = 0 for Kerr-like black holes and attributes k = 3 to black holes with vacuum-energy
interiors (`paper_couple_rev.tex:132, 174`), so a puncture giving k = 0 tests the claim only for
ordinary black holes (as the brief says) and cannot refute it for the non-singular objects the
claim is about; and the result should be compared with the lattice bound above, which it must
match or beat.

## 4. Binary black holes in a particle dark-matter environment, full numerical relativity

Queries: b_k1 to b_k15, b_a1, b_a2 (INSPIRE: binary black hole and dark matter with numerical
relativity in the full text; with collisionless, Vlasov, particles, N-body, spike or halo; with
Einstein-Vlasov in the full text; with test particles or geodesics; dynamical friction with
relativistic or NR; citations of the wave-dark-matter NR paper 2210.09254 (79, the 25 most recent
read); citations of 1805.09034 with NR (34, 25 read); citations of 2611.12831 (none); recent papers
of the two authors of 2611.12831), four web searches, one knowledge-base search.

Closest papers:

- **arXiv:2611.12831** (Wu, Most 2026, the target paper), section 4 [VERIFIED]: a stable
  relativistic cluster (M_c = 0.76 M, areal radius 30 M) with two Gaussian clumps of 0.12 M each
  on near-circular orbits (`2611.12831/v1/src/main.tex:1335-1336`), 5e6 particles, 11 refinement
  levels (`:1338`); both clumps collapse to black holes at t = 8.475 M and 8.525 M, the binary
  inspirals in the collisionless envelope and merges, common horizon at t_m = 64.15625 M (`:1340`);
  between 20 M and 60 M the binary's orbital angular momentum falls by 27.3 per cent while the
  envelope gains a comparable amount (`:1358`); the remnant accretes from the envelope
  (`:1360`); the waveform has "no inspiral signal" because of the rapid orbital decay (`:1362`);
  conclusion: binary evolution and accretion from collisionless matter "within a single
  dynamical-spacetime calculation" (`:1384-1391`). This is a full-NR binary black hole in a
  particle environment.
- NR binaries in wave (scalar-field) dark matter: 2210.09254 (equal-mass binaries, quasi-stationary
  profile, `2210.09254/v2/src/main.tex:72-74`), 2311.18156 (dephasing over the last ten orbits,
  `2311.18156/v2/src/main.tex:63-65`), 2409.01937 (self-interacting scalar,
  `2409.01937/v2/src/main.tex:86-88`), 2510.20037, 2610.15053, 2507.18934 (two-dimensional drag on a
  binary) (`inspire-query:b_k1`, `b_k4`).
- Particle dark matter around binaries, Newtonian only: 1805.09034 (Gadget, gravity only,
  `1805.09034/v3/src/main.tex:61, 286`), 2402.13762 (NbodyIMRI, "The dynamics of all particles in the
  simulation is Newtonian. We do not include any Post-Newtonian (PN) corrections",
  `2402.13762/v1/src/main.tex:191, 238`).

Verdict [JUDGEMENT]: as worded in brief line 1749 the item is not new; 2611.12831 has done a
full-NR binary black hole inside collisionless particles. What was not found, and remains open:
(i) a binary of pre-existing black holes (punctures) on a quasi-circular inspiral of many orbits
inside a dark-matter particle distribution of astrophysical density contrast (a spike or halo
much lighter than the binary, unlike the envelope of 2611.12831, which is three times the mass of
the clumps); (ii) the dephasing of the waveform against the same binary in vacuum; (iii)
convergence in particle number and resolution of that dephasing; (iv) a comparison of the
particle result with the wave-dark-matter NR results and with the Newtonian N-body friction.
Limits: two authors' publication lists were read (b_a1, b_a2); other groups with Einstein-Vlasov
codes (East, Shibata, Yoo) were found only through the topic queries.

## Requests and consequences

- For `coord/BRIEF_ERRATA.md`: the rows in `ERRATA_ROWS.md` (line 434 corrected; line 1749
  binary item corrected; lines 400 and 437 and the S5 items imprecise or answered).
- For Track D (S4): the null test must beat abs(k) <= 5e-4 from 1903.01490 to add information,
  and its design needs the accretion flux through the horizon as a separate diagnostic.
- For Track D and the group's ranking (section 5 of the brief): the binary-in-dark-matter item
  should be narrowed to (i)-(iv) above.
- For the S5 owner (no track yet): 2303.07980 and 2406.11417 belong in its key references.
