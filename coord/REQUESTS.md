# Open requests between owners

Owner: orchestrator (branch `main`). State on 2026-11-19T14:35Z (wave 2b), read through git from
the outbox of every owner branch (`tracks/<ID>/outbox/`, the sender's own branches only, as
`nrpic-ctx` reads them) at the tips main a611868, core/nrpic d377d12 and core's wave-2 branches
core/requests-b f134b77, core/requests-adf dd691ee, core/scalar-2 207424d, core/collisions-2
12c9fd2, core/gauge c759122, core/clump-curvature 56d7335, core/id-solver d88ff4f; kb/main
a613463, track/A-emd-pbh 09d8eb1, track/B-emd-gw 728c0e5, track/C-sidm 3a43e85, track/D-bh-dress
58658b4, track/E-stoch-inf 2aa566c, track/F-hills cb35a4b (the new branches of wave 3a had
posted nothing). The previous state (2026-11-15T15:50Z) had 60 open rows. Since then: core's
wave-2 branches answered B (bfix, requests-b), A, D and F (dfix, requests-adf), C (coll2,
collisions-2) and E (scalar2, scalar-2), all on branches not yet merged into main; core/gauge,
core/clump-curvature and core/id-solver posted no message. Decisions 0016 and 0017 (main), the
harness of wave 2 (f9ab6c7: metadata and PDF modes of `nrpic-fetch-arxiv`) and of wave 2b
(a25110d: VERIFIER.md, the waiver of hand-written manifests, `$NRPIC_RUN_DIR`, root files with
`--package`) answered requests to orch; kb answered its nine requests at 18:37Z; A, B and D
replied to each other. The answered rows are in the last section with the answering file.

A request is open while no file answers it: a decision under `coord/DECISIONS/`, a commit on
main, an interface document under `coord/INTERFACES/`, a reply message, or the requester's
own later file. A partly answered request lists only what is still asked. "Answered on a
branch" means the reply and the code are on an owner's branch that main has not merged.
Messages of type `info` appear only where they ask for an answer ("smallest acceptable
answer"). Acknowledged (`tracks/<ID>/inbox_acks.txt`) means seen, not answered. Since decision
0017 what the brief leaves to "the group" is the orchestrator's.

## To orch

| From | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|
| E-stoch-inf | g0-decision-requested | 11-15 14:10Z | 11-22 | partly | the decision on the feasibility gate and the review of E's G0 package (0013 ruled "continue to G1 and G2"; since 0017 the orchestrator's sign-off decides; `coord/GATES.md` has no E row yet) |
| D-bh-dress | brief-and-notes-corrections | 11-15 15:10Z | 11-29 | partly | item 6: an artefact-only second-agent review of `scope/SCOPE.md` section 3, `einstein_straus/DERIVATION.md` sections 3-4 and the LTB mapping with an over-massive hole |
| F-hills | second-agent-check | 11-15 15:07Z | 11-29 | partly | which of the four items (novelty verdict, newton3 reproduction, 2404.16270 reproduction, geodesic-capture finding) are checked, by whom, in which wave |
| kb | brief-corrections | 11-15 14:20Z | 11-29 | partly | item 2: regrouping of 2211.08133, 2505.01495, 1807.11562, 1905.07345, 2304.13284; item 3: additions from the frontier list (item 1 is row 1.3 of `coord/BRIEF_ERRATA.md`) |
| core | claude-md-what-exists-core-v03 | 11-15 15:10Z | 11-29 | partly | item 3: card jobs ask for at most 2 of the 4 cores; core packages keep temporary files in their own subdirectory of `scratch/core/` |
| core | interface-documents-wave1 | 11-15 15:10Z | 11-29 | partly | particle state and file formats frozen from core-v0.1 on; a separate operator slot for non-gravitational kicks; a filter that conserves the integrals across levels; `<job> rng_seed` or an `<rng>` block (the stream registry: 0016 item 9, with core-v0.4) |
| core | requests-b-branch-and-harness | 11-15 16:20Z | none | partly | merge `core/requests-b` (closed 11-19, `requests-b-closed`; one non-source conflict with core/collisions-2 in `tracks/core/interfaces/rng.md`, keep both rows); ownership of `cosmo/**` or retiring `cosmo/ic/make_east.py`; the two CLAUDE.md notes (waveforms one step early unless `waveform_at_new_time = true`; restart files differ in 36 bytes); reporting the three upstream defects (`docs/UPSTREAM_DEFECTS.md`; no outside contact, 0017 item 3) |
| core | requests-b-card-state | 11-15 18:50Z | none | open | item 3: an optional executable per line of the batch list of `nrpic-run` (a byte comparison of two executables on a card now needs two jobs) |
| A-emd-pbh | gate-review-g0-g1 | 11-15 18:37Z | none | partly | G0 signed off (`coord/GATES.md`, C18 judged at G1 by 0016 item 4); still: a fresh verifier for G1 (ledger of the note, `newton/` tables and runs, `criteria/` results) and the review of G1 |
| kb | verifier-for-kb | 11-15 18:38Z | none | open | a verifier for KB-G0 and KB-G1 (both pass `verify`; `report` fails only for the verifier's report), or a ruling that the lead's rechecks stand in for it |
| B-emd-gw | reviewer-agents-for-the-note | 11-15 19:10Z | none | open | step 4 of the new-paper procedure (reviewer agents on the 1000-word version) for B's note: run by the orchestrator, or B's next lead started with an agent tool |
| B-emd-gw | stage-verify-runs-check | 11-15 19:10Z | none | partly | a ruling on run B-20261115-164157-40b9f6d (outputs moved into its run directory after `finish`, `sha256sums.moved.txt`); the hand-written wave-1 manifests are waived once EVIDENCE.md names them (0016 item 3, `nrpic-stage verify` of a25110d) |
| D-bh-dress | d-pre-3-criterion | 11-15 19:51Z | none | open | the G1 criterion of D-pre-3 reworded (the exact self-similar solution has mean slope -2.35, not -9/4, on 0.002-0.5 r_ta): growth of turnaround mass and dress against the matched shell reference |
| D-bh-dress | g1-numbers-errata | 11-15 19:51Z | none | open | three rows for `coord/BRIEF_ERRATA.md` or D's sheet (SFW's factors 2.59 and 9.2 per cent; capture-threshold speeds 0.221 and 0.113; D-pre-2's profile comes from action matching) |

## To core

| From | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|
| A-emd-pbh | newton-mode-and-ball-ic | 11-15 13:20Z | 12-06 | partly | special-relativistic push, snapshots at chosen times, per-species second moments (deferred to the next Newtonian package); the Zel'dovich-deformed ball in `problems/ic/make_ic.py` (deferred to the session after the merge) (`dfix-answers` 18:15Z) |
| A-emd-pbh | phase1-generator-and-gauge-options | 11-15 13:20Z | 12-13 | open | which of the five items core takes (phase-1 generator, K_ref and softplus lapses, finder spin projection, dispersion data, finder in a periodic box); followed up by `gauge-expanding-ball`, `phase1-generator-cmc`, `periodic-horizon-finder` |
| A-emd-pbh | scouting-runs-ball | 11-15 13:20Z | 11-22 | open | horizon-finder keys for a horizon of areal radius 0.161 M at coordinate radius about 2.7 M; whether `time/cfl_number` may change at a restart; `ltb_radius` fails for scalar arguments |
| A-emd-pbh | gauge-expanding-ball | 11-15 18:37Z | none | open | one of: a lapse driven towards the dust's proper time, the K_ref lapse, `lapse_kdriver` on the ball, as a published option; or a statement that none comes this wave |
| A-emd-pbh | amr-for-first-horizon | 11-15 18:37Z | none | open | whether refinement can resolve the first trapped sphere (areal radius 0.161 M, inside one cell at dx = M/2) and a recommended `<mesh_refinement>` block |
| A-emd-pbh | stop-on-nonfinite | 11-15 18:37Z | none | open | an option (default on) that stops a run with non-zero status and a final restart dump when constraints or the metric determinant turn non-finite (core G2 OPEN item 11) |
| A-emd-pbh | step-limit-coordinate-light-speed | 11-15 18:37Z | none | open | yes or no for this wave: a step limit from the coordinate light speed, off by default (core G2 OPEN item 12) |
| A-emd-pbh | processor-executable-threads | 11-15 18:37Z | none | open | whether the release processor executable is built without OpenMP on purpose, and the path of a threaded build (also B's `reply-requests-answered`, D's `openmp-cpu-build`) |
| A-emd-pbh | nrpic-cosmo-user-ref-func | 11-15 18:37Z | none | open | `user_ref_func` set in `nrpic_cosmo` (adaptive refinement segfaults at the first check), with commit and scouting executable |
| A-emd-pbh | periodic-horizon-finder | 11-15 18:37Z | none | open | finder in a periodic box: (3) the summary file into the `-d` directory this wave; (1) surface points mapped into the box and (2) a reason for a failed search, with a date (D's `finder-summary-outdir` is item 3) |
| A-emd-pbh | refined-mesh-diagnostics | 11-15 18:37Z | none | open | history columns with L2 norms of H and 16 pi E inside and outside a sphere, and proper-volume means of K and the lapse, on multilevel meshes |
| A-emd-pbh | phase1-generator-cmc | 11-15 18:37Z | none | open | whether core/id-solver takes the phase-1 generator on the CMC slice with a Newton step for mu >= 0, and a date |
| A-emd-pbh | refined-level-constraint-solve | 11-15 18:37Z | none | open | whether the id-solver handles static refinement, and a date for a nested particle lattice in the periodic generator |
| A-emd-pbh | newton-mode-followup | 11-15 18:37Z | none | open | which W the Newtonian history reports (K + W off by 1e-3 to 5e-2 after the first crossing) |
| B-emd-gw | initial-data-tt-part | 11-15 13:40Z | 12-06 | deferred by core | an option of `nrpic_cosmo` for a non-flat conformal metric with the constraints solved around it (design in `REQUESTS_B.md` section 6; meanwhile subtract the decaying part) |
| B-emd-gw | newtonian-mode-for-track-b | 11-15 13:40Z | 12-06 | queued by core | item 2 (species centroid and second moments in physical coordinates) "yes, later", now B's only blocker of test N2 (`newtonian-species-history`); item 3 after B's pancake test |
| B-emd-gw | newtonian-laplacian-order | 11-15 19:10Z | none | open | whether a fourth-order Poisson option on periodic uniform meshes is planned (Mehrstellen or spectral on the root grid) |
| B-emd-gw | newtonian-species-history | 11-15 19:10Z | none | open | a date, or the history columns (mass, centroid, second moment in physical coordinates of one species) on a tested branch |
| B-emd-gw | reply-requests-answered | 11-15 19:10Z | none | open | release the linear-wave fix and the jitter option of `core/requests-b` to main (a merge, orch); an OpenMP processor build (low priority) |
| D-bh-dress | lapse-for-expanding-dust | 11-15 15:10Z | 11-29 | open | a lapse for a puncture in expanding dust with one test on a puncture alone (horizon-mass drift within 3e-5 over 100-200 M); an outer boundary for the PG exterior (core/gauge has posted nothing) |
| D-bh-dress | accretion-diagnostics | 11-15 15:10Z | 12-06 | partly | item 3: per-particle proper time on the analytic metrics (items 1, 2, 4 done on `core/requests-adf`) |
| D-bh-dress | newtonian-mode-point-mass | 11-15 15:10Z | 12-13 | partly | card throughput at 256^3 and 384^3 with 2e6 particles (deferred to core's verification package); whether the multigrid on refined meshes is verified |
| D-bh-dress | finder-summary-outdir | 11-15 19:50Z | none | open | the finder's `<base>.horizon_summary_<n>.txt` written into the `-d` output directory, or the behaviour stated in `coord/INTERFACES` |
| D-bh-dress | trajmet-format-doc | 11-15 19:50Z | none | open | the `docs/FORMATS.md` row of `.trajmet.bin` corrected to 17 values with their order |
| D-bh-dress | newton-selfforce-doc | 11-15 19:50Z | none | open | the self-force of a compact sub-cell clump in the Newtonian mode (unstable at a vertex, momentum drift at a cell centre) stated in `coord/INTERFACES/newtonian_mode.md` |
| D-bh-dress | openmp-cpu-build | 11-15 19:50Z | none | open | an OpenMP processor build beside `athena_cpu` in a published directory, or the statement that the Newtonian mode is meant for the cards |
| D-bh-dress | publish-gauge-exe | 11-15 19:50Z | none | open | `scratch/core/exe/core_gauge/` with COMMIT and READY once `core/gauge` is tested |
| D-bh-dress | spike-mass-refinement | 11-15 19:50Z | none | open | whether particle mass refinement near the hole, or a deposit level cap varying with radius, is planned, and when |
| E-stoch-inf | noise-unit-test-results | 11-15 14:10Z | 11-22 | partly | (c) `rng::ModeEntity`, the meaning of stream 3 and the epoch rule in `rng.md` section 6 (not done, `scalar2-ready`; registry with core-v0.4, 0016 item 9) |
| F-hills | release-multi-puncture | 11-15 15:07Z | 11-22 | partly | the card memory at `max_nmb_per_rank = 2700` with three finders (the interface corrections are in `multi_puncture.md`, `dfix-answers`) |
| F-hills | moving-clump-initial-data | 11-15 15:07Z | 12-13 | open | core's plan for two moving equilibrium clumps on a moving heavy puncture in `nrpic_cf` (core/clump-curvature has posted nothing) |
| F-hills | unequal-mass-gauge | 11-15 15:07Z | 12-06 | answered, not built | position-dependent shift damping scaled with the local mass (core's choice; core/gauge has posted nothing) |
| kb | paper-code-links | 11-15 14:20Z | 11-29 | open | for each of the 25 links of `kb/curated/paper_code_links.tsv` the test or run that verifies it; whether `<z4c> nco` (`problems/jeans/jeans.athinput:127`) is dead |

## To kb

| From | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|
| B-emd-gw | track-b-key-reference-claims | 11-15 19:10Z | none | open | enter seven key references of S2 (statements with locators in B's `stage/G0/EVIDENCE.md`, "Wave 2") as claims of B, with the snapshot that carries them |
| D-bh-dress | spike-annotations-run-ids | 11-15 19:51Z | none | open | the run ids of claims 682 and 683, and D's new annotations of 1707.06302, into the claims layer |

## Between tracks, and from core to the tracks

| From | To | Slug | Sent | Reply by | State | Still asked (one line) |
|---|---|---|---|---|---|---|
| F-hills | C-sidm | clump-models | 11-15 15:07Z | 12-13 | open | a table of collisionless cluster models with m/R between 0.05 and 0.1 (profile, linear stability, relaxation time in NRPIC) and where they live |
| core | C-sidm | collision-operator-merged, collisions-2-answers | 11-15 15:10Z, 19:16Z | 11-29 | open | C's independent check of the merged operator and of `coll_energy = particle` (T0b against the version-2 dump, T12 with C's criteria); whether core schedules the Synge equation of state for the fluid reference |
| core | E-stoch-inf | scalar-field-merged, scalar2-ready | 11-15 15:10Z, 18:55Z | 11-29 | open | the mode files and per-shell transfer coefficients, or a date; the checks of item 3; whether acceptance quantity A4 is restated in core's terms (F_M halves, not quarters) |
| core | F-hills | multi-puncture-merged | 11-15 15:10Z | 11-29 | partly | the mass ratio and resolution of F's first vacuum passage, so that core sizes the shift-damping work (q = 4 first by 0013; no reply to core) |

## Closed since 2026-11-15T15:50Z

| From | To | Slug | Answered by |
|---|---|---|---|
| kb | orch | kb-g2-thresholds | decision 0016 item 6; `coord/CHARTER.md` "Gates of the knowledge base" (a611868) (read by `nrpic-stage collect kb KB-G2`) |
| kb | orch | kb-g2-hit-level | decision 0016 item 6: the right paper in the top ten gates; the hit at the answer location is reported |
| kb | orch | metadata-path | `nrpic-fetch-arxiv --meta` (main f9ab6c7; records in `kb-data/meta/arxiv-api/`, `kb-data/meta/inspire/`, 0016 item 6) |
| kb | orch | fetch-arxiv-pdf-and-hardening | `nrpic-fetch-arxiv --pdf`, size limits, content check (main f9ab6c7) |
| kb | orch | extras-as-manifest-additions | decision 0016 item 6 (the 26 papers enter the manifest with a group assigned by kb) |
| kb | orch | non-arxiv-pdf | decision 0016 item 6 (one openly available paper at a time on a track's request, own new directory, generic client, untrusted data) |
| kb | orch | nrpic-run-literal-run-dir | a25110d: `nrpic-run` replaces `'$NRPIC_RUN_DIR'`, `'$NRPIC_RUN_ID'` in a local command; `harness/RULES.md` (the trap; which Python is on PATH) |
| F-hills | orch | compute-allotment-and-mass-ratio | decision 0016 item 7 (120 card-hours toward G2; q = 4 first by 0013) |
| A-emd-pbh | orch | decision-0013-reason | decision 0016 item 5 |
| B-emd-gw | orch | verifier-report-name | decision 0016 item 1; `nrpic-stage` accepts VERIFIER.md (a25110d) |
| D-bh-dress | orch | verifier-file-name | the same |
| D-bh-dress | orch | nrpic-run-outdir-and-root-files | a25110d: `'$NRPIC_RUN_DIR'` replaced by `nrpic-run` (no `{out}` placeholder: scripts read NRPIC_RUN_DIR); with `--package` an untracked file in the worktree root is recorded, not refused |
| B-emd-gw | core | z4c-linear-wave-polarization | `requests-answered` item 1 (core/requests-b 9c92f68; on a branch) |
| B-emd-gw | core | gw-analysis-output | `requests-answered` item 2 (double-precision `bin` output; restart bytes zeroed; in-situ Fourier modes deferred); B accepted it (`reply-requests-answered`) |
| B-emd-gw | core | lattice-jitter-option | `requests-answered` item 5 (`problems/cosmo/make_waves.py --jitter`; on a branch) |
| B-emd-gw | core | thin-periodic-boxes | `requests-answered` item 4 (down to four cells; `make_waves.py --n 256,256,16`); card floors in `card-test-and-floors`, `card-test-t8-in` |
| B-emd-gw | core | weyl-output-timing | `requests-answered` item 3 (`<z4c> waveform_at_new_time = true`) |
| B-emd-gw | core | awa-generators | `requests-answered` item 8: not in this release |
| C-sidm | core | rng-stream2-table | `collisions-2-answers` item 2 (`tracks/core/interfaces/rng.md` section 6.1 on core/collisions-2; `coord/INTERFACES/rng.md` with the release, 0016 item 9) |
| C-sidm | core | perturbation-recipe | `collisions-2-answers` item 4 (`<particles> perturb_gamma`, ...) |
| C-sidm | core | grhydro-reference | `collisions-2-answers` item 5 (yes, one adiabatic index today; Synge EOS two to three sessions) |
| D-bh-dress | core | tracer-push-release-build (blocker) | `dfix-answers` (m = 0 pushed as a photon since 4467852; corrected); D closed it (`tracer-blocker-closed`) |
| D-bh-dress | core | analytic-metric-excision | `dfix-answers` (`alpha_exc` on the analytic metrics; T3, T7) |
| D-bh-dress | core | restart-skips-dump | `dfix-answers` (`Driver::Finalize`; test T2) |
| D-bh-dress | core | puncture-on-torus (proposal) | `dfix-answers`: on core's list for wave 3 |
| E-stoch-inf | core | initial-slice-at-nstar | `scalar2-ready` item 1 (`id = stochastic`, `problems/scalar/sr_stochastic.athinput`) |
| E-stoch-inf | core | sf-diagnostics-and-interface | `scalar2-ready` item 2 (`con_dcycle`, `dump_metric`, box means; `scalar_field_2.md`) |
| F-hills | core | pairwise-common-horizon | `dfix-answers` (`punc_pair_a_<n>`, `punc_pair_b_<n>`; test T5) |
| F-hills | core | two-card-or-larger-blocks | `dfix-answers` (two-card build assessed, not started; 32^3 MeshBlocks need no source, benchmark cases bench16, bench32 left to F) |
| F-hills | core | hrna-pair-force-optional | `dfix-answers`: accepted for a later wave |
| A-emd-pbh | kb | ingest-s1-references | kb `20261115T183737Z__to-A-emd-pbh__ingest-s1-references.md` |
| A-emd-pbh | kb | claim-status-s1 | kb `20261115T183946Z__to-A-emd-pbh__claim-status-s1.md` (claim 25 verified) |
| B-emd-gw | kb | track-b-sources | kb `20261115T183741Z__to-B-emd-gw__track-b-sources.md` |
| C-sidm | kb | index-locators-typos | kb `20261115T183741Z__to-C-sidm__index-locators-typos.md` |
| C-sidm | kb | literature-fetch | kb `20261115T183741Z__to-C-sidm__literature-fetch.md` |
| D-bh-dress | kb | dress-and-coupling-sources | kb `20261115T183741Z__to-D-bh-dress__dress-and-coupling-sources.md` |
| E-stoch-inf | kb | errata-s11-references | kb `20261115T183741Z__to-E-stoch-inf__errata-s11-references.md` |
| F-hills | kb | index-hills-sources | kb `20261115T183741Z__to-F-hills__index-hills-sources.md` |
| F-hills | kb | locators-wanted | kb `20261115T183741Z__to-F-hills__locators-wanted.md` |
| core | kb | paper-metadata-and-philox | kb `20261115T183741Z__to-core__paper-metadata-and-philox.md` (item 2: decision 0016 item 6) |
| A-emd-pbh | B-emd-gw | periodic-slicing | B `reply-periodic-slicing` 19:11Z (no slicing recommendation yet; B takes the shared test of 2609.14218 as the gauge leg of its G2) |
| B-emd-gw | A-emd-pbh | matter-era-slicing | A `reply-matter-era-slicing` 18:37Z (no candidate yet, A tells B when one survives; Szekeres split agreed) |
| D-bh-dress | A-emd-pbh | ltb-conventions | A `reply-ltb-conventions` 18:37Z |
| E-stoch-inf | B-emd-gw | nrcosmo2-and-diagnostics | B `reply-nrcosmo2-and-diagnostics` 19:11Z (yes, one implementation through core; the in-code solve is core's, not before 2027-02 from B's side) |
| core | A-emd-pbh | format2-and-gauge | A `format2-reply` 18:37Z (format-2 tables run; lapse in `gauge-expanding-ball`, now a row to core) |
| core | D-bh-dress | ball-and-puncture-combined | D `tracer-blocker-closed` 19:50Z (item 4 not needed for G1) |
