# Charter of the NRPIC-cosmology program

Owner: orchestrator (branch `main`). Tracks read this file and never write it; changes are
proposed through `tracks/<ID>/outbox/`. Source: the brief
`einstein_vlasov_pic_cosmology_agent_brief.en.md` (version 2, 2026-11-15), sections 9 and
10, copied below; where this charter and the brief differ, the charter governs.

## Goal

Do cosmology with the numerical-relativity particle-in-cell method of arXiv:2611.12831,
advancing science problems and method innovation side by side: six science tracks (A to F),
the shared implementation (core) and the knowledge base (kb), in parallel.

## What differs from the brief (state on 2026-11-15)

1. The shared implementation exists in this repository and is verified (decision 0002).
   For core, steps C0 to C4 of section 9.3 become: document the interfaces from the code,
   re-verify the ladder of section 10 on the current source, tag `core-v0.1`
   (asymptotically flat) and `core-v0.2` (periodic particles, cosmological gauge). The
   tracks do not wait: work "that depends on core" may start as soon as the capability it
   needs is listed in `CLAUDE.md`, registered as scouting until the tag exists.
2. For Track B, the work packages B-pre-2 (cosmological gauge), part of B-pre-5
   (constraint-solved periodic initial data) and the rows "FLRW dust" and "growth of
   linear perturbations" of section 10 are already done in the cosmology extension
   (`cosmo/`): B verifies them against its own criteria instead of redoing them.
3. Layout, pushing, budgets, configuration, sessions and models: decisions 0001, 0003,
   0006, 0008, 0009.
4. Paths: the brief's `src/` is `athenak/src/`, its `inputs/` is `problems/`.

## Owners

| Owner id | Worktree | Branch | Problem | First work |
|---|---|---|---|---|
| orch | main checkout | `main` | orchestration, integration, review | harness, decisions, reviews |
| core | `wt/core` | `core/nrpic` | shared implementation | interfaces from the code, verification ladder, tags; initial data with extrinsic curvature; random-number interface |
| kb | `wt/kb` | `kb/main` | knowledge base | K0 to K3 of brief section 12 |
| A-emd-pbh | `wt/A-emd-pbh` | `track/A-emd-pbh` | S1 | A-pre-1 to A-pre-4 |
| B-emd-gw | `wt/B-emd-gw` | `track/B-emd-gw` | S2 | B-pre-1, B-pre-3, B-pre-4; verification of what `cosmo/` already has |
| C-sidm | `wt/C-sidm` | `track/C-sidm` | S3 | C-pre-1 to C-pre-4 |
| D-bh-dress | `wt/D-bh-dress` | `track/D-bh-dress` | S4 | D-pre-1 to D-pre-4 |
| E-stoch-inf | `wt/E-stoch-inf` | `track/E-stoch-inf` | S11 (feasibility gate first) | E-pre-1 to E-pre-4 |
| F-hills | `wt/F-hills` | `track/F-hills` | S12 | F-pre-5, F-pre-1, F-pre-2, then F-pre-3 |

Budgets: decision 0006. Open decisions for the group: 0002 (request to the authors), 0004,
0005, 0006, 0007, 0008.

## Text of the brief, sections 9.2 to 9.11 and 10

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

