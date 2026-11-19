# Frontier after the brief's survey: groups and lines of work of brief section 3.9

Owner kb, work package s39_frontier, wave 3a, 2026-11-19. What is new for each of the tracks A
to F (and core) since the survey of the brief (version 2, 2026-11-15; its newest id is
2611.15050), for the groups and lines of work named in brief lines 243-255, with one line on
whether it changes a track's plan or overlaps with it.

## How it was searched

- Forward citations (INSPIRE `refersto:recid:`) of all 32 ids of lines 243-255, and topic and
  author queries per row, restricted to recent months: run kb-20261119-152359-851b963 (59
  queries). Track D has no row in section 3.9, so it got its own queries (dark-matter spikes,
  dress, Einstein-Vlasov environments, relativistic dynamical friction), together with extra
  topics for A, B, C, E, F and the last weeks: run kb-20261119-152939-22939e5 (15 queries).
  The queries are `specs/inspire_queries.txt`, `specs/inspire_queries2.txt`; each result is
  stored as served under `kb-data/meta/inspire/query/` (paths in `queries.tsv` of each run).
- Scan: run kb-20261119-153319-ad2a3a7 (`scripts/fig_frontier.py`, `scripts/frontier_scan.py`)
  merged the 74 results: 284 distinct papers with an arXiv id, 226 of them not cited anywhere in
  the brief (the brief's text searched for the id), 47 of those dated 2026-10 or later, 11 in
  2026-11. No query was truncated (every hit count ≤ 25, the page size). Output:
  `scratch/kb/kb-20261119-153319-ad2a3a7/{candidates,abstracts,queries_summary}.tsv`,
  `fwd_counts.json`, `tally.json`; figure `figures/fig_frontier.png`.
- Exact dates of the 11 November items and four October ones: arXiv API, run
  kb-20261119-153125-0836e49 (`kb-data/meta/arxiv-api/<id>.json`).
- Only one paper found is dated after the survey: 2611.23627 (2026-11-17). The ten other
  November items (2026-11-02 to 11-11) and everything earlier are papers the survey did not
  cite. Limit: INSPIRE indexes new arXiv papers with a delay of days, so the week
  2026-11-12 to 11-19 is covered only as far as INSPIRE had it at 15:24-15:31Z; the arXiv
  listing itself cannot be searched with the fetch tool (it takes ids, not queries).

Evidence. One-line summaries rest on the abstract as served by INSPIRE (`abstracts.tsv` of
run kb-20261119-153319-ad2a3a7) and are [VERIFIED: abstract]; where the TeX source is in the
store and was read, the locator is given. "Plan" lines are [JUDGEMENT] of this package, for
the track lead to accept or reject. Nothing here is a number for a note: the numbers quoted
are the abstracts' and must be taken from the paper before use (CLAUDE.md rule 7).

Headline. No paper found does three-dimensional Einstein-Vlasov (particle) evolution in
cosmology, a full-GR Hills disruption, a 3D kinetic general-relativistic SIDM collapse, or a
full-NR black hole in a particle dark-matter environment: the novelty claims of tracks A, C, D
and F stand as far as these searches reach. 2611.12831 has no citing paper in INSPIRE yet.

## Track A (PBH formation in an early matter era, S1)

| arXiv (date) | Authors | What is new | Plan |
|---|---|---|---|
| 2610.01964 (2026-10-01) | Bambague, Bezares, Clough | Automatic differentiation locates a line of critical solutions in a 2D parameter space of scalar collapse with 35 runs, against 270 runs for 10 points by bisection; computes the unstable mode directly | Overlaps in aim with A's threshold line in (ellipticity, amplitude); AthenaK is not differentiable, so no change, but the run count is a benchmark for A's scan budget |
| 2607.08738 (2026-07) | Escrivà | Finite-action statistics of curvature-profile dispersion around peak profiles, applied to spherical collapse thresholds | Context for the statistics of A's thresholds; no change |
| 2607.27343 (2026-07) | Redondo-Yuste, Aurrekoetxea | NR test of perturbation theory near the collapse threshold of a scalar field | Context; no change |
| 2611.05996 (2026-11-04) | Kishimoto, Joana, Suyama | Full NR of a massive cosmic string in a radiation background, cylindrical symmetry | Cosmological-gauge experience only; no change |
| forward citations of 2609.14218 | — | Three citing papers (2608.13206, 2610.08045, 2610.23218), all already in the brief | The direct competitor has no newer particle follow-up; A's plan (decision 0016 item 5) stands |

## Track B (gravitational waves from early-matter-era structure, S2)

| arXiv (date) | Authors | What is new | Plan |
|---|---|---|---|
| 2609.11891 (2026-09) | del-Corral, Spalding | Relations mapping the characteristic frequencies of a GW background onto the mass and abundance of PBHs whose domination made an early matter era | Context for the population spectrum (B's second goal); no change |
| forward citations of 2605.04487 | — | 2605.11332, 2604.13012, 2504.20135: background phenomenology, none computes structure-formation waves | No competitor to B's full-GR pancake; no change |
| Macpherson group | — | No paper by Macpherson after 2026-06 in INSPIRE (author query, 0 hits) | Nothing to add to the S6 benchmark |
| Adamek group | 2607.28207 (Nouri-Zonoz, Hassani, Adamek et al.), 2605.09004 (Fremstad, Adamek, Mota) | Late-universe applications (kinetic gravity braiding signatures; a separate-universe super-resolution emulator) | Weak-field late universe; no overlap with B |
| 2608.27962 (2026-08) | Bendtsen, Koksbang | Learning the averaged history of an inhomogeneous universe from its present density field | Backreaction context (S6); no change |

The searches did not include "pancake" or "shell crossing" as terms; the B-specific literature
on plane-symmetric collapse is outside this package (brief lines 239-256 name none).

## Track C (relativistic collapse of an SIDM core, S3)

| arXiv (date) | Authors | What is new | Plan |
|---|---|---|---|
| 2610.28890 (2026-10-20) | van den Bosch, Tokayer | Spherical direct-simulation Monte Carlo code without force softening; N-body converges to it only with much smaller softening than usual; several scatterings per particle per step are harmless if implemented appropriately; the usual harmonic interpolation between long- and short-mean-free-path conductivities is inaccurate, a gentler transition fits; collapse slows once the core is optically thick | May change C's Newtonian fluid reference: if C's reference model uses the harmonic interpolation of the conductivities, check it against this calibration. Also a Newtonian check for C's Monte Carlo step (several scatterings per step). Request to C below |
| 2610.28745 (2026-10-20) | Gurian, Gandhi, Dalal | Kinetic simulations (KiSS-SIDM) of isolated halos over cross sections 50 to 250 000 cm^2/g; the collapse time is predicted by the Knudsen number at the scale radius; a hydrostatic fluid model calibrated to them | Overlaps with C's goal (collapsed mass fraction against Knudsen number) in the Newtonian regime: the Newtonian Kn dependence now exists, C's addition is the relativistic endpoint; use as the Newtonian baseline |
| 2609.16122 (2026-09) | Gu, Jiang, Chen, Li et al. | Applies the relativistic non-equilibrium (Misner-Sharp) halo model of 2601.17117 to little red dots: seeding and super-Bondi accretion | Same spherical fluid model as 2601.17117; no 3D kinetic GR; no change |
| 2510.24565 (2025-10) | Feng, Yu, Zhong | GR instability of a self-gravitating thermal system with Fermi degeneracy (truncated Fermi-Dirac, TOV, Chandrasekhar criterion) | A further onset criterion beside 2108.11967 for C's threshold stage; no change |
| 2610.37852, 2606.19428, 2609.22758 | Batteas et al.; Schmidt, Fischer, Garny; Zeng et al. | Inelastic SIDM universality (fluid); dissipative SIDM (N-body); post-collapse BH-halo co-evolution (N-body) | Newtonian context; no change |

Abstract check: among the 40 papers found by the C queries and the forward citations of
2601.17117 and 2506.17641, only 2601.17117 (in the brief), 2609.16122, 2510.24565 and
2511.09311 mention a relativistic treatment, and none is a 3D kinetic calculation
(`grep` over `abstracts.tsv`, this package's journal entry 4).

## Track D (black-hole growth and dark-matter dress, S4)

| arXiv (date) | Authors | What is new | Plan |
|---|---|---|---|
| 2610.33150 (2026-10-23) | Hoefken Zink, Piantadosi | A general-relativistic Eddington inversion: the distribution function in the energy at infinity from a density profile on a TOV background (dark matter as an effective perfect fluid), with a regularization of the boundary term; applied to an NFW halo with a Gondolo-Silk spike around Sgr A* | Overlaps with D's spike in the strong field: a candidate reference distribution function for sampling a relativistic spike as initial data (isotropic, static background) |
| 2611.08145 (2026-11-05) | Hassanabadi, Zare | A truncated spike as an Einstein cluster (circular orbits only, vanishing radial pressure) around Schwarzschild, with closed-form metrics for indices 7/3 and 3/2 | A closed-form GR test configuration for D's particle initial data; not the adiabatically grown spike; no change |
| 2609.14755 (2026-09) | Pradhan, Ghaderi, Zeyauddin et al. | Static, spherical, self-consistent Einstein-Vlasov black-hole environments parametrized by the occupation of orbital actions; the horizon response to orbital redistribution at fixed masses (`2609.14755/v1/src/Paper.tex:33-57`) | Overlaps with D's strong-field spike: equilibrium families to compare with; static only, no change |
| 2611.13170 (2026-11-09) | Sharpe, Spieksma, Ginat et al. | A massive-black-hole merger depletes the spike within about 100 Schwarzschild radii by orders of magnitude (q = 0.03), and even q = 0.005 depletes it | Bears on D's later goal, dressed binaries: the dress may not survive a merger history; a motivation caveat, no change to the first goals |
| 2610.13684 (2026-10) | Wang, Chadha-Day, Clough et al. | Relativistic dynamical friction of matter on a static boosted Kerr-Schild background (first order in the matter density) | Comparison for drag on a dressed binary; no change |
| 2610.15053, 2507.18934 | Zhang, Wei, Liu; Xin, Most | Full NR of binaries in scalar (wave) dark-matter environments; relativistic scalar drag forces | Wave dark matter, not particles: the "full NR with particle dark matter" gap (brief line 235) stays open; no change |

## Track E (stochastic inflation, S11)

| arXiv (date) | Authors | What is new | Plan |
|---|---|---|---|
| 2610.26669 (2026-10) | Braglia, Franciolini et al. | Mean-field backreaction in single-field inflation (decoupling limit): Bunch-Davies UV modes distort backreaction unless adiabatically subtracted; reproduces lattice results but shows a spurious UV sensitivity in some cases | Bears on E's acceptance criteria (UV sensitivity of the noise and of backreaction); no change, add as a check |
| 2602.11652, 2605.00476 | Kawasaki, Kuroda; Cruces, Kuroda | Stochastic formalism with non-Markovian noise: UV modes evolved on the stochastic IR background | A known alternative to the Markovian noise of E's implementation; context for the validity discussion; no change |
| 2606.28005 (2026-06) | Barnert, Iacconi, Assadullahi et al. | Smooth Hubble-flow parametrisations of USR hide sharp spikes in higher derivatives of the reconstructed potential | Check E's inflection-point test potential for such features; no change otherwise |
| 2609.21578 (2026-09) | del-Corral, Gondolo, Kumar et al. | Metric fluctuations stop being negligible during preheating (linearized constraints) | Extends the warning of 2606.14853 to reheating; relevant to a later field-to-particle hand-over; no change |
| 2610.42044 (2026-10) | Blachier | Elastic (interpolating) end-of-diffusion boundaries in stochastic delta-N | Context; no change |
| Launay, Rigopoulos, Shellard | — | Nothing after the thesis 2610.32592 (author query since 2026-06: only the thesis) | E's comparison base unchanged |

## Track F (Hills mechanism, S12)

| arXiv (date) | Authors | What is new | Plan |
|---|---|---|---|
| 2605.20320 (2026-05) | Cardoso, Ficarra, Redondo-Yuste et al. | Full NR (Einstein Toolkit) of head-on collisions of a black-hole pair next to a companion, three holes from rest; configurations chosen to satisfy the Hills criterion so that the pair is not disrupted (`2605.20320/v2/src/main.tex:86, 169, 205-220, 274`) | Partial overlap: the first full-NR three-hole set-up with a Hills-criterion check, but in the non-disruptive, head-on regime; F's disruptive pericentre scan stays new; cite it |
| 2604.27429 (2026-04) | Sharma, Heger, Price et al. | A benchmark of binary-SMBH encounters with post-Newtonian schemes and a scalar perturbation of the background metric (`2604.27429/v1/src/template.tex:22, 45, 72-74`) | A baseline in the approximation ladder below F; no change |
| 2605.22525 (2026-05) | Maeda, Okawa | A binary in a local inertial frame of Kerr: adiabatic, tidally affected, chaotic and disruptive scattering regimes by semimajor axis | Regime boundaries to compare with F's pericentre scan line; no change |
| 2610.09336 (2026-10) | Qiao, Liu | Head-on collisions of several black holes in BSSN (AMSS-NCKU) from rest | Context for multi-hole data; no change |
| 2608.22735, 2607.18761 | González-Servín, Tejeda et al.; McGuire et al. | Restricted three-body plus SPH for star-white-dwarf binaries; semi-analytic binaries in the empty loss cone | Newtonian context; no change |

## core and the NRPIC authors' group

| arXiv (date) | Authors | What is new | Plan |
|---|---|---|---|
| 2611.23627 (2026-11-17, after the survey) | Solod, Kim, Most | A five-point smoothness indicator as a refinement criterion, implemented in AthenaK and tested on Newtonian, special- and general-relativistic MHD benchmarks | Relevant to core's refinement work for periodic runs (cosmo-amr package): a candidate criterion that lives in the same code base; information for core, no change forced |
| 2611.12831 | Wu, Most | No citing paper in INSPIRE at 15:24Z | Nothing to follow yet |
| 2609.25240, 2609.25241 | Asenjo, Winkler, Comisso; Comisso, Asenjo | Frozen-in gravitational field lines and their reconnection in the electrodynamic formulation of GR (citing 2504.15978, 2509.19769) | Formulation follow-ups by another group; no effect on the pusher |
| 2611.15318 (2026-11-11) | Shen, Song, Wan | Weak null singularities for the massive and massless Einstein-Vlasov systems without symmetry (mathematics) | No effect |
