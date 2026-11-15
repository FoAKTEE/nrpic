# Open requests between owners

Owner: orchestrator (branch `main`). State on 2026-11-15T15:50Z, read through git from the
outbox of every owner branch (`tracks/<ID>/outbox/`, the sender's own branches only, as
`nrpic-ctx` reads them) at the tips core/nrpic b17f40d, kb/main ca81acd, track/A-emd-pbh
dc27b98, track/B-emd-gw 767eb93, track/C-sidm 904eb96, track/D-bh-dress 3276791,
track/E-stoch-inf 6330493, track/F-hills dd48b3e, main 2267b92. All messages were sent on
2026-11-15 (UTC time given). The harness fix 2267b92 on main (nrpic-run reads the hand-written
manifests of wave 1, `nrpic-run lint`, a local Python run without the worktree's `.venv` is
refused with the fix) answers A's `harness-manifests-and-ignore` item 2, C's
`nrpic-run-manifest-schema` and E's `harness-and-brief-notes` item 1; the tracks receive it
with their next `nrpic-ctx sync`.

A request is open while no file answers it: a decision under `coord/DECISIONS/`, a commit on
main, an interface document under `coord/INTERFACES/`, a reply message, or the requester's
own later file. A partly answered request lists only what is still asked. "Ruled, not built"
means a decision says yes and the implementation is not on main yet. Messages of type `info`
appear only where they ask for an answer ("smallest acceptable answer"). Acknowledged
(`tracks/<ID>/inbox_acks.txt`) means seen, not answered. The answered requests and the
answering files are listed in `coord/digests/2026-W46.md`.

## To orch

| From | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|
| E-stoch-inf | g0-decision-requested | 14:10Z | 11-22 | partly | the group's decision on the feasibility gate (0013 records the orchestrator's ruling "continue to G1 and G2", pending the group), and whether G0 may pass with the note and schematics following at G1 |
| D-bh-dress | brief-and-notes-corrections | 15:10Z | 11-29 | partly | item 6: an artefact-only second-agent review of `scope/SCOPE.md` section 3, `einstein_straus/DERIVATION.md` sections 3-4 and the LTB mapping with an over-massive hole (items 1-5 are in `coord/BRIEF_ERRATA.md` and the derivations note; the wave-2 plan names a D verifier without these items) |
| F-hills | compute-allotment-and-mass-ratio | 15:07Z | 11-22 | partly | the allotment for G2 (about 120 card-hours; G3 about 500), a decision for the user (G1 raised to 50 in 0014; q = 4 accepted in 0013) |
| F-hills | second-agent-check | 15:07Z | 11-29 | partly | which of the four items (novelty verdict, newton3 reproduction, 2404.16270 reproduction, geodesic-capture finding) are checked, by whom, in which wave (the wave-2 plan names F's own helper `second_check`) |
| kb | brief-corrections | 14:20Z | 11-29 | partly | item 2: regrouping of 2211.08133, 2505.01495, 1807.11562, 1905.07345, 2304.13284; item 3: additions from the frontier list (item 1 is row 1.3 of `coord/BRIEF_ERRATA.md`) |
| kb | kb-g2-thresholds | 14:20Z | 11-29 | open | write the KB-G2 parse success rate (proposed at least 95 percent) and retrieval hit rate (proposed at least 80 percent in the top 10 on at least 30 golden questions) into the charter |
| kb | metadata-path | 14:20Z | 11-22 | ruled, not built | a `--meta` mode of `nrpic-fetch-arxiv` for arXiv-API and INSPIRE records (yes in 0015); blocks K1, core's metadata request and C's literature fetch |
| kb | fetch-arxiv-pdf-and-hardening | 14:20Z | 11-29 | ruled, not built | the `--pdf` mode with size limits and a content check (yes in 0015) for gr-qc/9412071 and astro-ph/9407016; hardening item 2 at the orchestrator's pace |
| core | claude-md-what-exists-core-v03 | 15:10Z | 11-29 | partly | item 3: the rules that card jobs ask for at most 2 of the 4 cores and that core packages keep temporary files in their own subdirectory of `scratch/core/` (items 1-2 and the reproducibility rule are in CLAUDE.md since 4ebb05f) |
| core | interface-documents-wave1 | 15:10Z | 11-29 | partly | the choices left to the orchestrator: particle state and file formats frozen from core-v0.1 on; a separate operator slot for non-gravitational kicks; a filter that conserves the integrals across levels; `<job> rng_seed` or an `<rng>` block; the stream registry of `coord/INTERFACES/rng.md` section 6 completed with streams 1-3 (documents accepted in 0011) |

## To core

| From | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|
| A-emd-pbh | newton-mode-and-ball-ic | 13:20Z | 12-06 | partly | in the Newtonian mode the external background acceleration -(4 pi/3) G rho_b(t) r and the special-relativistic push (core: wave-2 items), per-species second moments; item 2 the Zel'dovich-deformed ball in `problems/ic/make_ic.py`; item 3 the halting tests as acceptance tests; dates (mode itself on main in core-v0.3) |
| A-emd-pbh | phase1-generator-and-gauge-options | 13:20Z | 12-13 | open | which of the five items core takes in wave 2 (phase-1 generator on `nrpic_cosmo` for the data of 2609.14218, K_ref and softplus lapses, finder spin projection, dispersion data, finder in a periodic box) and the interface text for item 1 |
| A-emd-pbh | scouting-runs-ball | 13:20Z | 11-22 | partly | horizon-finder keys for a horizon of areal radius 0.161 M at coordinate radius about 2.7 M; whether `time/cfl_number` may change at a restart; `ltb_radius` fails for scalar arguments (the T2e outcome is item 3 of core's `format2-and-gauge`) |
| B-emd-gw | z4c-linear-wave-polarization | 13:40Z | 11-22 | open | flip the signs of `axy` (line 108) and `ayz` (line 111) in `z4c_linear_wave.cpp` so that oblique waves are transverse, with B's two checks; blocks B's G1 |
| B-emd-gw | gw-analysis-output | 13:40Z | 12-06 | open | a double-precision Z4c output without ghost zones at the GW cadence, or confirmation that restart files are the route; optionally in-situ Fourier modes and S_ij; a note on the 36 uninitialised bytes of restart files |
| B-emd-gw | initial-data-tt-part | 13:40Z | 12-06 | open | an option of `nrpic_cosmo` (id = file) for a non-flat conformal metric with the constraints solved around it, or a statement that subtracting the junk in analysis is preferred |
| B-emd-gw | lattice-jitter-option | 13:40Z | 11-29 | open | `--jitter A --jitter-axes y,z --seed N` in `cosmo/ic/make_east.py` (and `make_field.py`), or agreement that B adds it on `proposal/B-emd-gw/lattice-jitter` (`cosmo/` is on main, outside core's OWNERSHIP) |
| B-emd-gw | newtonian-mode-for-track-b | 13:40Z | 12-06 | partly | item 2: species selection and centroid second moments in physical coordinates in the Newtonian history; item 3: yes or no to an isolated patch in comoving coordinates with the Einstein-de Sitter background force (item 1 done: core-v0.3 on main) |
| B-emd-gw | thin-periodic-boxes | 13:40Z | 11-29 | open | whether `nrpic_cosmo`, the deposit and the Z4c ghost exchange work with nx3 = 16 and periodic z, and the minimal nx3 |
| B-emd-gw | weyl-output-timing | 13:40Z | 11-29 | open | confirm or refute that the `weyl` output written at t_n holds Psi_4 of t_n - 7 dt; fix the label or document the lag; whether `CalcWaveForm` carries the offset |
| B-emd-gw | awa-generators | 13:40Z | 12-13 | open | yes or no: register `z4c_gauge_wave` and `z4c_stability` as built-in problem generators |
| C-sidm | rng-stream2-table | 13:20Z | 11-29 | partly | the stream-2 table (sub-streams 0 pairing, 1 acceptance, 2 direction; step = cycle) and the tag rules in `rng.md` section 6; now only in `coord/INTERFACES/collisions.md` section 4, while `coord/INTERFACES/rng.md` section 6 still reads "to be fixed" (core proposed it to orch) |
| C-sidm | perturbation-recipe | 13:20Z | 12-06 | open | core's view on a pusher option of `nrpic_cf` for the radial force gamma x/r during [0, T_pert] of 2009.08163, or on scaling the momenta and re-solving the Hamiltonian constraint instead |
| C-sidm | grhydro-reference | 13:20Z | 12-13 | open | yes or no, with a one-line reason: is `dyn_grmhd` usable for a static spherical star with tabulated data on the mesh of `nrpic_cf` |
| D-bh-dress | tracer-push-release-build (blocker) | 15:10Z | 11-22 | open | the cause of the six massless tracers of `horizon_calib.athinput` leaving their geodesics on the release card executable `.work/build_gpu_c3`, and a fixed build or input convention (circular orbits within 1 percent for 250 M); core's wave-2 branch `core/requests-adf` has predictions for reproduction runs (be2fe59), no outcome yet |
| D-bh-dress | lapse-for-expanding-dust | 15:10Z | 11-29 | open | a lapse option for a puncture in expanding dust (singularity-avoiding at the hole, no front from the dust edges) with one test on a puncture alone (horizon-mass drift within 3e-5 over 100-200 M); an outer boundary for the Painleve-Gullstrand exterior |
| D-bh-dress | accretion-diagnostics | 15:10Z | 12-06 | open | for G2: (1) a per-particle removal record and (3) per-particle proper time in the trajectory output; later (2) the flux through a sphere about the tracker and (4) a pericentre counter (core's `JOURNAL-id.md` entry 1 records the particles' proper time in snapshots and `.trajmet.bin`; not stated to D) |
| D-bh-dress | analytic-metric-excision | 15:10Z | 12-13 | open | excision by `alpha_exc` and removal of flagged particles for every analytic metric, counted in `n_excised`, `m_excised`; acceptance with `spike_lc.nrp` |
| D-bh-dress | newtonian-mode-point-mass | 15:10Z | 12-13 | open | a fixed softened point mass in the Newtonian mode; card throughput at 256^3 and 384^3 with 2e6 particles; whether the multigrid on refined meshes is verified; the pericentre counter in this mode |
| D-bh-dress | restart-skips-dump | 15:10Z | 12-20 | open | write the final restart of a chained run without advancing `last_time` (`restart.cpp:193-201`), so that every scheduled dump is written |
| D-bh-dress | puncture-on-torus (proposal) | 15:10Z | 2027-01-31 | open | put a puncture in a dust-filled torus (constraint solve with a puncture in a periodic box) on core's list for wave 3 |
| E-stoch-inf | initial-slice-at-nstar | 14:10Z | 11-22 | open | a problem-generator id that reads the background state and the mode file and writes the slice at N* with the corrected delta Pi, with a first-order constraint test (core asks E for per-shell transfer coefficients, `scalar-field-merged` item 2) |
| E-stoch-inf | noise-unit-test-results | 14:10Z | 11-22 | open | (a) the cancellation-free window increment in `NoiseShellFactors`, with a commit id; (b) test U9 on a card; (c) `rng::ModeEntity`, the meaning of stream 3 and the epoch rule in `rng.md` section 6 |
| E-stoch-inf | sf-diagnostics-and-interface | 14:10Z | 11-29 | partly | option names for (1) H/[H] and M/[M] in the history, (2) double-precision dumps of phi, Pi and the Z4c fields, (3) box means of phi, Pi, K, alpha ((4) the interface document is `coord/INTERFACES/scalar_field.md`, 0011) |
| F-hills | release-multi-puncture | 15:07Z | 11-22 | partly | the card memory at `max_nmb_per_rank = 2700` with three finders, and the correction of "about 190 leaves per level and hole" (measured 1.5-2.4 times that) in `multi_puncture.md` (release done: core-v0.3 on main) |
| F-hills | pairwise-common-horizon | 15:07Z | 12-06 | open | a common-horizon trigger per pair of punctures (`fastflow.cpp:1606-1612` uses the largest distance), or a tested confirmation that the heavy hole's finder finds the merged horizon after a 20:1 merger |
| F-hills | two-card-or-larger-blocks | 15:07Z | 12-13 | open | a two-card MPI build (vacuum Z4c) or a benchmark of 32^3 MeshBlocks on the three-puncture mesh, with MeshBlock-cycles per second and memory |
| F-hills | moving-clump-initial-data | 15:07Z | 12-13 | partly | core's plan for two moving equilibrium clumps on a moving heavy puncture in `nrpic_cf` (the wave-2 plan lists core's item `clump`; no reply from core) |
| F-hills | unequal-mass-gauge | 15:07Z | 12-06 | answered, not built | position-dependent shift damping that scales with the local mass (core's choice, `multi-puncture-merged` item 3; core's wave-2 item `gauge`) |
| F-hills | hrna-pair-force-optional | 15:07Z | 2027-01-15 | open | accept for a later wave or decline: a Newtonian pair force between test particles of the NRPIC pusher (HRNA in AthenaK) |
| kb | paper-code-links | 14:20Z | 11-29 | open | for each of the 25 links of `kb/curated/paper_code_links.tsv` the test or run that verifies it; whether `<z4c> nco` (`problems/jeans/jeans.athinput:127`) is dead |

## To kb

| From | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|
| A-emd-pbh | ingest-s1-references | 13:20Z | 12-06 | acknowledged, queued | entry ids of the twelve S1 references; ingest 1708.09143, 2608.13206, 2403.15126, 2605.30145, 1810.03490 (2605.30145 fetched in wave 2, kb/main 8a93349) |
| B-emd-gw | track-b-sources | 13:40Z | 11-29 | acknowledged, queued | index the eleven sources; fetch and index 2212.00425, 2312.12499, 1704.03500, 2012.14016, 2610.08045, 1708.09143 |
| C-sidm | index-locators-typos | 13:20Z | 12-13 | acknowledged, queued | index the locators of C's G0 report section 6 and record the source defects (`coord/BRIEF_ERRATA.md` section 5) |
| C-sidm | literature-fetch | 13:20Z | 12-06 | acknowledged, queued | the identifier of "Gurian:2025zpc" (item 1), then six further sources; kb notes it needs the metadata path |
| D-bh-dress | dress-and-coupling-sources | 15:10Z | 12-06 | open | Bertschinger 1985 and Fillmore-Goldreich 1984 (3/2 or 9/4), Einstein-Straus 1945, Mack-Ostriker-Ricotti 2007 and two arXiv ids, NR black-hole lattices and black holes in particle dark matter; record the annotations of 1305.2619 and 1707.06302 |
| E-stoch-inf | errata-s11-references | 14:10Z | 12-06 | acknowledged, queued | record the four checked errata as claims with their evidence and return the claim ids |
| F-hills | index-hills-sources | 15:07Z | 11-29 | open | index the nine Hills sources into group G21; the snapshot in which they appear |
| F-hills | locators-wanted | 15:07Z | 12-06 | open | one locator each for the flyby GW energy, gauges for punctures of mass ratio 10-20, junk-radiation energies of boosted Bowen-York punctures, the Roche-lobe fit |
| core | paper-metadata-and-philox | 15:10Z | 11-29 | open | page count, submission date and categories of arXiv:2611.12831 from the abstract record; Salmon et al. 2011 (Philox) or a statement that it is not obtainable |

## Between tracks, and from core to the tracks

| From | To | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|---|
| A-emd-pbh | B-emd-gw | periodic-slicing | 13:20Z | 12-13 | open | the slicing B recommends for collapse to a horizon in a periodic box, and whether B takes the shared test (profile of 2609.14218 at mu = 0.5, e = 0) |
| B-emd-gw | A-emd-pbh | matter-era-slicing | 13:40Z | 12-13 | open | tell B when A has a slicing candidate (B reruns delta = 0.05); agreement that A owns the general Szekeres solution and B its planar reduction |
| D-bh-dress | A-emd-pbh | ltb-conventions | 15:10Z | 12-06 | open | A's LTB table conventions with format 2, the lapse A chooses after its scouting runs, A's generator for comparison with `es_model.py` |
| E-stoch-inf | B-emd-gw | nrcosmo2-and-diagnostics | 14:10Z | 12-06 | open | yes or no to one shared spectrum and constraint-ratio code in `python/nrpic/` through core; a month for the in-code constraint solve (B-pre-5) |
| F-hills | C-sidm | clump-models | 15:07Z | 12-13 | open | a table of collisionless cluster models with m/R between 0.05 and 0.1 (profile, linear stability, relaxation time in NRPIC) and where they live |
| core | A-emd-pbh | format2-and-gauge | 15:10Z | 11-29 | partly | A's lapse choice among the untried options (`lapse_kdriver`, `lapse_volume`, a driver towards dust slicing, a wider edge); A's earlier proposal ranks other options (K_ref, softplus, shock-avoiding term; `phase1-generator-and-gauge-options` item 2). The cross-check of `expanding_ball.py` is done (run A-20261115-130257-a7374a4, `scouting-runs-ball` item 5) |
| core (info) | C-sidm | collision-operator-merged | 15:10Z | 11-29 | open | the date of C's independent check on the merged executable, and C's choice on the energy defect: smaller collision cells or a pair-energy correction at the particles' positions |
| core (info) | D-bh-dress | ball-and-puncture-combined | 15:10Z | 11-29 | open | whether D needs the background factor of the puncture correction to count matter components (item 4) for G1 |
| core (info) | E-stoch-inf | scalar-field-merged | 15:10Z | 11-29 | open | the mode files and per-shell transfer coefficients of delta phi, delta Pi, delta chi, delta K, or a date; the checks of item 3 (inflection potential, phase convention, test L5, level and k^2 choice) |
| core (info) | F-hills | multi-puncture-merged | 15:10Z | 11-29 | partly | the mass ratio and resolution of F's first vacuum passage, so that core sizes the shift-damping work (F's `stage/G1/STATUS.md` names q = 10 at m/8; decision 0013 puts q = 4 first; no reply to core) |
