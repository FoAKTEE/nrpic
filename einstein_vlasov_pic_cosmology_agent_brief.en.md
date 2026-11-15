# Einstein–Vlasov PIC (NRPIC) for cosmology: survey, assessment, parallel execution plan and literature base

> Nature of this document: a start-up prompt for Claude Code agents and an index to the knowledge base. Version 2, 2026-11-15 (the Chinese version is the file of the same name without `.en`; section numbers, references and command blocks correspond one to one).
> Goal of the project: do cosmology starting from the numerical-relativity particle-in-cell method of arXiv:2611.12831, advancing science problems and method innovation side by side.
> What changed in version 2: six science tracks run at the same time, each in its own git worktree (§9); a harness for context sharing and environment isolation (§11), a procedure for building the knowledge base (§12), git discipline and stage-check commands (§13) and kick-off prompts (§14) were added; stochastic inflation and the Hills mechanism were added as new directions (§3.10, §3.11, S11 and S12 in §5); the critical-path risk that the NRPIC module cannot be found in public AthenaK is recorded (§2.2).

**File structure (read by line ranges; §0–§15 are the main text, §16–§17 are for lookup).**

- lines 30–68: 0. How to use this document
- lines 69–83: 1. Bottom line first
- lines 84–137: 2. Starting point: the NRPIC of Wu & Most (2026)
- lines 138–278: 3. Landscape: numerical relativity × cosmology
- lines 279–313: 4. Criteria: which problems need both NR and kinetics
- lines 314–492: 5. Ranking of the science problems
- lines 493–553: 6. Directions for method innovation
- lines 554–595: 7. List of open questions (known unknowns)
- lines 596–625: 8. Unknown unknowns: where to look for surprises
- lines 626–833: 9. Execution plan: six parallel tracks
- lines 834–862: 10. Verification and benchmark suite
- lines 863–1217: 11. Harness: context sharing and environment isolation
- lines 1218–1461: 12. Building the knowledge base (after the arXiv sources and the GitHub code have been downloaded)
- lines 1462–1625: 13. Git discipline, working notes and stage checks
- lines 1626–1742: 14. Kick-off prompts
- lines 1743–1762: 15. Items for the agents to verify or complete
- lines 1763–2529: 16. References
- lines 2530–3299: 17. Machine-readable manifests and download rules

---

## 0. How to use this document

**Your role.** You work for a numerical-relativity and cosmology group. This document serves four kinds of session. First establish which one you are, then read according to the table:

| Session | Worktree | Must read | Reference |
|---|---|---|---|
| Orchestrator | main checkout `repo/` (main) | §0, §1, §2.2, §9, §11, §13 | §12, §14 |
| Knowledge-base builder | `wt/kb` | §0, §12, §16, §17 | §11.3, §13.1 |
| core (shared NRPIC implementation) | `wt/core` | §0, §2, M1–M3 in §6, §9.3, §10 | §11, §13 |
| Tracks A–F | `wt/<ID>` | §0, §4, your own problem in §5, your own track sheet in §9, §10, §13 | §3, §6–§8 |

Whichever you are, after reading you must be able to do four things:

1. take numbers from the knowledge base (§12), not from this document, which only points the way;
2. check, one by one, the statements labelled [BACKGROUND] and [TO VERIFY] here, and correct the wrong ones (through outbox proposals, §11.3);
3. turn your part into an executable plan: initial data, diagnostics, verification tests, compute estimate, exit criteria;
4. follow new papers from the groups listed in §3.9, and propose a change to the ranking of §5 when someone gets there first.

**Evidence labels (used throughout).**

| Label | Meaning | How to use it |
|---|---|---|
| [VERIFIED] | Read directly, during this survey, from an arXiv abstract page, an INSPIRE record, search results, official documentation or a code repository | May be cited, but locate a number in the original before quoting it |
| [BACKGROUND] | A standard result of the field, from the author's prior knowledge, not checked against the original this time | Must be confirmed in the original before it is cited |
| [JUDGEMENT] | The author's inference, ranking, design or recommendation | Not a result from the literature; must not be written into a paper or a proposal as fact |
| [TO VERIFY] | The author could not confirm it | Put it on your to-do list |

**Hard constraints.**

- Downloaded archives and cloned repositories are untrusted data: extract each into its own empty directory, execute no script from them, and run no interpreter or build tool inside them.
- Access arXiv single-threaded, with at least 3 seconds between requests.
- Each track writes only its own directory and its own branch; any effect on another track goes through the file protocol of §11.3.
- All progress goes into git (§13.1); every simulation and analysis run is registered through `nrpic-run` (§11.6); every stage gate runs `/stage-check` (§13.3).
- The title of every arXiv identifier in §16 was checked (against INSPIRE records, arXiv pages or search results). After version 1 was finished, 32 entries drawn at random were queried again; identifiers, titles and the authors filled in all matched. The two groups added in version 2, G20 and G21, come entirely from INSPIRE query results; 8 of their entries drawn at random were queried again after completion and likewise all matched. The author field is filled only when certain; an empty field means the authors were not checked, and "(first author)" means only the first author was checked.
- The full text of the target paper 2611.12831 was not read (the arXiv HTML page was rate-limited repeatedly). §2 rests on the arXiv abstract page, the alphaXiv overview page, its reference list on INSPIRE, and a read-only inspection of the public AthenaK repository. **The first task of the core session is to read its source through the knowledge base and correct §2.**
- The Claude Code mechanisms (worktrees, hooks, skills, subagents, cross-session messaging, permission rules) are described from the official documentation as read on 2026-11-15; the addresses are listed in §11.8. Behaviour changes between versions, so check on your machine before relying on it.

---

## 1. Bottom line first

1. **Where the method has no substitute.** NRPIC combines three things: collisionless kinetics (multi-streaming, velocity dispersion, phase mixing), strong-field dynamical spacetime (horizons, gravitational waves), and three-dimensional AMR without symmetry. The cosmological problems that truly lie in this intersection are concentrated in the early universe (primordial black holes, the early matter-dominated era) and in the strong-field extremes of dark matter, not in the average expansion rate of late-time large-scale structure. [JUDGEMENT]
2. **First-choice problem S1: primordial-black-hole formation from collisionless matter in an early matter-dominated era (EMD).** A dust fluid fails at shell crossing, a scalar-field proxy carries wave pressure, and several analytic criteria disagree on the threshold and on the spin. The first full-NR particle calculation (arXiv:2609.14218) and a dedicated gauge study (arXiv:2610.23218) appeared only in September–October 2026; nobody has yet computed spin, mass function, gravitational waves or binary formation with full-GR particle methods. [JUDGEMENT; basis in §3.5 and §5]
3. **Second tier.** S2: gravitational waves from nonlinear EMD structure formation, obtained directly from the metric, non-perturbatively and without the quadrupole approximation; S3: the relativistic end state of the collapse of a self-interacting dark-matter core, which requires adding collisions to NRPIC; S4: the growth law of a black hole in an expanding collisionless medium and its "dark-matter dress".
4. **The late universe comes later.** Several independent lines of evidence show that backreaction has a very small effect on the average expansion (§3.3), while the light-speed CFL condition makes full-NR late-time structure formation two to three orders of magnitude more expensive than Newtonian simulations. Its value lies in a decisive multi-stream test of timescape and of "inhomogeneity mimicking evolving dark energy" (S6), which suits a long-term project. [JUDGEMENT]
5. **Three main lines of method innovation.** Cosmologization (boundaries, gauge, initial data); control of noise and constraints (constraint-compatible deposition, phase-space sheets, δf); collisions and multiple species (self-interaction, decay, massless particles, coupling to fluids). See §6.
6. **A starting route that barely changes the code.** Time-reversing the Oppenheimer–Snyder collapse already verified by Wu and Most gives an "expanding dust ball": the interior is exactly an Einstein–de Sitter universe and the exterior is Schwarzschild. Sub-horizon collapse in EMD can then be done in an asymptotically flat domain, before periodic boundaries and cosmological gauges are solved. See S1 in §5 and §9.4. [JUDGEMENT]
7. **Two highly novel exploratory directions.** Massless Vlasov particles as an effective description of high-frequency gravitational waves, giving a 3+1 numerical test of the Burnett conjecture (S7); primordial-black-hole formation with a free-streaming component (S5). I found no existing full-GR kinetic calculation for either; do a novelty search before starting. [JUDGEMENT + TO VERIFY]
8. **The execution plan already decided (by the group).** Six tracks advance at the same time, each in its own git worktree: A = S1, B = S2, C = S3, D = S4, E = stochastic inflation ("if possible", with a feasibility gate first), F = the Hills mechanism studied with NRPIC. Two supporting worktrees, core (shared implementation) and kb (knowledge base), complete the set; the main checkout is used only for orchestration and integration. See §9.
9. **Critical-path risk: the particle–spacetime coupling of NRPIC is not in the public code.** Public AthenaK was inspected on 2026-11-15: in `main` (commit c5a0d7f) and in the latest commits of nine particle-related branches, the particle module contains no reference to Z4c, to the stress–energy source or to deposition (§2.2) [VERIFIED]. None of the six tracks may therefore assume that the code can simply be taken and run. Two responses proceed in parallel: asking the authors for the code (a decision for the group, D2), and an independent rebuild from the paper by the core track. Every track has a preparatory work package that does not depend on the coupling module, so the parallelism is real from the first day (§9). [JUDGEMENT]
10. **Where the two new directions stand.** Stochastic inflation is a scalar-field problem, not an Einstein–Vlasov problem; it meets this project in three places: the shared NR backbone with cosmological gauge and initial data, the shared infrastructure for reproducible random numbers, and the non-Gaussian statistics of initial perturbations that it can supply to Track A (§3.10, S11). For the Hills mechanism, the strongly relativistic regime (a binary pulled apart at a few gravitational radii) has so far been treated only with approximations of the "geodesic plus Newtonian self-gravity" kind, and full-NR three-body work stops at early pure black-hole studies; what NRPIC can add is collisionless members with internal structure and black holes with dark-matter dresses (§3.11, S12). [JUDGEMENT]

---

## 2. Starting point: the NRPIC of Wu & Most (2026)

### 2.1 The paper

**Bibliographic data [VERIFIED].** Jiaxi Wu and Elias R. Most, *Numerical-Relativity Particle-in-Cell Simulations: Self-Gravitating Collisionless Matter in Dynamical Spacetimes*, arXiv:2611.12831, submitted 2026-11-09, 37 pages, 23 figures, categories gr-qc / astro-ph.GA / astro-ph.HE / physics.plasm-ph.

**Main points of the method [VERIFIED: abstract + alphaXiv overview].**

- Solves the three-dimensional Einstein–Vlasov system, implemented in the performance-portable AthenaK (arXiv:2409.16053, arXiv:2409.10383).
- The spacetime is evolved in the Z4c formulation with moving-puncture gauge.
- Macro-particles move on geodesics; the stress–energy is deposited conservatively on an adaptively refined mesh. The overview page explains "conservative" as follows: the integrated source is conserved algebraically, up to floating-point summation error.
- At refinement boundaries the particle shape function is evaluated on the finest nearby level, and the contributions of the virtual fine cells are then accumulated into the coarse cells.
- Techniques of relativistic plasma PIC are carried over through the electrodynamics-like formulation of gravity. The geodesic force is written in Lorentz-force form, from which a Boris-type pusher (DGREM–Boris) is built. The tests in the paper actually use an implicit-midpoint pusher; in the fixed-Kerr test both are second order, and the accuracy in practice is limited by the spacetime interpolation.
- The electrodynamic analogy comes from arXiv:2111.05282 (the first-order dGREM formulation) and arXiv:2504.15978.

**Tests and numbers [VERIFIED: alphaXiv overview].**

| Test | Result |
|---|---|
| Oppenheimer–Snyder dust collapse | Relative error of about 10⁻³ between the final horizon mass and the initial ADM mass. At fixed mesh the error falls as the particle number grows; at fixed particle number the error does not fall monotonically as the mesh is refined |
| Prolate collapse | Followed beyond the collisionless caustic phase; a common apparent horizon is found; the peak curvature depends on resolution at every resolution tested |
| Relativistic clusters | Stability and nonlinear migration |
| Two overdense clumps in a common envelope | Total mass M=1, envelope 0.76M, each clump 0.12M; 5 million particles. Each clump forms an apparent horizon at t≈8.5M; the common horizon appears at t≈64.16M with mass 0.383M; the orbital angular momentum falls by 27.3% between 20M and 60M; the remnant horizon mass is 0.647M at t=100M; the waveform shows a late ringdown and no inspiral signal |

**Limitations acknowledged by the authors or pointed out by the overview page [VERIFIED: alphaXiv overview].** There is no direct benchmark against established methods and no item-by-item ablation; the two-clump test is an idealized demonstration (no shear inside the clumps, zero net angular momentum of the envelope), and the cause of the rapid orbital decay is not uniquely identified.

**The three readings that matter most for this project [JUDGEMENT].**

1. "Convergent in particle number but not monotonic in mesh spacing" shows that the tests sit in the noise-dominated regime. In cosmological applications the initial perturbations are small, so the noise problem can only be worse; M2 and M3 of §6 are therefore mandatory.
2. All existing tests are in asymptotically flat domains. The words cosmology, periodic boundary, expanding background and collision do not occur in the abstract or the overview; its reference list does cite the cosmological Einstein–Vlasov work of East et al. (arXiv:1908.05683) and a review of dark-matter simulations (arXiv:2112.05165). Cosmologization is an open slot for now. Whether the full text discusses it is [TO VERIFY].
3. The two-clump demonstration (two overdensities each forming a black hole, inspiralling and merging inside a common envelope, the remnant continuing to accrete) is physically the asymptotically flat version of "neighbouring density peaks forming a primordial black-hole binary". Moving it into an expanding background is the shortest path; placing a heavier black hole beside it gives the collisionless version of the Hills mechanism (S12).

### 2.2 State of the public code (read-only inspection, 2026-11-15) [VERIFIED]

The object inspected is `IAS-Astrophysics/athenak` on GitHub (BSD 3-Clause licence). It was cloned shallowly and only listed and searched; nothing was compiled or run.

| Item checked | Result |
|---|---|
| Latest commit on `main` | c5a0d7f, 2026-09-11, commit message "Cyclic zoom (#713)" |
| Modules under `src/` | bvals, coordinates, cyclic_zoom, diffusion, driver, dyn_grmhd, eos, geodesic-grid, gravity, hydro, ion-neutral, mesh, mhd, multigrid, outputs, particles, pgen, radiation, reconstruct, shearing_box, srcterms, tasklist, units, utils, z4c |
| `src/particles/` (main) | Four files; the pusher enumeration is drift, leap_frog, lagrangian_tracer, lagrangian_mc; the only particle type is cosmic_ray |
| Coupling of the particle module to the spacetime | No file under `src/particles/` mentions z4c, tmunu, adm or deposit |
| `src/z4c/` | Has `tmunu` (the matter-source interface, used by dyn_grmhd), compact_object_tracker, horizon_dump, wave extraction, CCE, `z4c_Sbc` (by its name, a Sommerfeld-type outer boundary); the gauge options include several lapse and shift parameters |
| Z4c problem generators and inputs | One puncture, two punctures, boosted puncture, linear wave, the `awa` directory (by its name, the Apples-with-Apples standard tests), `spectre_bbh` (by its name, import of SpECTRE binary-black-hole data) |
| Periodic boundaries | `BoundaryFlag` includes periodic |
| Scalar fields, cosmology | No related keyword found under `src/` |
| Particle-related branches (124 remote branches in total; 11 selected by name, 9 of them inspected) | particles_gr (latest commit 2025-05-20; adds four pushers, boris, only_gr, full_gr and gca_gr, which by their names and file names are relativistic pushers in a given spacetime), feature/particles-infrastructure (2026-09-06; a refactoring of the particle infrastructure with creation, time step and restart), particles_montecarlo, feature/lagrangian_mc, fix/update-prtcl, tracer_particle, collapse, project/tidal-interactions, id_solve. In the latest commits of these nine branches the particle module likewise contains no reference to z4c, tmunu, adm or deposit |

**Conclusion.** The part of the code described in the paper as "particles deposit stress–energy that acts back on Z4c" is not public within the scope of this inspection. The inspection did not cover the content of the remaining branches (including id_solve_porting and project/collapse_relaxation, selected by name but not read), nor other repositories the authors may use; `kb watch upstream` (§12) must repeat the check every week. The branch names project/tidal-interactions, collapse and id_solve indicate upstream work on tidal interactions, collapse and initial-data solving; their content was not read.

**[TO VERIFY] list.** Order of the deposition shape function and whether it is filtered; Z4c constraint-damping parameters; how the particle initial data satisfy the constraints; GPU performance numbers; the paper's code-availability statement; whether NRPIC keeps AthenaK's single time step across levels; the follow-up directions listed in the authors' conclusions.

---

## 3. Landscape: numerical relativity × cosmology

### 3.1 The ladder of methods

| Level | Gravity | Matter | Representative work | Main limitation |
|---|---|---|---|---|
| Newtonian N-body + relativistic interpretation | Poisson | particles | N-body gauge: arXiv:1505.04756, arXiv:1606.05588; correspondence: arXiv:1101.3555, arXiv:1111.2997; light-cone post-processing: arXiv:1703.03407, arXiv:2111.08745 | Relativistic corrections only at linear order or in post-processing; no strong field |
| Weak-field expansion | Metric perturbations in Poisson gauge, elliptic/parabolic solves | particles, relativistic species allowed | gevolution: arXiv:1308.6524, arXiv:1604.06065, arXiv:1509.01699; GPU version arXiv:2607.17929; GrGadget arXiv:2301.11854; splicing with Newtonian simulations arXiv:2404.02783 | Requires small potentials; no horizons |
| Post-Friedmann | 1/c expansion | particles (post-processing) | arXiv:1306.1562, arXiv:1502.02985 | As above |
| Constrained formulation | Elliptic system | particles + AMR | GRAMSES: arXiv:1905.08890, arXiv:2001.07968 | Does not evolve the radiative degrees of freedom [BACKGROUND; defer to the original] |
| Full NR + dust fluid | Hyperbolic formulations such as BSSN or generalized harmonic | fluid | arXiv:1511.01105, arXiv:1511.01106, arXiv:1511.05124, arXiv:1611.05447, arXiv:1807.01711, arXiv:1711.06681; code comparison arXiv:2003.08014 | The fluid description fails once multi-stream regions appear |
| Full NR + particles (Einstein–Vlasov) | Hyperbolic formulation | particles | arXiv:1908.05683, arXiv:1810.05203, arXiv:1611.03437, arXiv:1904.07841; SPH particles arXiv:2307.15194; black-hole formation in a matter-dominated era arXiv:2609.14218; NRPIC arXiv:2611.12831 | Expensive; particle noise; gauge |
| Full NR + scalar field | Hyperbolic formulation | scalar field | GRChombo family: arXiv:1503.03436, arXiv:2201.03458 | A different matter model; cannot stand in for collisionless particles |

The characterizations of the technical route of each code in this table are [BACKGROUND]; defer to the originals before citing. The entry review for the whole field is arXiv:2409.01939 (Living Reviews in Relativity); for a review leaning towards the early universe see arXiv:2201.03752.

### 3.2 Numerical work on collisionless matter in full GR (non-cosmological)

- **Spherical symmetry.** PIC studies of critical collapse and of the stability of steady states: arXiv:gr-qc/9804040, arXiv:gr-qc/0107076, arXiv:gr-qc/0601112, arXiv:1409.5176. The convergence of spherically symmetric PIC has a rigorous proof (arXiv:math/0209336); that paper also points out that the source terms of Einstein–Vlasov enter the field equations pointwise, instead of first being smoothed by an elliptic operator as in Vlasov–Poisson, which adds difficulty for both analysis and numerics [VERIFIED].
- **Critical behaviour.** The critical solutions of collisionless matter are static, which shows up as a finite mass threshold (Type I), and there is no universal critical solution [BACKGROUND; "no universal critical solution" is in arXiv:gr-qc/0601112, VERIFIED]. This differs in kind from the Type II scaling of a radiation fluid (arXiv:gr-qc/9402041, review arXiv:0711.4620) and has direct consequences for the mass spectrum of EMD primordial black holes (S1 in §5).
- **Axisymmetry.** PIC in (2+1)+1 form: arXiv:2010.15771; hoop conjecture and weak cosmic censorship: arXiv:2305.04360.
- **Three dimensions.** Early work arXiv:gr-qc/9905058; spindle collapse arXiv:1611.07906; cosmic censorship holds in oblate and prolate collapse arXiv:1901.04498; source of the method arXiv:1807.11562.
- **Charged collisionless matter and extremal black holes.** Rigorous result: threshold solutions can be extremal Reissner–Nordström black holes (arXiv:2402.10190); numerical study arXiv:2511.20567 [VERIFIED]. The abstract of Wu and Most lists the formation of extremal black holes among its motivations.
- **Clusters of discrete black holes.** Full-GR evolution of 25 equal-mass black holes (arXiv:2505.01495) [VERIFIED], a reference point for the limit "the particles are black holes".
- **Related particle methods.** Lagrangian SPH coupled to NR: arXiv:2203.06478, arXiv:2306.06226. GRPIC on fixed backgrounds: arXiv:1810.03613, arXiv:1908.06919, arXiv:2511.17701, arXiv:2503.04558.

### 3.3 Late universe: structure formation, backreaction, light-cone observables

**What full-NR fluid simulations found.** In 2016 three groups independently produced the first full-NR cosmological simulations without symmetry (arXiv:1511.01105, arXiv:1511.05124, arXiv:1611.05447). Simulations evolved from CMB initial conditions to today give a global backreaction energy density of about 10⁻⁸ of the matter energy density (arXiv:1807.01711) [VERIFIED]. Averaged on hypersurfaces of a Newtonian-like gauge, backreaction is negligible on small scales as well; yet in sub-volumes of radius about 200 Mpc the curvature parameter can fluctuate by about 10%, and fluid flowing in and out changes the density by up to about 5% between z=1 and 0 (arXiv:2408.03049) [VERIFIED].

**From fluid to particles.** The fluid description fails once multi-stream regions appear, and multi-stream regions are a generic feature of structure formation (introduction of arXiv:1908.05683) [VERIFIED]. East et al. compared full Einstein–Vlasov solutions with Newtonian N-body particle by particle; the Living Review summarizes this body of work as follows: as long as the Newtonian potential stays in the weak-field range, the two differ at the sub-percent level (arXiv:2409.01939) [VERIFIED]. Giblin et al. ran N-body + BSSN in harmonic and Newtonian gauges and reported very poor N-body convergence in comoving synchronous gauge (arXiv:1810.05203) [VERIFIED]. Other particle-type implementations: arXiv:1611.03437, arXiv:1904.07841, arXiv:2307.15194.

**Light-cone observables.** A general-relativistic ray-tracing framework for NR spacetimes is given in arXiv:2209.06775. Three results from 2026 [all VERIFIED]:

- Weak-lensing convergence on large angular scales: 20 synthetic observers, ℓ<100, 0.05<z<3; the prediction of linear perturbation theory deviates from the nonlinear convergence by about 3%–30% on average, and most of the differences lie below cosmic variance (arXiv:2603.24838).
- Whether inhomogeneity can mimic evolving dark energy: 1 of 20 observers infers dark-energy parameters close to DESI's within 2σ (arXiv:2606.05479).
- Growth rate from magnitude fluctuations: at z≲0.2 the difference between the full-NR and the FLRW treatment is smaller than the statistical error of current data (arXiv:2606.18437).

Others: anisotropy of the Hubble flow and the local H₀ (arXiv:1807.01714, arXiv:2103.11918, arXiv:2111.14423, arXiv:2402.09659, arXiv:2507.01095); measurement of spatial curvature (arXiv:2010.07274); redshift drift (arXiv:2404.06242); void statistics (arXiv:2403.15134).

**What the weak-field route already covers.** gevolution solves all six metric degrees of freedom in Poisson gauge and pushes particles with canonical momenta, which holds for relativistic particles too (arXiv:1604.06065) [VERIFIED]. It now has a GPU version (arXiv:2607.17929) [VERIFIED] and keeps producing light-cone observables: rotation and B modes of weak lensing (arXiv:2603.24179), number counts (arXiv:2106.01347), redshift drift (arXiv:2505.04731). For most relativistic effects in the late universe this route is both fast and sufficient. Any increment from NRPIC in the late universe can only come from places where the weak-field expansion fails or where independent verification is needed. [JUDGEMENT]

**The theoretical dispute.** The Green–Wald framework argues that the effective stress–energy of small-scale inhomogeneity is traceless, like radiation and unlike dark energy (arXiv:1011.4920, arXiv:1407.8084) [BACKGROUND]; Buchert et al. dispute its range of validity (arXiv:1505.07800). The backreaction term defined by spatial averaging depends on the choice of foliation, that is, of gauge (arXiv:2310.19451, arXiv:2409.00024) [VERIFIED]. Reviews: arXiv:1112.5335, arXiv:1109.2314, arXiv:1612.08222, arXiv:2509.01320.

**timescape and DESI.** timescape is one concrete realization of the Buchert averaging scheme (arXiv:gr-qc/0702082, arXiv:0909.0749). The Pantheon+ analysis reports a Bayesian preference for timescape: ln B>5 for the full sample, and still ln B>1 when restricted to z>0.075 (arXiv:2412.15143, arXiv:2311.01438) [VERIFIED]. When the DES supernova team combined supernovae with BAO angular scales, the two data sets were mutually inconsistent under timescape, and the AIC judged it worse than flat ΛCDM (arXiv:2406.05048) [VERIFIED]. The hint of evolving dark energy in DESI DR2 (arXiv:2503.14738) revived the "inhomogeneity explanation": besides arXiv:2606.05479 there is an estimate with three toy models, concluding that the magnitude is similar but probably insufficient to explain the whole deviation (arXiv:2601.20633) [VERIFIED].

**Local voids and large-scale anomalies.** A local void as an explanation of the H₀ tension: arXiv:1304.2884, arXiv:2009.11292, arXiv:2602.03928; a test with DESI DR2 BAO of the redshift offset required by local-void models gives a result compatible with zero (arXiv:2606.02712) [VERIFIED]. Tests of the cosmological principle and anomalies: arXiv:2207.05765, arXiv:2009.14826, arXiv:2206.05624, arXiv:2302.02028, arXiv:2510.05340.

### 3.4 Early universe (problems dominated by scalar fields)

This area is not a kinetic problem, but it is the main arena of the NR-cosmology community, and most of the experience with initial data, gauges and AMR comes from here.

- **Initial conditions for inflation.** arXiv:1511.05143, arXiv:1608.04408, arXiv:1712.07352, arXiv:1910.12547, arXiv:2011.12190, arXiv:2212.04479, arXiv:2405.03490, arXiv:2304.12150. Latest result: for the α-attractor T-model with order-one gradient and kinetic inhomogeneities, obtaining 60 e-folds requires a characteristic scale of about 0.02 m_P, corresponding to a tensor-to-scalar ratio of about 10⁻⁶ (arXiv:2512.13673) [VERIFIED].
- **NR implementation of stochastic inflation.** arXiv:2401.08530, arXiv:2512.14649, arXiv:2610.32592. Discussed at length in §3.10.
- **Slow contraction and bounces.** arXiv:0808.0542, arXiv:2006.01172, arXiv:2006.04999, arXiv:2103.00584, arXiv:2104.12293, arXiv:2404.00867, arXiv:1308.3044, arXiv:2206.08466.
- **Preheating and oscillons.** arXiv:1907.10601, arXiv:1912.09658, arXiv:2112.07626, arXiv:2311.01504, arXiv:2304.01673, arXiv:2504.08939.
- **Bubble collisions, cosmic strings.** arXiv:1112.4487, arXiv:1312.1357, arXiv:1808.06678, arXiv:2002.05177.

### 3.5 Primordial-black-hole formation

**Radiation era.** In spherical symmetry the threshold, the critical scaling and the dependence on the profile have been studied in detail (arXiv:gr-qc/9905064, arXiv:astro-ph/9709072, arXiv:1201.2379, arXiv:1309.4201, arXiv:1809.02127, arXiv:1907.13311; reviews arXiv:2111.12693, arXiv:2211.05767). Recent 3+1 progress [all VERIFIED]:

- Non-spherical and ellipsoidal collapse: arXiv:2004.01042, arXiv:2403.11147, arXiv:2410.03452, arXiv:2410.03451.
- Long 3+1 evolutions: GRChombo + relativistic fluid; the Gamma-driver is rescaled to cosmological scales so that the time step grows with the scale factor, reducing the number of coarse-level steps by a factor of about 94; the late-time mass growth follows the Zel'dovich–Novikov accretion law (arXiv:2608.13206).
- Multiple peaks: neighbouring curvature peaks end in one of three ways, dispersal, merger into one black hole, or formation of two black holes; the authors propose a non-spherical quasi-local compaction criterion based on the Hawking mass (arXiv:2609.03051).
- Initial data: solutions of the Hamiltonian constraint for strong cosmological overdensities may not exist or may not be unique; there are a strong-field and a weak-field branch, and which branch an iterative solver lands on depends on the initial guess (arXiv:2509.26470); a parabolic–hyperbolic constraint solve that does not rely on periodic boundaries (arXiv:2607.21308).

**Matter-dominated era: the analytic picture.** Without pressure the Jeans length vanishes, perturbations keep growing after horizon entry, and whether a black hole forms is decided by non-sphericity, angular momentum, inhomogeneity and velocity dispersion [BACKGROUND].

- Non-sphericity and the hoop criterion: arXiv:1609.01588. Spin: arXiv:1707.03595 predicts large, near-extremal spins [BACKGROUND]. Inhomogeneity: arXiv:1810.03490. Velocity dispersion: arXiv:2211.13950.
- Two reassessments from 2025 [VERIFIED]: once the statistics of peak profiles are included, the effective threshold rises from the ζ_rms^(2/5) scaling of the idealized top-hat to about ζ_rms^(1/10), and the spin scales as ζ_rms^(7/4), far below 1 (arXiv:2507.18312); peak theory + Zel'dovich approximation + hoop criterion give an abundance that varies roughly as the fifth power of the variance at horizon entry, and for a monochromatic spectrum the abundance is about 19 times the earlier prediction (arXiv:2508.10070).
- The analytic works disagree on the spin (near-extremal versus very small); estimates of threshold and abundance vary strongly with the physics included (peak statistics, velocity dispersion, non-sphericity).

**Matter-dominated era: full NR.**

- A scalar field as the matter (arXiv:2109.04896) [VERIFIED]: there are two mechanisms, direct collapse and accretion-driven collapse, and the latter does not require the initial perturbation to satisfy the hoop condition; formation takes about one Hubble time. Spin (arXiv:2306.11810) [VERIFIED]: after formation, accretion of non-rotating background matter lowers the dimensionless spin, and the final spin is negligible when the matter-dominated era lasts more than a few e-folds.
- **Particles versus dust fluid (arXiv:2609.14218) [VERIFIED].** Triaxial initial curvature perturbations. The dust fluid breaks down where the density diverges, unless the singularity is hidden deep inside an apparent horizon; to see a horizon before the breakdown the initial amplitude must be about twice the earlier analytic estimate. The particle system does not break down and can be followed after black-hole formation; its formation threshold is about an order of magnitude below the earlier analytic estimate.
- **Gauge (arXiv:2610.23218) [VERIFIED].** Three-dimensional dust collapse often fails before a black hole forms. The standard lapse slicing conditions need modification in the cosmological setting; the Gamma-driver shift condition fails under shell focusing, and the best shift damping depends on the resolution of the focusing region. With the improvements the runs get further, but the gauge still needs work.

### 3.6 Structure formation and gravitational waves in the early matter-dominated era

- **Physical background.** Review arXiv:2006.16182. In EMD small-scale perturbations go nonlinear early and form microhalos: arXiv:1106.0536, arXiv:1311.4034, arXiv:1405.7373, arXiv:2107.10293. "Inflaton halos" during the oscillating phase of the inflaton condensate: arXiv:2011.13333, arXiv:1911.01661, arXiv:2110.15109, arXiv:1909.11678.
- **N-body simulations (all Newtonian or semi-relativistic) [VERIFIED].** EMD structure formation and its evaporation at reheating (gravitational heating): arXiv:2306.14961. Gravitational waves from inflaton-halo formation and tidal interactions: arXiv:2212.00425. Hybrid N-body + lattice simulations including decay of the metastable matter into radiation, finding that nonlinearity enhances the gravitational waves significantly: arXiv:2312.12499. Gravitational waves from pancake collapse and the violent-relaxation phase: arXiv:2403.15126. Semi-relativistic N-body, a homogeneous ball with Zel'dovich deformation in an EdS background, with gravitational waves computed from the numerical quadrupole; it finds that fitting formulae and the Zel'dovich estimate miss the evolution after shell crossing and misestimate the radiated power, and that the main contribution comes from peaks of height ν≈3: arXiv:2605.04487.
- **Perturbative calculations and their limits.** Review of scalar-induced gravitational waves arXiv:2109.01398; effect of the speed of the transition from EMD to radiation domination on the signal: arXiv:1904.12878, arXiv:1904.12879, arXiv:2311.12340, arXiv:2410.17291. The gauge-dependence problem is sharpest in a matter-dominated era: arXiv:1704.03500, arXiv:1911.09689, arXiv:1912.00785, arXiv:2012.14016, arXiv:2009.11081. Third-order induced gravitational waves in a matter-dominated era show secular growth (arXiv:2610.08045) [title only verified].
- **Black-hole-dominated early matter era.** N-body with primordial black holes as particles: arXiv:1907.08129; gravitational waves from a gas of black holes: arXiv:2010.11573, arXiv:2012.08151, arXiv:2003.10455. Accretion growth of primordial black holes in EMD (by about two orders of magnitude at most) and the resulting doubly peaked gravitational-wave spectrum, in linear perturbation theory: arXiv:2505.21885 [VERIFIED].

### 3.7 Singularities, stability and mathematical results on Einstein–Vlasov

- **Introductions and reviews.** arXiv:gr-qc/9604001, arXiv:1106.1367, arXiv:2106.09235, arXiv:1309.2036. Variational principle: arXiv:1910.12152.
- **Stability theorems.** Minkowski: arXiv:1707.06141, arXiv:1707.06079, arXiv:1602.02611, arXiv:2210.00512. Cosmological backgrounds: nonlinear stability of the Milne model under Einstein–Vlasov (arXiv:1709.00267); cosmic no-hair under T³-Gowdy symmetry (arXiv:1306.6223). For the stabilization of fluids on non-accelerating expanding backgrounds see arXiv:2002.02119.
- **Phenomena specific to kinetics.** Nonlinear phase mixing near Schwarzschild, valid up to the time-scale set by the nonlinear echo mechanism (arXiv:2609.13394) [VERIFIED]. Rigorous proof of the quadrupole formula (arXiv:2309.00431). Formation of trapped surfaces (arXiv:2510.12429).
- **Near singularities.** The past asymptotics of Bianchi I Einstein–Vlasov differ from those of a perfect fluid (arXiv:gr-qc/0512031) [BACKGROUND]. Numerical studies of generic singularities (BKL, spikes): arXiv:gr-qc/9805063, arXiv:gr-qc/0312117, arXiv:0904.1546, arXiv:2010.01399; review arXiv:gr-qc/0201056.
- **Burnett conjecture.** Weak limits of high-frequency vacuum spacetimes satisfy the Einstein equations with massless Vlasov matter [BACKGROUND]; proofs under U(1) symmetry: arXiv:1706.09501, arXiv:1907.10743. The converse holds as well: under U(1) symmetry, small and localized Einstein–massless-Vlasov solutions can be approximated by high-frequency vacuum spacetimes (arXiv:2506.21779) [VERIFIED]. This is the mathematical basis for "representing high-frequency gravitational waves by massless particles" (S7 in §5).

### 3.8 Dark matter and strong gravity

- **Gravothermal collapse of self-interacting dark matter (SIDM).** The classic picture: arXiv:astro-ph/0110561, arXiv:astro-ph/0111176. As seeds of supermassive black holes: arXiv:1501.00017, arXiv:1812.05088, arXiv:2010.15132. Relativistic instability criterion: arXiv:2108.11967. Connection with the JWST "little red dots" (arXiv:2506.17641) [VERIFIED]: triggering the general-relativistic instability requires a central one-dimensional velocity dispersion of about 0.3c; along the gravothermal evolution only about 10⁻¹⁰–10⁻⁸ of the halo mass can reach this condition, a halo of 10⁹ solar masses corresponds to an initial seed of about 1 solar mass, which then grows by accretion. The seed picture for dissipative SIDM: arXiv:2504.00075. **Latest progress (arXiv:2601.17117) [VERIFIED]:** the Misner–Sharp formalism is brought into SIDM, the assumption of hydrostatic equilibrium is dropped and general-relativistic effects are added; the outward heat flux is found to drive a rapid expansion of the outer envelope that carries mass away from the core and slows the collapse markedly. This is a spherically symmetric, fluid-type treatment; a three-dimensional full-GR kinetic calculation does not exist yet.
- **Dark matter around black holes.** Spikes: arXiv:astro-ph/9906391, arXiv:1305.2619, arXiv:2411.12007. Effect on binary-black-hole waveforms: arXiv:2002.12811, arXiv:2211.01362, arXiv:2402.13762; a fully relativistic treatment of EMRI environments: arXiv:2505.09715. Full NR with wave-dark-matter environments: arXiv:2210.09254, arXiv:2311.18156, arXiv:2409.01937. Full NR with a particle-dark-matter environment was not found [TO VERIFY].
- **Dark-matter dress of primordial black holes.** arXiv:1607.00612, arXiv:1901.08528, arXiv:2106.07480, arXiv:1712.06383, arXiv:2002.10771; effect on the merger rate: arXiv:1805.09034.
- **"Cosmologically coupled" black holes.** Observational claim: arXiv:2302.07878; theoretical discussion: arXiv:2306.11588.

### 3.9 Developments in 2025–2026 and active groups

| Direction | Recent representative work | Relation to this project |
|---|---|---|
| Black-hole formation in a matter-dominated era, full-NR particles | Yoo, Escrivà, Harada, Kohri: arXiv:2609.14218; semi-relativistic gravitational waves by the same authors arXiv:2605.04487 | Direct competition |
| Cosmological gauges for dust collapse | Munoz, Byrnes, Bruni, Hawke: arXiv:2610.23218 | The gauge scheme can be borrowed directly |
| 3+1 black-hole formation in the radiation era | arXiv:2608.13206, arXiv:2609.03051 | Cosmological Gamma-driver, multi-peak diagnostics |
| Late universe with NR + ray tracing | Macpherson et al.: arXiv:2603.24838, arXiv:2606.05479, arXiv:2606.18437 | Benchmark and potential collaborators for S6 |
| Weak-field relativistic N-body | Adamek et al.: arXiv:2607.17929, arXiv:2603.24179, arXiv:2508.20606 | Comparison code in the weak-field regime |
| Cosmological initial data | arXiv:2501.13046, arXiv:2509.26470, arXiv:2607.21308 | Foundation of M1 |
| NR of initial conditions for inflation | arXiv:2512.13673, arXiv:2607.06441 | Community focus; experience with initial data and gauges |
| NR implementation of stochastic inflation | Launay, Rigopoulos, Shellard: arXiv:2401.08530, arXiv:2512.14649, arXiv:2610.32592 | Starting point and direct comparison for Track E |
| Lattice inflation and super-horizon freezing | arXiv:2606.14853, arXiv:2604.00978, arXiv:2506.11795 | Source of the acceptance criteria for Track E |
| Relativistic Hills mechanism | arXiv:2404.16270, arXiv:2402.02178, arXiv:2610.13294 | Baselines and comparison for Track F |
| Full-GR black-hole clusters and extremal black holes | arXiv:2505.01495, arXiv:2511.20567 | Reference for S9 and §8 |
| The NRPIC authors' group | arXiv:2611.12831, arXiv:2504.15978, arXiv:2509.19769 | Source of the method; watch its follow-up directions |
| Relativistic SIDM collapse | arXiv:2601.17117, arXiv:2506.17641 | Frontier of S3 |

### 3.10 Stochastic inflation and lattice inflation (background for Track E)

- **What it is [BACKGROUND].** Stochastic inflation treats the long-wavelength modes outside the horizon as a classical random field that receives a random kick whenever short-wavelength quantum fluctuations cross the horizon, so that the long-wavelength field obeys a Langevin equation (arXiv:astro-ph/9407016). Reviews: arXiv:2203.13852, arXiv:2009.08715. δN and the separate-universe approach: arXiv:astro-ph/0003278, arXiv:astro-ph/0306620, arXiv:astro-ph/0504508, arXiv:1308.4754, arXiv:2110.11720, arXiv:2408.09964, arXiv:2408.13673. Early comparisons and correlation functions: arXiv:gr-qc/9911029, arXiv:0808.1786, arXiv:1003.1327, arXiv:1506.04732, arXiv:1409.7399.
- **Why it matters for primordial black holes [BACKGROUND; titles VERIFIED].** Quantum diffusion gives the probability distribution of the curvature perturbation a non-Gaussian tail, and the abundance of primordial black holes is extremely sensitive to the tail: arXiv:1707.00537, arXiv:1912.05399, arXiv:2012.06551, arXiv:2111.07437, arXiv:2101.05741, arXiv:2402.12672. Clustering: arXiv:2402.08642. Work that gives the statistics of the compaction function directly: arXiv:2312.12911, arXiv:2510.09303. Sampling with trees: arXiv:2501.05371. Ultra-slow-roll (USR) background: arXiv:astro-ph/0101406, arXiv:1911.00057, arXiv:1910.08487, arXiv:2507.04114, arXiv:2504.05937.
- **Numerical implementations outside NR [titles VERIFIED].** Direct solution of the Langevin equation and importance sampling: arXiv:2206.11234, arXiv:2410.13683; frozen noise: arXiv:2210.17441; Itô versus Stratonovich: arXiv:2411.12465; spectral method: arXiv:2606.09690; the stochastic lattice code STOLAS: arXiv:2405.10692; conventional lattice inflation: arXiv:2102.06378, arXiv:2403.12811; lattice simulations of USR: arXiv:2410.23942, arXiv:2506.11795; scalar-induced gravitational waves on the lattice: arXiv:2604.03628; codes: arXiv:2102.01031 (CosmoLattice), arXiv:hep-ph/0011159 (LATTICEEASY), arXiv:1609.00381 (PyTransport), arXiv:2302.00655.
- **NR implementation [VERIFIED: abstracts].** Launay, Rigopoulos and Shellard give gauge-invariant Langevin source terms for the full ADM equations: metric and field are coarse-grained, the sources depend on the time derivative of the window function and on the Mukhanov–Sasaki mode functions, and the sources in BSSN form are derived (arXiv:2401.08530). The subsequent BSSN implementation ran slow-roll and USR tests and reports that the constraints are satisfied (arXiv:2512.14649). Launay's thesis gives a validity criterion based on the Keldysh formalism, analytic solutions of the constraints for inhomogeneous initial conditions, and a first look at eternal inflation (arXiv:2610.32592). Related: Bunch–Davies initial conditions that satisfy the constraints at leading order, with geodesic gauges (arXiv:2502.06783); tensor perturbations in NR codes (arXiv:2412.19731); a quantitative criterion for the quantum-to-classical transition (arXiv:2412.16143); an extension to scalar–tensor theories (arXiv:2606.07467).
- **Three warnings [VERIFIED: abstracts].** (i) Lattice codes on an FLRW background do not freeze super-horizon modes, and the problem is worse in USR; the authors give a validity check within CosmoLattice (arXiv:2606.14853). (ii) The nonlinear lattice scheme with shear-free, locally FLRW geometry is limited when the inflaton velocity is very small (arXiv:2604.00978). (iii) A study of starting inflation in asymptotically flat spacetimes points out that the box length of a periodic domain may introduce a bias (arXiv:2607.06441).
- **Foundational questions still debated [titles only verified].** The role of the stochastic formalism in nonlinear perturbations is being reassessed (arXiv:2611.15050); non-Gaussian tails can be obtained without stochastic inflation (arXiv:2406.02417); the noise deviates from Gaussian white noise (arXiv:2512.17070); stochastic inflation beyond slow roll (arXiv:1905.06300, arXiv:2107.12735, arXiv:2410.17987); validity of the separate-universe approach at sudden transitions (arXiv:2311.03281); gradient interactions (arXiv:2509.05124); the view from perturbation theory (arXiv:2311.17644); loop corrections in USR (arXiv:2305.03491); the challenge that eternal inflation near inflection points poses to primordial-black-hole models (arXiv:2507.15522). More peripheral theoretical developments: arXiv:2404.15416, arXiv:2605.11096, arXiv:2504.17680, arXiv:2605.31323, arXiv:2511.21388, arXiv:2604.15219, arXiv:2506.21423, arXiv:2506.03860.
- **Relation to this project [JUDGEMENT].** Stochastic inflation needs no particles, but it has four interfaces: (a) it shares the periodic domain, the cosmological gauge and the constrained initial data with Track B; (b) spatially correlated random sources need reproducible parallel random numbers, the same infrastructure as the Monte Carlo collisions of Track C (M11); (c) the statistics of large perturbations it produces can serve as the distribution of initial conditions for Track A; (d) after inflation the oscillating inflaton condensate behaves like pressureless matter on large scales (the inflaton-halo literature of §3.6), and a "field-to-particle" hand-over is the way to connect inflation to an Einstein–Vlasov calculation of EMD. Public AthenaK has no scalar field (§2.2), so Track E either adds a scalar field to AthenaK or builds on GRChombo/GRTeclyn (decision D4).

### 3.11 Hills mechanism, tidal separation and strong-field three-body dynamics (background for Track F)

- **The classic picture [BACKGROUND].** Hills (1988, no arXiv version): a binary of mass m_b and separation a_b that passes a black hole of mass M on a near-parabolic orbit is pulled apart inside the tidal radius r_t ≈ a_b (M/m_b)^(1/3); one member is ejected with speed v_ej ~ v_b (M/m_b)^(1/6) and the other is captured on a bound orbit of high eccentricity, where v_b is the orbital speed of the binary. Hypervelocity stars and S-stars at the Galactic centre: arXiv:astro-ph/0309084, arXiv:astro-ph/0501177, arXiv:astro-ph/0608159, arXiv:1105.1432, arXiv:1210.1901, arXiv:2002.10547.
- **Restricted three-body problem and parameter scans [titles VERIFIED].** arXiv:0911.1136, arXiv:1201.4794, arXiv:1307.1134, arXiv:1804.02911. Full three-body, stellar collisions and double tidal disruptions: arXiv:0909.1959, arXiv:astro-ph/0609440, arXiv:2409.09597, arXiv:1504.02787, arXiv:1703.05796. Repeating partial tidal disruptions: arXiv:2203.08162.
- **Gravitational-wave source channels [titles VERIFIED].** The captured member becomes an EMRI: arXiv:astro-ph/0507133, arXiv:2610.13294. Compact binaries and massive black holes: arXiv:1501.07856, arXiv:1801.05780, arXiv:1805.09593, arXiv:1903.02685, arXiv:1203.2938, arXiv:1706.09896. Tests of general relativity with "binary EMRIs": arXiv:1801.07060. Waveform effects for binaries near a massive black hole: arXiv:1703.10543, arXiv:2105.02230, arXiv:1604.02148, arXiv:2310.00042, arXiv:0704.2612.
- **How far the relativistic treatment has gone [VERIFIED: abstracts or search snippets].** (i) The exact relativistic acceleration of a Schwarzschild black hole combined with Newtonian self-gravity of the binary, compared with Newtonian and 1PN results; the paper estimates that relativistic effects start to matter when the pericentre distance is below about 100 gravitational radii (arXiv:2404.16270). (ii) Dynamics and waveform of a binary black hole flying close to a Kerr black hole on a parabolic orbit; the paper says the dynamical range of such systems is too large for a direct full-NR solution and stresses the need for new numerical tools (arXiv:2402.02178). (iii) Perturbative treatment: arXiv:1203.6185. (iv) Members with internal structure: SPH simulations of white-dwarf binaries tidally disrupted by intermediate-mass black holes, including spin (arXiv:2508.03463, arXiv:2601.04870); relativistic kicks and spin effects in the tidal disruption of single stars (arXiv:1502.02039, arXiv:1305.4634, arXiv:1411.5022, arXiv:1701.00303, arXiv:1903.09147, arXiv:1207.6401).
- **Related full-NR work.** Evolutions of three or more black holes: arXiv:0710.0879, arXiv:0711.1165, arXiv:1004.1353; a cluster of 25 black holes: arXiv:2505.01495. Stellar tidal disruption in full GR: arXiv:1201.4389, arXiv:1502.05740, arXiv:1408.1695. A Hills-type full-NR calculation of "binary + massive black hole" was not found, nor a version whose members are self-gravitating collisionless clumps. [TO VERIFY; novelty search before starting]
- **The connection on the cosmological side [JUDGEMENT].** The formation of primordial-black-hole binaries and their history of perturbation by third bodies determine the merger rate (arXiv:1812.01930, arXiv:1908.09752, arXiv:2006.11172); for primordial-black-hole binaries with dark-matter dresses see arXiv:1805.09034. When neighbouring density peaks in EMD each form a black hole (the two-peak case of S1) and then meet a heavier third one, that is the early-universe version of the Hills process.
- **Scale estimate for the strong-field regime [JUDGEMENT; derivation to be checked].** In units of the gravitational radius of the large black hole, r_g = GM/c², r_t/r_g = (a_b/r_gb)·q^(−2/3), with q = M/m_b and r_gb = G m_b/c². A parabolic orbit in Schwarzschild with pericentre below 4 r_g plunges into the black hole, so separation before the plunge requires a_b/r_gb ≳ 4 q^(2/3): about 19 for q=10, about 86 for q=100, about 400 for q=1000. For compact binaries, full NR can reach q≈10–30 and a_b≈20–60 r_gb: the separation happens at a few r_g, and every pair of the three bodies is in the strong field. The gravitational-wave merger time of an equal-mass binary is, by the Peters formula, (5/64)(a_b/r_gb)⁴ G m_b/c³; for a_b=30 r_gb and q=10 this is about 6×10³ GM/c³, far longer than the few hundred GM/c³ of one passage, so the binary survives until the encounter.

---

## 4. Criteria: which problems need both NR and kinetics

**Signals that full NR is needed (any one suffices).**

- (N1) The compactness GM/(Rc²) reaches 0.1–1, and a horizon appears or nearly appears;
- (N2) bulk velocities or velocity dispersions approach the speed of light;
- (N3) perturbations are nonlinear on horizon scales, so that the initial-data constraints are themselves a nonlinear problem;
- (N4) the generation of gravitational waves needs a non-perturbative, gauge-unambiguous calculation, or their backreaction cannot be neglected;
- (N5) there is no trustworthy background to expand around;
- (N6) a decisive null result that depends on no approximation is required.

**Signals that kinetics (Vlasov) is needed and a fluid will not do (any one suffices).**

- (K1) multi-stream regions after shell crossing;
- (K2) velocity dispersion, anisotropic stress or free streaming is dynamically important;
- (K3) structures are supported by angular momentum and phase mixing, and go through violent relaxation;
- (K4) there is no thermalization and hence no equation of state.

**The intersection.**

| Problem | NR criteria | Kinetic criteria | Corresponding problem |
|---|---|---|---|
| Collapse to a black hole in EMD | N1, N3, N4 | K1, K3 | S1 |
| Gravitational waves from EMD structure formation | N4 | K1 | S2 |
| Relativistic collapse of an SIDM core | N1, N2 | K3, plus collisions | S3 |
| Black-hole growth in a collisionless medium, dark-matter dress, binaries | N1, N4 | K1, K3 | S4 |
| Black-hole formation with a free-streaming component | N1, N3 | K2 | S5 |
| Light-cone observables in late-time multi-stream regions | N6 | K1 | S6 |
| Backreaction of high-frequency gravitational waves | N4 | K2 (massless) | S7 |
| Vlasov matter near singularities | N5 | K2 | S8 |
| Large inflationary perturbations driven by stochastic sources | N3, N5 | Not applicable (scalar-field problem) | S11 |
| Tidal separation of a binary in the strong field | N1, N2, N4 | K1, K3 (when the members are collisionless clumps or dressed black holes) | S12 |

---

## 5. Ranking of the science problems

The ranking rests on four items: how irreplaceable the method is, how far existing code is from being able to compute, the physics return, and the state of the competition. Everything below is [JUDGEMENT] unless marked otherwise.

**The group's decision.** S1, S2, S3, S4, S11 and S12 advance at the same time and correspond, in this order, to Tracks A–F (§9). S5–S10 are kept in reserve and get no worktree. The column "distance of the code" in the table assumes that core already provides the particle–spacetime coupling; this premise does not hold at present (§2.2), which is why every track also has a preparatory package that does not depend on core.

| No. | Problem | Irreplaceability | Distance of the code | Return | Competition |
|---|---|---|---|---|---|
| S1 | Black-hole formation from collisionless matter in EMD: threshold, mass, spin, binaries, gravitational waves | High | Near (expanding-ball scheme) | High | Others have started; sub-directions are open |
| S2 | Non-perturbative gravitational waves from EMD structure formation | High | Medium (needs a periodic domain) | High | Newtonian N-body exists; full GR is open |
| S3 | Relativistic end state of SIDM core collapse | High | Medium (needs collisions) | High | Spherical fluid models exist; 3D kinetics is open |
| S4 | Black-hole growth and dress in an expanding collisionless medium | Medium-high | Near | Medium-high | Scalar-field and fluid versions exist |
| S5 | Black-hole formation with a free-streaming component | High | Far (massless particles + fluid) | Medium-high, uncertain | Not seen; novelty search needed |
| S6 | Decisive test in late-time multi-stream regions | Medium | Far (cosmological volume + ray tracing) | Medium, mostly null results | Fluid NR and weak-field codes are already there |
| S7 | 3+1 test of the Burnett conjecture and "graviton PIC" | High | Medium (massless particles) | Uncertain, strongly conceptual | Not seen; novelty search needed |
| S8 | Vlasov matter near singularities | High | Medium | Towards mathematical GR | Not seen |
| S9 | Hoop conjecture, cosmic censorship and extremal black holes on a cosmological background | Medium-high | Near | Towards mathematical GR | Asymptotically flat versions are being done |
| S10 | EMD-to-radiation transition with decay | High | Far (particles + radiation fluid + source terms) | High | Newtonian hybrid simulations exist |
| S11 | NR of stochastic inflation: statistics of large perturbations, connection to black-hole formation and EMD | Medium (a scalar-field problem; the NR formalism exists) | Far (scalar field + stochastic sources) | Medium-high | The group that created the formalism is ahead |
| S12 | Strong-field Hills mechanism: tidal separation of collisionless members and dressed black holes | High | Medium (multi-body initial data) | Medium-high, uncertain | Approximate treatments exist; full NR not seen; novelty search needed |

### S1 Primordial-black-hole formation in the early matter-dominated era (first choice)

**The problem.** Pressureless, collisionless matter collapses in an expanding background: under what conditions does a black hole form? What are its mass and spin? Do neighbouring peaks form a binary? How much gravitational radiation is emitted?

**Why it has to be Einstein–Vlasov + NR.** Black-hole formation is a strong-field problem (N1); generic collapse is triaxial, first flattening into a pancake along one axis, so shell crossing is unavoidable (K1); whether the collapse continues depends on the angular momentum and velocity dispersion in the multi-stream region (K3). A dust fluid breaks down here, and arXiv:2609.14218 has demonstrated directly that fluid and particles give different answers. A scalar-field proxy has gradient pressure on the de Broglie scale and is not the same kind of matter [BACKGROUND].

**State of the art.** See §3.5. The analytic estimates disagree markedly among themselves, and they differ from the full-NR particle result by about an order of magnitude (arXiv:2609.14218) [VERIFIED]; only this one full-NR particle calculation was found, and it gives the threshold for specific triaxial profiles.

**Differentiation from arXiv:2609.14218.** AMR, GPUs and moving punctures let NRPIC continue long after black-hole formation and handle several black holes; the two-clump test of Wu and Most has already gone through the full chain of formation, inspiral, merger and accretion, and extracted the waveform [VERIFIED]. Spin, binaries and waveforms are quantities their abstract does not touch.

**Deliverable physical quantities.**

1. The threshold surface: initial curvature-perturbation amplitude × ellipticity × prolateness × initial velocity dispersion, compared item by item with the hoop criterion (arXiv:1609.01588), the velocity-dispersion criterion (arXiv:2211.13950) and peak-profile statistics (arXiv:2507.18312, arXiv:2508.10070).
2. The black-hole mass at formation and the subsequent growth law; separation of direct collapse from accretion-driven collapse (arXiv:2109.04896). A test of whether there is a mass gap at threshold. If the critical behaviour is Type I, the mass spectrum of EMD primordial black holes has no critical-scaling tail towards small masses of the kind found in the radiation era.
3. Spin: at horizon formation and after accretion. Analytic predictions range from near-extremal (arXiv:1707.03595) to very small (arXiv:2507.18312), and scalar-field NR finds it negligible after accretion (arXiv:2306.11810). Nobody has computed the collisionless case.
4. Gravitational waveforms, extracted directly from the metric and compared with the quadrupole approximation (arXiv:2403.15126, arXiv:2605.04487).
5. Two-peak initial data: two neighbouring overdensities in a common envelope each form a black hole, inspiral and merge. This is the cosmological version of the two-clump demonstration of Wu and Most; the corresponding radiation-era work is arXiv:2609.03051.

**Code requirements.**

- Phase 0 leaves the evolution code unchanged (provided core already supplies the particle–spacetime coupling, see §2.2 and §9.3) and needs only new initial data: the **expanding dust ball**. The interior of a spherically symmetric homogeneous dust ball is exactly FLRW and the exterior is Schwarzschild. In the flat (marginally bound) case the Friedmann equation gives 2GM/(Rc²)=(HR/c)², so as long as the areal radius of the ball is smaller than the Hubble radius there is no anti-trapped surface on the initial slice. Collapse in EMD happens precisely in the sub-horizon phase: a perturbation is small when it enters the horizon, then grows with the scale factor and turns around only when it reaches order one, so this restriction is no obstacle. Superposing a Zel'dovich deformation or a curvature perturbation inside the ball gives non-spherical collapse. The semi-relativistic calculation of arXiv:2605.04487 uses exactly "a homogeneous ball with Zel'dovich deformation in an EdS background" [VERIFIED].
- In the marginally bound case, on a slicing of Painlevé–Gullstrand type the spatial metric is flat and the lapse is 1, so the initial data are analytic; after a non-spherical perturbation the constraints are solved once more. [JUDGEMENT; derivation to be checked]
- In spherical symmetry the exterior has no influence on the interior; without it, the tidal effect of the boundary has to be controlled by a convergence test in the ball radius.
- Phase 1 then moves to a periodic domain or an asymptotically FLRW boundary (M1).

**Risks.** Gauge pathologies (arXiv:2610.23218); resolution dependence of the curvature at caustics (reported by Wu and Most themselves); particle noise near threshold; the definition of "threshold" in the pressureless case depends on the duration of EMD and has to be stated beforehand.

**Minimum publishable unit.** Expanding ball + triaxial deformation, a scan of one threshold line in ellipticity and amplitude, with black-hole mass, spin and waveform, compared with the threshold of arXiv:2609.14218 and the criterion of arXiv:1609.01588.

**Key references.** arXiv:2609.14218, arXiv:2610.23218, arXiv:1609.01588, arXiv:1707.03595, arXiv:2211.13950, arXiv:2507.18312, arXiv:2508.10070, arXiv:2109.04896, arXiv:2306.11810, arXiv:2605.04487, arXiv:1611.07906, arXiv:1901.04498.

### S2 Gravitational waves from nonlinear structure formation in the early matter-dominated era

**The problem.** How much gravitational radiation comes from the formation, virialization and merging of halos in EMD? Within what range can estimates from Newtonian N-body plus the quadrupole formula be trusted?

**Why it is needed.** All existing simulations use Newtonian or semi-relativistic gravity (§3.6). Perturbation theory has gauge ambiguities in a matter-dominated era; there is also a report of secular growth of the third-order term (arXiv:2610.08045, title only verified), and if it holds, the reliability of the perturbative expansion is in doubt here. Full NR evolves the metric directly, so the radiative degrees of freedom are part of the solution; Weyl scalars or a covariant transverse-traceless projection (arXiv:2111.09163) give a gauge-unambiguous signal.

**Deliverable physical quantities.** The gravitational-wave burst when a single pancake passes through shell crossing; the stochastic-background spectrum of a population of halos in a small box; a wavenumber-by-wavenumber comparison with the Newtonian results of arXiv:2212.00425 and arXiv:2312.12499, showing when relativistic corrections become significant (expected when the initial power is large and the halos approach relativistic compactness).

**Code requirements.** A periodic domain, a cosmological gauge, gravitational-wave diagnostics in a periodic domain (M1, M8).

**Minimum publishable unit.** Pancake collapse of a plane-symmetric or single-mode perturbation, with the full-GR gravitational waves compared with the prediction of the Zel'dovich approximation.

**Key references.** arXiv:1002.3278, arXiv:2212.00425, arXiv:2312.12499, arXiv:2403.15126, arXiv:2605.04487, arXiv:1704.03500, arXiv:2012.14016, arXiv:2610.08045, arXiv:2109.01398.

### S3 Relativistic end state of the collapse of a self-interacting dark-matter core

**The problem.** After the core of an SIDM halo has gone through gravothermal collapse into the relativistic regime, how much mass ends up in the black hole? How do rotation, dissipation and non-equilibrium heat flux change the answer?

**Why it is needed.** The end state is strong-field (N1) with relativistic velocity dispersion (N2); the core passes from short to long mean free path, where fluid closures are unreliable (at the edge of K4). The best existing treatment is a spherically symmetric Misner–Sharp fluid model (arXiv:2601.17117). The seed mass decides directly whether SIDM can explain the massive high-redshift black holes seen by JWST (arXiv:2506.17641, arXiv:2504.00075).

**Code requirements.** Monte Carlo two-body collisions (M5). Start from a relativistic core model close to the instability threshold instead of evolving the whole gravothermal process, because the relaxation time is far longer than the dynamical time. The relativistic-cluster stability test already done by Wu and Most is the direct starting point.

**Risks.** The collision term is stiff in the short-mean-free-path regime; the choice of initial model affects the conclusion and has to be aligned with the instability criterion of arXiv:2108.11967.

**Minimum publishable unit.** The instability threshold of collisionless relativistic clusters (against arXiv:gr-qc/0601112, arXiv:2009.08163) → collisions switched on step by step, giving the collapsed mass fraction as a function of Knudsen number.

**Key references.** arXiv:astro-ph/0110561, arXiv:astro-ph/0111176, arXiv:2108.11967, arXiv:2010.15132, arXiv:2506.17641, arXiv:2601.17117, arXiv:1101.3097.

### S4 Black-hole growth in an expanding collisionless medium and the dark-matter dress

**The problem.** How does a black hole in a matter-dominated background grow by accreting collisionless matter? What is the shape of the density spike that forms around it in the strong field? How fast does a dressed black-hole binary merge?

**Why it is needed.** Newtonian self-similar secondary infall gives an r^(−9/4) density profile [BACKGROUND]; the relativistic corrections near the horizon and the growth of the black hole itself need full GR. The corresponding radiation-era fluid result is the Zel'dovich–Novikov law (arXiv:2608.13206); for the matter-era scalar-field result see arXiv:2109.04896. The effect of the dress on the merger rate of primordial-black-hole binaries is currently estimated in Newtonian terms (arXiv:1805.09034).

**A null test that comes for free.** Put a puncture black hole into an expanding particle medium and, after subtracting accretion, check whether the horizon mass changes with the scale factor. This is a direct numerical test, for an ordinary black hole, of the "cosmological coupling" claim (arXiv:2302.07878); a null result is expected.

**Code requirements.** The expanding-ball scheme plus a central puncture; possible in phase 0.

**Key references.** arXiv:1901.08528, arXiv:1607.00612, arXiv:2106.07480, arXiv:1805.09034, arXiv:2109.04896, arXiv:2608.13206, arXiv:2302.07878.

### S5 Primordial-black-hole formation with a free-streaming component

**The problem.** How does the formation threshold change when a substantial part of the radiation consists of free-streaming particles?

**Background.** Neutrinos decouple at about 1 MeV, when the horizon mass is of order 10⁵ solar masses; from then on neutrinos make up forty to fifty per cent of the radiation energy density and no longer provide a pressure response like a tightly coupled fluid [BACKGROUND]. Supermassive primordial black holes above this mass (arXiv:1609.02245, arXiv:1202.3848) therefore form while nearly half of the "radiation" is collisionless. Relativistic particles of a hidden sector (arXiv:2209.02735) pose the same kind of problem. The effect of the thermal history on the threshold through the equation of state has been studied (arXiv:1906.08217), but at the fluid level.

**Why it is needed.** Free streaming is a kinetic effect (K2) and black-hole formation is strong-field (N1). Einstein–massless-Vlasov has to be coupled to a radiation fluid.

**State of the art.** I found no full-GR kinetic calculation of this problem. [TO VERIFY; novelty search required before starting]

**Code requirements.** Massless particles (M6) coupled to the dynamical-spacetime fluid module (arXiv:2409.10384).

### S6 Decisive test in late-time multi-stream regions

**The problem.** In a full-GR particle simulation that resolves virialized structures and voids, measure directly the quantities timescape relies on (the difference in clock rates between voids and walls, the difference between volume averages and observers), and give the distance–redshift relation, the dipole and lensing on the light cone.

**Why it is needed.** Fluid NR reaches only the smoothing scales before shell crossing; weak-field codes assume an FLRW background plus small perturbations from the outset, which is exactly the assumption the proponents of timescape question. Only a method without a background assumption that can also handle multi-stream regions can give a result both sides accept (N6 + K1).

**Expectation.** A null result is likely. The value lies in ending the dispute and in providing a benchmark for relativistic effects in the era of Euclid and DESI.

**Cost.** The light-speed CFL condition multiplies the number of steps by c/v compared with Newtonian simulations, that is, by two to three orders of magnitude; AthenaK's AMR uses a single time step for all levels (main text of arXiv:2409.16053) [VERIFIED], so deep refinement slows everything down; whether NRPIC keeps this is [TO VERIFY]. The hybrid strategy of M10 is needed.

**Key references.** arXiv:1908.05683, arXiv:1810.05203, arXiv:2209.06775, arXiv:2606.05479, arXiv:2601.20633, arXiv:2403.15134, arXiv:2408.03049, arXiv:2412.15143, arXiv:2406.05048, arXiv:1706.09309.

### S7 3+1 numerical test of the Burnett conjecture and "graviton PIC"

**The idea.** Mathematically, the backreaction of high-frequency gravitational waves is equivalent, in the limit, to massless Vlasov matter (§3.7). With massless particles added, NRPIC can do two things:

1. A test: evolve a high-frequency vacuum gravitational wave packet with full NR and, alongside it, the corresponding particle distribution with massless NRPIC, and compare the coarse-grained metrics. All existing proofs assume U(1) symmetry; the 3+1 case without symmetry is open.
2. An application: treat the high-frequency gravitational waves that the mesh cannot resolve as sub-grid transport of massless particles, and thereby simulate spacetimes dominated by gravitational waves or by gravitational-wave turbulence (arXiv:2509.19769), and test numerically the Green–Wald conclusion that the effective stress is traceless (arXiv:1011.4920). For related full-NR gravitational-wave cosmology see arXiv:1505.02959, arXiv:1801.08362.

**State of the art.** No numerical work was found. [TO VERIFY]

### S8–S10 (exploratory)

- **S8 Vlasov matter near singularities.** In the homogeneous case Vlasov matter is known to behave differently from a perfect fluid (arXiv:gr-qc/0512031); the inhomogeneous case (spikes, mixmaster) with Vlasov matter has no numerical study. Reference points: arXiv:0904.1546, arXiv:2010.01399.
- **S9 Hoop conjecture, cosmic censorship and extremal black holes on a cosmological background.** Put spindle collapse (arXiv:1611.07906, arXiv:1901.04498) into an expanding background or add a cosmological constant; replace charge by rotation and test whether the threshold solutions of collisionless collapse tend to extremal Kerr (for the charged case see arXiv:2402.10190, arXiv:2511.20567). This and the spin question of S1 are two sides of the same coin.
- **S10 EMD-to-radiation transition with decay.** Particles decay into a radiation fluid and the halos evaporate with them; the more abrupt the transition, the stronger the induced gravitational waves (arXiv:1904.12879, arXiv:2003.10455). Newtonian hybrid simulations exist (arXiv:2312.12499, arXiv:2306.14961), and for the relativistic treatment of decaying matter in N-body see arXiv:1904.11773. A full-GR version needs particles, a radiation fluid and the exchange source terms all in place.

### S11 Numerical relativity of stochastic inflation (Track E, "if possible")

**The problem.** Once quantum fluctuations enter the full Einstein–scalar-field equations as stochastic sources, how far do the statistics of large perturbations (the seeds of primordial black holes) differ from the predictions of stochastic δN? How large a role do gradients, shear and the constraints play during ultra-slow roll?

**Why NR is needed.** Stochastic δN relies on the separate-universe approximation, whose validity at the sudden transitions of USR is disputed (arXiv:2311.03281); lattice codes on an FLRW background have the problem that super-horizon modes do not freeze (arXiv:2606.14853). The full ADM/BSSN formalism (arXiv:2401.08530, arXiv:2512.14649) includes metric backreaction and the constraints automatically (N3, N5). It is not a kinetic problem.

**State of the art.** See §3.10. The formalism and the first BSSN implementation come from the same group, and the tests are one slow-roll and one USR case. I found no large-sample tail statistics, no calculation running from inflation through to black-hole formation, and no connection to EMD. [JUDGEMENT; novelty search pending]

**Deliverable physical quantities (ordered by feasibility).**

1. Reproduce the slow-roll and USR cases of arXiv:2512.14649, accepted against the freezing criterion of arXiv:2606.14853.
2. The distribution of the compaction function in USR configurations, compared with the stochastic-δN results (arXiv:2312.12911, arXiv:2510.09303) and handed to Track A as a distribution of initial conditions.
3. The field-to-particle hand-over: the oscillating phase of the inflaton condensate converted into Vlasov particles and connected to EMD, compared with the inflaton-halo literature of §3.6.
4. Backreaction in the eternal-inflation regime (exploratory).

**Code requirements.** A scalar field plus stochastic sources (M11); periodic domain, cosmological gauge, constrained initial data (shared with Track B, M1). For the code base see decision D4.

**Risks and exit criteria.** The choices of window function and gauge affect the result; the statistics need many realizations and the compute may not suffice; direct competition with the group that created the formalism. If by G1 the slow-roll or USR reproduction does not meet the freezing criterion, or the cost of a single realization exceeds the budget, Track E is downgraded to "supplying Track A with statistics of initial conditions from a non-NR stochastic-δN solver".

**Key references.** arXiv:2401.08530, arXiv:2512.14649, arXiv:2610.32592, arXiv:2502.06783, arXiv:2606.14853, arXiv:2604.00978, arXiv:2405.10692, arXiv:2312.12911, arXiv:2510.09303, arXiv:2203.13852, arXiv:2009.08715.

### S12 The Hills mechanism studied with NRPIC (Track F)

**The problem.** When a binary passes a massive black hole at a few gravitational radii, what are the separation probability, the split of energy between ejection and capture, the internal heating and mass stripping of the members, and the gravitational-wave burst? How do the spin of the black hole and the internal structure of the members (collisionless clumps, dressed black holes) change the scaling laws of the Newtonian restricted three-body problem?

**Why NR and kinetics are needed.** In the strong-field regime every pair of the three bodies is relativistic (N1, N2), and gravitational-wave backreaction and absorption by the horizon enter the energy budget (N4); existing relativistic treatments regard the members as point particles or use a Newtonian approximation for the self-gravity of the binary (§3.11). When the members are collisionless clumps or black holes with dark-matter dresses, tidal heating, stripping and phase mixing are kinetic processes (K1, K3) for which neither fluid nor point-particle models are adequate.

**Reading of the group's instruction [JUDGEMENT; to be confirmed].** "Study the Hills mechanism with NRPIC" has three workable objects, to be chosen in decision D5: (a) a binary black hole (two punctures) passing a large black hole, pure vacuum, no particles needed, as the baseline; (b) a binary of two self-gravitating collisionless clumps passing a puncture, closest to the two-clump test of Wu and Most and the regime only NRPIC reaches; (c) two black holes with collisionless dresses, connecting to Track D. The default order is (a)→(b)→(c).

**Deliverable physical quantities.**

1. In the Newtonian limit, reproduce the scaling of separation probability and ejection energy of the restricted three-body problem (arXiv:0911.1136, arXiv:1804.02911), as verification.
2. Relativistic corrections to the separation probability, the ejection speed and the parameters of the capture orbit as functions of r_p/r_g, compared with the "exact geodesic plus Newtonian self-gravity" model of arXiv:2404.16270 and with arXiv:2402.02178.
3. Mass-stripping rate and internal heating of collisionless members, and the fate of the stripped matter (plunging, bound, ejected).
4. The gravitational-wave burst of the passage: waveform and radiated energy.
5. Dependence on the spin of the large black hole and on the orbital inclination.
6. The eccentricity of the subsequent orbit of the captured member, compared with the EMRI literature (arXiv:2610.13294).

**Code requirements.** Three-puncture initial data, constrained initial data for clump–black-hole and clump–clump systems (M12); trajectory and binding-energy diagnostics for several bodies (M8). For the size of the problem see the last item of §3.11.

**Risks.** The mass ratio is limited by resolution (q≲30); orbital eccentricity and junk radiation from the finite initial separation; numerical relaxation of the collisionless clumps while they wait for the encounter; "truly not done before" needs a novelty search.

**Minimum publishable unit.** For q≈10, one scan line in pericentre distance each for (a) and (b), giving the separation boundary, the energy split and the waveform, compared with the Newtonian and the geodesic models.

**Key references.** arXiv:0911.1136, arXiv:1201.4794, arXiv:1804.02911, arXiv:2404.16270, arXiv:2402.02178, arXiv:2610.13294, arXiv:1501.07856, arXiv:1801.05780, arXiv:0710.0879, arXiv:1004.1353, arXiv:2505.01495, arXiv:1408.1695.

---

## 6. Directions for method innovation

Everything below is [JUDGEMENT]; the references in parentheses are those to draw on.

### M1 Cosmologization: boundaries, gauge, initial data

- **Boundaries.** Three routes: a periodic domain; an outer boundary that is asymptotically FLRW; an expanding ball embedded in an asymptotically flat domain (phase 0 of S1). For an approach to non-periodic, curved geometries see arXiv:2508.20606. A periodic domain is not a harmless numerical convenience in GR: the constraint equations bring global integrability conditions (arXiv:1305.5576, arXiv:2207.03125), and the topology of the three-torus has physical effects of its own (arXiv:astro-ph/0602159, arXiv:2210.11426).
- **Gauge.** Available starting points: factoring out an FLRW reference metric (arXiv:1704.04307); the cosmologically rescaled Gamma-driver (arXiv:2608.13206); the lapse equation modified for dust collapse (arXiv:2610.23218); slicings that avoid gauge shocks (arXiv:2207.06376, arXiv:gr-qc/0210050). Comoving synchronous gauge converges poorly with particles (arXiv:1810.05203). For more general discussion see arXiv:1809.07010, arXiv:2001.00394.
- **Initial data.** Constraint solving for particle distributions: CTTK and GRTresna (arXiv:2207.03125, arXiv:2501.13046); existence of solutions and branches (arXiv:2509.26470); a non-periodic scheme (arXiv:2607.21308); super-horizon long-wavelength solutions (arXiv:1503.03934); relativistic N-body initial conditions (arXiv:1702.03221, arXiv:2110.11249, arXiv:2001.07968); East et al. satisfy the constraints by adjusting the particle masses (arXiv:1908.05683).

### M2 Noise control

- High-order shape functions and filtering (arXiv:2605.15260).
- Phase-space sheets: under cold initial conditions the matter occupies a three-dimensional submanifold of phase space, and deposition by tetrahedral tessellation gives a noise-free density both before and after shell crossing (arXiv:1111.3944, arXiv:1210.6652, arXiv:1501.01959, arXiv:1909.00008). Giblin et al. have already used a sheet representation in BSSN (arXiv:1810.05203). Extending it to the deposition of the full stress–energy tensor is an open engineering problem.
- The δf method: particles represent only the departure from a known distribution (arXiv:2010.07321). How to choose the reference distribution in full NR, where there is no background split, is a theoretical problem to be solved.
- Systematic effects of discreteness: arXiv:astro-ph/0702575, arXiv:1606.02038, arXiv:1801.03906.

### M3 Constraint-compatible deposition

Electromagnetic PIC guarantees the discrete Gauss law through charge-conserving current deposition [BACKGROUND]. The gravitational counterpart is to make the stress–energy deposited by the particles satisfy a discrete energy–momentum balance equation, so that the Hamiltonian and momentum constraints are preserved automatically during the evolution. The dGREM formulation (arXiv:2111.05282) writes the Einstein equations in a Maxwell-like flux-conservative form, and the original paper points out that it suits Yee-grid and constrained-transport discretizations [VERIFIED]. Building, in this formulation, an "energy–momentum-conserving deposition" analogous to charge-conserving deposition is the natural step from the "conserved integrated source" of Wu and Most to "constraints preserved pointwise". The difficulties: the energy–momentum flux equation of matter has source terms (exchange with the gravitational field), unlike charge, which is strictly conserved; and the hyperbolicity and numerical stability of dGREM as an evolution system have to be established first (arXiv:2211.13659). [TO VERIFY]

### M4 Structure preservation

Einstein–Vlasov has a variational principle (arXiv:1910.12152). In plasma physics, geometric PIC built from an action or a Poisson bracket (arXiv:1609.03053, arXiv:1612.06734) performs very well on long-time energy and Casimir invariants. A gravitational version of geometric PIC could aim at the fidelity of long-time phase mixing (the phase mixing and echo of §3.7). For symplectic integrators in NR see arXiv:0807.0734; for energy-conserving geodesic integrators see arXiv:1801.02378.

### M5 Collisions

Monte Carlo two-body scattering in the local inertial frame, conserving four-momentum pair by pair, gives an Einstein–Boltzmann solver. It serves S3; with decay and annihilation channels added it serves S10. A continuum relativistic kinetic solver (arXiv:2602.17487) can be used for cross-validation.

### M6 Multiple species

- Massless particles: null-geodesic pushing (arXiv:1801.02378, arXiv:1208.3927), serving S5 and S7.
- Particles + dynamical-spacetime fluid (arXiv:2409.10384): serving S5 and S10.
- Particles + puncture black holes: already a capability of Wu and Most, serving S4.

### M7 On-the-fly ray tracing

Treat photon bundles as another particle species and integrate the optical equations along the past light cone during the evolution, outputting distances, redshift drift and lensing quantities directly (arXiv:2209.06775, arXiv:2107.06306, arXiv:2110.00893). The data structures of GPU PIC suit this naturally. Serves S6.

### M8 Diagnostics

Gauge-invariant characterization of spacetime (arXiv:2211.08133, arXiv:2602.00155); horizon finding in expanding backgrounds (arXiv:2505.15912, arXiv:2306.11810); non-spherical quasi-local compaction (arXiv:2609.03051, arXiv:2304.13284); gravitational-wave extraction in non-asymptotically-flat domains (arXiv:2111.09163); averages and foliations (arXiv:2408.03049, arXiv:2409.00024).

### M9 Verification suite

See §10.

### M10 Performance and multiple scales

Use NRPIC only in the strong-field region and a weak-field or Newtonian solver outside, joined through the existing dictionaries (arXiv:1101.3555, arXiv:1505.04756, arXiv:1711.06681, arXiv:2404.02783). AMR engineering experience: arXiv:2112.10567, arXiv:2101.12149. The cyclic zoom built into AthenaK (arXiv:2504.16802) is another ready-made route for problems spanning many scales; whether it suits particle problems has to be assessed separately.

### M11 Stochastic sources and reproducible parallel random numbers

Monte Carlo collisions (M5) and the Langevin sources of stochastic inflation (S11) both require random numbers that are reproducible on GPUs and under MPI: the result must not depend on the number of processes, on the decomposition into mesh blocks, or on where a restart happened. The way to get this is a counter-based generator (of the Random123 kind), with the global particle index or cell index, the time step and a purpose tag as the counter and the run seed as the key [JUDGEMENT]. Spatially correlated noise (stochastic inflation needs it coloured by the window function) can be generated in Fourier space and transformed back, or produced by local filtering; whether the two agree on AMR has to be verified specifically. The interface goes into `coord/INTERFACES/rng.md`, proposed jointly by Tracks C and E.

### M12 Multi-body initial data: punctures, collisionless clumps and dresses

The Hills mechanism (S12) and dressed black-hole binaries (S4) need constrained initial data for "several punctures plus a particle distribution". Methods and accuracy comparisons for pure multi-black-hole initial data exist (arXiv:0710.0879, arXiv:0711.1165, arXiv:1004.1353); public AthenaK ships problem generators for one and two punctures (§2.2). Three things are new: conformally flat data for three or more punctures; superposing a collisionless clump in equilibrium (a relativistic cluster model) on a puncture background and re-solving the constraints; giving a puncture a collisionless dress that is approximately stationary (one can start from the adiabatically grown spike distribution, arXiv:1305.2619). The junk radiation and the initial eccentricity introduced by superposed data have to be quantified.

---

## 7. List of open questions (known unknowns)

**A. Formulation and gauge**

1. Which slicing and shift conditions carry pressureless matter stably through caustics all the way to black-hole formation? (arXiv:2610.23218, arXiv:2608.13206)
2. When do initial data for strong cosmological perturbations exist, and when are they unique? What physics does each non-unique branch correspond to? (arXiv:2509.26470)
3. Under what conditions do the three settings, periodic domain, non-periodic domain and asymptotically FLRW boundary, give consistent results? (arXiv:2607.21308, arXiv:2312.03285, arXiv:2508.20606)
4. Without an asymptotically flat region, how can gravitational-wave energy be defined and extracted unambiguously? (arXiv:2111.09163)
5. Can the dependence of averages on the foliation be removed by a gauge-invariant construction? (arXiv:2310.19451, arXiv:2409.00024, arXiv:2202.10798)

**B. Kinetic numerics in general relativity**

6. Convergence of three-dimensional NRPIC as particle number and mesh spacing go to their limits together. There is a proof in spherical symmetry (arXiv:math/0209336), none in three dimensions.
7. How does particle noise enter constraint violation and spurious gravitational waves? What are the quantitative scalings?
8. The cold limit (velocity dispersion going to zero) is a singular limit. In what sense do Vlasov solutions with tiny velocity dispersion approach the dust solution, especially near caustics?
9. Is the curvature at caustics physical or numerical? In the prolate test of Wu and Most the peak curvature still depends on resolution at the resolutions tested.
10. Numerical fidelity of long-time phase mixing and echoes. (arXiv:2609.13394)

**C. Physics**

11. Threshold, mass spectrum and spin distribution of black-hole formation in EMD. (§3.5)
12. The gravitational-wave spectrum of EMD structure formation, and the range of validity of perturbative calculations. (§3.6)
13. Collective collapse of several peaks and the formation rate of primordial binaries. (arXiv:2609.03051)
14. The seed mass from SIDM core collapse. (§3.8)
15. The relativistic profile of particle dark matter around black holes and its backreaction on mergers. (arXiv:2505.09715)
16. Whether the Green–Wald conclusion still holds in multi-stream regions; whether the core assumption of timescape can be measured directly. (§3.3)
17. How far inhomogeneity affects dark-energy inference at the DESI level. (arXiv:2606.05479, arXiv:2601.20633)
18. The structure of generic cosmological singularities with Vlasov matter. (arXiv:gr-qc/0512031)
19. Whether the Burnett conjecture holds without symmetry. (arXiv:2506.21779)
20. Nonlinear stability of matter-dominated FLRW solutions under Einstein–Vlasov. Existing results cover the Milne model (arXiv:1709.00267) and cases with symmetry or a cosmological constant; the case of an Einstein–de Sitter-type background is [TO VERIFY].

**D. Questions raised by the new tracks**

21. Stochastic sources in full NR: how far do the choices of window function, coarse-graining scale and slicing affect the tail statistics of large perturbations? (arXiv:2401.08530, arXiv:2512.14649, arXiv:2611.15050)
22. Under what conditions do the NR results of stochastic inflation agree with stochastic δN and with the stochastic lattice (arXiv:2405.10692)? Are the sudden transitions of USR the source of disagreement? (arXiv:2311.03281, arXiv:2606.14853)
23. When can the inflaton condensate be replaced by Vlasov particles? How are stress–energy and constraints matched across the hand-over surface?
24. Outcome boundaries of the strong-field Hills mechanism: when the pericentre distance approaches 4 r_g, how are the three outcomes, separation, plunge of the whole binary and capture of the whole binary, delimited? How does spin move the boundaries? (arXiv:2404.16270, arXiv:2402.02178)
25. Is there a universal scaling for the stripping and heating of collisionless members in a strong tidal field?
26. How much of the dress is left after a dressed black hole has gone through a Hills process? What does this imply for estimates of the merger rate of primordial-black-hole binaries (arXiv:1805.09034)?

---

## 8. Unknown unknowns: where to look for surprises

Everything below is [JUDGEMENT]; the candidate phenomena listed are speculation, not prediction.

**The principle for finding surprises.** Each existing tool rests on one assumption: weak-field codes assume a background plus small perturbations; fluid NR assumes a single stream; Einstein–Vlasov studies with symmetry assume spherical or axial symmetry; Newtonian kinetics assumes weak fields and low speeds. No tool could previously enter the cell "strong field × kinetics × no symmetry × cosmological boundaries". Surprises are most likely where all four assumptions fail together.

**Candidates.**

- **U1 Kinetic instabilities and echoes of gravity.** Plasmas have a whole family of kinetic phenomena: two-stream, Weibel, echoes. Of the gravitational counterparts, the Newtonian limit is known to have Jeans-type, radial-orbit and two-stream instabilities among others; in relativistic counter-streaming collisionless flows gravitomagnetic effects enter, and the gravitomagnetic interaction between co-moving mass currents is repulsive, opposite in sign to electromagnetism [BACKGROUND]. Dispersion relations and nonlinear saturation in the relativistic regime have hardly been studied systematically. The NRPIC authors' group already describes gravity in the language of electrodynamics and has a natural advantage here.
- **U2 Caustic-driven curvature spikes and gravitational-wave bursts.** Generic collapse in an expanding background first forms a pancake. Whether the strong curvature at the caustic is briefly not enclosed by a horizon in some geometries is the cosmological version of the spindle-collapse dispute (arXiv:1901.04498, arXiv:2305.04360).
- **U3 Extremal Kerr at threshold.** If rotating collisionless collapse has a structure similar to that of arXiv:2402.10190, EMD may contain a family of primordial black holes with near-extremal spin.
- **U4 Mass gap.** If the critical behaviour of black-hole formation in EMD is Type I, the mass of primordial black holes has a lower bound relative to the horizon mass, and the shape of the mass function differs fundamentally from the radiation-era expectation.
- **U5 The strong-field branch of the initial data.** If the other branch of solutions pointed out by arXiv:2509.26470 can be evolved, what cosmology does it correspond to?
- **U6 Topology.** The finite topology of a periodic box affects the dynamics through the constraints in full GR; the size of the effect is unknown.
- **U7 Matter becoming important again near singularities.** The standard picture holds that matter does not matter near a singularity; Vlasov matter may be an exception.
- **U8 Failure modes of representing gravitational waves by massless particles.** At graviton "caustics" the high-frequency approximation breaks down and may give an informative failure.
- **U9 Multi-species non-equilibrium.** Runaway behaviour when decay and annihilation couple to strong gravity.
- **U10 Discreteness as physics.** When the macro-particles really are black holes, does a system of many black holes converge to the Einstein–Vlasov solution as their number goes to infinity? This mean-field limit has not been proved in general relativity. Black-hole lattices (arXiv:1801.01083, arXiv:1306.1389) and black-hole clusters (arXiv:2505.01495) are data points on the discrete side, NRPIC is the data point on the continuum side, and the convergence between them can be tested numerically.
- **U11 Interaction of stochastic sources with the constraints.** If a random kick does not satisfy the constraints, constraint damping turns part of it into spurious gravitational waves or spurious curvature. Where the line runs between "physical" stochastic backreaction and numerical artefact is not known at present.
- **U12 Resonances and chaos in the strong-field three-body problem.** The separation probability of the Newtonian restricted three-body problem is sensitive to the binary phase. With spin precession, gravitational-wave recoil and absorption by the horizon added in the strong field, the dependence of the outcome on the initial phase may show structure absent from the Newtonian picture.

**Exploration protocol.**

1. Every scan outputs, at the same time, gauge-invariant scalars (the Kretschmann scalar, the electric and magnetic parts of the Weyl tensor), constraint norms and the budgets of conserved quantities.
2. Any anomaly first passes the "three-way convergence": change particle number, mesh spacing and gauge, one at a time. Treat it as physics only when it is stable under all three.
3. A result in the weak-field regime must agree with a weak-field or Newtonian code before it is extrapolated to the strong field.
4. Record failed runs. Where the gauge collapses and where the constraints blow up is information in itself.

---

## 9. Execution plan: six parallel tracks

This section replaces the sequential roadmap of version 1. Everything is [JUDGEMENT] unless marked otherwise.

### 9.1 Overview, dependencies and open decisions

**Reading of the group's instruction.** "1 problem set" is taken to mean the first-choice problem S1; "2 (2.1; 2.2; 2.3)" the second-tier problems S2, S3 and S4; to these are added stochastic inflation, "if possible", and the Hills mechanism requested afterwards. If something else was meant, only the track table in `coord/CHARTER.md` has to change; the harness does not depend on the particular problems.

| Worktree | Branch | Owner of | Problem | What can be done on day one (without core) |
|---|---|---|---|---|
| `repo/` | main | Orchestration, integration, review | — | Build the harness (§11), record decisions D1–D7 |
| `wt/core` | core/nrpic | The shared NRPIC implementation | — | Read the paper's source; interface proposals; unit tests for pusher and deposition |
| `wt/kb` | kb/main | The knowledge base | — | K0–K3 of §12 |
| `wt/A-emd-pbh` | track/A-emd-pbh | EMD primordial-black-hole formation | S1 | Expanding-ball initial-data module; analytic criteria as code; Newtonian precursor scan |
| `wt/B-emd-gw` | track/B-emd-gw | Gravitational waves from EMD structure formation | S2 | Z4c tests in a periodic domain; gravitational-wave diagnostics; Newtonian and weak-field baselines |
| `wt/C-sidm` | track/C-sidm | Relativistic collapse of an SIDM core | S3 | Prototype of the relativistic Monte Carlo collision operator; spherically symmetric baseline |
| `wt/D-bh-dress` | track/D-bh-dress | Black-hole growth and dark-matter dress | S4 | Exact-solution benchmark; spike in the probe limit; Newtonian secondary infall |
| `wt/E-stoch-inf` | track/E-stoch-inf | Stochastic inflation (if possible) | S11 | Reproduction specification; assessment of the code base; random-number interface |
| `wt/F-hills` | track/F-hills | Hills mechanism | S12 | Newtonian and geodesic baselines; three-puncture vacuum runs |

**Dependencies.** Providers are on the left of each arrow, users on the right:

```text
kb    --read-only snapshots----------------------------------------------> every owner
core  --core-v0.1: interpolation, pusher, deposit, Z4c coupling, particle ID--> A, C, D, F(b), F(c)
core  --core-v0.2: periodic particles, cosmological-gauge hooks--------------> B, A (periodic phase), D (periodic phase)
B     --cosmological gauge, periodic initial data, GW diagnostics-----------> A, D, E
A     --expanding-ball initial data, horizon mass/spin diagnostics----------> D, F
C     --collision operator--------------------------------------------------> core (later: S10)
C + E --reproducible RNG interface------------------------------------------> core
D     --dressed-black-hole initial data-------------------------------------> F(c)
E     --statistics of large perturbations-----------------------------------> A
F     --multi-puncture initial data, multi-body diagnostics-----------------> core, D
F(a) three punctures in vacuum, and every pre-core package, need public AthenaK or no AthenaK at all.
```

**Decisions for the group.** The orchestrator records them as `coord/DECISIONS/0001…0007`; where there is no answer the default is taken and marked PROVISIONAL.

| No. | Decision | Default | Remarks |
|---|---|---|---|
| D1 | Repository layout | The fork of AthenaK is the main repository, with four added top-level directories `harness/`, `coord/`, `kb/`, `tracks/` | The alternative is a separate project repository with AthenaK as a submodule; choose it to keep science notes apart from code that may later go upstream. AthenaK is BSD 3-Clause [VERIFIED] |
| D2 | Source of the NRPIC code | Both in parallel: ask the authors, and rebuild from the paper | The request is made by the group; steps C0 and C1 of core are needed in any case |
| D3 | Remote and pushing | A local commit at the end of every session is mandatory; pushing needs human confirmation | For unattended pushing, move the rule for "push own branch" to allow |
| D4 | Code base of Track E | Decided at E's G0 from the assessment | Add a scalar field to AthenaK, or build on GRChombo/GRTeclyn |
| D5 | Objects studied in Track F | (a) binary-black-hole baseline → (b) binary of collisionless clumps → (c) dressed black holes | If other objects were meant (stellar binaries, for example), change at F's G0 |
| D6 | Compute budget and machines per track | Undecided | Goes into CHARTER.md; `nrpic-run` refuses runs beyond it |
| D7 | Claude Code auto memory | Switched off in the project settings | All worktrees of one repository share one auto-memory directory [VERIFIED]; with it off, all durable knowledge goes into files under git |

### 9.2 Stage gates

Every track (core and kb included) passes five gates in order. The only way through a gate is `/stage-check` (§13.3) plus the group's sign-off; a failed check is tagged and reported as well.

| Gate | Name | Evidence required | Main products |
|---|---|---|---|
| G0 | Scoping | Problem statement, parameter ranges, exit criteria, test plan; the statements of the key references verified in the knowledge base; risk list; compute estimate | Working note v0; architecture schematic; stage timeline |
| G1 | Pre-core baseline | Baseline results obtainable without the NRPIC coupling; the analysis pipeline validated on them; interface proposals submitted | Baseline data and figures; interface documents |
| G2 | Verified capability | The code paths used by the track pass their tests of §10; three-way convergence in particle number, mesh spacing, and gauge or boundary; constraints behave; a first minimal full-GR kinetic run | Verification report; reproducibility package |
| G3 | Science runs | The pre-registered scan is complete; robustness checks; comparison with the literature; null results and failed runs are on record | Result figures and tables; the numerical ledger in the Supplemental Material |
| G4 | Paper | A manuscript written through the new-paper procedure of `/paper-writing`; manifests, scripts and tags complete, so that a third party can redo the work | Manuscript; reproducibility package |

Indicative timing (can be changed once written into CHARTER.md): G0 within week 2; G1 within week 8; G2 depends on core-v0.1, target within month 4; G3 within month 9; G4 within month 12. The six tracks need not pass gates in step.

### 9.3 core: the shared NRPIC implementation (critical path)

**Goal.** A verified implementation of the particle–spacetime coupling that every track can use, released as tagged versions (core-v0.1, core-v0.2, …).

**Two routes in parallel.** Ask the authors for the code (D2); rebuild independently from the paper. Even if the first succeeds, the first two steps of the second (reading the paper, fixing interfaces) are not wasted.

**Starting point [VERIFIED, §2.2].** Public AthenaK has: a particle container (the only pushers are drift, leap_frog and two kinds of tracer), Z4c with puncture tracking, horizon output, wave extraction, the matter-source interface `tmunu`, a multigrid directory, periodic boundaries. It lacks: deposition and coupling for self-gravitating particles, scalar fields, any cosmological setting. The branch particles_gr contains pushers that are relativistic by their names and is worth reading first.

**Work packages.**

- C0 Read the source of arXiv:2611.12831 through the knowledge base, correct §2, and list separately the implementation details the paper states and those it does not.
- C1 Interface proposals: `deposit.md` (definition and centring on the mesh of the matter sources Z4c needs), `pusher.md`, `particle_id.md`, `diagnostics.md`.
- C2 Implementation, each step with its own test: interpolation of the metric and its derivatives to particle positions → geodesic pushers (implicit midpoint and DGREM–Boris) → deposition on a uniform mesh → coupling into the Z4c sources → deposition across refinement boundaries → constraint-satisfying particle initial data → restart and output.
- C3 Verification ladder (the rows of §10 marked CORE): order and conserved quantities of geodesics on a fixed Kerr background; Oppenheimer–Snyder collapse with a horizon-mass error of the same order as in the paper; prolate collapse; stability of relativistic clusters.
- C4 core-v0.2: particles in a periodic domain and hooks for cosmological gauges, designed together with Track B; afterwards one release per accepted interface change.

**Track-specific criteria.** G1: C0 and C1 complete, interfaces accepted. G2: all of C3 passed, core-v0.1 released.

**Main risks.** The details the paper leaves out (order of deposition, filtering, the precise treatment at refinement boundaries) have to be filled in independently, and the result may differ from the authors'; upstream may publish an official implementation at any time, and it then has to be decided whether to merge or to keep both.

### 9.4 Track A: EMD primordial-black-hole formation (S1)

**Goal.** Expanding ball plus triaxial deformation, a scan of one threshold line in ellipticity and amplitude, with black-hole mass, spin and waveform; then two-peak initial data leading to a binary.

**Pre-core work packages.**

- A-pre-1 An initial-data module for the expanding dust ball, a standalone Python package independent of AthenaK: the time-reversed Oppenheimer–Snyder solution on a slicing of Painlevé–Gullstrand type; output of particle phase-space samples and of the metric quantities on a mesh; offline checks of the Hamiltonian and momentum constraints. First settle the two relations marked "derivation to be checked" under S1 in §5, and write the derivation into `notes/`.
- A-pre-2 The analytic criteria as code: hoop (arXiv:1609.01588), spin (arXiv:1707.03595), velocity dispersion (arXiv:2211.13950), peak statistics (arXiv:2507.18312, arXiv:2508.10070). For one set of initial-data parameters, output the table of predictions of each criterion, to be compared item by item later.
- A-pre-3 Newtonian precursor scan: run the same "EdS ball with Zel'dovich deformation" in Newtonian N-body first (set-up following arXiv:2605.04487) to fix the parameter range, the particle number and the ball radius of the full-NR scan.
- A-pre-4 Gauge and diagnostics: read arXiv:2610.23218 and arXiv:2608.13206, write the list of candidate lapse and shift conditions with the criteria for choosing among them; write the plan for horizon-mass and spin diagnostics.

**Work that depends on core.** Expansion, turnaround and collapse of the spherical expanding ball, compared with the exact solution; the threshold line with triaxial deformation; mass, spin, waveform; two-peak initial data.

**Track-specific criteria.** G1: the constraint residuals of A-pre-1 converge at the expected order; the prediction table of A-pre-2; the scan design from A-pre-3. G2: in the spherical case, the errors of the turnaround time and of the horizon-formation time relative to the exact solution converge in particle number, mesh spacing and ball radius; the horizon-mass error is of the same order as in the Oppenheimer–Snyder test of Wu and Most. G3: three-way convergence of the threshold line; comparison with the threshold of arXiv:2609.14218 and the criterion of arXiv:1609.01588; if it disagrees with the former, the origin of the difference is tracked down.

**Provides.** The expanding-ball initial-data module and the horizon and spin diagnostics (to D and F). **Needs.** core-v0.1; B's cosmological gauge when moving to a periodic domain; E's perturbation statistics (optional).

**Main risks.** Gauge pathologies; non-convergent curvature at caustics; particle noise near threshold; overlap with the authors of arXiv:2609.14218.

### 9.5 Track B: gravitational waves from EMD structure formation (S2)

**Goal.** The full-GR gravitational waves of a plane-symmetric pancake passing through shell crossing, compared with the prediction of the Zel'dovich approximation; then the stochastic-background spectrum of a population of halos in a small box.

**Pre-core work packages.**

- B-pre-1 Z4c in a periodic domain with public AthenaK: propagation of linear gravitational waves in a periodic box, standard tests of the gauge-wave kind; a record of how the existing lapse and shift options behave.
- B-pre-2 Design of the cosmological gauge and of the factoring of an FLRW reference metric (arXiv:1704.04307, arXiv:2608.13206, arXiv:2610.23218). Evolve an FLRW background with AthenaK's existing dynamical-spacetime fluid module as stand-in matter, to measure the background expansion, the scaling of the time step and the behaviour of the constraints first. Whether the module can be used this way requires reading the code first.
- B-pre-3 Gravitational-wave diagnostics in a periodic domain: the transverse-traceless projection in Fourier space (arXiv:2111.09163) and Weyl scalars, both validated on analytic linear waves.
- B-pre-4 Baselines: a Newtonian N-body pancake with the quadrupole formula, reproducing the gravitational-wave scaling of the literature (arXiv:2403.15126, arXiv:2605.04487); gevolution for the weak-field comparison (arXiv:1604.06065).
- B-pre-5 Constrained initial data in a periodic domain: the integrability condition and the CTTK scheme (arXiv:2207.03125, arXiv:2501.13046), first made to work for a fluid source.

**Work that depends on core.** The FLRW background with particles and linear growth (needs core-v0.2); the pancake case; the small box with a halo population.

**Track-specific criteria.** G1: the two diagnostics agree on analytic linear waves; the Newtonian baseline reproduces the scaling of the literature; background error and constraint convergence with the stand-in matter. G2: the scale-factor error and the linear growth rate of the particle FLRW run reach the sub-percent level and converge in particle number and mesh; agreement with gevolution in the weak-field regime. G3: three-way convergence of the pancake gravitational waves; a quantitative statement of when relativistic corrections become significant.

**Provides.** The cosmological-gauge module, periodic initial data and gravitational-wave diagnostics (to A, D and E). **Needs.** core-v0.2.

**Main risks.** Spurious gravitational waves from particle noise at small perturbation amplitude (item 7 of §7); the integrability condition of the periodic domain; gauge.

### 9.6 Track C: relativistic collapse of an SIDM core (S3)

**Goal.** First reproduce the instability threshold of collisionless relativistic clusters, then switch collisions on step by step and give the collapsed mass fraction as a function of Knudsen number.

**Pre-core work packages.**

- C-pre-1 A standalone prototype of the relativistic Monte Carlo collision operator (Minkowski box, CPU first, then Kokkos): isotropic elastic scattering in the centre-of-momentum frame, conserving four-momentum pair by pair. Tests: relaxation to the Maxwell–Jüttner distribution, collision rate, monotonic entropy increase, heat conduction at both the long and the short mean-free-path end.
- C-pre-2 The reproducible random-number interface (M11), proposed jointly with E.
- C-pre-3 Spherically symmetric baseline: reproduce the equilibrium sequence and the instability criterion of relativistic gravothermal evolution (arXiv:2108.11967, arXiv:2601.17117), at least up to the instability threshold.
- C-pre-4 Initial data: relativistic cluster equilibria close to the instability threshold (against arXiv:gr-qc/0601112, arXiv:2009.08163), output as particle samples; fix the conversion between Knudsen number and cross-section per unit mass.

**Work that depends on core.** The stability threshold of collisionless clusters; switching collisions on; the effect of rotation.

**Track-specific criteria.** G1: all tests of C-pre-1 pass; the baseline is reproduced. G2: the collisionless threshold reproduces the literature value with three-way convergence; once the collision module is in core, the budgets of conserved quantities close in curved spacetime. G3: the curve of mass fraction against Knudsen number, converged in collision time step and particle number.

**Provides.** The collision module (to core); the random-number interface. **Needs.** core-v0.1 and its relativistic-cluster test.

**Main risks.** The collision term is stiff in the short-mean-free-path regime; the choice of initial model can sway the conclusion; the relaxation time is far longer than the dynamical time, so the whole gravothermal process cannot be evolved.

### 9.7 Track D: black-hole growth and dark-matter dress (S4)

**Goal.** The growth law of a black hole accreting collisionless matter in a matter-dominated background, the shape of the density spike in the strong field, and the null test of "cosmological coupling"; then dressed black-hole binaries.

**Pre-core work packages.**

- D-pre-1 Exact-solution benchmark: cut a vacuum bubble at the centre of the expanding dust ball and put a black hole at its centre (a construction of Einstein–Straus type), with Schwarzschild still outside the ball. While the bubble wall is comoving, the black-hole mass is strictly constant, which gives the null test an exact reference. [Derivation to be checked]
- D-pre-2 The spike in the probe limit: integrate geodesics on Schwarzschild and Kerr backgrounds to obtain the adiabatically grown density profile, reproducing the known relativistic-spike results (arXiv:1305.2619).
- D-pre-3 Newtonian self-similar secondary infall: reproduce the r^(−9/4) profile and the growth of the dress mass (arXiv:1901.08528, arXiv:2106.07480), fixing the parameters of the full-NR runs.
- D-pre-4 A long evolution of a single puncture with public AthenaK: measure the numerical drift of the horizon mass without matter, as the noise floor of the null test.

**Work that depends on core.** Puncture plus expanding ball: growth law, spike, null test; dressed black-hole binaries.

**Track-specific criteria.** G1: derivation and offline check of D-pre-1; the baselines of D-pre-2 and D-pre-3; the noise floor of D-pre-4. G2: in the vacuum-bubble case the drift of the horizon mass does not exceed the noise floor; with matter filled in, the mass growth agrees with the integrated particle flux through the horizon. G3: three-way convergence of the growth law and the spike profile; the upper limit from the null test.

**Provides.** Initial data for dressed black holes (to F). **Needs.** core-v0.1; A's expanding-ball module; B's gauge for the periodic version.

**Main risks.** Particle resolution near the puncture; numerical relaxation of the dress; the null result holds only for ordinary black holes and has to be worded with restraint.

### 9.8 Track E: stochastic inflation (S11, if possible)

**Goal.** Pass the feasibility gate first, then decide how far to go.

**Pre-core work packages (none depends on core).**

- E-pre-1 Read arXiv:2401.08530, arXiv:2512.14649, arXiv:2610.32592 and arXiv:2502.06783 closely and write the reproduction specification: equations, window function, gauge, initial data, parameters and acceptance quantities of the two test cases.
- E-pre-2 Assessment of the code base (D4): add a minimally coupled scalar field and stochastic sources to AthenaK's Z4c, or build on GRChombo/GRTeclyn, which already have scalar fields. Assess effort, GPU performance, how much is shared with Track B, and support for a later field-to-particle hand-over.
- E-pre-3 Comparisons outside NR: a Langevin solver for stochastic δN (following arXiv:1308.4754, arXiv:2206.11234) and a stochastic-lattice comparison (arXiv:2405.10692), giving reference statistics for the same potential.
- E-pre-4 The random-number interface (M11), proposed jointly with C; generation and validation of coloured noise in a periodic box.

**Subsequent work.** Reproduce the slow-roll and USR cases; statistics of the compaction function; the field-to-particle hand-over (only here is core needed).

**Track-specific criteria.** G0 (feasibility gate): reproduction specification, code-base assessment and compute estimate are complete, and the group decides to continue, to shrink or to downgrade. G1: the power spectrum of the slow-roll case agrees with the analytic result, super-horizon modes freeze by the criterion of arXiv:2606.14853, the constraints converge. G2: the USR case is reproduced; sensitivity to window-function parameters and resolution. G3: tail statistics, compared with E-pre-3.

**Provides.** Statistics of large perturbations (to A); the random-number interface. **Needs.** B's periodic initial data and gauge, if built on AthenaK.

**Main risks and exit criteria.** See S11 in §5.

### 9.9 Track F: Hills mechanism (S12)

**Goal.** At a mass ratio of about 10, one scan line in pericentre distance each for a binary black hole and for a "binary of collisionless clumps".

**Pre-core work packages.**

- F-pre-1 Newtonian baseline: three-body scattering with REBOUND, reproducing the relation between separation probability and penetration factor and the scaling of the ejection energy of the restricted three-body problem (arXiv:0911.1136, arXiv:1201.4794, arXiv:1804.02911). Every later comparison uses it as the frame of reference.
- F-pre-2 Relativistic baseline: implement the "exact Schwarzschild acceleration plus Newtonian self-gravity" model and reproduce the results of arXiv:2404.16270; for Kerr follow arXiv:2402.02178.
- F-pre-3 Three-puncture vacuum NR: "binary black hole plus large black hole" with public AthenaK, with parameters in the range estimated in the last item of §3.11. It needs three-puncture initial data (M12): first assess the junk radiation of approximately superposed data, then decide whether to solve the constraints. This step needs no particles.
- F-pre-4 Diagnostics: puncture trajectories, an estimate of the binding energy of each member relative to the large black hole, wave extraction, horizon mass and spin.
- F-pre-5 Novelty search: confirm that no Hills-type full-NR calculation has been published (the item marked TO VERIFY in §3.11).

**Work that depends on core.** A binary of collisionless clumps passing a puncture (object b); a dressed black-hole binary (object c, needs D's initial data).

**Track-specific criteria.** G1: F-pre-1 and F-pre-2 reproduce the curves of the literature; constraint residuals and junk radiation of the three-puncture data are quantified; one complete vacuum passage is done. G2: at large pericentre distance the vacuum case returns to the results of the Newtonian and geodesic models and converges with resolution; the numerical relaxation time of an isolated collisionless clump is far longer than the encounter time. G3: three-way convergence of the two scan lines.

**Provides.** Three-body initial data and multi-body diagnostics (to core and D). **Needs.** core-v0.1 for objects b and c; A's horizon diagnostics; D's dressed initial data.

**Main risks.** See S12 in §5.

### 9.10 The knowledge-base track

The procedure is in §12 and its gate criteria in §12.10. The knowledge base does not wait for the other tracks, and they do not wait for it: until a snapshot is available, tracks read the source files in `kb-data/raw` directly, but no number without a locator may enter a note.

### 9.11 Priority when resources conflict

When compute or human review is queued, the order is: verification runs of core; Track A; the track closest to its next gate; production runs of Track E last. The pre-core packages use almost no GPU time and do not queue.

---

## 10. Verification and benchmark suite

The column "Owner" names who turns the test into an automated test and maintains it; the rows marked CORE form the verification ladder of core (C3 in §9.3).

| Test | What it checks | Reference | Owner |
|---|---|---|---|
| Geodesics on a fixed background | Order and conservation of the pusher | arXiv:1801.02378, arXiv:1710.09164 | CORE |
| Oppenheimer–Snyder collapse and its time reverse | Horizon formation; expanding-ball initial data | Exact solution; arXiv:1109.0546 | CORE (collapse), A (time reverse) |
| Oblate and prolate collapse | Three-dimensional caustics and horizons | arXiv:1611.07906, arXiv:1901.04498 | CORE, A |
| Spherically symmetric Einstein–Vlasov steady states and their stability threshold | Long-time phase-space fidelity | arXiv:gr-qc/0601112, arXiv:2009.08163, arXiv:2105.05556, arXiv:1707.08666 | CORE, C |
| Spherically symmetric critical collapse | Behaviour near threshold | arXiv:gr-qc/9804040, arXiv:gr-qc/0107076, arXiv:1409.5176 | C (optional) |
| FLRW dust (Einstein–de Sitter) | Background expansion, gauge, scaling of the time step | Exact solution; arXiv:1611.05447 | B |
| Growth of linear perturbations | Particle noise and convergence at small amplitude | Linear theory; arXiv:1611.05447, arXiv:2003.08014 | B |
| Linear gravitational waves in a periodic box | Gravitational-wave diagnostics | Analytic solution; arXiv:2111.09163 | B |
| Plane-symmetric pancake through shell crossing | Multi-stream region; the fluid fails while particles continue | In Newtonian theory the Zel'dovich solution is exact in plane symmetry up to shell crossing [BACKGROUND]; arXiv:1505.04756, arXiv:2010.12584 | B |
| Multi-code comparison (weak-field regime) | Consistency with gevolution, GRAMSES and fluid NR | arXiv:2003.08014, arXiv:1908.05683 | B |
| Lemaître–Tolman–Bondi spherically symmetric inhomogeneous dust | Nonlinear evolution before shell crossing | Exact solution | A |
| Szekeres-type dust solutions without symmetry | Nonlinear evolution without symmetry | Exact solution; arXiv:1708.09143 | A, B |
| Collisional relaxation in a Minkowski box | Collision operator: equilibrium distribution, conservation, heat conduction | Relativistic kinetic theory; arXiv:2602.17487 | C |
| Reproducible random numbers | Results independent of process count, block decomposition and restart position | Interface document `rng.md` | C, E |
| Self-similar secondary infall | Density profile of the virialized region | Newtonian self-similar solution | D |
| Black hole in a vacuum bubble (Einstein–Straus type) | Horizon mass does not change with the expansion | Exact solution [derivation to be checked] | D |
| Slow-roll and USR cases of stochastic inflation | Power spectrum; freezing of super-horizon modes | arXiv:2512.14649, arXiv:2606.14853 | E |
| Hills scattering in the restricted three-body problem | Scaling of separation probability and ejection energy | arXiv:0911.1136, arXiv:1804.02911 | F |
| Geodesic binary passing a Schwarzschild black hole | Approximate baseline for strong-field separation | arXiv:2404.16270 | F |
| Three-puncture vacuum evolution | Multi-body initial data, trajectories, waveform | arXiv:0710.0879, arXiv:1004.1353 | F |

---

## 11. Harness: context sharing and environment isolation

This section is the construction brief for the orchestrator: build all of it and pass the acceptance tests of §11.7 before the tracks start. The design itself is [JUDGEMENT]; every statement about the behaviour of Claude Code is marked [VERIFIED] and rests on the official documentation listed in §11.8.

**Two design principles.**

1. **Write only to your own branch; read through the git object store.** All worktrees share one `.git`. As soon as anything is committed on any branch, every other worktree can read it with `git show <branch>:<path>`, with no merge and without writing into anyone else's directory. Claude Code applies isolation checks to worktree sessions: it blocks edits to files in the main checkout, commands whose working directory lies in the main checkout, and git commands redirected into the main checkout [VERIFIED]. "Write only your own, read the others through git" is fully compatible with these checks.
2. **Files are the record; messages are only the doorbell.** A cross-session message can tell another session to go and look at a file, but it cannot replace the file and it cannot approve anything on the user's behalf [VERIFIED].

### 11.1 Directory layout

```text
$NRPIC_HOME/                          # one root per machine; its path is recorded in ~/.config/nrpic/home
├── repo/                             # MAIN CHECKOUT (branch main): orchestrator and integration only
│   ├── CLAUDE.md                     # <= 200 lines; imports coord/CHARTER.md and harness/RULES.md
│   ├── .claude/
│   │   ├── settings.json             # permissions, hooks, env (tracked, identical on every branch)
│   │   ├── rules/                    # git.md  numerics.md  writing.md  safety.md (path-scoped where useful)
│   │   ├── agents/                   # verifier.md  kb-librarian.md  figure-checker.md  upstream-watch.md
│   │   └── skills/                   # stage-check/  ctx/  run/  kb/   (project skills = slash commands)
│   ├── harness/
│   │   ├── bin/                      # nrpic-wt  nrpic-env  nrpic-run  nrpic-ctx  nrpic-stage  nrpic-doctor
│   │   ├── hooks/                    # session_start.sh  pre_tool_guard.py  stop_gate.sh
│   │   ├── env/                      # pyproject.toml  uv.lock  machines/<host>.sh  container/nrpic.def
│   │   ├── style/                    # czstyle.py  cyclic_zoom.mplstyle  paperfig.py  SHA256SUMS (vendored)
│   │   ├── templates/                # STATUS.md  JOURNAL.md  HANDOFF.md  ADR.md  run_manifest.json  STAGE_REPORT.md
│   │   └── tests/                    # harness self-tests, run by nrpic-doctor
│   ├── coord/                        # owned by the orchestrator; tracks read it and never write it
│   │   ├── CHARTER.md                # goals, track list, gate table, budgets, decisions D1-D7
│   │   ├── BOARD.md                  # generated by `nrpic-ctx board` from all track branches
│   │   ├── DECISIONS/NNNN-slug.md    # accepted proposals (ADR format)
│   │   ├── INTERFACES/               # deposit.md  pusher.md  cosmo_gauge.md  rng.md  diagnostics.md  run_manifest.md
│   │   ├── NOTATION.md  GLOSSARY.md  # project-wide notation, upstream of every track's NOTATION.md
│   │   └── digests/YYYY-Www.md       # weekly cross-track digest
│   ├── kb/                           # knowledge-base tools, schema, manifests, tests (data lives in kb-data/)
│   ├── src/  inputs/  kokkos/  ...   # AthenaK fork, if decision D1 = fork-as-monorepo
│   └── tracks/<ID>/                  # present on every branch; each track writes ONLY its own directory
│       ├── STATUS.md  JOURNAL.md  HANDOFF.md  RISKS.md  OWNERSHIP
│       ├── outbox/                   # messages and proposals addressed to other tracks or the orchestrator
│       ├── runs/<run_id>/manifest.json
│       ├── analysis/  notes/  stage/G<k>/
│       ├── WRITING_GUIDE.md  NOTATION.md
│       └── note/                     # REVTeX working note: main.tex  sections/  figures/  scripts/  supplement.tex
├── wt/                               # LINKED WORKTREES, one per owner (created by nrpic-wt)
│   ├── core/         -> branch core/nrpic
│   ├── kb/           -> branch kb/main
│   ├── A-emd-pbh/    -> branch track/A-emd-pbh
│   ├── B-emd-gw/     -> branch track/B-emd-gw
│   ├── C-sidm/       -> branch track/C-sidm
│   ├── D-bh-dress/   -> branch track/D-bh-dress
│   ├── E-stoch-inf/  -> branch track/E-stoch-inf
│   └── F-hills/      -> branch track/F-hills
├── kb-data/                          # raw sources, parsed text, SQLite, embeddings (NOT in git; checksummed)
├── scratch/<ID>/<run_id>/            # simulation output (NOT in git; checksummed in run manifests)
├── cache/                            # ccache, Kokkos installs keyed by hash, uv cache (content-addressed)
└── locks/                            # gpu<N>.lock  kb-writer.lock
```

Ownership: `coord/`, `harness/`, `.claude/` and `kb/` belong to the orchestrator and the knowledge-base session and change only on main (or kb/main); `tracks/<ID>/` belongs to its track and changes only on that track's branch; the shared part of the AthenaK source belongs to core, and the problem generators and input files specific to a track are listed in `tracks/<ID>/OWNERSHIP`.

### 11.2 Creating the worktrees and starting sessions

```bash
# One-time, from the main checkout ($NRPIC_HOME/repo) on branch main with a clean tree.
# nrpic-wt wraps exactly these commands; they are shown so that the result can be checked by hand.
git worktree add -b core/nrpic ../wt/core main
git worktree add -b kb/main    ../wt/kb   main
for t in A-emd-pbh B-emd-gw C-sidm D-bh-dress E-stoch-inf F-hills; do
  git worktree add -b "track/$t" "../wt/$t" main
done
git worktree list                      # expect nine entries: repo + eight linked worktrees

# Per worktree: environment bootstrap. build/ and .venv/ are never shared or symlinked between worktrees.
cd "$NRPIC_HOME/wt/A-emd-pbh"
harness/bin/nrpic-env create           # .venv from the branch's uv.lock, machine file, .env.track
harness/bin/nrpic-doctor               # isolation self-test; must print PASS for every row of the isolation table

# One named Claude Code session per worktree (separate terminals, or background sessions).
cd "$NRPIC_HOME/wt/A-emd-pbh" && claude --name track-A --add-dir "$NRPIC_HOME/kb-data"
cd "$NRPIC_HOME/wt/A-emd-pbh" && claude --bg --name track-A "Read tracks/A-emd-pbh/HANDOFF.md and continue."

# Housekeeping (orchestrator only, after asking the user).
git worktree list
git worktree remove "../wt/$ID"        # only for a retired track $ID; its branch and tags stay
```

Points to note:

- **Why the worktrees are created by hand.** `claude --worktree <name>` puts the worktree under `.claude/worktrees/<name>/`, fixes the branch name to `worktree-<name>`, and can only base it on the remote default branch or on the current HEAD, not on a chosen existing branch [VERIFIED]. Here the branch names and a location outside the repository are prescribed, so `git worktree add` is used. Worktrees you create yourself are not removed by Claude Code's periodic clean-up [VERIFIED].
- **A new worktree is a fresh checkout.** Untracked files do not come along. `.worktreeinclude` applies only to worktrees that Claude Code itself creates [VERIFIED], so machine-specific files are copied explicitly by `nrpic-wt`.
- **Session names.** Every session gets a name with `--name` (track-A, core, kb, orch), used by `/list-agents` and for addressing cross-session messages [VERIFIED].
- **Background sessions.** A background session started from inside a linked worktree stays there and is not moved into another isolated worktree [VERIFIED].
- **One writing session per worktree at a time.** For parallelism inside a track, use subagents or open another temporary worktree.

### 11.3 Context-sharing protocol

Every owner maintains four files and an outbox:

```text
tracks/<ID>/STATUS.md        (<= 60 lines, rewritten at the end of every session; the board is built from it)
  gate:        G1 in progress | G1 package submitted 2026-12-03 | ...
  headline:    one sentence on the current state of knowledge
  last-result: what was established last, with run ids / KB locators
  next:        the next three actions, most important first
  blockers:    what stops progress, and who can remove it
  needs:       requests to other tracks or to core (each one also exists as an outbox file)
  offers:      modules, data or results other tracks can already use (path + commit)
  budget:      GPU-hours used / allotted

tracks/<ID>/JOURNAL.md       (append-only, newest at the bottom; one entry per session)
  ## 2026-11-20T18:40Z  session track-A  commits 3f9c2ab..7d1e0c4  runs A-20261120-143015-3f9c2ab
  did / found / evidence / changed my mind about / open

tracks/<ID>/HANDOFF.md       (rewritten for a reader with no memory of the session)
  state in three lines; exact command to run next; files to read first; decisions pending; traps

tracks/<ID>/outbox/20261120T1840Z__to-core__deposit-order.md
  ---
  from: A-emd-pbh
  to: core                    # a track id, core, kb, orch, or all
  type: request               # info | request | proposal | interface-change | blocker | kb-request
  needs_reply_by: 2026-11-27
  refs: [arXiv:2611.12831, run:A-20261120-143015-3f9c2ab]
  ---
  body: what is asked or announced, why, the evidence, the smallest acceptable answer

tracks/<ID>/OWNERSHIP        (one glob per line: source paths outside tracks/<ID>/ that this track may edit)
  src/pgen/trackA_*.cpp
  inputs/trackA/**
```

Rules:

1. **Writing.** Each owner writes only `tracks/<ID>/**` and the source paths listed in OWNERSHIP, and commits only on its own branch.
2. **Reading others.** `nrpic-ctx show <ID> [file]` reads a file at the tip of another branch; `nrpic-ctx board` collects the STATUS of all branches; `nrpic-ctx inbox` lists the messages in other branches' outboxes that are addressed to me or to all and that I have not yet acknowledged. Acknowledgements are recorded in my own `tracks/<ID>/inbox_acks.txt`.
3. **Shared content flows downwards.** Shared directories change only on main. Every track runs `nrpic-ctx sync` at the start of each session, merging main into its branch. Tracks do not touch shared paths, so this merge cannot conflict; a conflict means someone crossed a boundary.
4. **Proposals flow upwards.** To change shared content or core, write a file of type proposal into the outbox; where code is involved, also open a branch `proposal/<ID>/<slug>`. Once accepted it becomes `coord/DECISIONS/NNNN-*.md` or is merged into core, and reaches everyone with the next sync.
5. **Code moves only through main.** Tracks do not cherry-pick from one another. Core releases, the release is merged into main, the tracks sync.
6. **Injection at session start.** The SessionStart hook prints the output of `nrpic-ctx brief` to standard output: who I am, which gate I am at, the summary of STATUS, the number of inbox items, how many commits main is ahead, in at most 40 lines. Claude Code adds this output to the context [VERIFIED].
7. **Persisting at session end.** Rewrite STATUS.md, append to JOURNAL.md, rewrite HANDOFF.md, commit. The Stop hook enforces it (§11.5).
8. **Live doorbell (optional).** Named sessions on the same machine can alert one another with Claude Code's cross-session messaging, which requires version 2.1.224 or later. A message is plain text; the receiver knows it comes from another session and not from the user, and it can neither answer a permission prompt nor make the receiver change configuration [VERIFIED]. An unattended `-p` worker that should receive messages must be started with `crossSessionInbound` set to `accept` in its `--settings` [VERIFIED].
9. **Weekly digest.** The orchestrator runs `nrpic-ctx digest` and writes `coord/digests/YYYY-Www.md`: each track's gate, results and blockers, and whether cross-track requests have been picked up.

**Reference implementation of the read side.** The following was tested on 2026-11-15 with git 2.43 in a scratch repository with five owners [VERIFIED]: each message appears exactly once, with no merge and no write across worktrees.

```bash
# Reference implementation of the read side of nrpic-ctx. Plain git, no merge, no write outside the own worktree.
owner_of() {   # branch name -> owner id
  case "$1" in track/*) echo "${1#track/}";; core/*) echo core;; kb/*) echo kb;; main) echo orch;; *) return 1;; esac
}
me=$(git rev-parse --abbrev-ref HEAD); my_id=$(owner_of "$me")

# show: one file at the tip of another owner's branch
git show "track/B-emd-gw:tracks/B-emd-gw/STATUS.md"

# inbox: outbox files of the other owners that are addressed to me or to all.
# Only each branch's OWN directory is scanned; copies of other owners' files that arrived through main are stale.
git for-each-ref --format='%(refname:short)' refs/heads/track refs/heads/core refs/heads/kb refs/heads/main |
while read -r br; do
  id=$(owner_of "$br") || continue
  [ "$br" = "$me" ] && continue
  git ls-tree -r --name-only "$br" -- "tracks/$id/outbox" 2>/dev/null |
    grep -E "__to-($my_id|all)__" | sed "s|^|$br:|"
done

# sync: shared content from main into the own branch (cannot conflict while nobody edits shared paths)
git merge --no-edit main

# Empty directories are not tracked by git: seed outbox/, runs/, notes/ with a .gitkeep, and let
# `nrpic-ctx post` and `nrpic-run` create directories on demand.
```

**Why agent teams are not used.** They are an experimental feature; a session has exactly one team, and teams cannot be nested; resuming a session does not restore in-process teammates; no teammates are spawned in non-interactive mode [VERIFIED]. Six long-running tracks are better served by "one independent named session per worktree". Subagents are kept for short tasks inside a track (independent verification, literature look-ups): a subagent does not inherit the conversation history, nesting is limited to three levels by default, and `isolation: worktree` gives it a temporary worktree [VERIFIED].

### 11.4 Environment isolation

| Resource | How it is isolated | Shared between tracks? |
|---|---|---|
| Source tree | One git worktree per owner | No |
| Build products | A `build/` of its own in each worktree, out-of-source, no symbolic links | No; ccache is content-addressed and may be shared |
| Python environment | A `.venv/` of its own in each worktree, generated from that branch's `uv.lock` | No; uv's download cache may be shared |
| Compiler, MPI, CUDA, HDF5 | `harness/env/machines/<host>.sh`, or a container image pinned by digest | Shared read-only |
| Kokkos and other third-party code | Pinned to commit hashes; pre-built products under `cache/` in directories named by hash | Shared read-only |
| Run output | `scratch/<ID>/<run_id>/` | No |
| GPUs and jobs | Slots allocated by file locks, or left to Slurm; job names carry the track prefix | Arbitrated |
| Knowledge base | `kb-data/` is read-only for tracks; only the kb session writes | Shared read-only |
| Claude Code sessions | One named session per worktree; the isolation checks protect the main checkout | — |
| Claude Code auto memory | All worktrees of one repository share one directory [VERIFIED]; off by default (D7) | Off |
| Permission approvals | A "don't ask again" approval is saved in the main checkout's `.claude/settings.local.json` and applies to all worktrees [VERIFIED] | Shared, so approve with care |

Additional rules:

- Builds and runs always go through `nrpic-env exec -- <command>` and never rely on shell state left over in a session. The SessionStart hook may write variables into `CLAUDE_ENV_FILE` for later Bash calls (the events that support this variable are SessionStart, Setup, CwdChanged and FileChanged) [VERIFIED]; this is a convenience, not a means of isolation.
- Claude Code itself runs on the host, and containers wrap only builds and runs. The reason: a session inside a container and a session on the host cannot reach each other with cross-session messages [VERIFIED].
- A track may add Python dependencies on its own branch; upgrading a shared pinned version needs a proposal.
- The identity of an environment is one hash: the sha256 of the machine file, of `uv.lock` and of the container digest combined. Every run manifest records it.

`nrpic-doctor` must verify, item by item, that the isolation really holds:

```text
nrpic-doctor, run inside a track worktree, must print PASS for each line:
  [wt]      `git rev-parse --show-toplevel` equals $NRPIC_HOME/wt/<ID>; branch equals track/<ID>
  [build]   build/ exists only inside this worktree; no symlink in the worktree points into another worktree or into repo/
  [venv]    `python -c "import sys; print(sys.prefix)"` (via nrpic-env exec) is this worktree's .venv; uv.lock hash recorded
  [env]     NRPIC_TRACK, NRPIC_WT, NRPIC_SCRATCH, NRPIC_KB are set by nrpic-env and point to this track's paths
  [scratch] a write to scratch/<ID>/ succeeds; a write to scratch/<other>/ is refused by the guard
  [guard]   an Edit of coord/CHARTER.md, harness/bin/nrpic-run or tracks/<other>/STATUS.md is denied with a reason
  [main]    an Edit of a file in $NRPIC_HOME/repo is refused (Claude Code worktree isolation)
  [kb]      `kb status` works read-only; an attempt to open kb.sqlite for writing fails
  [gpu]     nrpic-run acquires and releases a slot; two concurrent runs never share one
  [ctx]     `nrpic-ctx board` lists every owner; a test outbox message on another branch shows up in `nrpic-ctx inbox`
  [git]     the tree is clean; pre-commit hooks are installed; a 6 MB file and a fake secret are both rejected at commit
  [stop]    with a dirty tree the Stop gate blocks once with instructions, then lets the turn end after the commit
```

### 11.5 Claude Code configuration: permissions, hooks, instruction files

`.claude/settings.json` (tracked, identical on all branches):

```json
{
  "autoMemoryEnabled": false,
  "env": { "NRPIC_HARNESS": "1" },
  "permissions": {
    "allow": [
      "Bash(harness/bin/nrpic-ctx *)",
      "Bash(harness/bin/nrpic-env *)",
      "Bash(harness/bin/nrpic-run *)",
      "Bash(harness/bin/nrpic-stage *)",
      "Bash(harness/bin/nrpic-doctor *)",
      "Bash(git status *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git show *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git tag *)",
      "Bash(git merge --no-edit main)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(git rebase *)",
      "Bash(git reset *)",
      "Bash(git checkout *)",
      "Bash(rm -r *)",
      "Bash(sbatch *)"
    ],
    "deny": [
      "Bash(git push --force *)",
      "Bash(git push -f *)",
      "Bash(git commit --no-verify *)",
      "Bash(git worktree remove *)",
      "Bash(git branch -D *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Read(./.env)",
      "Read(./**/*.pem)"
    ]
  },
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/harness/hooks/session_start.sh" } ] }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit|Bash",
        "hooks": [ { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/harness/hooks/pre_tool_guard.py" } ]
      }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/harness/hooks/stop_gate.sh" } ] }
    ]
  }
}
```

Notes:

- Permission rules are evaluated in the order deny, ask, allow, and the first match decides; an allow rule cannot carve an exception out of a deny rule [VERIFIED].
- Bash rules match the text of the command. The official documentation says explicitly that patterns trying to constrain arguments are fragile; a rule for `git push`, for example, does not reach `git -C . push` [VERIFIED]. The real boundaries therefore rest on three things: the worktree isolation checks, the PreToolUse guard script, and a sandbox where available.
- `git push` is under ask as the default of decision D3.
- **`session_start.sh`.** Takes `cwd` from the JSON on standard input, determines the owner from the branch name, prints `nrpic-ctx brief`; if `CLAUDE_ENV_FILE` exists it writes `NRPIC_TRACK` and the other variables into it.
- **`pre_tool_guard.py`.** For Edit, Write and NotebookEdit: deny when the target path is outside this owner's paths, and say in the reason how to make a proposal instead. For Bash: deny force pushes, `--no-verify`, writes into another track's scratch, and starting a simulation without `nrpic-run`. Denial is expressed by printing JSON with `hookSpecificOutput.permissionDecision` set to `deny` and a reason [VERIFIED].
- **`stop_gate.sh`.** If the worktree is not clean, or STATUS.md is older than the last code commit, exit with code 2 and say on standard error what has to be done; exit code 2 blocks the Stop event [VERIFIED]. Guard against loops: once it has blocked in a turn, let the next attempt pass. The hooks reference has an input field for this; I did not read that part, [TO VERIFY].
- `${CLAUDE_PROJECT_DIR}` in a hook command is the project root where the session started; for a session started in a worktree directory it is that worktree. The `cwd` in the hook input follows Claude's current directory [VERIFIED].
- **Instruction files.** Each CLAUDE.md should stay under 200 lines; `@path` imports nest at most four levels deep; a CLAUDE.md in a subdirectory loads only when Claude reads a file in that directory; `.claude/rules/*.md` can be restricted with `paths` [VERIFIED]. Accordingly the root CLAUDE.md holds only global rules and imports `coord/CHARTER.md`, and the rules specific to a track live in `tracks/<ID>/CLAUDE.md`.
- **Subagents.** Definitions go into `.claude/agents/`. At least a verifier is needed: read-only tools and a restricted Bash, with the task of recomputing numbers from the manifests alone, without having seen how they were produced.
- **Skills.** Project skills live in `.claude/skills/<name>/SKILL.md`, and the directory name is the slash command; `disable-model-invocation: true` makes a skill invocable only by a person [VERIFIED]. Skills synced from the account are in `~/.claude/skills/synced/` [VERIFIED], so `/paper-writing`, `/sleep-paper-figure-style` and `/zoom-figure-style` are available to the session of every worktree and need not be copied into the repository.

### 11.6 Specification of the harness commands

| Command | Purpose | Must satisfy |
|---|---|---|
| `nrpic-wt new\|list\|retire` | Create, list, retire worktrees | Branches and paths as in §11.1; before retiring, confirm that the work is pushed or tagged |
| `nrpic-env create\|exec\|hash` | Create the environment; run a command inside it; print the environment hash | Same behaviour in every worktree; does not read the caller's environment variables |
| `nrpic-run submit\|status\|finish` | Register and start a run; query; close | Refuses a dirty worktree; writes and commits the manifest before starting; afterwards writes checksums, updates and commits the manifest; refuses runs beyond the CHARTER budget |
| `nrpic-ctx sync\|brief\|board\|show\|inbox\|ack\|post\|digest\|audit` | All read and write operations of §11.3 | Writes only on the own branch; reads others through git only |
| `nrpic-stage collect\|verify\|report` | The three harness steps of the stage check (§13.3) | verify re-runs on a clean checkout |
| `nrpic-doctor` | Self-test of isolation and configuration | Every item of the list in §11.4 passes |

Format of the run manifest (`coord/INTERFACES/run_manifest.md` defines the fields):

```json
{
  "run_id": "A-20261120-143015-3f9c2ab",
  "track": "A-emd-pbh",
  "gate": "G2",
  "purpose": "spherical expanding ball, turnaround and collapse, resolution level 3 of 4",
  "preregistered_in": "tracks/A-emd-pbh/stage/G2/PLAN.md#scan-1",
  "git": { "sha": "3f9c2ab0…", "branch": "track/A-emd-pbh", "dirty": false, "merge_base_main": "91c0de4…" },
  "code": { "core_tag": "core-v0.1", "athenak_upstream_sha": "c5a0d7f…", "kokkos_sha": "…",
            "problem": "trackA_expanding_ball", "cmake_flags": ["-DKokkos_ENABLE_CUDA=ON"] },
  "env":  { "host": "…", "machine_file_sha256": "…", "uv_lock_sha256": "…", "container_digest": null,
            "compiler": "…", "mpi": "…", "gpu": "…" },
  "input": { "file": "inputs/trackA/ball_sph_l3.athinput", "sha256": "…", "overrides": { "mesh/nx1": 256 } },
  "resources": { "nodes": 1, "gpus": 1, "walltime_s": 13820, "particles": 5.0e7 },
  "outputs": { "dir": "scratch/A-emd-pbh/A-20261120-143015-3f9c2ab", "sha256sums": "sha256sums.txt", "bytes": 81234567890 },
  "status": "completed",
  "exit_code": 0,
  "started": "2026-11-20T14:30:15Z",
  "ended": "2026-11-20T18:20:35Z",
  "parents": [],
  "notes": ""
}
```

### 11.7 Acceptance tests

The harness counts as built when all of the following hold:

1. `nrpic-doctor` passes in all eight worktrees.
2. **Context round trip.** A message addressed to B is committed on A's branch; it appears in the start-up brief of B's next session; B acknowledges it; A's board shows the acknowledgement. No file is written across worktrees at any point.
3. **Proposal round trip.** A submits an interface-change proposal; the orchestrator accepts it and writes it into DECISIONS; after sync every track can read it.
4. **Run registration.** A 30-second dummy run goes through `nrpic-run`, its manifest is committed and the checksums of its output can be re-verified; a dirty worktree is refused.
5. **Destructive test.** From A's session, attempts to edit the main checkout, to edit B's directory, to write into B's scratch and to force-push are all refused with a reason.
6. **Stage-check rehearsal.** `/stage-check` runs to completion on a dummy track, producing the note PDF, two schematics, one data figure, the report and the tag.
7. **Cold start.** With all sessions closed, a new session can say what to do next from HANDOFF.md and `nrpic-ctx brief` alone.

### 11.8 The Claude Code documentation relied on

Read on 2026-11-15. Only part of the hooks reference page was read: the input fields of Stop and WorktreeCreate were not. After a version update, the behaviour on your machine takes precedence.

- Worktrees: `https://code.claude.com/docs/en/worktrees`
- Cross-session messaging: `https://code.claude.com/docs/en/cross-session-messaging`
- Subagents: `https://code.claude.com/docs/en/sub-agents`
- Skills: `https://code.claude.com/docs/en/skills`
- Hooks: `https://code.claude.com/docs/en/hooks`
- Instruction files and auto memory: `https://code.claude.com/docs/en/memory`
- Permissions: `https://code.claude.com/docs/en/permissions`
- Non-interactive mode: `https://code.claude.com/docs/en/headless`
- Agent teams: `https://code.claude.com/docs/en/agent-teams`
- Background sessions: `https://code.claude.com/docs/en/agent-view`

---

## 12. Building the knowledge base (after the arXiv sources and the GitHub code have been downloaded)

Precondition: both manifests of §17 have been downloaded, the arXiv e-prints into `kb-data/raw/arxiv/` and the repositories into `kb-data/raw/github/`. This section is written for the knowledge-base session; other sessions need only §12.1 and §12.10. The design is [JUDGEMENT].

### 12.1 Goals and principles

The knowledge base has to answer four kinds of question, and every answer carries a locator (paper, section, equation or figure number, character range):

1. where exactly in which paper a statement comes from;
2. who cites whom, and in what context;
3. in which function of which code an equation or algorithm is implemented;
4. how far each labelled statement of this document has been verified so far.

Principles:

- Raw files are read-only and untrusted; all derived data can be rebuilt; the database is a derived product.
- Every record can be traced to a source file, a character range and a tool version.
- Retrieval is hybrid: full-text index, vector neighbours and structured filters together.
- The text of the papers does not leave the machine; the embedding model runs locally.
- One writer, many readers; readers use read-only snapshots.
- The licences of arXiv sources vary, so the knowledge base is for the group's internal use only and neither original text nor large derived passages are redistributed. Repositories are recorded with their SPDX licence; a repository without a licence is indexed only, and no code fragment from it is copied into notes.

### 12.2 Layout and database schema

```text
$NRPIC_HOME/kb-data/                       # NOT in git; single writer = the kb worktree session
├── raw/
│   ├── arxiv/<id_>/<vN>/                  # <id_> = arXiv id with "/" replaced by "_" ; vN = version actually downloaded
│   │   ├── source.bin                     # the e-print exactly as downloaded (tar.gz, gz or single TeX); read-only
│   │   ├── source.pdf                     # only when no TeX source exists
│   │   └── src/                           # safe extraction of source.bin; never executed, never compiled in place
│   └── github/<owner>__<repo>/            # checkout at the pinned commit; read-only
├── meta/
│   ├── arxiv/<id_>.json                   # arXiv + INSPIRE metadata, license, download record, sha256
│   └── github/<owner>__<repo>.json        # url, commit sha + date, default branch, SPDX license, size, role
├── build/
│   ├── tex/<id_>/flat.tex                 # flattened, comment-stripped main file
│   ├── tex/<id_>/doc.json                 # sections, chunks, equations, figures, bib entries, citations, macros
│   └── code/<owner>__<repo>/{files,symbols,params}.jsonl
├── db/
│   ├── kb.sqlite                          # the working database (WAL); schema in kb/schema.sql
│   ├── kb-YYYYMMDD-<sha>.sqlite           # frozen read-only snapshots
│   └── current -> kb-YYYYMMDD-<sha>.sqlite
├── manifests/{arxiv.tsv,github.tsv,SHA256SUMS}
└── logs/

$NRPIC_HOME/repo/kb/                       # in git (branch kb/main, merged to main)
├── pyproject.toml  uv.lock                # the KB tool environment (separate from the simulation environment)
├── schema.sql  migrations/
├── kbtool/                                # download check, extract, flatten, parse, resolve, embed, index, query, qa
├── golden/questions.yaml                  # retrieval test set with expected paper ids and locators
├── curated/{paper_code_links.tsv,equation_tags.yaml,seed_claims.jsonl}
├── tests/
└── QA_REPORT.md  STATE.json               # regenerated by `kb qa run` and `kb status --json`; committed after each stage
```

Database schema (SQLite; `kb/schema.sql`):

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE schema_version(version INTEGER NOT NULL, applied_at TEXT NOT NULL);

-- ---------- papers ----------
CREATE TABLE papers(
  paper_id TEXT PRIMARY KEY,              -- arXiv id: '2611.12831' or 'gr-qc/9804040'
  title TEXT NOT NULL, authors_json TEXT, abstract TEXT, primary_class TEXT,
  grp TEXT, priority INTEGER,             -- group code (G01...) and priority (3/2/1) from the manifest of this brief
  version TEXT, submitted TEXT, updated TEXT, doi TEXT, inspire_recid INTEGER, journal_ref TEXT, license TEXT,
  source_kind TEXT CHECK(source_kind IN ('tex','pdf','none')),
  main_tex TEXT, parse_status TEXT, parse_score REAL, sha256 TEXT, ingested_at TEXT,
  brief_title TEXT, brief_authors TEXT, title_matches_brief INTEGER);   -- cross-check against the brief
CREATE TABLE sections(
  section_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, parent_id INTEGER,
  level INTEGER, number TEXT, title TEXT, label TEXT, char_start INTEGER, char_end INTEGER);
CREATE TABLE chunks(
  chunk_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, section_id INTEGER REFERENCES sections,
  kind TEXT CHECK(kind IN ('abstract','body','caption','footnote','appendix','comment')),
  text TEXT NOT NULL, tex TEXT, n_tokens INTEGER, char_start INTEGER, char_end INTEGER);
CREATE VIRTUAL TABLE chunks_fts USING fts5(text, content='chunks', content_rowid='chunk_id', tokenize='porter unicode61');
CREATE TABLE equations(
  eq_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, section_id INTEGER REFERENCES sections,
  env TEXT, label TEXT, number TEXT, tex_raw TEXT NOT NULL, tex_norm TEXT, symbols_json TEXT, context TEXT, tags_json TEXT);
CREATE VIRTUAL TABLE equations_fts USING fts5(tex_norm, context, content='equations', content_rowid='eq_id');
CREATE TABLE figures(
  fig_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, label TEXT, number TEXT, caption TEXT, files_json TEXT);

-- ---------- bibliography and citation graph ----------
CREATE TABLE bib_entries(
  bib_id INTEGER PRIMARY KEY, paper_id TEXT NOT NULL REFERENCES papers, cite_key TEXT, raw TEXT,
  target_arxiv TEXT, target_doi TEXT, target_recid INTEGER, resolved_by TEXT, confidence REAL);
CREATE TABLE citations(
  cit_id INTEGER PRIMARY KEY, citing TEXT NOT NULL REFERENCES papers, cited_arxiv TEXT, cited_doi TEXT,
  bib_id INTEGER REFERENCES bib_entries, chunk_id INTEGER REFERENCES chunks, context TEXT, in_corpus INTEGER);
CREATE INDEX citations_cited ON citations(cited_arxiv);

-- ---------- code ----------
CREATE TABLE repos(
  repo_id TEXT PRIMARY KEY,               -- 'owner/name'
  url TEXT, commit_sha TEXT, commit_date TEXT, default_branch TEXT, license_spdx TEXT, role TEXT,
  paper_ids_json TEXT, branches_json TEXT, ingested_at TEXT);
CREATE TABLE code_files(
  file_id INTEGER PRIMARY KEY, repo_id TEXT NOT NULL REFERENCES repos, path TEXT, lang TEXT, loc INTEGER, sha256 TEXT);
CREATE TABLE symbols(
  sym_id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL REFERENCES code_files, name TEXT, qualname TEXT,
  kind TEXT, signature TEXT, line_start INTEGER, line_end INTEGER, doc TEXT);
CREATE TABLE code_chunks(
  cc_id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL REFERENCES code_files, sym_id INTEGER REFERENCES symbols,
  text TEXT NOT NULL, line_start INTEGER, line_end INTEGER);
CREATE VIRTUAL TABLE code_fts USING fts5(text, content='code_chunks', content_rowid='cc_id', tokenize='unicode61');
CREATE TABLE params(                       -- runtime parameters read by a code (e.g. AthenaK input blocks)
  param_id INTEGER PRIMARY KEY, repo_id TEXT NOT NULL REFERENCES repos, block TEXT, name TEXT, type TEXT,
  default_value TEXT, file_id INTEGER REFERENCES code_files, line INTEGER);

-- ---------- links, claims, embeddings, provenance ----------
CREATE TABLE impl_links(                   -- "symbol S implements equation E of paper P"
  link_id INTEGER PRIMARY KEY, paper_id TEXT, eq_id INTEGER, repo_id TEXT, sym_id INTEGER, relation TEXT,
  status TEXT CHECK(status IN ('claimed','verified','refuted')), evidence TEXT, by_owner TEXT, at TEXT);
CREATE TABLE claims(
  claim_id INTEGER PRIMARY KEY, text TEXT NOT NULL,
  kind TEXT CHECK(kind IN ('result','method','limitation','open_question','number','definition')),
  paper_id TEXT, locator TEXT, chunk_id INTEGER, quote_start INTEGER, quote_end INTEGER,
  label TEXT CHECK(label IN ('fulltext','abstract','title_only','background','judgement','to_verify','refuted')),
  origin TEXT, track_tags TEXT, verified_by TEXT, verified_at TEXT, supersedes INTEGER);
CREATE TABLE embeddings(                   -- float32 blobs are the source of truth; ANN indexes are rebuilt from them
  owner_kind TEXT CHECK(owner_kind IN ('chunk','equation','code_chunk','claim')),
  owner_id INTEGER, model TEXT, dim INTEGER, vec BLOB, PRIMARY KEY(owner_kind, owner_id, model));
CREATE TABLE ingest_log(
  log_id INTEGER PRIMARY KEY, at TEXT, step TEXT, target TEXT, status TEXT, message TEXT, tool_version TEXT);
```

### 12.3 K0–K1: tool environment, inventory and checks

**K0.** Create the directories and the tool environment. Candidate tools: pylatexenc, TexSoup, bibtexparser, LaTeXML or pandoc, sqlite-vec or faiss or lancedb, sentence-transformers, tree-sitter, universal-ctags, typer, pydantic, rapidfuzz, tenacity, duckdb, networkx. All these packages and repositories were confirmed to exist on 2026-11-15 [VERIFIED]; which to use is your choice, with the reasons recorded in JOURNAL.

**K1.** `kb verify-downloads` has to do all of the following:

- Compare with the manifests and list what is missing and what is extra.
- Identify the file type from the content, not the extension: gzip-compressed tar, gzip-compressed single TeX file, PDF. Record `source_kind`.
- Record the version actually downloaded. The e-print endpoint serves the latest version; take the version number from the arXiv metadata.
- Compute sha256 and write `manifests/SHA256SUMS`.
- Extract safely into `src/`: refuse absolute paths, `..`, symbolic links and device files; limit the size of single files and of the total.
- Repositories: record commit hash, commit date, default branch and licence. For AthenaK also store the names and tip commits of all remote branches, for the upstream watch.
- Metadata: title, authors, abstract, categories, version and licence from the arXiv API (one request every 3 seconds); record number, DOI and journal information from INSPIRE. Compare title and authors entry by entry with §16 of this document and write the outcome into `papers.title_matches_brief` and the QA report. Where they differ, the downloaded data win.
- A pitfall of INSPIRE [VERIFIED; met during this survey]: a malformed query raises no error and returns the whole database instead, with `hits.total` around 1.9 million. Check `hits.total` on every query and confirm that the set of identifiers returned equals the set requested. Querying `eprint <id>` one at a time or in small batches is the most reliable.

### 12.4 K2: TeX normalization and structure extraction

1. **Find the main file.** The file containing both `\documentclass` and `\begin{document}`; with several candidates, use the hints in `00README`, which file is `\input` by which, and file size.
2. **Flatten.** Expand `\input`, `\include`, `\subfile` and `\import` recursively, keeping a source map: which line of which file each piece of text came from.
3. **Comments.** Strip them from the body and store them separately as chunks of `kind='comment'`, excluded from retrieval by default. Comments often contain deleted passages and have low reliability.
4. **Macros.** Collect `\newcommand`, `\def` and `\DeclareMathOperator`, and expand them at the text level only, for equation normalization. Do not execute TeX.
5. **Extract.** Title, authors, abstract; the section tree (number, title, label); equations (equation, align, gather, multline, eqnarray, `\[ \]`, `$$`), storing for each the raw text, the normalized text, label, number, enclosing section, and two sentences of context on either side; caption, file names and label of figures and tables; footnotes; appendices; the sentence around every `\cite`.
6. **Convert to plain text.** Prefer LaTeXML to XML with mathematics, fall back to pylatexenc; if both fail the paper goes on the failure list. Papers with PDF only get PDF text extraction, are marked `source_kind='pdf'`, and have an empty equation index.
7. **Chunk.** By paragraph, targeting 200–400 tokens with about 15% overlap; never cut inside an equation; each chunk records its section and character range.
8. **Quality score.** Number of sections, number of equations, fraction of unresolved macros, similarity between the extracted abstract and the abstract in the metadata. Papers below threshold go on a list for manual review.

Never: run `latex`, `make`, `python` or any script inside an extracted directory. If compilation is really needed, copy the sources into a container without network access and compile with shell escape disabled.

### 12.5 K3: bibliography resolution and the citation graph

- Order of preference of sources: `.bbl`, then `.bib`, then the `thebibliography` environment.
- From each entry extract the arXiv identifier (new and old format), the DOI and the `eprint` field. Where none is found, match through INSPIRE by DOI or by fuzzy title, store the confidence, and draw no edge when the confidence is low.
- The `citations` table stores citing paper, cited paper, context sentence and chunk; `in_corpus` marks whether the cited paper is in the base.
- `kb frontier` lists papers cited many times by the corpus but absent from it. Look at the top 50 every week; the orchestrator decides what to add. Additions are checked to the same standard as §16: title and authors from INSPIRE or arXiv.
- Use the citation graph to check this document in turn: whether the grouping of §16 agrees with the actual citation clusters, and whether any paper sits in the wrong group.

### 12.6 K4–K5: embeddings and the equation index

- Name and revision hash of the embedding model are stored. On a change of model a new set of vectors is added and the old one is kept.
- Hybrid retrieval: the BM25 ranking of the full-text index and the vector neighbours are combined by reciprocal-rank fusion; `--group`, `--paper` and `--kind` are structured filters.
- Equation index: after macro expansion, whitespace removal and unification of equivalent notations, store `tex_norm`; extract the set of symbols; tag by the rules in `kb/curated/equation_tags.yaml`, for example Vlasov equation, geodesic equation, Hamiltonian constraint, momentum constraint, Z4c, deposition, compaction function, Langevin equation, tidal radius. Equation search uses text matching and the context vectors together.

### 12.7 K6–K7: code index and paper–code links

- Each repository is indexed at its pinned commit: file inventory (language, line count, licence header); symbols (JSON output of universal-ctags, or tree-sitter); chunks by function, with comments; full-text index.
- **Run-parameter index.** For AthenaK, extract block name, parameter name and default value from the parameter-reading calls in the source, compare them with the example inputs under `inputs/`, and build the `params` table. Tracks consult this table when writing input files and do not rely on memory.
- **Module descriptions for AthenaK.** For `src/z4c`, `src/particles`, `src/pgen`, `src/mesh` and `src/bvals`, generate descriptions from file headers and comments without adding interpretation; also extract the order in which the task list calls the physics modules.
- **Upstream watch.** Compare branch tips weekly with `git ls-remote`. If `src/particles` or `src/z4c` changes, or a branch appears whose name contains pic, vlasov, nrpic or deposit, send a message to core.
- **Paper–code links.** Two sources: explicit ones (repository addresses that occur in papers, and the hand-curated correspondences in `kb/curated/paper_code_links.tsv`, for example arXiv:2611.12831 with AthenaK); and those submitted by tracks ("function X implements a given equation of a given paper"), which start as claimed and become verified once a test is attached.

### 12.8 K8: the layer of statements and evidence

- Import the labelled statements of the main text of this document one by one into the `claims` table as seeds: [VERIFIED] as abstract or title_only according to the level noted in the text; [BACKGROUND] as background; [JUDGEMENT] as judgement; [TO VERIFY] as to_verify.
- The daily work of the knowledge-base session is to advance this queue: when a supporting passage is found in the full text, upgrade to fulltext and record the locator; when a counter-example is found, mark refuted and notify the tracks that cited the statement.
- Tracks cite statements from the literature in their notes by claim number. `nrpic-ctx audit` checks whether the numbers in a note that come from the literature carry a claim number or a locator.
- Statements marked judgement are never upgraded to fulltext. They can only be supported or overturned by computed results, which is the tracks' business.

### 12.9 K9: quality checks and the first questions

`kb qa run` produces `kb/QA_REPORT.md`, containing:

- counts that agree with the manifests; an abstract and at least one section for every paper;
- the list of parse failures with a classification of causes;
- 30 papers drawn at random, with title and authors compared with INSPIRE;
- the resolution rate of bibliography entries; the fraction of in-corpus edges in the citation graph;
- detection of duplicates among versions of the same paper;
- retrieval regression: at least 30 questions with known answer locations in `kb/golden/questions.yaml`, reporting the hit rate within the top 10. Seed questions come from this document; for example "which paper writes the Einstein equations as a first-order system in electrodynamics-like form" should hit arXiv:2111.05282.

**First questions** (deliverable of gate KB-G1; every answer with a locator):

1. Of what order are the shape functions used for deposition in arXiv:2611.12831? Is there filtering?
2. How do its particle initial data satisfy the constraints?
3. Which values do its Z4c constraint-damping and gauge parameters take?
4. Does it have a code-availability statement? Which follow-up directions do the conclusions list? Does it mention cosmology, collisions or tidal interactions?
5. Which performance numbers does it report?
6. How are the initial data, the gauge and the black-hole-formation threshold defined in arXiv:2609.14218?
7. Which parameters do the two test cases of arXiv:2512.14649 use, and what are the acceptance quantities?
8. In which parameter range do the relativistic corrections of arXiv:2404.16270 become significant?
9. Are the Z4c variables of AthenaK vertex-centred or cell-centred? Which quantities does the `tmunu` interface need, and at which stage of the task list are they filled?

### 12.10 K10–K11: query interface, snapshots, incremental updates, and the gates of the knowledge base

```text
kb status [--json]                          counts, parse failures, schema version, snapshot id
kb verify-downloads                         manifests <-> kb-data/raw : missing, extra, checksum, source kind, version
kb ingest arxiv [--id ID | --priority 3 | --all | --new]     stages K2-K5 for papers
kb ingest repo  [--repo owner/name | --all]                  stage K6 for code
kb resolve-bib [--paper ID]                 bibliography entries -> arXiv id / DOI / INSPIRE record
kb embed [--model NAME] [--only chunks|equations|code]
kb search "QUERY" [-k 10] [--kind text|eq|code|caption] [--group G14] [--paper ID] [--hybrid]
kb show PAPER_ID [--abstract | --section "3.2" | --eq LABEL | --fig N] [--max-chars N]
kb eq "LATEX or keywords" [-k 10]
kb cites PAPER_ID [--in | --out] [--context]
kb frontier [-n 50]                         works cited often by the corpus but absent from it
kb code "SYMBOL or text" [--repo owner/name] [--kind function|class|param]
kb link add --paper ID --eq LABEL --repo R --symbol S --relation implements [--status claimed]
kb claim add|list|verify|refute ...         evidence queue, seeded from the labelled statements of this brief
kb export PAPER_ID --format md              flattened text with section numbers, for reading inside a session
kb qa run                                   integrity checks + golden-question retrieval test -> kb/QA_REPORT.md
kb snapshot                                 freeze kb.sqlite -> kb-YYYYMMDD-<sha>.sqlite and move `current`
kb watch upstream                           diff of `git ls-remote` for the watched repositories -> outbox message
```

- Tracks have read-only access: the `kb` command opens `db/current` by default, and a session adds `kb-data/` to its readable directories with `--add-dir` at start-up.
- An MCP server can be wrapped around it so that sessions query through tool calls, removing the coupling through paths. This is optional.
- Run `kb snapshot` at the end of every stage. A note that cites content of the knowledge base records the snapshot identifier.
- Incremental updates: after a new paper has entered the manifest through a proposal, run `kb ingest arxiv --new`; after a repository has moved to a new pinned commit, run `kb ingest repo`; schema changes go into `migrations/`.

**Gates of the knowledge base.** KB-G0: tools chosen, directories in place. KB-G1: the inventory report; all priority-3 papers ingested; code index and parameter index of AthenaK; the answers to the first questions. KB-G2: all papers and repositories ingested; the QA report meets the parse success rate and retrieval hit rate written in CHARTER. KB-G3: every statement in the evidence queue that bears on G1 of the six tracks has been processed. After that the track goes into service mode.

---

## 13. Git discipline, working notes and stage checks

Three hard requirements come from the group: all progress is tracked by git; working notes are written with `/paper-writing`; the figures for stage checks are drawn with `/sleep-paper-figure-style` and `/zoom-figure-style`. This section turns them into commands. The three skills belong to the group, and the rules inside the skills take precedence over any suggestion here; this section only fixes how they connect to the harness.

### 13.1 Git: all progress must be traceable

"Progress" covers code, input files, run manifests, analysis scripts, figures, notes, status files and decisions. Output data stay out of git, but their manifests and checksums go in.

```text
Branches  main (infrastructure, coord/, merged core releases) · core/nrpic · kb/main · track/<ID> · proposal/<ID>/<slug>
Commits   <ID>(<area>): <imperative summary, <= 72 chars>          e.g.  A(run): register spherical ball level 3
          areas: code pgen input run analysis fig note status ctx env kb harness fix
          body: why; evidence (run ids, test names, KB locators); what is NOT done
          trailers:  Run-Id: <run_id>    Gate: G<k>    Refs: arXiv:XXXX.XXXXX
Cadence   after every logical unit · before every run (nrpic-run refuses a dirty tree) · at the end of every session
Never     force-push · rewrite pushed history · --no-verify · commit files > 5 MB · commit secrets
          · edit paths owned by someone else · amend a commit that a run manifest or a tag refers to
Tags      stage/<ID>/G<k>-pass-YYYYMMDD   annotated; message = the gate table with pass/fail
          stage/<ID>/G<k>-fail-YYYYMMDD   a failed check is tagged too
          core-vX.Y                       core releases consumed by the tracks
          run/<run_id>                    optional, for runs cited in a note
Data      scratch/ and kb-data/ stay outside git; every number in a note is reachable through
          manifest.json + sha256sums.txt; small derived tables (<= 5 MB) used by figure scripts are committed
Remote    if a remote exists: push the own branch and its tags at the end of every session (policy: decision D3)
Audit     `nrpic-ctx audit` lists: runs without a manifest commit, figures without a script, numbers in notes
          without a run id, commits touching foreign paths, sessions that ended with a dirty tree
```

How this is enforced:

- **Commit first, then run.** `nrpic-run` refuses to start with a dirty worktree, so the commit recorded in the manifest is the complete code that produced the result.
- **No loose ends at session end.** The Stop hook blocks once when the worktree is dirty and asks for a commit and an updated STATUS (§11.5).
- **Commit hooks.** pre-commit rejects files above 5 MB and suspected secrets, validates the format of run manifests, and checks whether the commit touches someone else's paths.
- **Direction of merges.** From main to a track by merge, once at the start of every session. Each time a track passes a gate, the orchestrator merges that track's branch into main; a track changes only its own paths, so this merge cannot conflict, and main therefore always holds the state of every track at its most recent passed check. Pushed history is never rebased.
- **Audit.** The orchestrator runs `nrpic-ctx audit` weekly and writes the result into the weekly digest.

### 13.2 Working notes: `/paper-writing`

The working note of each track is a REVTeX manuscript in `tracks/<ID>/note/`. It is updated at every gate, and by G4 it is the first draft of the paper. Invoke the skill by typing `/paper-writing` in the track session; if the skill menu shows a prefix, use the name as displayed.

The points of the skill as I read them [VERIFIED: skill file, 2026-11-15], and how they are implemented in this project:

| Rule of the skill | Implementation in this project |
|---|---|
| Each manuscript has its own WRITING_GUIDE.md and NOTATION.md, next to the manuscript or one level up | In `tracks/<ID>/`, one level above `note/`; NOTATION.md has `coord/NOTATION.md` as its upstream |
| The dated scientific record lives in `notes/`, outside the manuscript | `tracks/<ID>/notes/`, indexed by JOURNAL.md |
| Scripts live with the manuscript and find files relative to their own path | `tracks/<ID>/note/scripts/`; scripts locate outputs through run manifests and hard-code no machine path |
| No explicit numbers or percentages in the main text; the Supplemental Material is the numerical ledger | The main text states conclusions and trends; `supplement.tex` lists every number |
| Project records (commit hashes, script names, hardware, wall times) do not enter the manuscript, not even in LaTeX comments | Provenance goes into `tracks/<ID>/stage/G<k>/PROVENANCE.md` and the run manifests; the Supplemental Material refers to runs by labels internal to the manuscript (R1, R2, …), and the table from labels to run identifiers is in PROVENANCE.md |
| No `\eqref`, no boxed equations; write "black hole", never "hole" | Followed |
| Captions of at most 5 lines; legends without frames | Consistent with the frameless legends of the data-figure style |
| Before committing, run the skill's manuscript checker with `--compile` | Step 6 of the stage check; if the check fails, the gate is not passed |
| New-manuscript procedure: a 300-word version, a 1000-word version, review from the viewpoint of a first-year graduate student (parallel subagents), then the main text | The 300-word version at G0, the 1000-word version at G1, the main text from G2 |

### 13.3 The stage-check command

```text
/stage-check <ID> G<k>          project skill; expands to the steps below. Never skip a step, never reorder.

 1  harness/bin/nrpic-ctx sync                merge main into the track branch; stop if shared paths conflict
 2  harness/bin/nrpic-stage collect <ID> G<k> gate criteria from coord/CHARTER.md -> tracks/<ID>/stage/G<k>/CHECKLIST.md
 3  harness/bin/nrpic-stage verify  <ID> G<k> re-run the registered tests and analysis scripts on a clean checkout of HEAD
 4  /zoom-figure-style                        data figures   -> tracks/<ID>/note/figures/fig_*.pdf   (scripts in note/scripts/)
 5  /sleep-paper-figure-style                 schematics     -> tracks/<ID>/note/figures/schem_*.png and .svg
 6  /paper-writing                            working note   -> tracks/<ID>/note/main.tex + supplement.tex; run its checker
 7  verifier subagent (fresh context)         recomputes every number of the Supplemental Material from the run manifests,
                                              opens every figure, reads the note as a first-year graduate student would
 8  harness/bin/nrpic-stage report  <ID> G<k> STAGE_REPORT.md: criterion-by-criterion pass/fail, figure list, open risks,
                                              the decision requested from the user
 9  git add -A && git commit -m "<ID>(note): stage G<k> package" && git tag -a stage/<ID>/G<k>-pass-YYYYMMDD
10  harness/bin/nrpic-ctx post --to all --type info   one paragraph + paths; rewrite STATUS.md; stop and wait for sign-off
```

Make it a project skill, `.claude/skills/stage-check/SKILL.md`:

```markdown
---
name: stage-check
description: Assemble and verify the stage-gate package of one track (working note, figures, report, tag). Use only when a stage check is requested.
disable-model-invocation: true
argument-hint: [track-id] [gate]
arguments: [track, gate]
---
Stage check for track $track, gate $gate. Work in the worktree of $track. Do the ten steps in order; if a step
fails, stop, write the failure into tracks/$track/stage/$gate/STAGE_REPORT.md, tag stage/$track/$gate-fail-<date>.

1. `harness/bin/nrpic-ctx sync`
2. `harness/bin/nrpic-stage collect $track $gate`
3. `harness/bin/nrpic-stage verify $track $gate`
4. Data figures: invoke the skill `zoom-figure-style`; follow its workflow and its checks before delivering.
   Use the project's czstyle.py (the copy in tracks/$track/note/scripts/, identical to harness/style/). One script
   per figure in tracks/$track/note/scripts/, reading registered run outputs only, saved with save(fig, stem).
5. Schematics: invoke the skill `sleep-paper-figure-style`; with the project's paperfig.py draw (a) the track
   architecture with the status legend exists / to be ported / new, (b) the gate timeline with the current position.
6. Working note: invoke the skill `paper-writing`; write or revise tracks/$track/note/main.tex and
   supplement.tex under its rules; run its manuscript checker with --compile and fix what it reports.
7. Spawn the `verifier` subagent with no context except the paths of the note, the manifests and the checklist.
8. `harness/bin/nrpic-stage report $track $gate`
9. Commit and tag: `git add -A && git commit -m "$track(note): stage $gate package"`, then
   `git tag -a stage/$track/$gate-pass-<date> -F tracks/$track/stage/$gate/STAGE_REPORT.md`
10. `harness/bin/nrpic-ctx post --to all --type info`, rewrite STATUS.md, then stop and wait for the user's sign-off.
```

Rules:

- The stage check is run by the track session, the orchestrator gives the final review, and the group signs off.
- A failed check is committed too, tagged `-fail`, and STATUS states what is still missing.
- Meaning of step 3: on a clean temporary checkout, re-run the registered tests and all analysis scripts from the manifests; the tables and figures produced must agree with those committed (numbers within tolerance, figures regenerated by the same script).
- No production runs for the next gate before the sign-off.

### 13.4 Figures: two skills, a style card, vendored libraries

Data figures use `/zoom-figure-style`, schematics use `/sleep-paper-figure-style`. The essentials of both are collected in one style card:

```text
DATA FIGURES — /zoom-figure-style (style of arXiv:2504.16802; module czstyle.py, style sheet cyclic_zoom.mplstyle)
  font        DejaVu Serif for text and math (mathtext.fontset = dejavuserif); text.usetex = False; pdf.fonttype = 3
  sizes       10 pt everywhere; 12 pt panel titles; 8 pt legends only in dense grids
  ticks       inward, on all four sides, minor ticks on; axes.linewidth 0.8; lines.linewidth 1.5; annotations 1.0
  series      reference #3369E8 (blue) · new method #EA4335 (red) · third #FBBC05 · fourth #009925 · extra comparison #FF7F0E
  encoding    colour = which run; line style = which component (solid total, dashed first part, dotted second part)
  bands       10-90 % band: fill_between, alpha 0.2, series colour; averaging window: axvspan, alpha 0.1
  legends     frameon=False, inside the axes, usually ncol=2
  colormaps   density-like: magma truncated to [0.2, 1]; ratio or signed-log quantities: RdBu_r with LogNorm symmetric about 1;
              temperature-like: RdYlBu_r; images rasterized inside a vector PDF, aspect='equal', no interpolation
  zoom rows   square touching panels, one zoom level per column; black box (lw 1.0) marks the previous panel's extent,
              dotted connectors (lw 1.0) run from the panel corners to the box; ticks at -L/2, 0, +L/2
  geometry    8 in wide (full page) or 4 in (one column); margins by subplots_adjust; save at the exact figsize
              (no bbox_inches='tight'); stack separate PDFs with consecutive \includegraphics[width=\linewidth]
  panel ids   none; captions say "Top left", "Bottom right"
  save        save(fig, stem) -> stem.pdf at the exact figsize + stem.png preview; clear every overflow warning it prints
  project use blue = baseline (exact solution, Newtonian, weak-field, or lower resolution); red = the NRPIC result

SCHEMATICS — /sleep-paper-figure-style (library paperfig.py; layouts A hierarchy + zoom-in, B multi-panel pipeline, C timeline)
  save        pf.save(fig, "path/stem") -> stem.png (300 dpi) + stem.svg; open the PNG and iterate once or twice
  palette     fixed; status legend: green = exists, slate = to be ported, red = new
  text        serif labels; never below 8 pt
  project use one architecture figure per track (what exists / is ported / is new) and one gate timeline per stage check
```

**State of `/zoom-figure-style` [VERIFIED: skill file, 2026-11-15].** The skill was updated once during that day. The version synced earlier had a body of a single sentence asking for a Google document to be made into a skill; the updated version is complete: workflow, palette, colormaps, line styles and layout, a helper module `czstyle.py` embedded in its section 9 together with the command that extracts it from the skill file, recipes for each kind of figure in section 10, and a checklist before delivery in section 11. Its essentials agree with the style card above, and where the two differ the skill wins. Three rules of the skill matter for the connection: `czstyle.py` sits in the same directory as the figure script, and one that already exists in the project is reused; figures are saved with `save(fig, stem)`, which writes the PDF at the exact size plus a PNG preview and warns when a label is cut by the figure edge; a figure is finished only after the PNG has been looked at and the checklist of section 11 has been gone through. If some environment still returns the old one-sentence version, the skill has not synced to the latest state there; sync first.

**Vendored libraries.** When building the harness, the orchestrator generates `czstyle.py` with the extraction command of the skill's section 9, generates `cyclic_zoom.mplstyle` with its `write_mplstyle()`, and takes `paperfig.py` from `scripts/` in the skill directory of `/sleep-paper-figure-style`. The three files go into `harness/style/` with their sha256 recorded. `/zoom-figure-style` requires the module to sit beside the figure script, and `/paper-writing` requires scripts to live with the manuscript, so every track copies the three files unchanged into `tracks/<ID>/note/scripts/` and its plotting scripts import from the same directory; `nrpic-stage verify` checks that the sha256 of every copy equals that in `harness/style/`. This is what keeps the figures of the six tracks consistent and reproducible. A change to a library goes through a proposal against `harness/style/`, after which the tracks refresh their copies.

**Minimum figures at each gate.**

| Gate | Schematics | Data figures |
|---|---|---|
| G0 | Track architecture (three states: exists, to be ported, new); stage timeline | None required; data from the literature may be redrawn |
| G1 | Updated architecture; data-flow diagram | Baseline results; validation figures for the analysis pipeline |
| G2 | Verification ladder | Convergence figures (one each for particle number, mesh, gauge); constraint norms against time; at least one multi-scale slice mosaic with zoom boxes |
| G3 | Sketch of the parameter space | Main results; robustness; comparison with the literature |
| G4 | Method overview | All figures of the paper |

Each figure has one script, with the same name as the figure. After a figure is generated the bitmap must be opened and looked at; the schematic skill requires viewing the PNG and iterating once or twice. The figure-checker subagent checks item by item against the style card and the checklist in section 11 of `/zoom-figure-style`: font, font size not below 8 pt, frameless legends, the meaning of the colours, the number of caption lines.

### 13.5 Independent verification and sign-off

- **The verifier subagent.** A subagent does not inherit the session history [VERIFIED], which is exactly what a check by someone who has not seen the production needs. It receives only the paths of the note, the manifests and the checklist. It has three tasks: recompute every number of the Supplemental Material from the manifests; open every figure; read the note as a first-year graduate student would and list the sentences that cannot be understood or have no support. Its output is `VERIFIER_REPORT.md`.
- **Cross-review.** G2 and G4 are reviewed once more by the orchestrator session.
- **Sign-off.** The group adds a record "accept G<k> of <ID>" under `coord/DECISIONS/`, or replies to the track session directly; the track records the sign-off in JOURNAL.

---

## 14. Kick-off prompts

The blocks below can be pasted unchanged into the corresponding session. They are written in English, and the Chinese and English versions of this document share the same text, so that no two inconsistent versions exist when they are executed; a session can restate them in Chinese if needed.

### 14.1 Orchestrator

```text
ROLE   You are the orchestrator of the NRPIC-cosmology program. You work only in the main checkout
       ($NRPIC_HOME/repo, branch main). You build the harness, then act as integrator and reviewer.
READ   The brief: sections 0, 1, 2.2, 9, 11, 13 in full; sections 12 and 14 as reference.
DO     In this order, with one commit per numbered step:
  1. Record decisions D1-D7 (section 9.1) as coord/DECISIONS/0001...0007. Where the user has not answered,
     take the stated default and mark the record PROVISIONAL.
  2. Create the layout of section 11.1. Write CLAUDE.md (<= 200 lines), .claude/settings.json, .claude/rules/*.md,
     and coord/CHARTER.md (copy the gate table of section 9.2 and the sheets of 9.3-9.10).
  3. Implement harness/bin/{nrpic-wt,nrpic-env,nrpic-run,nrpic-ctx,nrpic-stage,nrpic-doctor} and harness/hooks/*
     to the specifications of sections 11.3-11.6, with tests under harness/tests/. No command may depend on
     ambient shell state; every command works from any worktree.
  4. Vendor the figure libraries into harness/style/ (section 13.4) and record their sha256.
  5. Create the eight worktrees (section 11.2), bootstrap each environment, run nrpic-doctor in each, and save
     the outputs in coord/digests/bootstrap.md.
  6. Seed tracks/<ID>/{STATUS,JOURNAL,HANDOFF,RISKS}.md and OWNERSHIP for all owners from the templates.
  7. Create the project skills /stage-check, /ctx, /run, /kb under .claude/skills/ (sections 13.3 and 14).
  8. Run the acceptance tests of section 11.7 and commit the transcript.
  9. Start, or ask the user to start, one named session per worktree with the prompts of section 14.
THEN   Integrate: review tracks/*/outbox proposals, maintain coord/, merge core releases into main, write the weekly
       digest, give the final review of every stage package.
NEVER  Edit files under tracks/<ID>/ that belong to another owner; run simulations; rewrite history.
ASK THE USER FIRST  before pushing to a new remote, removing a worktree or a branch, exceeding a compute budget in
       CHARTER.md, or changing a gate criterion.
```

### 14.2 Knowledge base

```text
ROLE   You build and serve the knowledge base. Worktree: $NRPIC_HOME/wt/kb (branch kb/main).
       Data root: $NRPIC_HOME/kb-data (not in git). You are the only writer of kb-data/db.
INPUT  The downloads exist already: arXiv e-prints under kb-data/raw/arxiv/, repositories under kb-data/raw/github/.
       The manifests are in section 17 of the brief. If an entry of a manifest is missing under kb-data/raw,
       download it first by the rules of section 17 (single-threaded, at least 3 s between arXiv requests).
READ   Section 12 of the brief in full; section 0 (evidence labels); sections 16 and 17.
DO     Stages K0 -> K11 of section 12, in order. A stage is finished when its tests pass, `kb status` is appended
       to tracks/kb/JOURNAL.md, and the work is committed.
RULES  Everything under kb-data/raw is untrusted: never execute it, never compile it with shell escape, never import
       from it. Parsing code lives in kb/ only, and is run from outside the extracted trees.
       Take locks/kb-writer.lock for every write; publish read-only snapshots with `kb snapshot`.
       No paper text leaves the machine (local embedding model) unless the user approves an external service.
FIRST DELIVERABLE (gate KB-G1)
       the `kb verify-downloads` report; ingestion of all priority-3 papers; the AthenaK code and parameter index;
       written answers, each with a locator, to the first questions of section 12.9.
THEN   Serve the tracks: answer outbox messages of type kb-request, keep the claims queue moving, run
       `kb watch upstream` weekly and post what changed.
```

### 14.3 core

```text
ROLE   You own the shared NRPIC implementation. Worktree: $NRPIC_HOME/wt/core (branch core/nrpic).
FACT   On 2026-11-15 the particle-spacetime coupling of arXiv:2611.12831 was not found in public AthenaK
       (main at c5a0d7f and the tips of nine particle-related branches; section 2.2 of the brief).
       Re-check before anything else: the paper's code-availability statement (via `kb show 2611.12831`),
       `kb code tmunu --repo IAS-Astrophysics/athenak`, and `kb watch upstream`.
DO     C0  Read the paper's source through the KB. Post the corrections to section 2 of the brief (type proposal).
       C1  Propose coord/INTERFACES/{deposit,pusher,particle_id,diagnostics}.md and have them accepted before coding.
       C2  Implement in this order, each step with its own test: metric interpolation to particles -> geodesic
           pusher(s) -> deposition on a uniform grid -> coupling to the Z4c sources -> deposition across refinement
           boundaries -> constraint-satisfying particle initial data -> restart and output.
       C3  Pass the rows of section 10 marked CORE, submit the stage package for G2, and tag core-v0.1 with a
           CHANGELOG. Afterwards: one tagged release per accepted interface change.
RULES  Keep the fork mergeable with upstream: isolated changes, upstream style, no track-specific physics in core.
       Every performance or accuracy statement needs a run manifest.
ASK THE USER (decision D2) whether to request code access from the authors before investing in C2.
```

### 14.4 Tracks A–F (template)

```text
ROLE   You own Track <ID> (<title>). Worktree: $NRPIC_HOME/wt/<ID> (branch track/<ID>).
       You write only tracks/<ID>/** and the source paths listed in tracks/<ID>/OWNERSHIP.
START  every session with:
       harness/bin/nrpic-ctx sync && harness/bin/nrpic-ctx brief && cat tracks/<ID>/HANDOFF.md
READ   The brief: section 0, section 4, the entry of your problem in section 5, your track sheet in section 9,
       sections 10 and 13. For papers use `kb search` and `kb show`; never take a number from the brief.
WORK   Follow the track sheet. The pre-core package comes first and must not wait for core; core-dependent work
       starts when the release it needs is tagged.
       Every simulation and every analysis run goes through harness/bin/nrpic-run.
       Every figure has a script under tracks/<ID>/note/scripts/ that reads registered outputs only.
       What you need from core, the KB or another track: write an outbox file (type request, proposal, blocker or
       kb-request); if sessions are live, also send a one-line cross-session message that points to the file.
EVIDENCE  Use the four labels of section 0. A number enters a note only with a run id or a KB locator.
END    every session with: STATUS.md rewritten (<= 60 lines); one JOURNAL.md entry; HANDOFF.md rewritten for a reader
       with no memory; a clean `git status`; a push if a remote exists.
GATES  When you believe a gate of section 9.2 is met, run /stage-check <ID> G<k> and stop for sign-off. Do not
       start the next gate's production runs before sign-off; scouting runs are allowed if registered as scouting.
```

Substitute `<ID>` and `<title>` from this table:

| `<ID>` | `<title>` | What to do first in the first session |
|---|---|---|
| A-emd-pbh | EMD primordial-black-hole formation with collisionless matter | A-pre-1: derivation of the expanding-ball initial data and the offline constraint check |
| B-emd-gw | Gravitational waves from nonlinear EMD structure formation | B-pre-1 and B-pre-3 |
| C-sidm | Relativistic end state of SIDM core collapse | C-pre-1 |
| D-bh-dress | Black-hole growth and dark-matter dress in an expanding collisionless medium | The derivation of D-pre-1 |
| E-stoch-inf | Stochastic inflation in numerical relativity | E-pre-1, then E-pre-2 |
| F-hills | Hills mechanism with NRPIC | The novelty search F-pre-5, then F-pre-1 |

### 14.5 Recurring tasks

- **Weekly, orchestrator:** `nrpic-ctx digest` and `nrpic-ctx audit`, with the results written under `coord/digests/`.
- **Weekly, knowledge base:** `kb watch upstream` and `kb frontier`; report new papers of the groups of §3.9 to the tracks concerned.
- **Every session, every owner:** `nrpic-ctx sync` at the start, and persisting according to item 7 of §11.3 at the end.

How these are triggered (background sessions, scheduled tasks or by hand) depends on the environment and is not prescribed here.

---

## 15. Items for the agents to verify or complete

1. **Full text of 2611.12831.** Order of deposition, filtering, constraint damping, the constraint solve for particle initial data, performance numbers, the code-availability statement, the follow-up directions in the conclusions. Responsible: core and the knowledge base (the first questions of §12.9).
2. **Availability of the NRPIC code.** Decision D2; upstream branches re-checked weekly (§12.7).
3. **The specific approximations of GRAMSES.** The wording in the table of §3.1 comes from prior knowledge.
4. **Current status of the hyperbolicity of dGREM.** Bears on whether M3 is feasible.
5. **Novelty searches.** S5 (black-hole formation with a free-streaming component), S7 (numerical test of the Burnett conjecture), the null test of S4 (an NR test of cosmological coupling), full-NR simulations of binary black holes in a particle-dark-matter environment, S11 (NR work on stochastic inflation outside the group that created the formalism), S12 (Hills-type full-NR calculations).
6. **Item 20 of §7.** Current status of stability results for matter-dominated FLRW under Einstein–Vlasov.
7. **Quantitative statements marked [BACKGROUND].** In particular: the Type I nature of collisionless critical collapse; the spin prediction of arXiv:1707.03595; the tracelessness conclusion of Green–Wald; horizon mass and energy fraction at neutrino decoupling; the r^(−9/4) profile; the scaling laws of the Hills mechanism.
8. **Three places where a derivation has to be checked.** The two relations of the expanding dust ball (S1 in §5); the vacuum-bubble benchmark of Einstein–Straus type (§9.7); the scale estimate for the strong-field Hills mechanism (last item of §3.11).
9. **Entries whose author field is empty or gives the first author only.** Complete them from the source files after download.
10. **New entries checked by title only.** In groups G20 and G21, apart from the few marked "VERIFIED: abstracts" in §3.10 and §3.11, the content was not read.
11. **Classic references without an arXiv version** (not listed in §16; obtain separately when needed): the series on relativistic clusters and spindle collapse by Shapiro & Teukolsky (1985–1992); critical collapse, Choptuik (1993); the high-frequency limit, Burnett (1989); the pancake approximation, Zel'dovich (1970); self-similar secondary infall, Bertschinger (1985); charge-conserving deposition, Esirkepov (2001) and Villasenor & Buneman (1992); the pusher of Boris (1970); the Hamiltonian structure of Vlasov–Einstein, Kandrup & Morrison (1993); tidal separation of binaries, Hills (1988); stochastic inflation, Starobinsky (1986); the vacuole model of Einstein & Straus (1945).
12. **Identifiers checked only against arXiv pages or search results, without an INSPIRE record:** 2409.16053, 1609.03053, 1612.06734, 1709.00267, 0909.0749, gr-qc/0012059, astro-ph/9607124, 2510.11611.
13. **Claude Code mechanisms.** The loop-guard input field of the Stop hook; which isolation checks constrain a session started in a hand-made worktree under the local version; whether cross-session messaging is available locally (`/list-agents`).
14. **The version of `/zoom-figure-style`.** Confirm that every environment has synced the complete version (the one that contains `czstyle.py`) and not the earlier one-sentence version; where the style card and the skill differ, the skill takes precedence.
15. **The repository manifest (§17).** The descriptions of what each repository is for come from prior knowledge; the names that did not resolve need their hosting addresses found.

---

## 16. References

684 entries in total, all with arXiv links. Marks: ★ must read, ◆ important, · extended. Format: `[arXiv:id](link)` — authors — title — note. An empty author field means the authors were not checked; "(first author)" means only the first author was checked. Groups G20 and G21 are new in version 2.

**Suggested reading order (a core of about 40 papers).**

1. arXiv:2611.12831 (the target method) → arXiv:2111.05282 (the electrodynamic analogy) → arXiv:2409.10383 (the Z4c module)
2. arXiv:2409.01939 (review of the whole field) → arXiv:1106.1367 (Einstein–Vlasov review) → arXiv:2110.06265 (review of cosmological Vlasov–Poisson)
3. arXiv:1908.05683, arXiv:1810.05203, arXiv:2003.08014 (precedents for cosmological Einstein–Vlasov and the code comparison)
4. arXiv:1611.07906, arXiv:1901.04498, arXiv:math/0209336 (three-dimensional collisionless collapse and the convergence of PIC)
5. arXiv:2609.14218, arXiv:2610.23218, arXiv:1609.01588, arXiv:1707.03595, arXiv:2211.13950, arXiv:2507.18312, arXiv:2508.10070, arXiv:2109.04896, arXiv:2306.11810 (S1)
6. arXiv:2605.04487, arXiv:2312.12499 (S2)
7. arXiv:2108.11967, arXiv:2601.17117 (S3)
8. arXiv:2509.26470, arXiv:2608.13206 (initial data and gauge)
9. arXiv:1604.06065, arXiv:1905.08890 (comparison codes of the weak-field and constrained formulations)
10. arXiv:2401.08530, arXiv:2512.14649, arXiv:2606.14853, arXiv:2203.13852 (Track E)
11. arXiv:0911.1136, arXiv:1804.02911, arXiv:2404.16270, arXiv:2402.02178 (Track F)

### G01 Target paper and direct methodological lineage (NRPIC, AthenaK, Z4c, moving puncture, dGREM) (21 entries)

- ★ [arXiv:2611.12831](https://arxiv.org/abs/2611.12831) — Wu, Most — *Numerical-Relativity Particle-in-Cell Simulations: Self-Gravitating Collisionless Matter in Dynamical Spacetimes* — starting point of this project: AthenaK + Z4c + moving puncture + conservative deposition + AMR
- ◆ [arXiv:2504.15978](https://arxiv.org/abs/2504.15978) — Boyeneni, Wu, Most — *Unveiling the electrodynamic nature of spacetime collisions* — exact rewriting of the Einstein equations in electrodynamics-like form, applied to binary black holes
- ★ [arXiv:2111.05282](https://arxiv.org/abs/2111.05282) — Olivares, Peshkov, Most, Guercilena, Papenfort — *A new first-order formulation of the Einstein equations exploiting analogies with electrodynamics* — dGREM formulation; proposes Yee-type / constrained-transport discretization to preserve the constraints
- · [arXiv:2211.13659](https://arxiv.org/abs/2211.13659) — Peshkov, Olivares, Romenski — *First-order hyperbolic formulation of the pure tetrad teleparallel gravity theory* — first-order formulation structurally close to dGREM, and its hyperbolicity
- · [arXiv:2509.19769](https://arxiv.org/abs/2509.19769) — (authors include J. Wu and E. R. Most) — *Toward a Theory of Gravitational Wave Turbulence*
- ◆ [arXiv:2409.16053](https://arxiv.org/abs/2409.16053) — Stone et al. — *AthenaK: A Performance-Portable Version of the Athena++ AMR Framework* — the framework itself (Kokkos, GPU)
- ◆ [arXiv:2409.10383](https://arxiv.org/abs/2409.10383) — Zhu et al. — *Performance-Portable Numerical Relativity with AthenaK* — Z4c module
- · [arXiv:2409.10384](https://arxiv.org/abs/2409.10384) — Fields et al. — *Performance-Portable Binary Neutron Star Mergers with AthenaK* — dynamical-spacetime GRMHD module; basis for coupling particles and fluid
- · [arXiv:2101.08289](https://arxiv.org/abs/2101.08289) — Daszuta et al. — *GR-Athena++: puncture evolutions on vertex-centered oct-tree AMR*
- ◆ [arXiv:0912.2920](https://arxiv.org/abs/0912.2920) — Bernuzzi, Hilditch — *Constraint violation in free evolution schemes: comparing BSSNOK with a conformal decomposition of Z4* — Z4c
- · [arXiv:1212.2901](https://arxiv.org/abs/1212.2901) — Hilditch et al. — *Compact binary evolutions with the Z4c formulation*
- · [arXiv:1106.2254](https://arxiv.org/abs/1106.2254) — Alic et al. — *Conformal and covariant formulation of the Z4 system with constraint-violation damping* — CCZ4
- · [arXiv:gr-qc/0504114](https://arxiv.org/abs/gr-qc/0504114) — Gundlach, Martín-García, Calabrese, Hinder — *Constraint damping in the Z4 formulation and harmonic gauge*
- · [arXiv:gr-qc/0511048](https://arxiv.org/abs/gr-qc/0511048) — Campanelli, Lousto, Marronetti, Zlochower — *Accurate evolutions of orbiting black-hole binaries without excision* — moving puncture
- · [arXiv:gr-qc/0511103](https://arxiv.org/abs/gr-qc/0511103) — Baker, Centrella, Choi, Koppitz, van Meter — *Gravitational wave extraction from an inspiraling configuration of merging black holes* — moving puncture
- · [arXiv:gr-qc/0605030](https://arxiv.org/abs/gr-qc/0605030) — van Meter, Baker, Koppitz, Choi — *How to move a black hole without excision: gauge conditions for the numerical evolution of a moving puncture*
- · [arXiv:gr-qc/0206072](https://arxiv.org/abs/gr-qc/0206072) — Alcubierre et al. — *Gauge conditions for long-term numerical black hole evolutions without excision* — 1+log slicing and Gamma-driver shift
- · [arXiv:gr-qc/9412071](https://arxiv.org/abs/gr-qc/9412071) — Bona, Massó, Seidel, Stela — *A New formalism for numerical relativity* — Bona–Massó family of slicings
- ◆ [arXiv:1109.0546](https://arxiv.org/abs/1109.0546) — Staley, Baumgarte, Brown, Farris, Shapiro — *Oppenheimer-Snyder Collapse in Moving-Puncture Coordinates* — moving-puncture version of the Oppenheimer–Snyder test
- · [arXiv:2404.01137](https://arxiv.org/abs/2404.01137) — Etienne — *Improved moving-puncture techniques for compact binary simulations*
- · [arXiv:2505.15912](https://arxiv.org/abs/2505.15912) — *BHaHAHA: a fast, robust apparent horizon finder library for numerical relativity*

### G02 Numerical work on collisionless matter in full GR (non-cosmological) (22 entries)

- ◆ [arXiv:gr-qc/9905058](https://arxiv.org/abs/gr-qc/9905058) — Shibata — *Fully general relativistic simulation of merging binary clusters: spatial gauge condition* — early 3+1 NR with collisionless particles
- ◆ [arXiv:gr-qc/9804040](https://arxiv.org/abs/gr-qc/9804040) — Rein, Rendall, Schaeffer — *Critical collapse of collisionless matter: a numerical investigation* — spherically symmetric PIC; critical behaviour
- · [arXiv:gr-qc/0012059](https://arxiv.org/abs/gr-qc/0012059) — Olabarrieta — *Critical Collapse of Collisionless Matter in Spherical Symmetry* — thesis
- ◆ [arXiv:gr-qc/0107076](https://arxiv.org/abs/gr-qc/0107076) — Olabarrieta, Choptuik — *Critical phenomena at the threshold of black hole formation for collisionless matter in spherical symmetry*
- ★ [arXiv:math/0209336](https://arxiv.org/abs/math/0209336) — Rein, Rodewis — *Convergence of a particle-in-cell scheme for the spherically symmetric Vlasov-Einstein system* — convergence proof for PIC; notes the difficulty that sources enter the field equations pointwise
- ◆ [arXiv:gr-qc/0601112](https://arxiv.org/abs/gr-qc/0601112) — Andréasson, Rein — *A numerical investigation of the stability of steady states and critical phenomena for the spherically symmetric Einstein-Vlasov system* — stability threshold of steady states; usable as a benchmark
- · [arXiv:gr-qc/0611053](https://arxiv.org/abs/gr-qc/0611053) — Andréasson, Rein — *On the steady states of the spherically symmetric Einstein-Vlasov system*
- ◆ [arXiv:1409.5176](https://arxiv.org/abs/1409.5176) — Akbarian, Choptuik — *Critical collapse in the spherically-symmetric Einstein-Vlasov model*
- ★ [arXiv:1611.07906](https://arxiv.org/abs/1611.07906) — Yoo, Harada, Okawa — *3D Simulation of Spindle Gravitational Collapse of a Collisionless Particle System* — 3D particles + NR; spindle collapse
- ◆ [arXiv:1807.11562](https://arxiv.org/abs/1807.11562) — Pretorius, East — *Black Hole Formation from the Collision of Plane-Fronted Gravitational Waves* — origin of the Einstein–Vlasov method used in East's series
- ★ [arXiv:1901.04498](https://arxiv.org/abs/1901.04498) — East — *Cosmic Censorship Upheld in Spheroidal Collapse of Collisionless Matter*
- ◆ [arXiv:2010.15771](https://arxiv.org/abs/2010.15771) — Ames, Andréasson, Rinne — *Dynamics of gravitational collapse in the axisymmetric Einstein-Vlasov system* — axisymmetric (2+1)+1 PIC
- ◆ [arXiv:2305.04360](https://arxiv.org/abs/2305.04360) — Ames, Andréasson, Rinne — *Hoop and weak cosmic censorship conjectures for the axisymmetric Einstein-Vlasov system*
- · [arXiv:2009.08163](https://arxiv.org/abs/2009.08163) — Günther et al. — *A numerical stability analysis for the Einstein-Vlasov system*
- · [arXiv:2105.05556](https://arxiv.org/abs/2105.05556) — Günther, Straub, Rein — *Collisionless Equilibria in General Relativity: Stable Configurations beyond the First Binding Energy Maximum*
- · [arXiv:1707.08666](https://arxiv.org/abs/1707.08666) — *Distribution functions for a family of general-relativistic hypervirial models in the collisionless regime* — usable for initial data and steady-state tests
- ◆ [arXiv:2511.20567](https://arxiv.org/abs/2511.20567) — East — *Gravitational collapse in the vicinity of the extremal black hole critical point* — Einstein–Maxwell–Vlasov numerics
- ◆ [arXiv:2505.01495](https://arxiv.org/abs/2505.01495) — Bamber, Shapiro, Ruiz, Tsokaros — *Evolution of a black hole cluster in full general relativity* — full-GR evolution of a cluster of 25 black holes
- · [arXiv:astro-ph/9607124](https://arxiv.org/abs/astro-ph/9607124) — Widrow — *Modeling Collisionless Matter in General Relativity: A New Numerical Technique* — scalar field as a model for collisionless matter
- · [arXiv:2203.06478](https://arxiv.org/abs/2203.06478) — Diener, Rosswog, Torsello — *Simulating neutron star mergers with the Lagrangian Numerical Relativity code SPHINCS_BSSN* — experience with particle–mesh mapping coupled to NR
- · [arXiv:2306.06226](https://arxiv.org/abs/2306.06226) — Rosswog, Torsello, Diener — *The Lagrangian Numerical Relativity code SPHINCS_BSSN_v1.0*
- · [arXiv:2408.11577](https://arxiv.org/abs/2408.11577) — *Threshold Mass of the General-relativistic Instability for Supermassive Star Cores*

### G03 Mathematics of Einstein–Vlasov and kinetic theory (24 entries)

- ◆ [arXiv:gr-qc/9604001](https://arxiv.org/abs/gr-qc/9604001) — Rendall — *An introduction to the Einstein-Vlasov system* — introduction
- ★ [arXiv:1106.1367](https://arxiv.org/abs/1106.1367) — Andréasson — *The Einstein-Vlasov System/Kinetic Theory* — Living Reviews article
- · [arXiv:1303.2899](https://arxiv.org/abs/1303.2899) — Sarbach, Zannias — *Relativistic Kinetic Theory: An Introduction*
- · [arXiv:1309.2036](https://arxiv.org/abs/1309.2036) — Sarbach, Zannias — *The geometry of the tangent bundle and the relativistic kinetic theory of gases*
- ◆ [arXiv:2106.09235](https://arxiv.org/abs/2106.09235) — Acuña-Cárdenas, Gabarrete, Sarbach — *An introduction to the relativistic kinetic theory on curved spacetimes*
- ◆ [arXiv:1910.12152](https://arxiv.org/abs/1910.12152) — Andersson, Korzyński — *Variational principle for the Einstein-Vlasov equations* — starting point for variational / geometric PIC
- · [arXiv:2310.00776](https://arxiv.org/abs/2310.00776) — Andréasson — *Stationary solutions of the axially symmetric Einstein-Vlasov system: present status and open problems*
- · [arXiv:1707.06141](https://arxiv.org/abs/1707.06141) — Fajman, Joudioux, Smulevici — *The stability of the Minkowski space for the Einstein-Vlasov system*
- · [arXiv:1707.06079](https://arxiv.org/abs/1707.06079) — Lindblad, Taylor — *Global stability of Minkowski space for the Einstein-Vlasov system in the harmonic gauge*
- · [arXiv:1602.02611](https://arxiv.org/abs/1602.02611) — Taylor — *The global nonlinear stability of Minkowski space for the massless Einstein-Vlasov system*
- · [arXiv:2210.00512](https://arxiv.org/abs/2210.00512) — *Global stability of the Minkowski spacetime for the Einstein-Vlasov system*
- ◆ [arXiv:1709.00267](https://arxiv.org/abs/1709.00267) — Andersson, Fajman — *Nonlinear stability of the Milne model with matter* — nonlinear stability of Einstein–Vlasov on a cosmological background
- ◆ [arXiv:1306.6223](https://arxiv.org/abs/1306.6223) — Andréasson, Ringström — *Proof of the cosmic no-hair conjecture in the T3-Gowdy symmetric Einstein-Vlasov setting*
- · [arXiv:2002.02119](https://arxiv.org/abs/2002.02119) — Fajman, Oliynyk, Wyatt — *Stabilizing relativistic fluids on spacetimes with non-accelerated expansion*
- ◆ [arXiv:gr-qc/0512031](https://arxiv.org/abs/gr-qc/0512031) — Heinzle, Uggla — *Dynamics of the spatially homogeneous Bianchi type I Einstein-Vlasov equations* — Vlasov matter behaves differently from a perfect fluid near the singularity
- · [arXiv:gr-qc/0112009](https://arxiv.org/abs/gr-qc/0112009) — Martín-García, Gundlach — *Self-similar spherically symmetric solutions of the massless Einstein-Vlasov system*
- · [arXiv:1009.2596](https://arxiv.org/abs/1009.2596) — Rendall, Velázquez — *A class of dust-like self-similar solutions of the massless Einstein-Vlasov system*
- ◆ [arXiv:2402.10190](https://arxiv.org/abs/2402.10190) — Kehle, Unger — *Extremal black hole formation as a critical phenomenon* — Einstein–Maxwell–Vlasov; threshold solutions are extremal black holes
- · [arXiv:2510.12429](https://arxiv.org/abs/2510.12429) — *Semi-Global Existence and Trapped Surface Formation for the Einstein-Vlasov System*
- · [arXiv:2309.00431](https://arxiv.org/abs/2309.00431) — *Proof of the Einstein quadrupole formula for solutions of the Einstein-Vlasov system close to Minkowski spacetime*
- ◆ [arXiv:2609.13394](https://arxiv.org/abs/2609.13394) — Eo — *Nonlinear Phase Mixing in Einstein-Vlasov System near Schwarzschild Spacetime* — phase mixing and the nonlinear echo time-scale
- ◆ [arXiv:1706.09501](https://arxiv.org/abs/1706.09501) — Huneau, Luk — *High-frequency backreaction for the Einstein equations under polarized U(1) symmetry* — Burnett conjecture
- ◆ [arXiv:1907.10743](https://arxiv.org/abs/1907.10743) — Huneau, Luk — *Trilinear compensated compactness and Burnett's conjecture in general relativity*
- ★ [arXiv:2506.21779](https://arxiv.org/abs/2506.21779) — Huneau, Luk — *High-frequency backreaction for the Einstein equations under U(1) symmetry: from Einstein-dust to Einstein-Vlasov* — massless Vlasov solutions can be approximated by high-frequency vacuum spacetimes

### G04 GRPIC, particle pushers and structure-preserving algorithms (19 entries)

- ◆ [arXiv:1810.03613](https://arxiv.org/abs/1810.03613) — Parfrey, Philippov, Cerutti — *First-Principles Plasma Simulations of Black-Hole Jet Launching* — GRPIC
- · [arXiv:1908.06919](https://arxiv.org/abs/1908.06919) — Chen, Yuan — *Physics of Pair Producing Gaps in Black Hole Magnetospheres II: General Relativity* — GRPIC
- · [arXiv:2012.07229](https://arxiv.org/abs/2012.07229) — *Two-dimensional Particle-in-Cell simulations of axisymmetric black hole magnetospheres* — GRPIC
- · [arXiv:2511.17710](https://arxiv.org/abs/2511.17710) — *Entity: Hardware-agnostic Particle-in-cell Code for Plasma Astrophysics. I. Curvilinear Special Relativistic Module*
- ◆ [arXiv:2511.17701](https://arxiv.org/abs/2511.17701) — Galishnikova, Hakobyan, Philippov, Crinquand — *Entity: Hardware-agnostic Particle-in-cell Code for Plasma Astrophysics. II. General Relativistic Module* — GPU GRPIC
- ◆ [arXiv:2605.15260](https://arxiv.org/abs/2605.15260) — Böss, Vanthieghem, Hakobyan, Gorbunov, Caprioli — *Entity: Hardware-agnostic Particle-in-Cell Code for Plasma Astrophysics. III. Higher-order shape functions & generalized field stencils* — high-order shape functions; relevant for noise reduction
- · [arXiv:2503.04558](https://arxiv.org/abs/2503.04558) — *Introducing APERTURE: A GPU-based General Relativistic Particle-in-Cell Simulation Framework*
- · [arXiv:2401.02908](https://arxiv.org/abs/2401.02908) — *OSIRIS-GR: General relativistic activation of the polar cap of a compact neutron star*
- · [arXiv:2101.12149](https://arxiv.org/abs/2101.12149) — Myers et al. — *Porting WarpX to GPU-accelerated platforms* — engineering experience with PIC on AMR and GPUs
- ◆ [arXiv:1801.02378](https://arxiv.org/abs/1801.02378) — Bacchini, Ripperda, Chen, Sironi — *Generalized, energy-conserving numerical simulations of particles in general relativity. I. Time-like and null geodesics* — geodesic integrators (including null geodesics)
- · [arXiv:1810.00842](https://arxiv.org/abs/1810.00842) — Bacchini, Ripperda, Porth, Sironi — *Generalized, energy-conserving numerical simulations of particles in general relativity. II. Test particles in electromagnetic fields and GRMHD*
- · [arXiv:1710.09164](https://arxiv.org/abs/1710.09164) — Ripperda et al. — *A comprehensive comparison of relativistic particle integrators*
- · [arXiv:2007.14401](https://arxiv.org/abs/2007.14401) — Bacchini, Ripperda, Philippov, Parfrey — *A Coupled Guiding Center–Boris Particle Pusher for Magnetized Plasmas in Compact-object Magnetospheres*
- · [arXiv:1006.3717](https://arxiv.org/abs/1006.3717) — Dodin, Fisch — *Vlasov equation and collisionless hydrodynamics adapted to curved spacetime*
- · [arXiv:2602.17487](https://arxiv.org/abs/2602.17487) — *Modeling of Relativistic Plasmas with a Conservative Discontinuous Galerkin Method* — reference for continuum (non-particle) relativistic kinetic solvers
- ◆ [arXiv:1609.03053](https://arxiv.org/abs/1609.03053) — Kraus, Kormann, Morrison, Sonnendrücker — *GEMPIC: Geometric ElectroMagnetic Particle-In-Cell Methods* — paradigm of structure-preserving PIC
- ◆ [arXiv:1612.06734](https://arxiv.org/abs/1612.06734) — Morrison — *Structure and structure-preserving algorithms for plasma physics* — review
- · [arXiv:0807.0734](https://arxiv.org/abs/0807.0734) — Richter, Lubich — *Free and constrained symplectic integrators for numerical general relativity*
- ◆ [arXiv:1208.3927](https://arxiv.org/abs/1208.3927) — Vincent, Gourgoulhon, Novak — *3+1 geodesic equation and images in numerical spacetimes* — geodesic equation in 3+1 form

### G05 Numerical methods for cosmological Vlasov–Poisson (phase-space sheets, δf, Schrödinger method, discreteness) (23 entries)

- ★ [arXiv:2110.06265](https://arxiv.org/abs/2110.06265) — Rampf — *Cosmological Vlasov–Poisson equations for dark matter: Recent developments and connections to selected plasma problems* — review; connects cosmology and plasma physics
- ★ [arXiv:2112.05165](https://arxiv.org/abs/2112.05165) — Angulo, Hahn — *Large-scale dark matter simulations* — review
- · [arXiv:1105.1082](https://arxiv.org/abs/1105.1082) — Dehnen, Read — *N-body simulations of gravitational dynamics* — review
- ◆ [arXiv:1111.3944](https://arxiv.org/abs/1111.3944) — Abel, Hahn, Kaehler — *Tracing the Dark Matter Sheet in Phase Space* — phase-space sheet
- ◆ [arXiv:1210.6652](https://arxiv.org/abs/1210.6652) — Hahn, Abel, Kaehler — *A new approach to simulating collisionless dark matter fluids*
- ◆ [arXiv:1501.01959](https://arxiv.org/abs/1501.01959) — Hahn, Angulo — *An adaptively refined phase-space element method for cosmological simulations and collisionless dynamics*
- · [arXiv:1509.07720](https://arxiv.org/abs/1509.07720) — Sousbie, Colombi — *ColDICE: a parallel Vlasov–Poisson solver using moving adaptive simplicial tessellation*
- · [arXiv:1909.00008](https://arxiv.org/abs/1909.00008) — Stücker, Hahn, Angulo, White — *Simulating the Complexity of the Dark Matter Sheet I: Numerical Algorithms*
- · [arXiv:1705.03750](https://arxiv.org/abs/1705.03750) — Colombi, Alard — *A 'metric' semi-Lagrangian Vlasov–Poisson solver*
- · [arXiv:2012.04409](https://arxiv.org/abs/2012.04409) — Colombi — *Phase-space structure of protohalos: Vlasov versus Particle-Mesh*
- · [arXiv:1206.6152](https://arxiv.org/abs/1206.6152) — Yoshikawa, Yoshida, Umemura — *Direct Integration of the Collisionless Boltzmann Equation in Six-dimensional Phase Space: Self-gravitating Systems*
- · [arXiv:2010.00248](https://arxiv.org/abs/2010.00248) — Yoshikawa, Tanaka, Yoshida, Saito — *Cosmological Vlasov–Poisson Simulations of Structure Formation with Relic Neutrinos: Nonlinear Clustering and the Neutrino Mass*
- ◆ [arXiv:2010.07321](https://arxiv.org/abs/2010.07321) — Elbers, Frenk, Jenkins, Li, Pascoli — *An optimal nonlinear method for simulating relic neutrinos* — δf method
- · [arXiv:1801.03906](https://arxiv.org/abs/1801.03906) — Banerjee, Powell, Abel, Villaescusa-Navarro — *Reducing Noise in Cosmological N-body Simulations with Neutrinos*
- · [arXiv:astro-ph/0702575](https://arxiv.org/abs/astro-ph/0702575) — Wang, White — *Discreteness effects in simulations of Hot/Warm dark matter*
- · [arXiv:1606.02038](https://arxiv.org/abs/1606.02038) — Power et al. — *Spurious Small-Scale Structure & Discreteness-Driven Relaxation in Cosmological Simulations*
- · [arXiv:1403.5567](https://arxiv.org/abs/1403.5567) — Uhlemann, Kopp, Haugg — *Schrödinger method as N-body double and UV completion of dust*
- · [arXiv:1801.03507](https://arxiv.org/abs/1801.03507) — Mocz et al. — *On the Schrödinger-Poisson–Vlasov-Poisson correspondence*
- · [arXiv:1911.04505](https://arxiv.org/abs/1911.04505) — Garny, Konstandin, Rubira — *The Schrödinger-Poisson method for Large-Scale Structure*
- · [arXiv:2010.12584](https://arxiv.org/abs/2010.12584) — Rampf, Hahn — *Shell-crossing in a ΛCDM Universe*
- · [arXiv:1912.00868](https://arxiv.org/abs/1912.00868) — Rampf, Frisch, Hahn — *Unveiling the singular dynamics in the cosmic large-scale structure*
- · [arXiv:2102.05690](https://arxiv.org/abs/2102.05690) — *Neutrinos in N-body simulations*
- · [arXiv:2510.13129](https://arxiv.org/abs/2510.13129) — *Numerical Cosmology* — lecture notes

### G06 NR infrastructure: codes, initial data, gauges, diagnostics (28 entries)

- · [arXiv:1503.03436](https://arxiv.org/abs/1503.03436) — Clough et al. — *GRChombo: Numerical Relativity with Adaptive Mesh Refinement*
- · [arXiv:2201.03458](https://arxiv.org/abs/2201.03458) — Andrade et al. — *GRChombo: An adaptable numerical relativity code for fundamental physics*
- ◆ [arXiv:2112.10567](https://arxiv.org/abs/2112.10567) — Radia et al. — *Lessons for adaptive mesh refinement in numerical relativity*
- · [arXiv:1111.3344](https://arxiv.org/abs/1111.3344) — Löffler et al. — *The Einstein Toolkit: A Community Computational Infrastructure for Relativistic Astrophysics*
- · [arXiv:1301.4498](https://arxiv.org/abs/1301.4498) — Almgren et al. — *Nyx: A Massively Parallel AMR Code for Computational Cosmology*
- ◆ [arXiv:2207.03125](https://arxiv.org/abs/2207.03125) — Aurrekoetxea, Clough, Lim — *CTTK: a new method to solve the initial data constraints in numerical relativity* — cosmological initial data
- ◆ [arXiv:2501.13046](https://arxiv.org/abs/2501.13046) — Aurrekoetxea et al. — *GRTresna: An open-source code to solve the initial data constraints in numerical relativity*
- ◆ [arXiv:2006.16360](https://arxiv.org/abs/2006.16360) — Garfinkle, Mead — *Cosmological initial data for numerical relativity*
- ◆ [arXiv:1305.5576](https://arxiv.org/abs/1305.5576) — Bentivegna — *Solving the Einstein constraints in periodic spaces with a multigrid approach* — constraint solving in periodic domains
- · [arXiv:1208.3473](https://arxiv.org/abs/1208.3473) — East, Ramazanoğlu, Pretorius — *Conformal Thin-Sandwich Solver for Generic Initial Data*
- ★ [arXiv:2509.26470](https://arxiv.org/abs/2509.26470) — Baumgarte, Clough, Giblin — *Restrictions on Initial Conditions in Cosmological Scenarios and Implications for Simulations of Primordial Black Holes and Inflation* — existence of initial-data solutions and two-branch non-uniqueness
- ◆ [arXiv:2607.21308](https://arxiv.org/abs/2607.21308) — Csukás — *Cosmological initial data without periodic boundary conditions* — parabolic–hyperbolic form of the constraints
- · [arXiv:2309.02946](https://arxiv.org/abs/2309.02946) — *Numerical stability of the Hyperbolic Formulation of the Constraint equations for T^3 cosmological space-times*
- · [arXiv:2312.03285](https://arxiv.org/abs/2312.03285) — *Periodic boundary conditions and G2 cosmology*
- ◆ [arXiv:2207.06376](https://arxiv.org/abs/2207.06376) — Baumgarte, Hilditch — *Shock-avoiding slicing conditions: Tests and calibrations*
- · [arXiv:gr-qc/0210050](https://arxiv.org/abs/gr-qc/0210050) — Alcubierre — *Hyperbolic slicings of spacetime: singularity avoidance and gauge shocks*
- ◆ [arXiv:1704.04307](https://arxiv.org/abs/1704.04307) — Giblin, Mertens, Starkman — *A cosmologically motivated reference formulation of numerical relativity* — factoring out an FLRW reference metric
- · [arXiv:1809.07010](https://arxiv.org/abs/1809.07010) — Ijjas, Pretorius, Steinhardt — *Stability and the Gauge Problem in Non-Perturbative Cosmology*
- · [arXiv:2304.07616](https://arxiv.org/abs/2304.07616) — Ijjas — *Gauge/frame invariant variables for the numerical relativity study of cosmological spacetimes*
- · [arXiv:2307.11701](https://arxiv.org/abs/2307.11701) — *Mean curvature flow method for numerical cosmology*
- ◆ [arXiv:2211.08133](https://arxiv.org/abs/2211.08133) — Munoz, Bruni — *EBWeyl: a Code to Invariantly Characterize Numerical Spacetimes* — gauge-invariant diagnostics
- · [arXiv:2602.00155](https://arxiv.org/abs/2602.00155) — *aurel: A Python package for automatic relativistic calculations*
- ◆ [arXiv:2111.09163](https://arxiv.org/abs/2111.09163) — (authors include H. J. Macpherson) — *Covariant transverse-traceless projection for secondary gravitational waves* — GW extraction in non-asymptotically-flat domains
- · [arXiv:2304.13284](https://arxiv.org/abs/2304.13284) — Harada, Yoo, Koga — *Revisiting compaction functions for primordial black hole formation*
- · [arXiv:1309.2012](https://arxiv.org/abs/1309.2012) — Hilditch — *An Introduction to Well-posedness and Free-evolution*
- · [arXiv:gr-qc/0703035](https://arxiv.org/abs/gr-qc/0703035) — Gourgoulhon — *3+1 Formalism and Bases of Numerical Relativity*
- · [arXiv:1307.7391](https://arxiv.org/abs/1307.7391) — Alic, Kastaun, Rezzolla — *Constraint damping of the conformal and covariant formulation of the Z4 system in simulations of binary neutron stars* — constraint damping in CCZ4
- ◆ [arXiv:2504.16802](https://arxiv.org/abs/2504.16802) — Guo, Stone, Quataert et al. — *Cyclic Zoom: Multiscale GRMHD Modeling of Black Hole Accretion and Feedback* — cyclic-zoom multiscale method in AthenaK; source of the data-figure style

### G07 Full-NR late universe: structure formation and observables (43 entries)

- ★ [arXiv:2409.01939](https://arxiv.org/abs/2409.01939) — Aurrekoetxea, Clough, Lim — *Cosmology using numerical relativity* — Living Reviews article; entry point to the whole field
- ◆ [arXiv:1511.01105](https://arxiv.org/abs/1511.01105) — Giblin, Mertens, Starkman — *Departures from the FLRW Cosmological Model in an Inhomogeneous Universe: A Numerical Examination* — one of the first full-NR cosmological simulations
- ◆ [arXiv:1511.01106](https://arxiv.org/abs/1511.01106) — Mertens, Giblin, Starkman — *Integration of inhomogeneous cosmological spacetimes in the BSSN formalism* — CosmoGRaPH
- ◆ [arXiv:1511.05124](https://arxiv.org/abs/1511.05124) — Bentivegna, Bruni — *Effects of nonlinear inhomogeneity on the cosmic expansion with numerical relativity* — one of the first full-NR cosmological simulations
- ◆ [arXiv:1611.05447](https://arxiv.org/abs/1611.05447) — Macpherson, Lasky, Price — *Inhomogeneous Cosmology with Numerical Relativity* — Einstein Toolkit + FLRWSolver
- ★ [arXiv:1807.01711](https://arxiv.org/abs/1807.01711) — Macpherson, Price, Lasky — *Einstein's Universe: Cosmological structure formation in numerical relativity* — magnitude of the global backreaction
- ◆ [arXiv:1807.01714](https://arxiv.org/abs/1807.01714) — Macpherson, Lasky, Price — *The trouble with Hubble: Local versus global expansion rates in inhomogeneous cosmological simulations with numerical relativity*
- · [arXiv:1608.04403](https://arxiv.org/abs/1608.04403) — Giblin, Mertens, Starkman — *Observable Deviations from Homogeneity in an Inhomogeneous Universe*
- · [arXiv:1707.06640](https://arxiv.org/abs/1707.06640) — Giblin, Mertens, Starkman, Zentner — *General Relativistic Corrections to the Weak Lensing Convergence Power Spectrum*
- ★ [arXiv:1711.06681](https://arxiv.org/abs/1711.06681) — East, Wojtak, Abel — *Comparing Fully General Relativistic and Newtonian Calculations of Structure Formation* — fluid; dictionary between GR and Newtonian simulations
- ★ [arXiv:1908.05683](https://arxiv.org/abs/1908.05683) — East, Wojtak, Pretorius — *Einstein-Vlasov Calculations of Structure Formation* — direct precedent for cosmological Einstein–Vlasov
- ★ [arXiv:1810.05203](https://arxiv.org/abs/1810.05203) — Giblin, Mertens, Starkman, Tian — *The Limited Accuracy of Linearized Gravity* — N-body (phase-space sheet) + BSSN
- ◆ [arXiv:1611.03437](https://arxiv.org/abs/1611.03437) — Daverio, Dirian, Mitsou — *A numerical relativity scheme for cosmological simulations*
- ◆ [arXiv:1904.07841](https://arxiv.org/abs/1904.07841) — Daverio, Dirian, Mitsou — *General Relativistic Cosmological N-body Simulations I: time integration*
- · [arXiv:1610.05198](https://arxiv.org/abs/1610.05198) — Bentivegna — *An automatically generated code for relativistic inhomogeneous cosmologies*
- ★ [arXiv:2003.08014](https://arxiv.org/abs/2003.08014) — Adamek, Barrera-Hinojosa, Bruni, Li, Macpherson, Mertens — *Numerical solutions to Einstein's equations in a shearing-dust Universe: a code comparison* — multi-code comparison benchmark
- ◆ [arXiv:2307.15194](https://arxiv.org/abs/2307.15194) — Magnall, Price, Lasky, Macpherson — *Inhomogeneous Cosmology using General Relativistic Smoothed Particle Hydrodynamics coupled to Numerical Relativity* — SPH particles + NR
- ◆ [arXiv:2302.09033](https://arxiv.org/abs/2302.09033) — Munoz, Bruni — *Structure formation and quasispherical collapse from initial curvature perturbations with numerical relativity simulations*
- · [arXiv:2010.07274](https://arxiv.org/abs/2010.07274) — Tian, Anselmi, Carney, Giblin, Mertens, Starkman — *On the question of measuring spatial curvature in an inhomogeneous universe*
- · [arXiv:2110.00893](https://arxiv.org/abs/2110.00893) — Tian, Carney, Mertens, Starkman — *Accurate relativistic observables from postprocessing light cone catalogs*
- ◆ [arXiv:2103.11918](https://arxiv.org/abs/2103.11918) — Macpherson, Heinesen — *Luminosity distance and anisotropic sky-sampling at low redshifts: A numerical relativity study*
- · [arXiv:2111.14423](https://arxiv.org/abs/2111.14423) — Heinesen, Macpherson — *A prediction for anisotropies in the nearby Hubble flow*
- ◆ [arXiv:2209.06775](https://arxiv.org/abs/2209.06775) — Macpherson — *Cosmological distances with general-relativistic ray tracing: framework and comparison to cosmographic predictions* — ray-tracing framework for NR spacetimes
- · [arXiv:2402.09659](https://arxiv.org/abs/2402.09659) — Macpherson — *The impact of anisotropic sky-sampling on the Hubble constant in numerical relativity*
- · [arXiv:2402.12165](https://arxiv.org/abs/2402.12165) — (authors include H. J. Macpherson) — *Towards Cosmography of the Local Universe*
- · [arXiv:2507.01095](https://arxiv.org/abs/2507.01095) — (authors include H. J. Macpherson) — *A theoretical prediction for the dipole in nearby distances using cosmography*
- · [arXiv:2212.13569](https://arxiv.org/abs/2212.13569) — (authors include H. J. Macpherson) — *Potential signature of a quadrupolar Hubble expansion in Pantheon+ supernovae*
- · [arXiv:2205.12692](https://arxiv.org/abs/2205.12692) — Dhawan, Borderies, Macpherson, Heinesen — *The quadrupole in the local Hubble parameter: first constraints using Type Ia supernova data and forecasts for future surveys*
- · [arXiv:1910.13380](https://arxiv.org/abs/1910.13380) — (authors include H. J. Macpherson) — *Inhomogeneous cosmology in an anisotropic Universe*
- ◆ [arXiv:2403.15134](https://arxiv.org/abs/2403.15134) — Williams, Macpherson, Wiltshire, Stevens — *First investigation of void statistics in numerical relativity simulations* — connection to timescape
- · [arXiv:2404.06242](https://arxiv.org/abs/2404.06242) — Koksbang, Heinesen, Macpherson — *Redshift drift in a universe with structure III: Numerical relativity*
- ◆ [arXiv:2408.03049](https://arxiv.org/abs/2408.03049) — Oestreicher, Koksbang — *Backreaction in Numerical Relativity: Averaging on Newtonian gauge-like hypersurfaces in Einstein Toolkit cosmological simulations*
- ◆ [arXiv:2603.24838](https://arxiv.org/abs/2603.24838) — Macpherson — *Large-scale weak lensing convergence in nonlinear general relativity* — 2026
- ★ [arXiv:2606.05479](https://arxiv.org/abs/2606.05479) — Macpherson, Valogiannis — *On the potential for inhomogeneities to mimic an evolving dark energy* — 2026; link to DESI evolving dark energy
- · [arXiv:2606.18437](https://arxiv.org/abs/2606.18437) — Nguyen, Blake, Macpherson — *Impact of inhomogeneous curvature on growth rate measurements from magnitude fluctuations* — 2026
- · [arXiv:2107.06306](https://arxiv.org/abs/2107.06306) — Grasso, Villa, Korzyński, Matarrese — *BiGONLight: light propagation with bilocal operators in numerical relativity*
- · [arXiv:1604.04001](https://arxiv.org/abs/1604.04001) — Braden, Johnson, Peiris, Aguirre — *Constraining cosmological ultralarge scale structure using numerical relativity*
- · [arXiv:1409.3476](https://arxiv.org/abs/1409.3476) — Rekier, Cordero-Carrión, Füzfa — *Fully relativistic non-linear cosmological evolution in spherical symmetry using the BSSN formalism*
- · [arXiv:1409.7953](https://arxiv.org/abs/1409.7953) — Torres et al. — *Cosmological nonlinear structure formation in full general relativity*
- · [arXiv:1501.06918](https://arxiv.org/abs/1501.06918) — Alcubierre, de la Macorra, Diez-Tejedor, Torres — *Cosmological scalar field perturbations can grow*
- · [arXiv:1801.08362](https://arxiv.org/abs/1801.08362) — *Numerical Relativity Investigation of the Effects of Gravitational Waves on the Inhomogeneity of the Universe*
- · [arXiv:1505.02959](https://arxiv.org/abs/1505.02959) — Ikeda, Yoo, Nambu — *Expanding universe with nonlinear gravitational waves*
- · [arXiv:1811.00762](https://arxiv.org/abs/1811.00762) — Yoo, Ikeda, Okawa — *Gravitational Collapse of a Massless Scalar Field in a Periodic Box* — gravitational collapse in a periodic box

### G08 Weak-field and constrained-formulation relativistic N-body; relativistic reading of Newtonian simulations (65 entries)

- ◆ [arXiv:1308.6524](https://arxiv.org/abs/1308.6524) — Adamek, Daverio, Durrer, Kunz — *General Relativistic N-body simulations in the weak field limit*
- ★ [arXiv:1509.01699](https://arxiv.org/abs/1509.01699) — Adamek, Daverio, Durrer, Kunz — *General relativity and cosmic structure formation*
- ★ [arXiv:1604.06065](https://arxiv.org/abs/1604.06065) — Adamek, Daverio, Durrer, Kunz — *gevolution: a cosmological N-body code based on General Relativity* — weak-field expansion; six metric degrees of freedom in Poisson gauge
- · [arXiv:1408.3352](https://arxiv.org/abs/1408.3352) — Adamek, Durrer, Kunz — *N-body methods for relativistic cosmology*
- ◆ [arXiv:1408.2741](https://arxiv.org/abs/1408.2741) — Adamek, Clarkson, Durrer, Kunz — *Does small scale structure significantly affect cosmological dynamics?*
- ◆ [arXiv:1706.09309](https://arxiv.org/abs/1706.09309) — Adamek, Clarkson, Daverio, Durrer, Kunz — *Safely smoothing spacetime: backreaction in relativistic cosmological simulations*
- ◆ [arXiv:1707.06938](https://arxiv.org/abs/1707.06938) — Adamek, Durrer, Kunz — *Relativistic N-body simulations with massive neutrinos* — relativistic particle species
- · [arXiv:1812.04336](https://arxiv.org/abs/1812.04336) — Adamek, Clarkson, Coates, Durrer, Kunz — *Bias and scatter in the Hubble diagram from cosmological large-scale structure*
- · [arXiv:2002.04024](https://arxiv.org/abs/2002.04024) — Lepori, Adamek, Durrer, Clarkson, Coates — *Weak-lensing observables in relativistic N-body simulations*
- · [arXiv:1509.01163](https://arxiv.org/abs/1509.01163) — Adamek, Gosenca, Hotchkiss — *Spherically Symmetric N-body Simulations with General Relativistic Dynamics*
- · [arXiv:1508.05610](https://arxiv.org/abs/1508.05610) — Daverio, Hindmarsh, Bevis — *LATfield2: A c++ library for classical lattice field theory*
- ★ [arXiv:2607.17929](https://arxiv.org/abs/2607.17929) — Adamek, Christiansen — *gevolution 2.0: GPU-accelerated relativistic N-body simulations for cosmology* — 2026; latest benchmark of the weak-field route
- ◆ [arXiv:2404.02783](https://arxiv.org/abs/2404.02783) — Montandon, Hahn, Stahl — *Simulating the Universe from the cosmological horizon to halo scales* — gevolution displacement field + Gadget-4
- · [arXiv:2603.24179](https://arxiv.org/abs/2603.24179) — Magi, Lepori, Adamek — *Perturbative and numerical study of nonlinear relativistic effects in weak lensing* — 2026
- · [arXiv:2106.01347](https://arxiv.org/abs/2106.01347) — Lepori, Adamek, Durrer — *Cosmological simulations of number counts*
- · [arXiv:2209.10533](https://arxiv.org/abs/2209.10533) — *The halo bias for number counts on the light cone from relativistic N-body simulations*
- · [arXiv:2011.12936](https://arxiv.org/abs/2011.12936) — Coates, Adamek, Bull, Guandalin, Clarkson — *Observing relativistic features in large-scale structure surveys – II. Doppler magnification in an ensemble of relativistic simulations*
- · [arXiv:2009.02284](https://arxiv.org/abs/2009.02284) — Guandalin et al. — *Observing relativistic features in large-scale structure surveys – I. Multipoles of the power spectrum*
- · [arXiv:2505.04731](https://arxiv.org/abs/2505.04731) — Oestreicher, Clarkson, Adamek, Koksbang — *Redshift Drift in Relativistic N-Body Simulations*
- · [arXiv:2510.05956](https://arxiv.org/abs/2510.05956) — *Transverse Velocities in Real-Time Cosmology: Position Drift in Relativistic N-Body Simulations*
- ◆ [arXiv:2508.20606](https://arxiv.org/abs/2508.20606) — Adamek, Boschetti — *Incorporating curved geometry in cosmological simulations* — approach to non-periodic, curved geometries
- ★ [arXiv:1905.08890](https://arxiv.org/abs/1905.08890) — Barrera-Hinojosa, Li — *GRAMSES: a new route to general relativistic N-body simulations in cosmology. Part I. Methodology and code description* — constrained formulation + AMR particles
- ◆ [arXiv:2001.07968](https://arxiv.org/abs/2001.07968) — Barrera-Hinojosa, Li — *GRAMSES: a new route to general relativistic N-body simulations in cosmology. Part II. Initial conditions*
- · [arXiv:2010.08257](https://arxiv.org/abs/2010.08257) — Barrera-Hinojosa, Li, Bruni, He — *Vector modes in ΛCDM: the gravitomagnetic potential in dark matter haloes from relativistic N-body simulations*
- · [arXiv:2109.02632](https://arxiv.org/abs/2109.02632) — Barrera-Hinojosa, Li, Cai — *Looking for a twist: probing the cosmological gravitomagnetic effect via weak lensing-kSZ cross-correlations*
- · [arXiv:2301.11854](https://arxiv.org/abs/2301.11854) — Quintana-Miranda, Monaco, Tornatore — *GrGadget: an N-body TreePM relativistic code for cosmological simulations*
- · [arXiv:1806.05146](https://arxiv.org/abs/1806.05146) — Jelic-Cizmek, Lepori, Adamek, Durrer — *The generation of vorticity in cosmological N-body simulations*
- · [arXiv:2512.08703](https://arxiv.org/abs/2512.08703) — *The frame-dragging vector potential on galaxy scales from Dark-Matter-only Newtonian N-body simulations*
- ◆ [arXiv:1101.3555](https://arxiv.org/abs/1101.3555) — Chisari, Zaldarriaga — *Connection between Newtonian simulations and general relativity*
- ◆ [arXiv:1111.2997](https://arxiv.org/abs/1111.2997) — Green, Wald — *Newtonian and Relativistic Cosmologies*
- · [arXiv:1207.2035](https://arxiv.org/abs/1207.2035) — Flender, Schwarz — *Newtonian versus relativistic cosmology*
- ◆ [arXiv:1505.04756](https://arxiv.org/abs/1505.04756) — Fidler, Rampf, Tram, Crittenden, Koyama, Wands — *General relativistic corrections to N-body simulations and the Zel'dovich approximation* — N-body gauge
- ◆ [arXiv:1606.05588](https://arxiv.org/abs/1606.05588) — Fidler, Tram, Rampf, Crittenden, Koyama, Wands — *Relativistic Interpretation of Newtonian Simulations for Cosmic Structure Formation*
- · [arXiv:1708.07769](https://arxiv.org/abs/1708.07769) — Fidler et al. — *General relativistic weak-field limit and Newtonian N-body simulations*
- ◆ [arXiv:1702.03221](https://arxiv.org/abs/1702.03221) — Fidler et al. — *Relativistic initial conditions for N-body simulations*
- · [arXiv:1602.07699](https://arxiv.org/abs/1602.07699) — Hahn, Paranjape — *General relativistic screening in cosmological simulations*
- · [arXiv:1610.04236](https://arxiv.org/abs/1610.04236) — Brandbyge, Rampf, Tram, Leclercq, Fidler, Hannestad — *Cosmological N-body simulations including radiation perturbations*
- · [arXiv:1703.08585](https://arxiv.org/abs/1703.08585) — Adamek, Brandbyge, Fidler, Hannestad, Rampf, Tram — *The effect of early radiation in N-body simulations of cosmic structure formation*
- · [arXiv:1811.00904](https://arxiv.org/abs/1811.00904) — Tram, Brandbyge, Dakin, Hannestad — *Fully relativistic treatment of light neutrinos in N-body simulations*
- · [arXiv:1904.11773](https://arxiv.org/abs/1904.11773) — Dakin, Hannestad, Tram — *Fully relativistic treatment of decaying cold dark matter in N-body simulations* — treatment of decaying matter
- · [arXiv:1712.03944](https://arxiv.org/abs/1712.03944) — Dakin, Brandbyge, Hannestad, Haugbølle, Tram — *νCONCEPT: Cosmological neutrino simulations from the non-linear Boltzmann hierarchy*
- · [arXiv:2112.01508](https://arxiv.org/abs/2112.01508) — Dakin, Hannestad, Tram — *The cosmological simulation code CONCEPT 1.0*
- · [arXiv:1807.03701](https://arxiv.org/abs/1807.03701) — Fidler, Kleinjohann, Tram, Rampf, Koyama — *A new approach to cosmological structure formation with massive neutrinos*
- · [arXiv:1905.11721](https://arxiv.org/abs/1905.11721) — Adamek, Fidler — *The large-scale general-relativistic correction for Newtonian mocks*
- · [arXiv:1703.03407](https://arxiv.org/abs/1703.03407) — Borzyszkowski, Bertacca, Porciani — *LIGER: mock relativistic light-cones from Newtonian simulations*
- · [arXiv:1803.04294](https://arxiv.org/abs/1803.04294) — Breton, Rasera, Taruya, Lacombe, Saga — *Imprints of relativistic effects on the asymmetry of the halo cross-correlation function: from linear to non-linear scales*
- · [arXiv:2111.08745](https://arxiv.org/abs/2111.08745) — Rasera et al. — *The RayGalGroupSims cosmological simulation suite for the study of relativistic effects: an application to lensing-matter clustering statistics*
- · [arXiv:1306.1562](https://arxiv.org/abs/1306.1562) — Bruni, Thomas, Wands — *Computing General Relativistic effects from Newtonian N-body simulations: Frame dragging in the post-Friedmann approach*
- · [arXiv:1501.00799](https://arxiv.org/abs/1501.00799) — Thomas, Bruni, Wands — *The fully non-linear post-Friedmann frame-dragging vector potential: Magnitude and time evolution from N-body simulations*
- · [arXiv:1403.4947](https://arxiv.org/abs/1403.4947) — Thomas, Bruni, Wands — *Relativistic weak lensing from a fully non-linear cosmological density field*
- · [arXiv:1502.02985](https://arxiv.org/abs/1502.02985) — Milillo, Bertacca, Bruni, Maselli — *Missing link: A nonlinear post-Friedmann framework for small and large scales*
- · [arXiv:1307.1478](https://arxiv.org/abs/1307.1478) — Bruni, Hidalgo, Meures, Wands — *Non-Gaussian Initial Conditions in ΛCDM: Newtonian, Relativistic, and Primordial Contributions*
- · [arXiv:1505.04782](https://arxiv.org/abs/1505.04782) — Villa, Rampf — *Relativistic perturbations in ΛCDM: Eulerian & Lagrangian approaches*
- ◆ [arXiv:2110.11249](https://arxiv.org/abs/2110.11249) — Adamek, Calles, Montandon, Noreña, Stahl — *Relativistic second-order initial conditions for simulations of large-scale structure* — relativistic second-order initial conditions
- · [arXiv:2212.06799](https://arxiv.org/abs/2212.06799) — Montandon et al. — *Relativistic matter bispectrum of cosmic structures on the light cone*
- · [arXiv:2109.13364](https://arxiv.org/abs/2109.13364) — *Including relativistic and primordial non-Gaussianity contributions in cosmological simulations by modifying the initial conditions*
- · [arXiv:0907.0707](https://arxiv.org/abs/0907.0707) — Yoo, Fitzpatrick, Zaldarriaga — *A New Perspective on Galaxy Clustering as a Cosmological Probe: General Relativistic Effects*
- · [arXiv:1105.5280](https://arxiv.org/abs/1105.5280) — Bonvin, Durrer — *What galaxy surveys really measure*
- · [arXiv:1105.5292](https://arxiv.org/abs/1105.5292) — Challinor, Lewis — *The linear power spectrum of observed source number counts*
- · [arXiv:1107.5427](https://arxiv.org/abs/1107.5427) — Jeong, Schmidt, Hirata — *Large-scale clustering of galaxies in general relativity*
- · [arXiv:1910.04894](https://arxiv.org/abs/1910.04894) — Gallagher, Clifton, Clarkson — *Multi-Scale Perturbation Theory I: Methodology and Leading-Order Bispectrum Corrections in the Matter-Dominated Era*
- ◆ [arXiv:2001.00394](https://arxiv.org/abs/2001.00394) — Clifton, Gallagher, Goldberg, Malik — *Viable Gauge Choices in Cosmologies with Non-Linear Structures*
- · [arXiv:1610.08882](https://arxiv.org/abs/1610.08882) — Goldberg, Clifton, Malik — *Cosmology on all scales: a two-parameter perturbation expansion*
- · [arXiv:1503.08747](https://arxiv.org/abs/1503.08747) — Sanghai, Clifton — *Post-Newtonian Cosmological Modelling*
- · [arXiv:2203.04009](https://arxiv.org/abs/2203.04009) — Marra et al. — *The BEHOMO project: ΛLTB N-body simulations*

### G09 Backreaction, averaging, light propagation, timescape, tensions and anomalies (79 entries)

- ★ [arXiv:gr-qc/9906015](https://arxiv.org/abs/gr-qc/9906015) — Buchert — *On average properties of inhomogeneous fluids in general relativity I: dust cosmologies* — Buchert averaging equations
- · [arXiv:astro-ph/9510056](https://arxiv.org/abs/astro-ph/9510056) — Buchert, Ehlers — *Averaging inhomogeneous Newtonian cosmologies*
- · [arXiv:0707.2153](https://arxiv.org/abs/0707.2153) — Buchert — *Dark Energy from Structure: A Status Report*
- · [arXiv:1912.04213](https://arxiv.org/abs/1912.04213) — Buchert, Mourier, Roy — *On average properties of inhomogeneous fluids in general relativity III: general fluid cosmologies*
- · [arXiv:2202.10798](https://arxiv.org/abs/2202.10798) — Buchert, van Elst, Heinesen — *The averaging problem on the past null cone in inhomogeneous dust cosmologies*
- ◆ [arXiv:1112.5335](https://arxiv.org/abs/1112.5335) — Buchert, Räsänen — *Backreaction in late-time cosmology* — review
- ◆ [arXiv:1109.2314](https://arxiv.org/abs/1109.2314) — Clarkson, Ellis, Larena, Umeh — *Does the growth of structure affect our dynamical models of the universe? The averaging, backreaction and fitting problems in cosmology* — review
- ★ [arXiv:1505.07800](https://arxiv.org/abs/1505.07800) — Buchert et al. — *Is there proof that backreaction of inhomogeneities is irrelevant in cosmology?* — response to Green–Wald
- ★ [arXiv:1011.4920](https://arxiv.org/abs/1011.4920) — Green, Wald — *A new framework for analyzing the effects of small scale inhomogeneities in cosmology* — argument that the effective stress is traceless
- ◆ [arXiv:1407.8084](https://arxiv.org/abs/1407.8084) — Green, Wald — *How well is our universe described by an FLRW model?*
- · [arXiv:gr-qc/0509108](https://arxiv.org/abs/gr-qc/0509108) — Ishibashi, Wald — *Can the acceleration of our universe be explained by the effects of inhomogeneities?*
- · [arXiv:hep-ph/0409038](https://arxiv.org/abs/hep-ph/0409038) — Kolb, Matarrese, Notari, Riotto — *The effect of inhomogeneities on the expansion rate of the universe*
- · [arXiv:1102.0408](https://arxiv.org/abs/1102.0408) — Räsänen — *Backreaction: directions of progress*
- · [arXiv:1002.4779](https://arxiv.org/abs/1002.4779) — Räsänen — *Applicability of the linearly perturbed FRW metric and Newtonian cosmology*
- · [arXiv:1703.08809](https://arxiv.org/abs/1703.08809) — Kaiser — *Why there is no Newtonian backreaction*
- · [arXiv:0710.5073](https://arxiv.org/abs/0710.5073) — Li, Schwarz — *Scale dependence of cosmological backreaction*
- ◆ [arXiv:1612.08222](https://arxiv.org/abs/1612.08222) — Bolejko, Korzyński — *Inhomogeneous cosmology and backreaction: current status and future prospects* — review
- · [arXiv:2106.06043](https://arxiv.org/abs/2106.06043) — Schander, Thiemann — *Backreaction in Cosmology* — review
- ◆ [arXiv:2509.01320](https://arxiv.org/abs/2509.01320) — Fleury — *Elements of cosmology beyond FLRW* — 2025 Les Houches lecture notes
- · [arXiv:2310.19451](https://arxiv.org/abs/2310.19451) — Verweg, Jones, van de Weygaert — *Averaging over cosmic structure: Cosmological backreaction and the gauge problem*
- · [arXiv:2409.00024](https://arxiv.org/abs/2409.00024) — Verweg, Jones, van de Weygaert — *Cosmic averaging over multiscaled structure: on foliations, gauges and backreaction*
- ◆ [arXiv:gr-qc/0702082](https://arxiv.org/abs/gr-qc/0702082) — Wiltshire — *Cosmic clocks, cosmic variance and cosmic averages* — timescape
- · [arXiv:0909.0749](https://arxiv.org/abs/0909.0749) — Wiltshire — *Average observational quantities in the timescape cosmology*
- ◆ [arXiv:2311.01438](https://arxiv.org/abs/2311.01438) — Lane et al. — *Cosmological foundations revisited with Pantheon+*
- ◆ [arXiv:2412.15143](https://arxiv.org/abs/2412.15143) — Seifert et al. — *Supernovae evidence for foundational change to cosmological models*
- ◆ [arXiv:2406.05048](https://arxiv.org/abs/2406.05048) — DES Collaboration — *The Dark Energy Survey Supernova Program: Investigating Beyond-ΛCDM* — includes a test of timescape
- · [arXiv:1607.08797](https://arxiv.org/abs/1607.08797) — Rácz et al. — *Concordance cosmology without dark energy*
- · [arXiv:1708.09143](https://arxiv.org/abs/1708.09143) — Bolejko — *Relativistic numerical cosmology with Silent Universes*
- · [arXiv:1712.02967](https://arxiv.org/abs/1712.02967) — Bolejko — *Emerging spatial curvature can resolve the tension between high-redshift CMB and low-redshift distance ladder measurements of the Hubble constant*
- · [arXiv:2002.10831](https://arxiv.org/abs/2002.10831) — Heinesen, Buchert — *Solving the curvature and Hubble parameter inconsistencies through structure formation-induced curvature*
- · [arXiv:1104.1167](https://arxiv.org/abs/1104.1167) — Gasperini, Marozzi, Nugier, Veneziano — *Light-cone averaging in cosmology: Formalism and applications*
- · [arXiv:1207.1286](https://arxiv.org/abs/1207.1286) — Ben-Dayan, Gasperini, Marozzi, Nugier, Veneziano — *Do stochastic inhomogeneities affect dark-energy precision measurements?*
- · [arXiv:1911.09469](https://arxiv.org/abs/1911.09469) — Fanizza, Gasperini, Marozzi, Veneziano — *Generalized covariant prescriptions for averaging cosmological observables*
- · [arXiv:1503.08506](https://arxiv.org/abs/1503.08506) — Kaiser, Peacock — *On the Bias of the Distance-Redshift Relation from Gravitational Lensing*
- · [arXiv:1503.07831](https://arxiv.org/abs/1503.07831) — Bonvin, Clarkson, Durrer, Maartens, Umeh — *Do we care about the distance to the CMB? Clarifying the impact of second-order lensing*
- · [arXiv:astro-ph/0412275](https://arxiv.org/abs/astro-ph/0412275) — Kibble, Lieu — *Average magnification effect of clumping of matter*
- · [arXiv:astro-ph/0511183](https://arxiv.org/abs/astro-ph/0511183) — Bonvin, Durrer, Gasparini — *Fluctuations of the luminosity distance*
- · [arXiv:1302.5308](https://arxiv.org/abs/1302.5308) — Fleury, Dupuy, Uzan — *Interpretation of the Hubble diagram in a nonhomogeneous universe*
- · [arXiv:1304.7791](https://arxiv.org/abs/1304.7791) — Fleury, Dupuy, Uzan — *Can all cosmological observations be accurately interpreted with a unique geometry?*
- · [arXiv:1612.03726](https://arxiv.org/abs/1612.03726) — Fleury, Clarkson, Maartens — *How does the cosmic large-scale structure bias the Hubble diagram?*
- · [arXiv:1109.2484](https://arxiv.org/abs/1109.2484) — Clarkson et al. — *(Mis-)Interpreting supernovae observations in a lumpy universe*
- · [arXiv:1204.0909](https://arxiv.org/abs/1204.0909) — *Ricci focusing, shearing, and the expansion rate in an almost homogeneous Universe*
- · [arXiv:2012.07802](https://arxiv.org/abs/2012.07802) — Breton, Fleury — *Theoretical and numerical perspectives on cosmic distance averages*
- ◆ [arXiv:2010.06534](https://arxiv.org/abs/2010.06534) — Heinesen — *Multipole decomposition of the general luminosity distance 'Hubble law' -- a new framework for observational cosmology*
- · [arXiv:2102.03774](https://arxiv.org/abs/2102.03774) — Heinesen — *Redshift drift as a model independent probe of dark energy*
- · [arXiv:2107.08674](https://arxiv.org/abs/2107.08674) — Heinesen — *Redshift drift cosmography for model-independent cosmological inference*
- · [arXiv:1909.13489](https://arxiv.org/abs/1909.13489) — Koksbang — *Another look at redshift drift and the backreaction conjecture*
- · [arXiv:2008.07108](https://arxiv.org/abs/2008.07108) — Koksbang — *Observations in statistically homogeneous, locally inhomogeneous cosmological toy-models without FLRW backgrounds*
- · [arXiv:2105.11880](https://arxiv.org/abs/2105.11880) — Koksbang — *Searching for signals of inhomogeneity using multiple probes of the cosmic expansion rate H(z)*
- · [arXiv:2205.11907](https://arxiv.org/abs/2205.11907) — Koksbang, Heinesen — *Redshift drift in a universe with structure I: Lemaître-Tolman-Bondi structures with arbitrary angle of entry of light*
- · [arXiv:2604.26690](https://arxiv.org/abs/2604.26690) — Béchaz, Fanizza, Marozzi, Medeiros Silva — *Nonlinear Relativistic Effects on Cosmological Redshift Drift* — 2026
- ◆ [arXiv:2601.20633](https://arxiv.org/abs/2601.20633) — Ginat, Ferreira — *Apparent Dark-Energy Evolution from Cosmic Inhomogeneities* — 2026
- · [arXiv:2507.17969](https://arxiv.org/abs/2507.17969) — *Designing concordant distances in the age of precision cosmology: The impact of density fluctuations*
- · [arXiv:2512.10585](https://arxiv.org/abs/2512.10585) — *Is Dark Energy Dynamical in the DESI Era? A Critical Review*
- · [arXiv:2404.03002](https://arxiv.org/abs/2404.03002) — DESI Collaboration — *DESI 2024 VI: Cosmological Constraints from the Measurements of Baryon Acoustic Oscillations*
- ◆ [arXiv:2503.14738](https://arxiv.org/abs/2503.14738) — DESI Collaboration — *DESI DR2 Results II: Measurements of Baryon Acoustic Oscillations and Cosmological Constraints*
- · [arXiv:2112.04510](https://arxiv.org/abs/2112.04510) — Riess et al. — *A Comprehensive Measurement of the Local Value of the Hubble Constant with 1 km/s/Mpc Uncertainty from the Hubble Space Telescope and the SH0ES Team*
- · [arXiv:2103.01183](https://arxiv.org/abs/2103.01183) — Di Valentino et al. — *In the realm of the Hubble tension—a review of solutions*
- · [arXiv:2504.01669](https://arxiv.org/abs/2504.01669) — CosmoVerse Network — *The CosmoVerse White Paper: Addressing observational tensions in cosmology with systematics and fundamental physics*
- · [arXiv:2203.06142](https://arxiv.org/abs/2203.06142) — Abdalla et al. — *Cosmology intertwined: A review of the particle physics, astrophysics, and cosmology associated with the cosmological tensions and anomalies*
- · [arXiv:2105.05208](https://arxiv.org/abs/2105.05208) — Perivolaropoulos, Skara — *Challenges for ΛCDM: An update*
- · [arXiv:2208.05018](https://arxiv.org/abs/2208.05018) — Peebles — *Anomalies in Physical Cosmology*
- ◆ [arXiv:2207.05765](https://arxiv.org/abs/2207.05765) — Aluri et al. — *Is the Observable Universe Consistent with the Cosmological Principle?*
- · [arXiv:2009.14826](https://arxiv.org/abs/2009.14826) — Secrest et al. — *A Test of the Cosmological Principle with Quasars*
- · [arXiv:2206.05624](https://arxiv.org/abs/2206.05624) — Secrest et al. — *A Challenge to the Standard Cosmological Model*
- · [arXiv:2302.02028](https://arxiv.org/abs/2302.02028) — Watkins et al. — *Analyzing the Large-Scale Bulk Flow using CosmicFlows4: Increasing Tension with the Standard Cosmological Model*
- · [arXiv:2305.16084](https://arxiv.org/abs/2305.16084) — *Bulk flows in the local Universe and the importance of relativistic effects*
- · [arXiv:2404.16719](https://arxiv.org/abs/2404.16719) — Tsagas — *General relativity and the bulk-flow puzzle*
- · [arXiv:2510.05340](https://arxiv.org/abs/2510.05340) — Tsagas, Perivolaropoulos, Asvesta — *Large-scale peculiar velocities in the universe* — review
- · [arXiv:1304.2884](https://arxiv.org/abs/1304.2884) — Keenan, Barger, Cowie — *Evidence for a ~300 Mpc Scale Under-density in the Local Galaxy Distribution*
- · [arXiv:2009.11292](https://arxiv.org/abs/2009.11292) — Haslbauer, Banik, Kroupa — *The KBC void and Hubble tension contradict ΛCDM on a Gpc scale − Milgromian dynamics as a possible solution*
- · [arXiv:2602.03928](https://arxiv.org/abs/2602.03928) — Banik, Desmond, Kalaitzidis, Mazurenko — *The local void model for the Hubble and BAO tensions*
- · [arXiv:2606.02712](https://arxiv.org/abs/2606.02712) — Banik, Nájera, Desmond — *Constraints on the gravitational potential from DESI DR2 BAO and its implications for the local void scenario*
- · [arXiv:1502.02011](https://arxiv.org/abs/1502.02011) — Dai, Pajer, Schmidt — *Conformal Fermi Coordinates*
- · [arXiv:1504.00351](https://arxiv.org/abs/1504.00351) — Dai, Pajer, Schmidt — *On Separate Universes*
- · [arXiv:2210.11426](https://arxiv.org/abs/2210.11426) — COMPACT Collaboration — *Promise of Future Searches for Cosmic Topology*
- · [arXiv:astro-ph/0602159](https://arxiv.org/abs/astro-ph/0602159) — Roukema et al. — *A weak acceleration effect due to residual gravity in a multiply connected universe* — physical effects of periodic topology
- · [arXiv:1104.1300](https://arxiv.org/abs/1104.1300) — Maartens — *Is the Universe homogeneous?*
- · [arXiv:1204.5505](https://arxiv.org/abs/1204.5505) — Clarkson — *Establishing homogeneity of the universe in the shadow of dark energy*

### G10 Black-hole lattices and discrete-mass universes (10 entries)

- ◆ [arXiv:1204.3568](https://arxiv.org/abs/1204.3568) — Bentivegna, Korzyński — *Evolution of a periodic eight-black-hole lattice in numerical relativity*
- · [arXiv:1306.4055](https://arxiv.org/abs/1306.4055) — Bentivegna, Korzyński — *Evolution of a family of expanding cubic black-hole lattices in numerical relativity*
- · [arXiv:1204.2411](https://arxiv.org/abs/1204.2411) — Yoo, Abe, Nakao, Takamori — *Black Hole Universe: Construction and Analysis of Initial Data*
- ◆ [arXiv:1306.1389](https://arxiv.org/abs/1306.1389) — Yoo, Okawa, Nakao — *Black Hole Universe: Time Evolution*
- · [arXiv:1404.1435](https://arxiv.org/abs/1404.1435) — Yoo, Okawa — *Black hole universe with a cosmological constant*
- · [arXiv:1610.05635](https://arxiv.org/abs/1610.05635) — Durk, Clifton — *Exact Initial Data for Black Hole Universes with a Cosmological Constant*
- · [arXiv:1611.09275](https://arxiv.org/abs/1611.09275) — Bentivegna, Korzyński, Hinder, Gerlicher — *Light propagation through black-hole lattices*
- ◆ [arXiv:1801.01083](https://arxiv.org/abs/1801.01083) — Bentivegna, Clifton, Durk, Korzyński, Rosquist — *Black-Hole Lattices as Cosmological Models* — review
- · [arXiv:1203.6478](https://arxiv.org/abs/1203.6478) — Clifton, Rosquist, Tavakol — *An Exact quantification of backreaction in relativistic cosmology*
- · [arXiv:1903.01490](https://arxiv.org/abs/1903.01490) — Giblin, Mertens, Starkman, Tian — *Cosmic expansion from spinning black holes*

### G11 Early-universe NR: initial conditions for inflation, stochastic inflation, contraction and bounces (39 entries)

- · [arXiv:astro-ph/9306009](https://arxiv.org/abs/astro-ph/9306009) — Kurki-Suonio, Laguna, Matzner — *Inhomogeneous inflation: Numerical evolution*
- · [arXiv:1601.01918](https://arxiv.org/abs/1601.01918) — Brandenberger — *Initial conditions for inflation — A short review*
- ◆ [arXiv:1511.05143](https://arxiv.org/abs/1511.05143) — East, Kleban, Linde, Senatore — *Beginning inflation in an inhomogeneous universe*
- ◆ [arXiv:1608.04408](https://arxiv.org/abs/1608.04408) — Clough, Lim, DiNunno, Fischler, Flauger, Paban — *Robustness of Inflation to Inhomogeneous Initial Conditions*
- · [arXiv:1712.07352](https://arxiv.org/abs/1712.07352) — Clough, Flauger, Lim — *Robustness of Inflation to Large Tensor Perturbations*
- · [arXiv:1910.12547](https://arxiv.org/abs/1910.12547) — Aurrekoetxea, Clough, Flauger, Lim — *The Effects of Potential Shape on Inhomogeneous Inflation*
- · [arXiv:2011.12190](https://arxiv.org/abs/2011.12190) — Joana, Clesse — *Inhomogeneous preinflation across Hubble scales in full general relativity*
- · [arXiv:2202.07604](https://arxiv.org/abs/2202.07604) — Joana — *Gravitational dynamics in Higgs inflation: Preinflation and preheating with an auxiliary field*
- · [arXiv:2212.04479](https://arxiv.org/abs/2212.04479) — Corman, East — *Starting inflation from inhomogeneous initial conditions with momentum*
- · [arXiv:2405.03490](https://arxiv.org/abs/2405.03490) — Elley et al. — *Robustness of inflation to kinetic inhomogeneities*
- · [arXiv:2304.12150](https://arxiv.org/abs/2304.12150) — Garfinkle, Ijjas, Steinhardt — *Initial conditions problem in cosmological inflation revisited*
- · [arXiv:1906.08651](https://arxiv.org/abs/1906.08651) — Bloomfield, Fitzpatrick, Hilbert, Kaiser — *Onset of inflation amid backreaction from inhomogeneities*
- · [arXiv:2406.00811](https://arxiv.org/abs/2406.00811) — Joana — *Beginning inflation in conformally curved spacetimes*
- · [arXiv:1607.00381](https://arxiv.org/abs/1607.00381) — East, Kearney, Shakya, Yoo, Zurek — *Spacetime Dynamics of a Higgs Vacuum Instability During Inflation*
- · [arXiv:2412.19731](https://arxiv.org/abs/2412.19731) — *Fully-relativistic evolution of vacuum tensor inhomogeneities during inflation*
- · [arXiv:2502.06783](https://arxiv.org/abs/2502.06783) — *Bunch-Davies initial conditions and non-perturbative inflationary dynamics in Numerical Relativity*
- · [arXiv:2512.13673](https://arxiv.org/abs/2512.13673) — Giannadakis, Elley, Flauger, Lim — *A critical value of the inflationary tensor-to-scalar ratio from inhomogeneous inflation*
- · [arXiv:2505.22763](https://arxiv.org/abs/2505.22763) — *Probability of the Initial Conditions for Inflation and Slow Contraction*
- · [arXiv:2607.06441](https://arxiv.org/abs/2607.06441) — *Starting inflation in asymptotically flat spacetimes* — 2026
- · [arXiv:2606.14853](https://arxiv.org/abs/2606.14853) — *The limits of lattice inflation: a cautionary tale* — 2026
- · [arXiv:2604.00978](https://arxiv.org/abs/2604.00978) — *Nonlinear Lattice Framework for Inflation: Bridging stochastic inflation and the δN formalism* — 2026
- · [arXiv:2401.08530](https://arxiv.org/abs/2401.08530) — Launay, Rigopoulos, Shellard — *Stochastic inflation in general relativity*
- · [arXiv:2512.14649](https://arxiv.org/abs/2512.14649) — Launay, Rigopoulos, Shellard — *Stochastic Inflation in Numerical Relativity*
- · [arXiv:2610.32592](https://arxiv.org/abs/2610.32592) — *Stochastic dynamics of cosmological inflation in general relativity* — 2026
- · [arXiv:1602.03520](https://arxiv.org/abs/1602.03520) — Kleban, Senatore — *Inhomogeneous Anisotropic Cosmology*
- · [arXiv:2004.10754](https://arxiv.org/abs/2004.10754) — Creminelli, Hershkovits, Senatore, Vasy — *A de Sitter no-hair theorem for 3+1d Cosmologies with isometry group forming 2-dimensional orbits*
- · [arXiv:1710.04278](https://arxiv.org/abs/1710.04278) — Linde — *On the problem of initial conditions for inflation*
- · [arXiv:0808.0542](https://arxiv.org/abs/0808.0542) — Garfinkle, Lim, Pretorius, Steinhardt — *Evolution to a smooth universe in an ekpyrotic contracting phase with w > 1*
- · [arXiv:1308.3044](https://arxiv.org/abs/1308.3044) — Xue, Garfinkle, Pretorius, Steinhardt — *Nonperturbative analysis of the evolution of cosmological perturbations through a nonsingular bounce*
- · [arXiv:2006.01172](https://arxiv.org/abs/2006.01172) — Cook, Glushchenko, Ijjas, Pretorius, Steinhardt — *Supersmoothing through Slow Contraction*
- · [arXiv:2006.04999](https://arxiv.org/abs/2006.04999) — Ijjas et al. — *Robustness of slow contraction to cosmic initial conditions*
- · [arXiv:2103.00584](https://arxiv.org/abs/2103.00584) — Ijjas et al. — *Ultralocality and slow contraction*
- · [arXiv:2104.12293](https://arxiv.org/abs/2104.12293) — Ijjas, Pretorius, Steinhardt, Sullivan — *The Effects of Multiple Modes and Reduced Symmetry on the Rapidity and Robustness of Slow Contraction*
- · [arXiv:2109.09768](https://arxiv.org/abs/2109.09768) — Ijjas, Pretorius, Steinhardt, Garfinkle — *Dynamical attractors in contracting spacetimes dominated by kinetically coupled scalar fields*
- · [arXiv:2205.01519](https://arxiv.org/abs/2205.01519) — Kist, Ijjas — *The robustness of slow contraction and the shape of the scalar field potential*
- · [arXiv:2404.00867](https://arxiv.org/abs/2404.00867) — Ijjas et al. — *Smoothing and flattening the universe through slow contraction versus inflation*
- · [arXiv:2206.08466](https://arxiv.org/abs/2206.08466) — Corman, East, Ripley — *Evolution of black holes through a nonsingular cosmological bounce*
- ◆ [arXiv:2201.03752](https://arxiv.org/abs/2201.03752) — Ijjas — *Numerical Relativity as a New Tool for Fundamental Cosmology* — review
- · [arXiv:2602.10223](https://arxiv.org/abs/2602.10223) — Jiménez-Aguilar — *Accelerated expansion of the universe purely driven by scalar field fluctuations*

### G12 Preheating, oscillons and post-inflationary scalar-field structure (25 entries)

- ◆ [arXiv:1907.10601](https://arxiv.org/abs/1907.10601) — Giblin, Tishue — *Preheating in Full General Relativity*
- · [arXiv:1912.09658](https://arxiv.org/abs/1912.09658) — Kou, Tian, Zhou — *Oscillon Preheating in Full General Relativity*
- · [arXiv:2112.07626](https://arxiv.org/abs/2112.07626) — Kou, Mertens, Tian, Zhou — *Gravitational waves from fully general relativistic oscillon preheating*
- · [arXiv:2311.01504](https://arxiv.org/abs/2311.01504) — Adshead, Giblin, Grutkoski, Weiner — *Gauge preheating with full general relativity*
- · [arXiv:2304.01673](https://arxiv.org/abs/2304.01673) — Aurrekoetxea, Clough, Muia — *Oscillon formation during inflationary preheating with general relativity*
- · [arXiv:2504.08939](https://arxiv.org/abs/2504.08939) — (authors include H. J. Macpherson) — *The Effect of Nonlinear Gravity on the Cosmological Background During Preheating*
- · [arXiv:1005.4054](https://arxiv.org/abs/1005.4054) — Bastero-Gil, Macias, Santos — *Non-linear metric perturbation enhancement of primordial gravitational waves*
- · [arXiv:0709.3510](https://arxiv.org/abs/0709.3510) — Bastero-Gil, Tristram, Macias, Santos — *Non-linear Preheating with Scalar Metric Perturbations*
- · [arXiv:hep-ph/9809574](https://arxiv.org/abs/hep-ph/9809574) — Parry, Easther — *Preheating and the Einstein field equations*
- · [arXiv:1410.3808](https://arxiv.org/abs/1410.3808) — Amin, Hertzberg, Kaiser, Karouby — *Nonperturbative Dynamics Of Reheating After Inflation: A Review* — review
- · [arXiv:1106.3335](https://arxiv.org/abs/1106.3335) — Amin et al. — *Oscillons After Inflation*
- · [arXiv:2006.15122](https://arxiv.org/abs/2006.15122) — Figueroa, Florio, Torrenti, Valkenburg — *The art of simulating the early Universe -- Part I: Integration techniques and canonical cases*
- · [arXiv:2010.05933](https://arxiv.org/abs/2010.05933) — Nazari, Cicoli, Clough, Muia — *Oscillon collapse to black holes*
- · [arXiv:1906.09346](https://arxiv.org/abs/1906.09346) — Muia et al. — *The Fate of Dense Scalar Stars*
- · [arXiv:1909.11678](https://arxiv.org/abs/1909.11678) — Musoke, Hotchkiss, Easther — *Lighting the Dark: Evolution of the Postinflationary Universe*
- ◆ [arXiv:2011.13333](https://arxiv.org/abs/2011.13333) — Eggemeier, Niemeyer, Easther — *Formation of inflaton halos after inflation* — halo formation in the post-inflationary early matter-dominated era
- · [arXiv:2110.15109](https://arxiv.org/abs/2110.15109) — Eggemeier, Schwabe, Niemeyer, Easther — *Gravitational collapse in the postinflationary Universe*
- · [arXiv:1911.01661](https://arxiv.org/abs/1911.01661) — Niemeyer, Easther — *Inflaton clusters and inflaton stars*
- · [arXiv:2311.08780](https://arxiv.org/abs/2311.08780) — *Postinflationary structure formation boosted by parametric self-resonance*
- · [arXiv:2204.07152](https://arxiv.org/abs/2204.07152) — *Enhanced Gravitational Waves from Inflaton Oscillons*
- · [arXiv:1002.3039](https://arxiv.org/abs/1002.3039) — Jedamzik, Lemoine, Martin — *Collapse of Small-Scale Density Perturbations during Preheating in Single Field Inflation*
- · [arXiv:2110.14584](https://arxiv.org/abs/2110.14584) — Padilla, Hidalgo, Malik — *A new mechanism for primordial black hole formation during reheating*
- · [arXiv:1806.09367](https://arxiv.org/abs/1806.09367) — Widdicombe, Helfer, Marsh, Lim — *Formation of Relativistic Axion Stars*
- · [arXiv:1609.04724](https://arxiv.org/abs/1609.04724) — Helfer et al. — *Black hole formation from axion stars*
- · [arXiv:1802.10085](https://arxiv.org/abs/1802.10085) — Michel, Moss — *Relativistic collapse of axion stars*

### G13 Primordial-black-hole formation: radiation era and general (49 entries)

- ◆ [arXiv:gr-qc/9905064](https://arxiv.org/abs/gr-qc/9905064) — Shibata, Sasaki — *Black hole formation in the Friedmann universe: Formulation and computation in numerical relativity*
- ◆ [arXiv:astro-ph/9709072](https://arxiv.org/abs/astro-ph/9709072) — Niemeyer, Jedamzik — *Near-critical gravitational collapse and the initial mass function of primordial black holes* — critical scaling in the PBH mass function
- · [arXiv:astro-ph/9901292](https://arxiv.org/abs/astro-ph/9901292) — Niemeyer, Jedamzik — *Dynamics of Primordial Black Hole Formation*
- · [arXiv:gr-qc/0412063](https://arxiv.org/abs/gr-qc/0412063) — Musco, Miller, Rezzolla — *Computations of primordial black hole formation*
- · [arXiv:gr-qc/0605122](https://arxiv.org/abs/gr-qc/0605122) — Polnarev, Musco — *Curvature profiles as initial conditions for primordial black hole formation*
- · [arXiv:0811.1452](https://arxiv.org/abs/0811.1452) — Musco, Miller, Polnarev — *Primordial black hole formation in the radiative era: investigation of the critical nature of the collapse*
- · [arXiv:1201.2379](https://arxiv.org/abs/1201.2379) — Musco, Miller — *Primordial black hole formation in the early universe: critical behaviour and self-similarity*
- ◆ [arXiv:1309.4201](https://arxiv.org/abs/1309.4201) — Harada, Yoo, Kohri — *Threshold of primordial black hole formation*
- ◆ [arXiv:1503.03934](https://arxiv.org/abs/1503.03934) — Harada, Yoo, Nakama, Koga — *Cosmological long-wavelength solutions and primordial black hole formation* — super-horizon long-wavelength initial data
- · [arXiv:1504.02071](https://arxiv.org/abs/1504.02071) — Bloomfield, Bulhosa, Face — *Formalism for Primordial Black Hole Formation in Spherical Symmetry*
- · [arXiv:1809.02127](https://arxiv.org/abs/1809.02127) — Musco — *Threshold for primordial black holes: Dependence on the shape of the cosmological perturbations*
- · [arXiv:1907.13065](https://arxiv.org/abs/1907.13065) — Escrivà — *Simulation of primordial black hole formation using pseudo-spectral methods*
- · [arXiv:1907.13311](https://arxiv.org/abs/1907.13311) — Escrivà, Germani, Sheth — *Universal threshold for primordial black hole formation*
- · [arXiv:2103.03867](https://arxiv.org/abs/2103.03867) — Escrivà, Romano — *Effects of the shape of curvature peaks on the size of primordial black holes*
- · [arXiv:2110.05982](https://arxiv.org/abs/2110.05982) — Musco, Papanikolaou — *Primordial black hole formation for an anisotropic perfect fluid: Initial conditions and estimation of the threshold*
- ◆ [arXiv:2111.12693](https://arxiv.org/abs/2111.12693) — Escrivà — *PBH formation from spherically symmetric hydrodynamical perturbations: a review* — review
- ◆ [arXiv:2211.05767](https://arxiv.org/abs/2211.05767) — Escrivà, Kuhnel, Tada — *Primordial Black Holes* — review
- · [arXiv:2211.13512](https://arxiv.org/abs/2211.13512) — Yoo — *The Basics of Primordial Black Hole Formation and Abundance Estimation* — review
- · [arXiv:2002.12778](https://arxiv.org/abs/2002.12778) — Carr, Kohri, Sendouda, Yokoyama — *Constraints on primordial black holes*
- · [arXiv:2601.06024](https://arxiv.org/abs/2601.06024) — *Primordial black holes: constraints, potential evidence and prospects* — 2026 review
- · [arXiv:2606.30641](https://arxiv.org/abs/2606.30641) — *Primordial Black Holes in a Radiation-Dominated Universe* — 2026
- ◆ [arXiv:2004.01042](https://arxiv.org/abs/2004.01042) — Yoo, Harada, Okawa — *Threshold of Primordial Black Hole Formation in Nonspherical Collapse* — 3+1, non-spherical
- · [arXiv:2403.11147](https://arxiv.org/abs/2403.11147) — Yoo — *Primordial black hole formation from a nonspherical density profile with a misaligned deformation tensor*
- · [arXiv:2410.03451](https://arxiv.org/abs/2410.03451) — Escrivà, Yoo — *Nonspherical effects on the mass function of primordial black holes*
- · [arXiv:2410.03452](https://arxiv.org/abs/2410.03452) — Escrivà, Yoo — *Simulations of ellipsoidal primordial black hole formation*
- · [arXiv:2310.16482](https://arxiv.org/abs/2310.16482) — Escrivà, Yoo — *Primordial Black hole formation from overlapping cosmological fluctuations*
- ◆ [arXiv:2609.03051](https://arxiv.org/abs/2609.03051) — Escrivà — *Beyond isolated curvature peaks: collective collapse and multiple Primordial Black Hole formation* — 2026; multiple peaks and binary black holes
- ★ [arXiv:2608.13206](https://arxiv.org/abs/2608.13206) — Ning, Cai, Wang, Yoo — *Long-term 3+1 simulations of primordial black hole formation during radiation domination* — 2026; cosmologically rescaled Gamma-driver
- · [arXiv:2504.05813](https://arxiv.org/abs/2504.05813) — *A new approach for simulating PBH formation from generic curvature fluctuations with the Misner-Sharp formalism*
- · [arXiv:2501.00295](https://arxiv.org/abs/2501.00295) — *Primordial Black Hole Formation from Power Spectrum with Finite-width*
- · [arXiv:2401.06329](https://arxiv.org/abs/2401.06329) — Uehara, Escrivà, Harada, Saito, Yoo — *Numerical simulation of type II primordial black hole formation*
- · [arXiv:2303.07980](https://arxiv.org/abs/2303.07980) — Musco, Jedamzik, Young — *Primordial black hole formation during the QCD phase transition: threshold, mass distribution and abundance*
- · [arXiv:2209.06196](https://arxiv.org/abs/2209.06196) — Escrivà, Bagui, Clesse — *Simulations of PBH formation at the QCD epoch and comparison with the GWTC-3 catalog*
- · [arXiv:2211.15674](https://arxiv.org/abs/2211.15674) — *Primordial Black Hole Formation during a Strongly Coupled Crossover*
- · [arXiv:2112.12335](https://arxiv.org/abs/2112.12335) — Yoo, Harada, Hirano, Okawa, Sasaki — *Primordial black hole formation from massless scalar isocurvature*
- · [arXiv:2507.19166](https://arxiv.org/abs/2507.19166) — *Non-linear Dynamics and Primordial Black Hole Formation During Kination*
- · [arXiv:2607.20423](https://arxiv.org/abs/2607.20423) — *Primordial black holes forming during kination: the trapped, the overdense, and the void* — 2026
- · [arXiv:2510.11611](https://arxiv.org/abs/2510.11611) — *Primordial Black Holes from Primordial Voids*
- · [arXiv:2510.22759](https://arxiv.org/abs/2510.22759) — Kitajima — *Primordial black hole formation from collapsing domain walls with full general relativity*
- · [arXiv:1710.02865](https://arxiv.org/abs/1710.02865) — Deng, Vilenkin — *Primordial black hole formation by vacuum bubbles*
- · [arXiv:1612.03753](https://arxiv.org/abs/1612.03753) — Deng, Garriga, Vilenkin — *Primordial black hole and wormhole formation by domain walls*
- · [arXiv:2306.09990](https://arxiv.org/abs/2306.09990) — Escrivà, Atal, Garriga — *Formation of trapped vacuum bubbles during inflation, and consequences for PBH scenarios*
- · [arXiv:2312.11982](https://arxiv.org/abs/2312.11982) — *Toward supermassive primordial black holes from inflationary bubbles*
- · [arXiv:2406.05838](https://arxiv.org/abs/2406.05838) — *Bubbles kick off primordial black holes to form more binaries*
- · [arXiv:1609.02245](https://arxiv.org/abs/1609.02245) — Nakama, Suyama, Yokoyama — *Supermassive black holes formed by direct collapse of inflationary perturbations* — supermassive PBHs
- · [arXiv:1202.3848](https://arxiv.org/abs/1202.3848) — Kawasaki, Kusenko, Yanagida — *Primordial seeds of supermassive black holes*
- · [arXiv:1906.08217](https://arxiv.org/abs/1906.08217) — Carr, Clesse, García-Bellido, Kühnel — *Cosmic Conundra Explained by Thermal History and Primordial Black Holes* — effect of the thermal history on the threshold
- · [arXiv:gr-qc/9402041](https://arxiv.org/abs/gr-qc/9402041) — Evans, Coleman — *Observation of critical phenomena and selfsimilarity in the gravitational collapse of radiation fluid*
- ◆ [arXiv:0711.4620](https://arxiv.org/abs/0711.4620) — Gundlach, Martín-García — *Critical phenomena in gravitational collapse* — Living Reviews article

### G14 Primordial-black-hole formation: matter-dominated era (14 entries)

- ★ [arXiv:1609.01588](https://arxiv.org/abs/1609.01588) — Harada, Yoo, Kohri, Nakao, Jhingan — *Primordial black hole formation in the matter-dominated phase of the Universe* — non-sphericity + hoop criterion
- ★ [arXiv:1707.03595](https://arxiv.org/abs/1707.03595) — Harada, Yoo, Kohri, Nakao — *Spins of primordial black holes formed in the matter-dominated phase of the Universe*
- ◆ [arXiv:1810.03490](https://arxiv.org/abs/1810.03490) — Kokubu, Kyutoku, Kohri, Harada — *Effect of Inhomogeneity on Primordial Black Hole Formation in the Matter Dominated Era*
- ★ [arXiv:2211.13950](https://arxiv.org/abs/2211.13950) — Harada, Kohri, Sasaki, Terada, Yoo — *Threshold of Primordial Black Hole Formation against Velocity Dispersion in Matter-Dominated Era* — velocity dispersion
- · [arXiv:2305.13830](https://arxiv.org/abs/2305.13830) — Saito, Harada, Koga, Yoo — *Spins of primordial black holes formed with a soft equation of state*
- · [arXiv:2409.00435](https://arxiv.org/abs/2409.00435) — Saito, Harada, Koga, Yoo — *Revisiting spins of primordial black holes in a matter-dominated era based on peak theory*
- ★ [arXiv:2507.18312](https://arxiv.org/abs/2507.18312) — Ebrahimian, Abolhasani, Mirbabayi — *Primordial black hole formation in matter domination* — peak-profile statistics raise the effective threshold; spin is small
- ★ [arXiv:2508.10070](https://arxiv.org/abs/2508.10070) — Ye, Gong, Harada, Kang, Kohri, Saito, Yoo — *Primordial Black Hole Formation and Spin in Matter Domination Revisited* — peak theory + Zel'dovich approximation + hoop criterion
- ★ [arXiv:2109.04896](https://arxiv.org/abs/2109.04896) — de Jong, Aurrekoetxea, Lim — *Primordial black hole formation with full numerical relativity* — scalar-field matter; 3+1
- ★ [arXiv:2306.11810](https://arxiv.org/abs/2306.11810) — de Jong, Aurrekoetxea, Lim, França — *Spinning primordial black holes formed during a matter-dominated era*
- · [arXiv:2403.02878](https://arxiv.org/abs/2403.02878) — de Jong — *Primordial black hole formation processes with full numerical relativity* — thesis
- ★ [arXiv:2609.14218](https://arxiv.org/abs/2609.14218) — Yoo, Escrivà, Harada, Kohri — *Simulation of PBH formation in a matter-dominated universe* — 2026; dust fluid versus particles in full NR; direct competitor
- ★ [arXiv:2610.23218](https://arxiv.org/abs/2610.23218) — Munoz, Byrnes, Bruni, Hawke — *Simulating dust collapse: the impact of gauge choices on primordial black hole formation* — 2026; gauge issues in cosmological dust collapse
- · [arXiv:2505.21885](https://arxiv.org/abs/2505.21885) — Allahverdi, Dent, Loc, Xu — *Gravitational wave signatures of primordial black hole accretion during early matter domination*

### G15 Structure formation and gravitational waves in the early matter-dominated era; scalar-induced gravitational waves (37 entries)

- ◆ [arXiv:2006.16182](https://arxiv.org/abs/2006.16182) — Allahverdi et al. — *The First Three Seconds: a Review of Possible Expansion Histories of the Early Universe* — review
- ◆ [arXiv:1106.0536](https://arxiv.org/abs/1106.0536) — Erickcek, Sigurdson — *Reheating Effects in the Matter Power Spectrum and Implications for Substructure*
- · [arXiv:1311.4034](https://arxiv.org/abs/1311.4034) — Barenboim, Rasero — *Structure Formation during an early period of matter domination*
- · [arXiv:1405.7373](https://arxiv.org/abs/1405.7373) — Fan, Özsoy, Watson — *Nonthermal histories and implications for structure formation*
- · [arXiv:1906.00010](https://arxiv.org/abs/1906.00010) — Blanco, Delos, Erickcek, Hooper — *Annihilation Signatures of Hidden Sector Dark Matter Within Early-Forming Microhalos*
- · [arXiv:2107.10293](https://arxiv.org/abs/2107.10293) — Barenboim, Blinov, Stebbins — *Smallest Remnants of Early Matter Domination*
- · [arXiv:2209.02735](https://arxiv.org/abs/2209.02735) — Ganjoo, Erickcek, Lin, Mack — *The Effects Of Relativistic Hidden Sector Particles on the Matter Power Spectrum*
- ◆ [arXiv:2306.14961](https://arxiv.org/abs/2306.14961) — Ganjoo, Delos — *Simulations of Gravitational Heating Due to Early Matter Domination* — N-body study of EMDE structure formation and evaporation
- ◆ [arXiv:1002.3278](https://arxiv.org/abs/1002.3278) — Jedamzik, Lemoine, Martin — *Generation of gravitational waves during early structure formation between cosmic inflation and reheating*
- · [arXiv:0901.0989](https://arxiv.org/abs/0901.0989) — Assadullahi, Wands — *Gravitational waves from an early matter era*
- · [arXiv:2012.09255](https://arxiv.org/abs/2012.09255) — Dalianis, Kouvaris — *Gravitational waves from density perturbations in an early matter domination era*
- ◆ [arXiv:2403.15126](https://arxiv.org/abs/2403.15126) — Dalianis, Kouvaris — *Gravitational Waves from Collapse of Pressureless Matter in the Early Universe* — Newtonian N-body
- ★ [arXiv:2605.04487](https://arxiv.org/abs/2605.04487) — Escrivà, Harada, Kohri, Terada, Yoo — *Gravitational wave emission from nonspherical collapse in an early matter-dominated era using N-body simulations* — 2026; semi-relativistic N-body
- ◆ [arXiv:2212.00425](https://arxiv.org/abs/2212.00425) — Eggemeier, Niemeyer, Jedamzik, Easther — *Stochastic Gravitational Waves from Post-inflationary Structure Formation*
- ★ [arXiv:2312.12499](https://arxiv.org/abs/2312.12499) — Fernandez, Foster, Lillard, Shelton — *Stochastic Gravitational Waves from Early Structure Formation* — hybrid N-body + lattice; includes decay
- · [arXiv:2209.04970](https://arxiv.org/abs/2209.04970) — *Gravitational Waves from Rapid Structure Formation on Microscopic Scales before Matter-Radiation Equality*
- · [arXiv:2504.11275](https://arxiv.org/abs/2504.11275) — *Relic gravitational waves from primordial gravitational collapses*
- · [arXiv:1904.12878](https://arxiv.org/abs/1904.12878) — Inomata, Kohri, Nakama, Terada — *Gravitational Waves Induced by Scalar Perturbations during a Gradual Transition from an Early Matter Era to the Radiation Era*
- ◆ [arXiv:1904.12879](https://arxiv.org/abs/1904.12879) — Inomata, Kohri, Nakama, Terada — *Enhancement of Gravitational Waves Induced by Scalar Perturbations due to a Sudden Transition from an Early Matter Era to the Radiation Era*
- · [arXiv:2311.12340](https://arxiv.org/abs/2311.12340) — Pearce, Pearce, White, Balázs — *Gravitational wave signals from early matter domination: interpolating between fast and slow transitions*
- · [arXiv:2410.17291](https://arxiv.org/abs/2410.17291) — Kumar, Tai, Wang — *Towards a complete treatment of scalar-induced gravitational waves with early matter domination*
- · [arXiv:2610.08045](https://arxiv.org/abs/2610.08045) — Zhou — *Third-order scalar induced gravitational waves during a matter-dominated era: secular growth and implications for primordial black hole domination* — 2026
- · [arXiv:2003.10455](https://arxiv.org/abs/2003.10455) — Inomata, Kawasaki, Mukaida, Terada, Yanagida — *Gravitational Wave Production right after a Primordial Black Hole Evaporation*
- ◆ [arXiv:1907.08129](https://arxiv.org/abs/1907.08129) — Inman, Ali-Haïmoud — *Early Structure Formation in ΛPBH Cosmologies* — N-body with primordial black holes as particles
- · [arXiv:2010.11573](https://arxiv.org/abs/2010.11573) — Papanikolaou, Vennin, Langlois — *Gravitational waves from a universe filled with primordial black holes*
- · [arXiv:2012.08151](https://arxiv.org/abs/2012.08151) — Domènech, Lin, Sasaki — *Gravitational wave constraints on the primordial black hole dominated early universe*
- · [arXiv:2207.11041](https://arxiv.org/abs/2207.11041) — *Gravitational waves induced from primordial black hole fluctuations: the effect of an extended mass function*
- · [arXiv:gr-qc/0612013](https://arxiv.org/abs/gr-qc/0612013) — Ananda, Clarkson, Wands — *The Cosmological gravitational wave background from primordial density perturbations*
- · [arXiv:hep-th/0703290](https://arxiv.org/abs/hep-th/0703290) — Baumann, Steinhardt, Takahashi, Ichiki — *Gravitational Wave Spectrum Induced by Primordial Scalar Perturbations*
- · [arXiv:1804.08577](https://arxiv.org/abs/1804.08577) — Kohri, Terada — *Semianalytic calculation of gravitational wave spectrum nonlinearly induced from primordial curvature perturbations*
- ◆ [arXiv:2109.01398](https://arxiv.org/abs/2109.01398) — Domènech — *Scalar induced gravitational waves review* — review
- ◆ [arXiv:1704.03500](https://arxiv.org/abs/1704.03500) — Hwang, Jeong, Noh — *Gauge dependence of gravitational waves generated from scalar perturbations*
- · [arXiv:1911.09689](https://arxiv.org/abs/1911.09689) — De Luca, Franciolini, Kehagias, Riotto — *On the Gauge Invariance of Cosmological Gravitational Waves*
- · [arXiv:1912.00785](https://arxiv.org/abs/1912.00785) — Inomata, Terada — *Gauge Independence of Induced Gravitational Waves*
- · [arXiv:2012.14016](https://arxiv.org/abs/2012.14016) — Domènech, Sasaki — *Approximate gauge independence of the induced gravitational wave spectrum*
- · [arXiv:2009.11081](https://arxiv.org/abs/2009.11081) — *Gauge transformation of scalar induced tensor perturbation during matter domination*
- · [arXiv:astro-ph/0306304](https://arxiv.org/abs/astro-ph/0306304) — Weinberg — *Damping of tensor modes in cosmology* — anisotropic stress of free-streaming neutrinos

### G16 Phase transitions, bubble collisions, topological defects (10 entries)

- · [arXiv:1112.4487](https://arxiv.org/abs/1112.4487) — Johnson, Peiris, Lehner — *Determining the outcome of cosmic bubble collisions in full General Relativity*
- · [arXiv:1312.1357](https://arxiv.org/abs/1312.1357) — Wainwright et al. — *Simulating the universe(s): from cosmic bubble collisions to cosmological observables with numerical relativity*
- · [arXiv:1407.2950](https://arxiv.org/abs/1407.2950) — Wainwright et al. — *Simulating the universe(s) II: phenomenology of cosmic bubble collisions in full General Relativity*
- · [arXiv:1508.03641](https://arxiv.org/abs/1508.03641) — Johnson, Wainwright, Aguirre, Peiris — *Simulating the Universe(s) III: Observables for the full bubble collision spacetime*
- · [arXiv:2307.12080](https://arxiv.org/abs/2307.12080) — *General relativistic bubble growth in cosmological phase transitions*
- · [arXiv:1808.06678](https://arxiv.org/abs/1808.06678) — Helfer, Aurrekoetxea, Lim — *Cosmic String Loop Collapse in Full General Relativity*
- · [arXiv:2002.05177](https://arxiv.org/abs/2002.05177) — Aurrekoetxea, Helfer, Lim — *Coherent Gravitational Waveforms and Memory from Cosmic String Loops*
- · [arXiv:2312.03860](https://arxiv.org/abs/2312.03860) — Aurrekoetxea, Hoy, Hannam — *Revisiting the Cosmic String Origin of GW190521*
- · [arXiv:1910.01718](https://arxiv.org/abs/1910.01718) — Drew, Shellard — *Radiation from Global Topological Strings using Adaptive Mesh Refinement: Methodology and Massless Modes*
- · [arXiv:2211.10184](https://arxiv.org/abs/2211.10184) — Drew, Shellard — *Radiation from Global Topological Strings using Adaptive Mesh Refinement: Massive Modes*

### G17 Singularities, BKL, black holes in de Sitter, roadmap-type papers (10 entries)

- · [arXiv:gr-qc/0201056](https://arxiv.org/abs/gr-qc/0201056) — Berger — *Numerical Approaches to Spacetime Singularities* — Living Reviews article
- · [arXiv:gr-qc/9805063](https://arxiv.org/abs/gr-qc/9805063) — Berger, Garfinkle, Isenberg, Moncrief, Weaver — *The singularity in generic gravitational collapse is spacelike, local, and oscillatory*
- · [arXiv:gr-qc/0312117](https://arxiv.org/abs/gr-qc/0312117) — Garfinkle — *Numerical simulations of generic singularities*
- · [arXiv:0808.0160](https://arxiv.org/abs/0808.0160) — Garfinkle — *Numerical simulations of general gravitational singularities*
- · [arXiv:0904.1546](https://arxiv.org/abs/0904.1546) — Lim, Andersson, Garfinkle, Pretorius — *Spikes in the Mixmaster regime of G2 cosmologies*
- · [arXiv:2010.01399](https://arxiv.org/abs/2010.01399) — Garfinkle, Pretorius — *Spike behavior in the approach to spacetime singularities*
- · [arXiv:gr-qc/0304002](https://arxiv.org/abs/gr-qc/0304002) — Uggla, van Elst, Wainwright, Ellis — *The past attractor in inhomogeneous cosmology*
- · [arXiv:1204.2019](https://arxiv.org/abs/1204.2019) — Zilhão et al. — *Dynamics of black holes in de Sitter spacetimes*
- · [arXiv:1606.02999](https://arxiv.org/abs/1606.02999) — Garfinkle — *Numerical Relativity Beyond Astrophysics* — review
- · [arXiv:1201.5118](https://arxiv.org/abs/1201.5118) — Cardoso et al. — *NR/HEP: roadmap for the future*

### G18 Dark matter and strong gravity: SIDM collapse, spikes, dark-matter dress, black-hole environments, cosmological coupling (32 entries)

- ◆ [arXiv:astro-ph/0110561](https://arxiv.org/abs/astro-ph/0110561) — Balberg, Shapiro, Inagaki — *Self-Interacting Dark Matter Halos and the Gravothermal Catastrophe*
- ◆ [arXiv:astro-ph/0111176](https://arxiv.org/abs/astro-ph/0111176) — Balberg, Shapiro — *Gravothermal Collapse of Self-Interacting Dark Matter Halos and the Origin of Massive Black Holes*
- · [arXiv:1101.3097](https://arxiv.org/abs/1101.3097) — Koda, Shapiro — *Gravothermal collapse of isolated self-interacting dark matter haloes: N-body simulation versus the fluid model*
- · [arXiv:1501.00017](https://arxiv.org/abs/1501.00017) — Pollack, Spergel, Steinhardt — *Supermassive Black Holes from Ultra-Strongly Self-Interacting Dark Matter*
- · [arXiv:1705.02358](https://arxiv.org/abs/1705.02358) — Tulin, Yu — *Dark Matter Self-interactions and Small Scale Structure* — review
- · [arXiv:1812.05088](https://arxiv.org/abs/1812.05088) — Choquette, Cline, Cornell — *Early formation of supermassive black holes via dark matter self-interactions*
- ◆ [arXiv:2010.15132](https://arxiv.org/abs/2010.15132) — Feng, Yu, Zhong — *Seeding Supermassive Black Holes with Self-Interacting Dark Matter: A Unified Scenario with Baryons*
- ★ [arXiv:2108.11967](https://arxiv.org/abs/2108.11967) — Feng, Yu, Zhong — *Dynamical instability of collapsed dark matter halos* — relativistic instability criterion
- · [arXiv:2103.13407](https://arxiv.org/abs/2103.13407) — Xiao, Shen, Hopkins, Zurek — *SMBH Seeds from Dissipative Dark Matter*
- · [arXiv:2210.01817](https://arxiv.org/abs/2210.01817) — Meshveliani, Zavala, Lovell — *Gravothermal collapse of Self-Interacting Dark Matter halos as the Origin of Intermediate Mass Black Holes in Milky Way satellites*
- · [arXiv:2312.09296](https://arxiv.org/abs/2312.09296) — Gad-Nasr, Boddy, Kaplinghat, Outmezguine, Sagunski — *On the Late-Time Evolution of Velocity-Dependent Self-Interacting Dark Matter Halos*
- · [arXiv:2504.00075](https://arxiv.org/abs/2504.00075) — Shen, Shen, Xiao, Vogelsberger, Jiang — *Massive Black Holes Seeded by Dark Matter -- Implications for Little Red Dots and Gravitational Wave Signatures*
- ◆ [arXiv:2506.17641](https://arxiv.org/abs/2506.17641) — Feng, Yu, Zhong — *Dark Bondi Accretion Aided by Baryons and the Origin of JWST Little Red Dots*
- ★ [arXiv:2601.17117](https://arxiv.org/abs/2601.17117) — Gu, Jiang, Chen, Li — *Non-Equilibrium Relativistic Core Collapse of Self-Interacting Dark Matter Halos -- Limits On Seed Black Hole Mass* — 2026; non-equilibrium relativistic treatment in the Misner–Sharp formalism
- · [arXiv:astro-ph/9906391](https://arxiv.org/abs/astro-ph/9906391) — Gondolo, Silk — *Dark matter annihilation at the galactic center* — dark-matter spike
- · [arXiv:1305.2619](https://arxiv.org/abs/1305.2619) — Sadeghian, Ferrer, Will — *Dark matter distributions around massive black holes: A general relativistic analysis*
- · [arXiv:2002.12811](https://arxiv.org/abs/2002.12811) — Kavanagh, Nichols, Bertone, Gaggero — *Detecting dark matter around black holes with gravitational waves: Effects of dark-matter dynamics on the gravitational waveform*
- · [arXiv:2211.01362](https://arxiv.org/abs/2211.01362) — Cole et al. — *Disks, spikes, and clouds: distinguishing environmental effects on BBH gravitational waveforms*
- · [arXiv:2402.13762](https://arxiv.org/abs/2402.13762) — Kavanagh, Karydas, Bertone, Di Cintio, Pasquato — *Sharpening the dark matter signature in gravitational waveforms II: Numerical simulations with the NbodyIMRI code*
- · [arXiv:2411.12007](https://arxiv.org/abs/2411.12007) — Kamermans, Wierda — *Darkness Visible: N-Body Simulations of Dark Matter Spikes in Hernquist Haloes*
- ◆ [arXiv:2505.09715](https://arxiv.org/abs/2505.09715) — Vicente, Karydas, Bertone — *Fully Relativistic Treatment of Extreme Mass-Ratio Inspirals in Collisionless Environments*
- · [arXiv:1607.00612](https://arxiv.org/abs/1607.00612) — Eroshenko — *Dark matter density spikes around primordial black holes*
- · [arXiv:1712.06383](https://arxiv.org/abs/1712.06383) — Boucenna, Kuhnel, Ohlsson, Visinelli — *Novel Constraints on Mixed Dark-Matter Scenarios of Primordial Black Holes and WIMPs*
- ◆ [arXiv:1805.09034](https://arxiv.org/abs/1805.09034) — Kavanagh, Gaggero, Bertone — *Black Holes' Dark Dress: On the merger rate of a subdominant population of primordial black holes*
- ◆ [arXiv:1901.08528](https://arxiv.org/abs/1901.08528) — Adamek, Byrnes, Gosenca, Hotchkiss — *WIMPs and stellar-mass primordial black holes are incompatible*
- · [arXiv:2002.10771](https://arxiv.org/abs/2002.10771) — Serpico, Poulin, Inman, Kohri — *Cosmic microwave background bounds on primordial black holes including dark matter halo accretion*
- · [arXiv:2106.07480](https://arxiv.org/abs/2106.07480) — Boudaud et al. — *In-depth analysis of the clustering of dark matter particles around primordial black holes. Part I. Density profiles*
- · [arXiv:2210.09254](https://arxiv.org/abs/2210.09254) — Bamber, Aurrekoetxea, Clough, Ferreira — *Black hole merger simulations in wave dark matter environments*
- · [arXiv:2311.18156](https://arxiv.org/abs/2311.18156) — Aurrekoetxea, Clough, Bamber, Ferreira — *The effect of wave dark matter on equal mass black hole mergers*
- · [arXiv:2409.01937](https://arxiv.org/abs/2409.01937) — Aurrekoetxea, Marsden, Clough, Ferreira — *Self-interacting scalar dark matter around binary black holes*
- · [arXiv:2302.07878](https://arxiv.org/abs/2302.07878) — Farrah et al. — *Observational evidence for cosmological coupling of black holes and its implications for an astrophysical source of dark energy*
- · [arXiv:2306.11588](https://arxiv.org/abs/2306.11588) — Cadoni et al. — *Cosmological coupling of nonsingular black holes*

### G19 Dark energy and modified gravity: relativistic N-body and well-posedness in NR (18 entries)

- · [arXiv:1910.01104](https://arxiv.org/abs/1910.01104) — Hassani, Adamek, Kunz, Vernizzi — *k-evolution: a relativistic N-body code for clustering dark energy*
- · [arXiv:2007.04968](https://arxiv.org/abs/2007.04968) — Hassani, Adamek, Kunz — *Clustering dark energy imprints on cosmological observables of the gravitational field*
- · [arXiv:2204.13098](https://arxiv.org/abs/2204.13098) — Hassani, Shi, Adamek, Kunz, Wittwer — *A new instability in clustering dark energy?*
- · [arXiv:1905.07345](https://arxiv.org/abs/1905.07345) — Reverberi, Daverio — *fRevolution – Relativistic Cosmological Simulations in f(R) Gravity I: Methodology*
- · [arXiv:2003.05927](https://arxiv.org/abs/2003.05927) — Hassani, Lombriser — *N-body simulations for parametrised modified gravity*
- · [arXiv:2302.07857](https://arxiv.org/abs/2302.07857) — Christiansen, Hassani, Jalilvand, Mota — *asevolution: a relativistic N-body implementation of the (a)symmetron*
- · [arXiv:2401.02409](https://arxiv.org/abs/2401.02409) — Christiansen, Adamek, Hassani, Mota — *Gravitational waves from dark domain walls*
- · [arXiv:2511.04676](https://arxiv.org/abs/2511.04676) — *KGB-evolution: a relativistic N-body code for kinetic gravity braiding models*
- · [arXiv:2611.03637](https://arxiv.org/abs/2611.03637) — Nouri-Zonoz, Hassani, Adamek, Bellini, Kunz — *Mercury (Hg): a relativistic N-body simulation for Horndeski gravity* — 2026
- · [arXiv:2610.36752](https://arxiv.org/abs/2610.36752) — Christiansen, Adamek, Baidya, da Fonseca, Linder, Mota — *Relativistic N-body simulations with mass-varying neutrinos* — 2026
- · [arXiv:2006.11019](https://arxiv.org/abs/2006.11019) — Brando, Koyama, Wands — *Relativistic Corrections to the Growth of Structure in Modified Gravity*
- · [arXiv:2003.04327](https://arxiv.org/abs/2003.04327) — Kovács, Reall — *Well-posed formulation of scalar-tensor effective field theory*
- · [arXiv:2011.03547](https://arxiv.org/abs/2011.03547) — East, Ripley — *Evolution of Einstein-scalar-Gauss-Bonnet gravity using a modified harmonic formulation*
- · [arXiv:2208.14470](https://arxiv.org/abs/2208.14470) — Aresté Saló, Clough, Figueras — *Well-posedness of the four-derivative scalar-tensor theory of gravity in singularity avoiding coordinates*
- · [arXiv:2407.08775](https://arxiv.org/abs/2407.08775) — Figueras, Held, Kovács — *Well-posed initial value formulation of general effective field theories of gravity*
- · [arXiv:2308.16791](https://arxiv.org/abs/2308.16791) — Brady et al. — *Solving the initial conditions problem for modified gravity theories*
- · [arXiv:1904.12866](https://arxiv.org/abs/1904.12866) — Bernard, Lehner, Luna — *Challenges to global solutions in Horndeski's theory*
- · [arXiv:2008.07546](https://arxiv.org/abs/2008.07546) — Bezares, Crisostomi, Palenzuela, Barausse — *K-dynamics: well-posed initial value 1+1 evolutions in K-essence*

### G20 Stochastic inflation, lattice inflation and the separate-universe approach (66 entries)

- ◆ [arXiv:astro-ph/9407016](https://arxiv.org/abs/astro-ph/9407016) — Starobinsky, Yokoyama — *Equilibrium state of a selfinteracting scalar field in the De Sitter background* — classic paper on stochastic inflation
- ★ [arXiv:2009.08715](https://arxiv.org/abs/2009.08715) — Vennin — *Stochastic inflation and primordial black holes* — review
- ★ [arXiv:2203.13852](https://arxiv.org/abs/2203.13852) — Cruces — *Review on stochastic approach to inflation* — review
- ◆ [arXiv:1308.4754](https://arxiv.org/abs/1308.4754) — Fujita, Kawasaki, Tada et al. — *A new algorithm for calculating the curvature perturbations in stochastic inflation* — numerical algorithm for stochastic δN
- ◆ [arXiv:1707.00537](https://arxiv.org/abs/1707.00537) — Pattison, Vennin, Assadullahi, Wands — *Quantum diffusion during inflation and primordial black holes* — quantum diffusion and non-Gaussian tails
- ◆ [arXiv:1912.05399](https://arxiv.org/abs/1912.05399) — Ezquiaga, García-Bellido, Vennin — *The exponential tail of inflationary fluctuations: consequences for primordial black holes* — quantum diffusion and non-Gaussian tails
- ◆ [arXiv:2101.05741](https://arxiv.org/abs/2101.05741) — Pattison, Vennin, Wands, Assadullahi — *Ultra-slow-roll inflation with quantum diffusion*
- ◆ [arXiv:2012.06551](https://arxiv.org/abs/2012.06551) — Figueroa, Raatikainen, Räsänen et al. — *Non-Gaussian Tail of the Curvature Perturbation in Stochastic Ultraslow-Roll Inflation: Implications for Primordial Black Hole Production*
- · [arXiv:2111.07437](https://arxiv.org/abs/2111.07437) — Figueroa, Raatikainen, Räsänen et al. — *Implications of stochastic effects for primordial black hole production in ultra-slow-roll inflation*
- ★ [arXiv:2312.12911](https://arxiv.org/abs/2312.12911) — Raatikainen, Räsänen, Tomberg — *Primordial black hole compaction function from stochastic fluctuations in ultra-slow-roll inflation* — stochastic statistics of the compaction function in USR
- ◆ [arXiv:2510.09303](https://arxiv.org/abs/2510.09303) — Raatikainen, Räsänen, Tomberg — *Effect of stochastic kicks on primordial black hole abundance and mass via the compaction function* — effect of stochastic kicks on abundance and mass
- · [arXiv:2402.08642](https://arxiv.org/abs/2402.08642) — Animali, Vennin — *Clustering of primordial black holes from quantum diffusion during inflation*
- ◆ [arXiv:2402.12672](https://arxiv.org/abs/2402.12672) — Vennin, Wands — *Quantum diffusion and large primordial perturbations from inflation*
- · [arXiv:2501.05371](https://arxiv.org/abs/2501.05371) — Animali, Auclair, Blachier et al. — *Harvesting primordial black holes from stochastic trees with FOREST* — sampling with stochastic trees
- ◆ [arXiv:2206.11234](https://arxiv.org/abs/2206.11234) — Jackson, Assadullahi, Koyama et al. — *Numerical simulations of stochastic inflation using importance sampling* — importance sampling
- ◆ [arXiv:2410.13683](https://arxiv.org/abs/2410.13683) — Jackson, Assadullahi, Gow et al. — *Stochastic inflation beyond slow roll: noise modelling and importance sampling* — noise modelling beyond slow roll
- ◆ [arXiv:2311.03281](https://arxiv.org/abs/2311.03281) — Jackson, Assadullahi, Gow et al. — *The separate-universe approach and sudden transitions during inflation* — validity of the separate-universe approach at sudden transitions
- ◆ [arXiv:2210.17441](https://arxiv.org/abs/2210.17441) — Tomberg — *Numerical stochastic inflation constrained by frozen noise* — frozen noise
- ◆ [arXiv:2411.12465](https://arxiv.org/abs/2411.12465) — Tomberg — *Itô, Stratonovich, and zoom-in schemes in stochastic inflation* — Itô versus Stratonovich
- · [arXiv:2606.09690](https://arxiv.org/abs/2606.09690) — Tomberg — *Stochastic constant-roll inflation beyond the hilltop with the spectral method* — 2026
- · [arXiv:2507.15522](https://arxiv.org/abs/2507.15522) — Tomberg, Dimopoulos — *Eternal inflation near inflection points: a challenge to primordial black hole models*
- ◆ [arXiv:1905.06300](https://arxiv.org/abs/1905.06300) — Pattison, Vennin, Assadullahi et al. — *Stochastic inflation beyond slow roll*
- · [arXiv:2107.12735](https://arxiv.org/abs/2107.12735) — Cruces, Germani — *Stochastic inflation at all order in slow-roll parameters: foundations*
- · [arXiv:2410.17987](https://arxiv.org/abs/2410.17987) — Cruces, Germani, Nassiri-Rad et al. — *Small noise expansion of stochastic inflation*
- ◆ [arXiv:2611.15050](https://arxiv.org/abs/2611.15050) — Cruces, Kuroda — *A consistent formulation of stochastic inflation II: Reassessing its role in nonlinear cosmological perturbations* — 2026; reassesses the role of the stochastic formalism
- · [arXiv:1910.08487](https://arxiv.org/abs/1910.08487) — Prokopec, Rigopoulos — *ΔN and the stochastic conveyor belt of Ultra Slow-Roll*
- · [arXiv:2507.04114](https://arxiv.org/abs/2507.04114) — Prokopec, Rigopoulos — *Inflaton perturbations through an Ultra-Slow Roll transition and Hamilton-Jacobi attractors*
- · [arXiv:2504.05937](https://arxiv.org/abs/2504.05937) — Artigas, Frion, Miranda et al. — *On the Hamilton-Jacobi approach to inflation beyond slow roll*
- · [arXiv:2110.11720](https://arxiv.org/abs/2110.11720) — Artigas, Grain, Vennin — *Hamiltonian formalism for cosmological perturbations: the separate-universe approach*
- · [arXiv:2408.09964](https://arxiv.org/abs/2408.09964) — Artigas, Pi, Tanaka — *Extended δN formalism: Nonspatially Flat Separate Universe Approach*
- · [arXiv:2408.13673](https://arxiv.org/abs/2408.13673) — Tanaka, Urakawa — *gδN formalism*
- ◆ [arXiv:astro-ph/0003278](https://arxiv.org/abs/astro-ph/0003278) — Wands, Malik, Lyth et al. — *A new approach to the evolution of cosmological perturbations on large scales* — separate universe and δN
- ◆ [arXiv:astro-ph/0306620](https://arxiv.org/abs/astro-ph/0306620) — Rigopoulos, Shellard — *The Separate Universe Approach and the Evolution of Nonlinear Superhorizon Cosmological Perturbations* — nonlinear separate-universe approach
- · [arXiv:astro-ph/0504508](https://arxiv.org/abs/astro-ph/0504508) — Rigopoulos, Shellard, van Tent — *Non-linear perturbations in multiple-field inflation*
- · [arXiv:astro-ph/0101406](https://arxiv.org/abs/astro-ph/0101406) — Leach, Sasaki, Wands et al. — *Enhancement of superhorizon scale inflationary curvature perturbations*
- · [arXiv:1911.00057](https://arxiv.org/abs/1911.00057) — Mishra, Sahni — *Primordial Black Holes from a tiny bump/dip in the Inflaton potential*
- · [arXiv:2305.03491](https://arxiv.org/abs/2305.03491) — Franciolini, Iovino, Taoso et al. — *One loop to rule them all: Perturbativity in the presence of ultra slow-roll dynamics*
- · [arXiv:gr-qc/9911029](https://arxiv.org/abs/gr-qc/9911029) — Winitzki, Vilenkin — *Effective noise in stochastic description of inflation*
- · [arXiv:0808.1786](https://arxiv.org/abs/0808.1786) — Finelli, Marozzi, Starobinsky et al. — *Generation of fluctuations during inflation: Comparison of stochastic and field-theoretic approaches*
- · [arXiv:1003.1327](https://arxiv.org/abs/1003.1327) — Finelli, Marozzi, Starobinsky et al. — *Stochastic growth of quantum fluctuations during slow-roll inflation*
- · [arXiv:1506.04732](https://arxiv.org/abs/1506.04732) — Vennin, Starobinsky — *Correlation Functions in Stochastic Inflation*
- · [arXiv:1409.7399](https://arxiv.org/abs/1409.7399) — Perreault Levasseur, McDonough — *Backreaction and Stochastic Effects in Single Field Inflation*
- · [arXiv:2311.17644](https://arxiv.org/abs/2311.17644) — Palma, Sypsas — *Revisiting stochastic inflation with perturbation theory*
- ◆ [arXiv:2406.02417](https://arxiv.org/abs/2406.02417) — Ballesteros, Konstandin, Pérez Rodríguez et al. — *Non-Gaussian tails without stochastic inflation* — non-Gaussian tails without stochastic inflation
- · [arXiv:2512.17070](https://arxiv.org/abs/2512.17070) — Ahmadi, Noorbala — *Deviations from Gaussian White Noise in Stochastic Inflation*
- ◆ [arXiv:2412.16143](https://arxiv.org/abs/2412.16143) — Launay, Rigopoulos, Shellard — *Quantitative classicality in cosmological interactions during inflation* — quantitative criterion for the quantum-to-classical transition
- · [arXiv:2509.05124](https://arxiv.org/abs/2509.05124) — Briaud, Kawaguchi, Vennin — *Stochastic inflation with gradient interactions*
- · [arXiv:2404.15416](https://arxiv.org/abs/2404.15416) — Salcedo, Colas, Pajer — *The Open Effective Field Theory of Inflation*
- · [arXiv:2605.11096](https://arxiv.org/abs/2605.11096) — Céspedes, Colas — *Stochastic inflation from a non-equilibrium renormalization group* — 2026
- · [arXiv:2606.07467](https://arxiv.org/abs/2606.07467) — Launay — *Stochastic scalar-tensor inflation and beyond* — 2026
- · [arXiv:2605.31323](https://arxiv.org/abs/2605.31323) — Animali, Blachier, Okada et al. — *Time-reversed stochastic inflation in the quantum well* — 2026
- · [arXiv:2504.17680](https://arxiv.org/abs/2504.17680) — Blachier, Ringeval — *Time-reversed Stochastic Inflation*
- · [arXiv:2511.21388](https://arxiv.org/abs/2511.21388) — Blachier, Ringeval — *Friction in Stochastic Inflation*
- · [arXiv:2604.15219](https://arxiv.org/abs/2604.15219) — Ye, Wang — *Nonperturbative stochastic inflation in perturbative dynamical background* — 2026
- · [arXiv:2506.21423](https://arxiv.org/abs/2506.21423) — Aldabergenov, Ding, Lin et al. — *Towards Stochastic Inflation in Higher-Curvature Gravity*
- · [arXiv:2506.03860](https://arxiv.org/abs/2506.03860) — Tasinato — *Stochastic inflation as a superfluid*
- · [arXiv:2302.00655](https://arxiv.org/abs/2302.00655) — Werth, Pinol, Renaux-Petel — *Cosmological Flow of Primordial Correlators*
- ★ [arXiv:2405.10692](https://arxiv.org/abs/2405.10692) — Mizuguchi, Murata, Tada — *STOLAS: STOchastic LAttice Simulation of cosmic inflation* — stochastic lattice simulation code
- ◆ [arXiv:2102.06378](https://arxiv.org/abs/2102.06378) — Caravano, Komatsu, Lozanov et al. — *Lattice Simulations of Inflation* — lattice inflation
- · [arXiv:2403.12811](https://arxiv.org/abs/2403.12811) — Caravano, Inomata, Renaux-Petel — *The Inflationary Butterfly Effect: Non-Perturbative Dynamics From Small-Scale Features*
- ◆ [arXiv:2410.23942](https://arxiv.org/abs/2410.23942) — Caravano, Franciolini, Renaux-Petel — *Ultra-Slow-Roll Inflation on the Lattice I: Backreaction and Nonlinear Effects* — lattice simulation of USR
- ◆ [arXiv:2506.11795](https://arxiv.org/abs/2506.11795) — Caravano, Franciolini, Renaux-Petel — *Ultra-Slow-Roll Inflation on the Lattice II: Nonperturbative Curvature Perturbation* — lattice simulation of USR
- · [arXiv:2604.03628](https://arxiv.org/abs/2604.03628) — Caravano, Franciolini, Renaux-Petel — *Lattice simulations of scalar-induced gravitational waves from inflation* — 2026; scalar-induced gravitational waves on the lattice
- ◆ [arXiv:2102.01031](https://arxiv.org/abs/2102.01031) — Figueroa, Florio, Torrenti, Valkenburg — *CosmoLattice: A modern code for lattice simulations of scalar and gauge field dynamics in an expanding universe* — lattice code
- · [arXiv:hep-ph/0011159](https://arxiv.org/abs/hep-ph/0011159) — Felder, Tkachev — *LATTICEEASY: A program for lattice simulations of scalar fields in an expanding universe* — lattice code
- · [arXiv:1609.00381](https://arxiv.org/abs/1609.00381) — Mulryne, Ronayne — *PyTransport: A Python package for the calculation of inflationary correlation functions* — code for inflationary correlation functions

### G21 Hills mechanism, tidal separation and strong-field three-body dynamics (50 entries)

- ◆ [arXiv:astro-ph/0309084](https://arxiv.org/abs/astro-ph/0309084) — Yu (first author) — *Ejection of hypervelocity stars by the (binary) black hole(s) in the Galactic center* — ejection rate of hypervelocity stars
- · [arXiv:astro-ph/0501177](https://arxiv.org/abs/astro-ph/0501177) — Brown (first author) — *Discovery of an Unbound Hyper-Velocity Star in the Milky Way Halo*
- · [arXiv:astro-ph/0608159](https://arxiv.org/abs/astro-ph/0608159) — Bromley (first author) — *Hypervelocity Stars: Predicting the Spectrum of Ejection Velocities*
- · [arXiv:astro-ph/0609440](https://arxiv.org/abs/astro-ph/0609440) — Ginsburg (first author) — *Hypervelocity Collisions of Binary Stars at the Galactic Centre*
- ★ [arXiv:0911.1136](https://arxiv.org/abs/0911.1136) — Sari, Kobayashi, Rossi — *Hyper Velocity Stars and the Restricted Parabolic 3-body Problem* — restricted parabolic three-body approximation
- ◆ [arXiv:1201.4794](https://arxiv.org/abs/1201.4794) — Kobayashi (first author) — *Ejection and Capture Dynamics in Restricted Three-Body Encounters* — ejection and capture in the restricted three-body problem
- ◆ [arXiv:1307.1134](https://arxiv.org/abs/1307.1134) — Rossi, Kobayashi, Sari — *The Velocity Distribution of Hypervelocity Stars*
- ★ [arXiv:1804.02911](https://arxiv.org/abs/1804.02911) — Brown, Kobayashi, Rossi et al. — *Tidal Disruption of Inclined or Eccentric Binaries by Massive Black Holes* — inclined and eccentric binaries
- ◆ [arXiv:0909.1959](https://arxiv.org/abs/0909.1959) — Antonini, Faber, Gualandris et al. — *Tidal break-up of binary stars at the Galactic center and its consequences*
- ◆ [arXiv:2409.09597](https://arxiv.org/abs/2409.09597) — Yu, Lai — *Binary Stars Approaching Supermassive Black Holes: Tidal Break-up, Double Stellar Disruptions and Stellar Collision*
- · [arXiv:1105.1432](https://arxiv.org/abs/1105.1432) — Zhang (first author) — *The spatial and velocity distributions of hypervelocity stars*
- · [arXiv:1210.1901](https://arxiv.org/abs/1210.1901) — Zhang (first author) — *S-stars in the Galactic center and hypervelocity stars in the Galactic halo: two faces of the tidal breakup of stellar binaries by the central massive black hole?*
- · [arXiv:2002.10547](https://arxiv.org/abs/2002.10547) — Generozov, Madigan — *The Hills Mechanism and the Galactic Center S-stars*
- · [arXiv:1203.2938](https://arxiv.org/abs/1203.2938) — Antonini (first author) — *Secular evolution of compact binaries near massive black holes: gravitational wave sources and other exotica*
- ◆ [arXiv:astro-ph/0507133](https://arxiv.org/abs/astro-ph/0507133) — Miller (first author) — *Binary Encounters With Supermassive Black Holes: Zero-Eccentricity LISA Events* — EMRIs produced by the Hills mechanism
- ★ [arXiv:2610.13294](https://arxiv.org/abs/2610.13294) — Sersante, Mancieri, Zavala et al. — *Extreme mass ratio inspirals from the Hills mechanism, The eccentricity distribution of Hills EMRIs in LISA* — 2026; eccentricity distribution of Hills EMRIs
- ◆ [arXiv:1801.05780](https://arxiv.org/abs/1801.05780) — Chen, Han — *A New Type of Extreme-mass-ratio Inspirals Produced by Tidal Capture of Binary Black Holes* — tidal capture of binary black holes
- · [arXiv:1801.07060](https://arxiv.org/abs/1801.07060) — Han (first author) — *Testing general relativity using binary extreme-mass-ratio inspirals*
- · [arXiv:1805.09593](https://arxiv.org/abs/1805.09593) — Fernández, Kobayashi — *Black Hole Mergers Induced by Tidal Encounters with a Galactic Centre Black Hole*
- · [arXiv:1903.02685](https://arxiv.org/abs/1903.02685) — Zhang, Shao, Zhu — *Gravitational-wave merging events from the dynamics of stellar mass binary black holes around the massive black hole in a galactic nucleus*
- ◆ [arXiv:1501.07856](https://arxiv.org/abs/1501.07856) — Addison, Laguna, Larson — *Busting Up Binaries: Encounters Between Compact Binaries and a Supermassive Black Hole* — compact binaries and a supermassive black hole
- ★ [arXiv:2404.16270](https://arxiv.org/abs/2404.16270) — Manzaneda, Navarrete, Tejeda — *Relativistic tidal separation of binary stars by supermassive black holes* — exact Schwarzschild acceleration plus Newtonian self-gravity; compared with Newtonian and 1PN
- ★ [arXiv:2402.02178](https://arxiv.org/abs/2402.02178) — Zhang, Chen — *The dynamics and gravitational-wave signal of a binary flying closely by a Kerr supermassive black hole* — binary black hole passing close to a Kerr black hole; notes the difficulty for full NR
- · [arXiv:1203.6185](https://arxiv.org/abs/1203.6185) — Bai (first author) — *Perturbational Treatment of the Gravitational Potential Effect on Binary Black Hole Evolution*
- · [arXiv:1703.10543](https://arxiv.org/abs/1703.10543) — Chen, Li, Cao — *Mass-redshift Degeneracy for Gravitational-wave Sources in the Vicinity of a Supermassive Black Hole*
- · [arXiv:2105.02230](https://arxiv.org/abs/2105.02230) — Liu (first author) — *Probing the Spins of Supermassive Black Holes with Gravitational Waves from Surrounding Compact Binaries*
- · [arXiv:0704.2612](https://arxiv.org/abs/0704.2612) — Yunes (first author) — *Relativistic Effects in Extreme Mass Ratio Gravitational Wave Bursts*
- ◆ [arXiv:2508.03463](https://arxiv.org/abs/2508.03463) — Mahapatra, Pandey, Banerjee et al. — *Tidal disruptions of close white dwarf binaries by intermediate mass black holes* — white-dwarf binaries disrupted by intermediate-mass black holes (SPH)
- ◆ [arXiv:2601.04870](https://arxiv.org/abs/2601.04870) — Mahapatra, Pandey, Banerjee, Sarkar — *Tidal encounters of close white dwarf binaries with spinning black holes* — 2026; includes black-hole spin
- · [arXiv:1504.02787](https://arxiv.org/abs/1504.02787) — Mandel (first author) — *Double tidal disruptions in galactic nuclei*
- · [arXiv:1703.05796](https://arxiv.org/abs/1703.05796) — Bradnick (first author) — *Stellar binaries in galactic nuclei: tidally stimulated mergers followed by tidal disruptions*
- · [arXiv:2203.08162](https://arxiv.org/abs/2203.08162) — Cufari, Coughlin, Nixon — *Using the Hills Mechanism to Generate Repeating Partial Tidal Disruption Events and ASASSN-14ko*
- · [arXiv:1502.02039](https://arxiv.org/abs/1502.02039) — Gafton (first author) — *Relativistic effects on tidal disruption kicks of solitary stars*
- · [arXiv:1305.4634](https://arxiv.org/abs/1305.4634) — Manukian, Guillochon, Ramirez-Ruiz, O'Leary — *Turbovelocity Stars: Kicks Resulting From the Tidal Disruption of Solitary Stars*
- · [arXiv:1411.5022](https://arxiv.org/abs/1411.5022) — Guillochon (first author) — *The Fastest Unbound Stars in the Universe*
- · [arXiv:1701.00303](https://arxiv.org/abs/1701.00303) — Tejeda, Gafton, Rosswog, Miller — *Tidal disruptions by rotating black holes: relativistic hydrodynamics with Newtonian codes*
- · [arXiv:1903.09147](https://arxiv.org/abs/1903.09147) — Gafton (first author) — *Tidal disruptions by rotating black holes: effects of spin and impact parameter*
- · [arXiv:1207.6401](https://arxiv.org/abs/1207.6401) — Kesden (first author) — *Black-Hole Spin Dependence in the Light Curves of Tidal Disruption Events*
- · [arXiv:1201.4389](https://arxiv.org/abs/1201.4389) — Haas, Shcherbakov, Bode et al. — *Tidal Disruptions of White Dwarfs from Ultra-Close Encounters with Intermediate Mass Spinning Black Holes* — tidal disruption in full GR
- · [arXiv:1502.05740](https://arxiv.org/abs/1502.05740) — Evans, Laguna, Eracleous — *Ultra-Close Encounters of Stars With Massive Black Holes: Tidal Disruption Events With Prompt Hyperaccretion* — tidal disruption in full GR
- ◆ [arXiv:1408.1695](https://arxiv.org/abs/1408.1695) — East — *Gravitational waves from the collision of tidally disrupted stars with massive black holes* — tidal disruption in full GR
- ◆ [arXiv:0710.0879](https://arxiv.org/abs/0710.0879) — Campanelli, Lousto, Zlochower — *Close encounters of three black holes* — three black holes in full NR
- ◆ [arXiv:0711.1165](https://arxiv.org/abs/0711.1165) — Lousto, Zlochower — *Foundations of multiple black hole evolutions* — multiple-black-hole evolutions
- ◆ [arXiv:1004.1353](https://arxiv.org/abs/1004.1353) — Galaviz, Bruegmann, Cao — *Numerical evolution of multiple black holes with accurate initial data* — accuracy of multiple-black-hole initial data
- · [arXiv:1812.01930](https://arxiv.org/abs/1812.01930) — Raidal, Spethmann, Vaskonen et al. — *Formation and Evolution of Primordial Black Hole Binaries in the Early Universe* — primordial-black-hole binaries
- · [arXiv:1908.09752](https://arxiv.org/abs/1908.09752) — Vaskonen, Veermäe — *A lower bound on the primordial black hole merger rate* — primordial-black-hole binaries
- · [arXiv:2006.11172](https://arxiv.org/abs/2006.11172) — Jedamzik — *Primordial Black Hole Dark Matter and the LIGO/Virgo observations* — primordial-black-hole binaries
- · [arXiv:1706.09896](https://arxiv.org/abs/1706.09896) — Hoang (first author) — *Black Hole Mergers in Galactic Nuclei Induced by the Eccentric Kozai-Lidov Effect*
- · [arXiv:1604.02148](https://arxiv.org/abs/1604.02148) — Meiron (first author) — *Detecting triple systems with gravitational wave observations*
- · [arXiv:2310.00042](https://arxiv.org/abs/2310.00042) — Xuan (first author) — *Detecting Gravitational Wave Bursts from Stellar-mass Binaries in the mHz Band*

---

## 17. Machine-readable manifests and download rules

**Rules for downloading from arXiv.**

- Source: `https://arxiv.org/e-print/<id>` (equivalent endpoint `https://arxiv.org/src/<id>`; switch when one fails; it returns tar.gz, gz or a single tex file); PDF: `https://arxiv.org/pdf/<id>`; abstract page: `https://arxiv.org/abs/<id>`. Old-style identifiers (such as `gr-qc/9804040`) go into the path as they are.
- Single-threaded, at least 3 seconds between requests; exponential back-off on failure, no concurrency.
- Storage as in §12.2: `kb-data/raw/arxiv/<id with the slash replaced by an underscore>/<version>/source.bin`, extracted into `src/` in the same directory; no file is executed.
- Download priority=3 first, then 2, then 1.
- The download record goes into `kb-data/meta/arxiv/<id>.json`. Title and authors are taken afresh from the metadata; where they differ from this document, the downloaded data win and the difference is recorded (§12.3).

**arXiv manifest.** One line each: `id<TAB>group<TAB>priority` (3=★, 2=◆, 1=·). For the group codes see the subsection headings of §16.

```tsv
2611.12831	G01	3
2504.15978	G01	2
2111.05282	G01	3
2211.13659	G01	1
2509.19769	G01	1
2409.16053	G01	2
2409.10383	G01	2
2409.10384	G01	1
2101.08289	G01	1
0912.2920	G01	2
1212.2901	G01	1
1106.2254	G01	1
gr-qc/0504114	G01	1
gr-qc/0511048	G01	1
gr-qc/0511103	G01	1
gr-qc/0605030	G01	1
gr-qc/0206072	G01	1
gr-qc/9412071	G01	1
1109.0546	G01	2
2404.01137	G01	1
2505.15912	G01	1
gr-qc/9905058	G02	2
gr-qc/9804040	G02	2
gr-qc/0012059	G02	1
gr-qc/0107076	G02	2
math/0209336	G02	3
gr-qc/0601112	G02	2
gr-qc/0611053	G02	1
1409.5176	G02	2
1611.07906	G02	3
1807.11562	G02	2
1901.04498	G02	3
2010.15771	G02	2
2305.04360	G02	2
2009.08163	G02	1
2105.05556	G02	1
1707.08666	G02	1
2511.20567	G02	2
2505.01495	G02	2
astro-ph/9607124	G02	1
2203.06478	G02	1
2306.06226	G02	1
2408.11577	G02	1
gr-qc/9604001	G03	2
1106.1367	G03	3
1303.2899	G03	1
1309.2036	G03	1
2106.09235	G03	2
1910.12152	G03	2
2310.00776	G03	1
1707.06141	G03	1
1707.06079	G03	1
1602.02611	G03	1
2210.00512	G03	1
1709.00267	G03	2
1306.6223	G03	2
2002.02119	G03	1
gr-qc/0512031	G03	2
gr-qc/0112009	G03	1
1009.2596	G03	1
2402.10190	G03	2
2510.12429	G03	1
2309.00431	G03	1
2609.13394	G03	2
1706.09501	G03	2
1907.10743	G03	2
2506.21779	G03	3
1810.03613	G04	2
1908.06919	G04	1
2012.07229	G04	1
2511.17710	G04	1
2511.17701	G04	2
2605.15260	G04	2
2503.04558	G04	1
2401.02908	G04	1
2101.12149	G04	1
1801.02378	G04	2
1810.00842	G04	1
1710.09164	G04	1
2007.14401	G04	1
1006.3717	G04	1
2602.17487	G04	1
1609.03053	G04	2
1612.06734	G04	2
0807.0734	G04	1
1208.3927	G04	2
2110.06265	G05	3
2112.05165	G05	3
1105.1082	G05	1
1111.3944	G05	2
1210.6652	G05	2
1501.01959	G05	2
1509.07720	G05	1
1909.00008	G05	1
1705.03750	G05	1
2012.04409	G05	1
1206.6152	G05	1
2010.00248	G05	1
2010.07321	G05	2
1801.03906	G05	1
astro-ph/0702575	G05	1
1606.02038	G05	1
1403.5567	G05	1
1801.03507	G05	1
1911.04505	G05	1
2010.12584	G05	1
1912.00868	G05	1
2102.05690	G05	1
2510.13129	G05	1
1503.03436	G06	1
2201.03458	G06	1
2112.10567	G06	2
1111.3344	G06	1
1301.4498	G06	1
2207.03125	G06	2
2501.13046	G06	2
2006.16360	G06	2
1305.5576	G06	2
1208.3473	G06	1
2509.26470	G06	3
2607.21308	G06	2
2309.02946	G06	1
2312.03285	G06	1
2207.06376	G06	2
gr-qc/0210050	G06	1
1704.04307	G06	2
1809.07010	G06	1
2304.07616	G06	1
2307.11701	G06	1
2211.08133	G06	2
2602.00155	G06	1
2111.09163	G06	2
2304.13284	G06	1
1309.2012	G06	1
gr-qc/0703035	G06	1
2409.01939	G07	3
1511.01105	G07	2
1511.01106	G07	2
1511.05124	G07	2
1611.05447	G07	2
1807.01711	G07	3
1807.01714	G07	2
1608.04403	G07	1
1707.06640	G07	1
1711.06681	G07	3
1908.05683	G07	3
1810.05203	G07	3
1611.03437	G07	2
1904.07841	G07	2
1610.05198	G07	1
2003.08014	G07	3
2307.15194	G07	2
2302.09033	G07	2
2010.07274	G07	1
2110.00893	G07	1
2103.11918	G07	2
2111.14423	G07	1
2209.06775	G07	2
2402.09659	G07	1
2402.12165	G07	1
2507.01095	G07	1
2212.13569	G07	1
2205.12692	G07	1
1910.13380	G07	1
2403.15134	G07	2
2404.06242	G07	1
2408.03049	G07	2
2603.24838	G07	2
2606.05479	G07	3
2606.18437	G07	1
2107.06306	G07	1
1604.04001	G07	1
1409.3476	G07	1
1409.7953	G07	1
1501.06918	G07	1
1801.08362	G07	1
1505.02959	G07	1
1811.00762	G07	1
1308.6524	G08	2
1509.01699	G08	3
1604.06065	G08	3
1408.3352	G08	1
1408.2741	G08	2
1706.09309	G08	2
1707.06938	G08	2
1812.04336	G08	1
2002.04024	G08	1
1509.01163	G08	1
1508.05610	G08	1
2607.17929	G08	3
2404.02783	G08	2
2603.24179	G08	1
2106.01347	G08	1
2209.10533	G08	1
2011.12936	G08	1
2009.02284	G08	1
2505.04731	G08	1
2510.05956	G08	1
2508.20606	G08	2
1905.08890	G08	3
2001.07968	G08	2
2010.08257	G08	1
2109.02632	G08	1
2301.11854	G08	1
1806.05146	G08	1
2512.08703	G08	1
1101.3555	G08	2
1111.2997	G08	2
1207.2035	G08	1
1505.04756	G08	2
1606.05588	G08	2
1708.07769	G08	1
1702.03221	G08	2
1602.07699	G08	1
1610.04236	G08	1
1703.08585	G08	1
1811.00904	G08	1
1904.11773	G08	1
1712.03944	G08	1
2112.01508	G08	1
1807.03701	G08	1
1905.11721	G08	1
1703.03407	G08	1
1803.04294	G08	1
2111.08745	G08	1
1306.1562	G08	1
1501.00799	G08	1
1403.4947	G08	1
1502.02985	G08	1
1307.1478	G08	1
1505.04782	G08	1
2110.11249	G08	2
2212.06799	G08	1
2109.13364	G08	1
0907.0707	G08	1
1105.5280	G08	1
1105.5292	G08	1
1107.5427	G08	1
1910.04894	G08	1
2001.00394	G08	2
1610.08882	G08	1
1503.08747	G08	1
2203.04009	G08	1
gr-qc/9906015	G09	3
astro-ph/9510056	G09	1
0707.2153	G09	1
1912.04213	G09	1
2202.10798	G09	1
1112.5335	G09	2
1109.2314	G09	2
1505.07800	G09	3
1011.4920	G09	3
1407.8084	G09	2
gr-qc/0509108	G09	1
hep-ph/0409038	G09	1
1102.0408	G09	1
1002.4779	G09	1
1703.08809	G09	1
0710.5073	G09	1
1612.08222	G09	2
2106.06043	G09	1
2509.01320	G09	2
2310.19451	G09	1
2409.00024	G09	1
gr-qc/0702082	G09	2
0909.0749	G09	1
2311.01438	G09	2
2412.15143	G09	2
2406.05048	G09	2
1607.08797	G09	1
1708.09143	G09	1
1712.02967	G09	1
2002.10831	G09	1
1104.1167	G09	1
1207.1286	G09	1
1911.09469	G09	1
1503.08506	G09	1
1503.07831	G09	1
astro-ph/0412275	G09	1
astro-ph/0511183	G09	1
1302.5308	G09	1
1304.7791	G09	1
1612.03726	G09	1
1109.2484	G09	1
1204.0909	G09	1
2012.07802	G09	1
2010.06534	G09	2
2102.03774	G09	1
2107.08674	G09	1
1909.13489	G09	1
2008.07108	G09	1
2105.11880	G09	1
2205.11907	G09	1
2604.26690	G09	1
2601.20633	G09	2
2507.17969	G09	1
2512.10585	G09	1
2404.03002	G09	1
2503.14738	G09	2
2112.04510	G09	1
2103.01183	G09	1
2504.01669	G09	1
2203.06142	G09	1
2105.05208	G09	1
2208.05018	G09	1
2207.05765	G09	2
2009.14826	G09	1
2206.05624	G09	1
2302.02028	G09	1
2305.16084	G09	1
2404.16719	G09	1
2510.05340	G09	1
1304.2884	G09	1
2009.11292	G09	1
2602.03928	G09	1
2606.02712	G09	1
1502.02011	G09	1
1504.00351	G09	1
2210.11426	G09	1
astro-ph/0602159	G09	1
1104.1300	G09	1
1204.5505	G09	1
1204.3568	G10	2
1306.4055	G10	1
1204.2411	G10	1
1306.1389	G10	2
1404.1435	G10	1
1610.05635	G10	1
1611.09275	G10	1
1801.01083	G10	2
1203.6478	G10	1
1903.01490	G10	1
astro-ph/9306009	G11	1
1601.01918	G11	1
1511.05143	G11	2
1608.04408	G11	2
1712.07352	G11	1
1910.12547	G11	1
2011.12190	G11	1
2202.07604	G11	1
2212.04479	G11	1
2405.03490	G11	1
2304.12150	G11	1
1906.08651	G11	1
2406.00811	G11	1
1607.00381	G11	1
2412.19731	G11	1
2502.06783	G11	1
2512.13673	G11	1
2505.22763	G11	1
2607.06441	G11	1
2606.14853	G11	1
2604.00978	G11	1
2401.08530	G11	1
2512.14649	G11	1
2610.32592	G11	1
1602.03520	G11	1
2004.10754	G11	1
1710.04278	G11	1
0808.0542	G11	1
1308.3044	G11	1
2006.01172	G11	1
2006.04999	G11	1
2103.00584	G11	1
2104.12293	G11	1
2109.09768	G11	1
2205.01519	G11	1
2404.00867	G11	1
2206.08466	G11	1
2201.03752	G11	2
2602.10223	G11	1
1907.10601	G12	2
1912.09658	G12	1
2112.07626	G12	1
2311.01504	G12	1
2304.01673	G12	1
2504.08939	G12	1
1005.4054	G12	1
0709.3510	G12	1
hep-ph/9809574	G12	1
1410.3808	G12	1
1106.3335	G12	1
2006.15122	G12	1
2010.05933	G12	1
1906.09346	G12	1
1909.11678	G12	1
2011.13333	G12	2
2110.15109	G12	1
1911.01661	G12	1
2311.08780	G12	1
2204.07152	G12	1
1002.3039	G12	1
2110.14584	G12	1
1806.09367	G12	1
1609.04724	G12	1
1802.10085	G12	1
gr-qc/9905064	G13	2
astro-ph/9709072	G13	2
astro-ph/9901292	G13	1
gr-qc/0412063	G13	1
gr-qc/0605122	G13	1
0811.1452	G13	1
1201.2379	G13	1
1309.4201	G13	2
1503.03934	G13	2
1504.02071	G13	1
1809.02127	G13	1
1907.13065	G13	1
1907.13311	G13	1
2103.03867	G13	1
2110.05982	G13	1
2111.12693	G13	2
2211.05767	G13	2
2211.13512	G13	1
2002.12778	G13	1
2601.06024	G13	1
2606.30641	G13	1
2004.01042	G13	2
2403.11147	G13	1
2410.03451	G13	1
2410.03452	G13	1
2310.16482	G13	1
2609.03051	G13	2
2608.13206	G13	3
2504.05813	G13	1
2501.00295	G13	1
2401.06329	G13	1
2303.07980	G13	1
2209.06196	G13	1
2211.15674	G13	1
2112.12335	G13	1
2507.19166	G13	1
2607.20423	G13	1
2510.11611	G13	1
2510.22759	G13	1
1710.02865	G13	1
1612.03753	G13	1
2306.09990	G13	1
2312.11982	G13	1
2406.05838	G13	1
1609.02245	G13	1
1202.3848	G13	1
1906.08217	G13	1
gr-qc/9402041	G13	1
0711.4620	G13	2
1609.01588	G14	3
1707.03595	G14	3
1810.03490	G14	2
2211.13950	G14	3
2305.13830	G14	1
2409.00435	G14	1
2507.18312	G14	3
2508.10070	G14	3
2109.04896	G14	3
2306.11810	G14	3
2403.02878	G14	1
2609.14218	G14	3
2610.23218	G14	3
2505.21885	G14	1
2006.16182	G15	2
1106.0536	G15	2
1311.4034	G15	1
1405.7373	G15	1
1906.00010	G15	1
2107.10293	G15	1
2209.02735	G15	1
2306.14961	G15	2
1002.3278	G15	2
0901.0989	G15	1
2012.09255	G15	1
2403.15126	G15	2
2605.04487	G15	3
2212.00425	G15	2
2312.12499	G15	3
2209.04970	G15	1
2504.11275	G15	1
1904.12878	G15	1
1904.12879	G15	2
2311.12340	G15	1
2410.17291	G15	1
2610.08045	G15	1
2003.10455	G15	1
1907.08129	G15	2
2010.11573	G15	1
2012.08151	G15	1
2207.11041	G15	1
gr-qc/0612013	G15	1
hep-th/0703290	G15	1
1804.08577	G15	1
2109.01398	G15	2
1704.03500	G15	2
1911.09689	G15	1
1912.00785	G15	1
2012.14016	G15	1
2009.11081	G15	1
astro-ph/0306304	G15	1
1112.4487	G16	1
1312.1357	G16	1
1407.2950	G16	1
1508.03641	G16	1
2307.12080	G16	1
1808.06678	G16	1
2002.05177	G16	1
2312.03860	G16	1
1910.01718	G16	1
2211.10184	G16	1
gr-qc/0201056	G17	1
gr-qc/9805063	G17	1
gr-qc/0312117	G17	1
0808.0160	G17	1
0904.1546	G17	1
2010.01399	G17	1
gr-qc/0304002	G17	1
1204.2019	G17	1
1606.02999	G17	1
1201.5118	G17	1
astro-ph/0110561	G18	2
astro-ph/0111176	G18	2
1101.3097	G18	1
1501.00017	G18	1
1705.02358	G18	1
1812.05088	G18	1
2010.15132	G18	2
2108.11967	G18	3
2103.13407	G18	1
2210.01817	G18	1
2312.09296	G18	1
2504.00075	G18	1
2506.17641	G18	2
2601.17117	G18	3
astro-ph/9906391	G18	1
1305.2619	G18	1
2002.12811	G18	1
2211.01362	G18	1
2402.13762	G18	1
2411.12007	G18	1
2505.09715	G18	2
1607.00612	G18	1
1712.06383	G18	1
1805.09034	G18	2
1901.08528	G18	2
2002.10771	G18	1
2106.07480	G18	1
2210.09254	G18	1
2311.18156	G18	1
2409.01937	G18	1
2302.07878	G18	1
2306.11588	G18	1
1910.01104	G19	1
2007.04968	G19	1
2204.13098	G19	1
1905.07345	G19	1
2003.05927	G19	1
2302.07857	G19	1
2401.02409	G19	1
2511.04676	G19	1
2611.03637	G19	1
2610.36752	G19	1
2006.11019	G19	1
2003.04327	G19	1
2011.03547	G19	1
2208.14470	G19	1
2407.08775	G19	1
2308.16791	G19	1
1904.12866	G19	1
2008.07546	G19	1
1307.7391	G06	1
2504.16802	G06	2
astro-ph/9407016	G20	2
2009.08715	G20	3
2203.13852	G20	3
1308.4754	G20	2
1707.00537	G20	2
1912.05399	G20	2
2101.05741	G20	2
2012.06551	G20	2
2111.07437	G20	1
2312.12911	G20	3
2510.09303	G20	2
2402.08642	G20	1
2402.12672	G20	2
2501.05371	G20	1
2206.11234	G20	2
2410.13683	G20	2
2311.03281	G20	2
2210.17441	G20	2
2411.12465	G20	2
2606.09690	G20	1
2507.15522	G20	1
1905.06300	G20	2
2107.12735	G20	1
2410.17987	G20	1
2611.15050	G20	2
1910.08487	G20	1
2507.04114	G20	1
2504.05937	G20	1
2110.11720	G20	1
2408.09964	G20	1
2408.13673	G20	1
astro-ph/0003278	G20	2
astro-ph/0306620	G20	2
astro-ph/0504508	G20	1
astro-ph/0101406	G20	1
1911.00057	G20	1
2305.03491	G20	1
gr-qc/9911029	G20	1
0808.1786	G20	1
1003.1327	G20	1
1506.04732	G20	1
1409.7399	G20	1
2311.17644	G20	1
2406.02417	G20	2
2512.17070	G20	1
2412.16143	G20	2
2509.05124	G20	1
2404.15416	G20	1
2605.11096	G20	1
2606.07467	G20	1
2605.31323	G20	1
2504.17680	G20	1
2511.21388	G20	1
2604.15219	G20	1
2506.21423	G20	1
2506.03860	G20	1
2302.00655	G20	1
2405.10692	G20	3
2102.06378	G20	2
2403.12811	G20	1
2410.23942	G20	2
2506.11795	G20	2
2604.03628	G20	1
2102.01031	G20	2
hep-ph/0011159	G20	1
1609.00381	G20	1
astro-ph/0309084	G21	2
astro-ph/0501177	G21	1
astro-ph/0608159	G21	1
astro-ph/0609440	G21	1
0911.1136	G21	3
1201.4794	G21	2
1307.1134	G21	2
1804.02911	G21	3
0909.1959	G21	2
2409.09597	G21	2
1105.1432	G21	1
1210.1901	G21	1
2002.10547	G21	1
1203.2938	G21	1
astro-ph/0507133	G21	2
2610.13294	G21	3
1801.05780	G21	2
1801.07060	G21	1
1805.09593	G21	1
1903.02685	G21	1
1501.07856	G21	2
2404.16270	G21	3
2402.02178	G21	3
1203.6185	G21	1
1703.10543	G21	1
2105.02230	G21	1
0704.2612	G21	1
2508.03463	G21	2
2601.04870	G21	2
1504.02787	G21	1
1703.05796	G21	1
2203.08162	G21	1
1502.02039	G21	1
1305.4634	G21	1
1411.5022	G21	1
1701.00303	G21	1
1903.09147	G21	1
1207.6401	G21	1
1201.4389	G21	1
1502.05740	G21	1
1408.1695	G21	2
0710.0879	G21	2
0711.1165	G21	2
1004.1353	G21	2
1812.01930	G21	1
1908.09752	G21	1
2006.11172	G21	1
1706.09896	G21	1
1604.02148	G21	1
2310.00042	G21	1
```

**GitHub repository manifest.** One line each: `owner/repo<TAB>role<TAB>owners concerned<TAB>description`. Roles: core is the base to be forked and modified, dep is a build or run dependency, ref is a read-only reference, tool is a tool for the knowledge base and the harness. These addresses were confirmed to resolve with `git ls-remote` on 2026-11-15 [VERIFIED]; the description column comes from prior knowledge [BACKGROUND].

Cloning rules: partial or shallow clone into `kb-data/raw/github/<owner>__<repo>/`, recording commit hash, date and licence; no script from a repository is run. Repositories that have to be built (AthenaK, Kokkos, REBOUND and others) are cloned separately into a worktree or `cache/` and never built inside the knowledge-base directory.

```tsv
IAS-Astrophysics/athenak	core	all	AthenaK: Kokkos AMR framework with Z4c; base of NRPIC (BSD-3-Clause at c5a0d7f)
kokkos/kokkos	dep	all	performance-portability layer (AthenaK submodule)
PrincetonUniversity/athena	ref	core	Athena++ (lineage of GR-Athena++ and AthenaK)
parthenon-hpc-lab/parthenon	ref	core	Kokkos AMR framework
entity-toolkit/entity	ref	core	GRPIC on Kokkos
BLAST-WarpX/warpx	ref	core	PIC with mesh refinement
ammarhakim/gkeyll	ref	core	continuum kinetic solver
nrpy/nrpy	ref	core	code generation for numerical relativity
sxs-collaboration/spectre	ref	core,F	NR code; AthenaK ships an input for importing its binary data
paralab/Dendro-GR	ref	core	octree NR
eschnett/CarpetX	ref	core	Einstein Toolkit AMR driver
GRTLCollaboration/GRChombo	ref	E,B	NR with scalar fields and AMR
GRTLCollaboration/GRTeclyn	ref	E	GPU successor of GRChombo on AMReX
GRTLCollaboration/GRTresna	ref	A,B,E	cosmological initial-data solver
GRTLCollaboration/GRDzhadzha	ref	D	matter on fixed black-hole backgrounds
GRTLCollaboration/engrenage	ref	A,C	spherically symmetric BSSN code
GRTLCollaboration/GRFolres	ref	-	modified gravity in NR
AMReX-Codes/amrex	dep	E	AMR framework
gevolution-code/gevolution-1.2	ref	B	weak-field relativistic N-body
gevolution-code/gevolution-2.0	ref	B	GPU version of gevolution
daverio/LATfield2	dep	B	lattice library used by gevolution
FarbodHassani/k-evolution	ref	-	k-essence on top of gevolution
jmd-dk/concept	ref	B	N-body with relativistic species
ramses-organisation/ramses	ref	B	AMR N-body (base of GRAMSES)
AMReX-Astro/Nyx	ref	B	cosmological N-body and hydrodynamics
AMReX-Astro/Castro	ref	-	compressible astrophysics
SWIFTSIM/SWIFT	ref	B	N-body and SPH
SWIFTSIM/swiftsimio	ref	-	reader for SWIFT outputs
danieljprice/phantom	ref	B	SPH code
cwru-pat/cosmograph	ref	B	BSSN with N-body and fluids
hayleyjm/FLRWSolver_public	ref	B	cosmological initial data for the Einstein Toolkit
hayleyjm/mescaline-1.0	ref	B	post-processing and ray tracing for NR cosmology
robynlm/ebweyl	ref	all	gravito-electromagnetic diagnostics
robynlm/aurel	ref	all	relativity diagnostics
lesgourg/class_public	ref	B,E	Boltzmann code
cosmolattice/cosmolattice	ref	E	lattice field theory in an expanding universe
caravangelo/inflation-easy	ref	E	lattice inflation
STOchasticLAtticeSimulation/STOLAS_dist	ref	E	stochastic lattice simulation of inflation
jronayne/PyTransport	ref	E	inflationary correlation functions
DEShawResearch/random123	dep	C,E	counter-based random numbers
bradkav/NbodyIMRI	ref	D,F	N-body for dark-matter spikes around binaries
bradkav/HaloFeedback	ref	D	spike feedback on inspirals
hannorein/rebound	dep	F	N-body integrator for the three-body baselines
dtamayo/reboundx	dep	F	additional forces for REBOUND, including relativistic corrections
BlackHolePerturbationToolkit/KerrGeodesics	ref	D,F	Kerr geodesics
phfaist/pylatexenc	tool	kb	LaTeX parsing
alvinwan/TexSoup	tool	kb	LaTeX tree
brucemiller/LaTeXML	tool	kb	LaTeX to XML/HTML
google-research/arxiv-latex-cleaner	tool	kb	source cleaning
jgm/pandoc	tool	kb	format conversion
lukasschwab/arxiv.py	tool	kb	arXiv API client
inspirehep/inspirehep	tool	kb	INSPIRE (API reference)
asg017/sqlite-vec	tool	kb	vector search inside SQLite
facebookresearch/faiss	tool	kb	vector index
lancedb/lancedb	tool	kb	vector database
universal-ctags/ctags	tool	kb	symbol index
tree-sitter/tree-sitter	tool	kb	incremental parsing
BurntSushi/ripgrep	tool	all	search
astral-sh/uv	tool	all	Python environments and lock files
pre-commit/pre-commit	tool	all	commit hooks
direnv/direnv	tool	all	per-directory environment
apptainer/apptainer	tool	all	containers on HPC
git-lfs/git-lfs	tool	all	large files in git
```

Names that did not resolve and need their hosting addresses found: Einstein Toolkit, MUSIC, monofonIC, SPriBHoS, Vlasiator, Arepo, GRBoondi.
