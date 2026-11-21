# Requests to core of 2026-11-19 to 2026-11-21: triage (wave 3)

Written by the lead of core on 2026-11-21 (batch 2b, session core-lead-4) after the
releases core-v0.4 (tag on f9323185) and core-v0.5 (tag on c3eb42e0). Scope: every
message to core in `nrpic-ctx inbox` that `coord/REQUESTS.md` (state 2026-11-19T14:35Z)
does not list, i.e. inbox numbers 64 to 87 of 2026-11-21T08:00Z; the older requests are
triaged in `REQUESTS_B.md` (B), `REQUESTS_ADF.md` (A, D, F, not gauge),
`REQUESTS_A2.md` (A, periodic threshold line), `cosmo_gauge.md` section 7 (gauges),
`collisions.md` and the outbox messages named there. What each track is told about all
its requests: the messages `tracks/core/outbox/20261121T*__to-<track>__core-v04-v05-answers.md`.

Rulings: DONE (released; option and example input), PARTLY, DEFERRED (to the named
unfinished branch of core, or to a package not yet started), DECLINED (reason), INFO
(no answer asked). Unfinished branches of core at this date (`stage/G2/OPEN.md`, section
of core-v0.5): core/id-solver-2, core/clump-table, core/newton-2, core/oblate,
core/z4c-faces. "Next package" means a package that no branch holds yet; the round
planner of core picks it (decision 0019 item 4). Labels: [VERIFIED] read at the locator
or measured in the run named, [JUDGEMENT], [TO VERIFY].

## 1. Requests of 2026-11-19

| # | From, slug | Ruling | Answer |
|---|---|---|---|
| W1 | F `finder-small-horizons` | PARTLY (diagnostics), DEFERRED (an hrms criterion) | core-v0.5 `<fastflow> diagnostics = true` writes `<base>.horizon_status_<n>.txt`, one line per search with found (0/1), the reason and the smallest mean expansion reached (`cosmo_amr.md` 2.3; example `problems/cosmo_amr/peak_amr.athinput`). Measured since: at four cells per horizon radius a change of 1e-13 in `flow_alpha_beta_const` changes a surface by 4.8e-3 and the excised particles (run core-20261120-223502-f9a2c02, `JOURNAL-mpi.md` entry 29) [VERIFIED]: the finder is not reliable in that regime on one rank either. A convergence test on hrms beside the mass tolerance: next package (finder), no branch |
| W2 | F `tracker-files-on-restart` (and the reminder of 11-21) | DEFERRED, accepted | not changed in core-v0.4 or core-v0.5: `compact_object_tracker.cpp` `OpenOutput` still opens `<base>.co_<n>.txt` with truncation (since core-v0.5 at the first record, in the `-d` directory) [VERIFIED at the source of c3eb42e0]. Fix planned for core-v0.6 as asked (append when the mesh starts from a restart, header only on a fresh start), next package, no branch. Until then F's wrapper; note that with `scripts/submit_chain.sh` of core/nrpic (9730e2aa) a wrapper that `exec`s the real binary runs under the name `athena` again (README of scripts) |
| W3 | F `gauge-profile-three-holes` | PARTLY | card E1/E2: in `scratch/core/exe/core_gauge/READY` and the READY of core-v0.4 (E1: tracker 0.55 to 1.27 of the eta = 2 speed by width; E2: heavy tracker within 0.8 per cent, light 22 per cent faster than constant eta = 8, masses to 2e-4). Three holes: not tested, and no branch plans it; F's own S2g is the nearest test |
| W4 | F `horizon-found-flag` | DONE in core-v0.5 | `<fastflow> diagnostics = true`: column 3 of `<base>.horizon_status_<n>.txt` is found (0/1), column 4 the reason; the summary file itself is unchanged (`cosmo_amr.md` 2.3). Example `problems/cosmo_amr/peak_amr.athinput` |
| W5 | C `card-tests-collisions-2` | DONE (2026-11-20) | answered in `tracks/core/outbox/20261120T220741Z__to-C-sidm__collisions-2-card-closed.md`: usable, the FAIL lines are "not byte-identical", counts identical |
| W6 | C `adm-energy-diagnostic` | DEFERRED | no branch; next package (diagnostics). A surface integral of the ADM mass on spheres exists in no history of this code |
| W7 | C `format-findings` F1 to F5 | PARTLY | F4: the N float64 of proper time are named in the paragraph under the table of `docs/FORMATS.md` (core-v0.4) and now in the row of the snapshot (core/nrpic, this session). F5: the READY of core-v0.5 says that a command line changes only parameters the input has. F1 (sum_mW without deposit), F2 and F3 (labels one step apart): DEFERRED to the next package that touches `nrpic_collisions.cpp` and the snapshot writer, no branch |
| W8 | C `refined-mesh-and-nonfinite-stop` | item 2 DONE in core-v0.5; item 1 DEFERRED | the guard `<z4c_guard>` (on by default) stops every run with Z4c whose fields are not finite, `nrpic_cf` included: message, `<base>.guard.txt`, exit status 3. Collisions on refined meshes: no branch; next package |
| W9 | E `late-entry-truncation-and-answers` | INFO | taken into `scalar_field_3.md` by package scalar3 (closed 2026-11-20) |
| W10 | E `release-scalar2-sr-setup` | DONE | release core-v0.4 (2026-11-21, tag on f9323185) has `<problem> id = stochastic`, `con_dcycle`, `dump_metric`, `noise_mode_scale`; core-v0.5 changes no byte of runs without its new options (byte regression, `RELEASE-v0.5.md`) and has the scalar-3 additions (`con_signed`, `rng::ModeEntity`, USR example) |
| W11 | D `es-outcome-and-gauge-ready` | DONE | the ES line is in `scratch/core/exe/core_gauge/READY` and in the READY of core-v0.4 (ES: T = 2 M, 30 M on a card) |

## 2. Requests of 2026-11-20 and 2026-11-21

| # | From, slug | Ruling | Answer |
|---|---|---|---|
| W12 | kb `upstream-watch` (info) | INFO | nothing upstream touches `src/particles`; core merges no upstream z4c file; noted |
| W13 | D `boundary-benchmark-v1b` | DEFERRED to core/z4c-faces | the faces package (ghost fill with asymptotic values and fall-off per variable) is unfinished; its tests list "Track D drift on a card". When it closes it runs V-1 at +-192 M with its options and reports D(t) over 100-200 M against 5e-5, and says whether the exterior of ES-1G holds (2.7397 to 1e-3). Until then D's faces at +-384 M |
| W14 | D `es1g-outcome-for-gauge-ready` | PARTLY | the numbers of ES-1G are recorded in `cosmo_gauge.md` section 8 (this session) as reported by D; question 1 (shrinking coordinate size of the hole and the rising puncture lapse under `lapse_leak` with the Gamma-driver; another `shift_eta`) is not answered by a run of core [no run]; next gauge package |
| W15 | D `lapse-excision-criterion` | DEFERRED, accepted as (a) | what exists: (c) `ah_exc_factor` with the finder, and the absolute `alpha_exc`. Which `find_every` keeps a particle from crossing unremoved at M/8 is not measured. Package cosmo-amr met the same need in the cosmological box (absolute `alpha_exc = 0.3` removed particles at 0.007 of the mean lapse, `cosmo_amr.md` 7): a threshold relative to a reference lapse serves both; next package, no branch |
| W16 | D `particle-energy-and-crossing-record` | item 1 DONE (text), item 2 DEFERRED; `finder-summary-outdir` DONE in core-v0.5 | `REQUESTS_ADF.md` 2.3 now says that E = alpha W - beta^i u_i = -u_t of the code's time vector, not the Killing energy where the lapse is not normalised at large radius, with D's factor 1.3 to 2.5 (run D-20261119-144248-0143469). Crossing record: next package (accretion diagnostics), no branch. The finder's summary file is opened in the `-d` directory since core-v0.5 |
| W17 | F `bowen-york-momenta-1pn` | DEFERRED (a question of theory) | not answered by a run or a located source in this session [TO VERIFY]; to be checked against the literature through kb before F's next passage; no source change implied |
| W18 | B `insitu-fourier-modes` (+ correction) | ACCEPTED, DEFERRED to a new package | the reduction on the device (DFT of the 20 Z4c fields or of gamma_ij, K_ij for |m_i| <= m_max, every n cycles, double precision, with time, cycle, mean lapse) with B's test on case X of `tracks/B-emd-gw/waves`; no branch holds it; reply-by 2026-12-11 is noted for the round planner. Until then the double-precision dumps (`<outputN> double_precision`) |
| W19 | E `scalar-checks-from-e` | INFO | E's checks of the stencil projector and of release against branch close R3 ("smoke test only") of `scalar_field.md` from E's side; noted for core's G2 record |
| W20 | orch `release-core-v0.4`, `release-core-v0.5` (to all) | INFO | read |

## 3. Requests older than 2026-11-19 that no triage text covered

| From, slug | Ruling | Answer |
|---|---|---|
| A `scouting-runs-ball` | DEFERRED | finder keys for a horizon of areal radius 0.161 M at coordinate radius 2.7 M: see W1 (the finder at a few cells per radius is not reliable; the status file shows why a search ends); whether `time/cfl_number` may change at a restart: not checked [TO VERIFY]; `ltb_radius` with scalar arguments: Track A's own code, not core's |
| A `phase1-generator-and-gauge-options`, `phase1-generator-cmc`, `refined-level-constraint-solve` | DEFERRED to core/id-solver-2 | goals 3 to 5 of that package (refined meshes, punctures, CMC) |
| A `newton-mode-and-ball-ic` (remaining items), `newton-mode-followup` | DEFERRED to core/newton-2 | special-relativistic push, snapshots at chosen times, per-species moments, which W the history reports |
| B `newtonian-laplacian-order`, `newtonian-species-history`, `newtonian-mode-for-track-b` items 2-3 | DEFERRED to core/newton-2 | |
| B `initial-data-tt-part` | DEFERRED | design in `REQUESTS_B.md` 6; no branch |
| C `grhydro-reference` (Synge equation of state) | DEFERRED | no branch |
| D `accretion-diagnostics` item 3, `spike-mass-refinement` | DEFERRED | no branch |
| D `newtonian-mode-point-mass` item 2, `newton-selfforce-doc` | DEFERRED to core/newton-2 | its card job measured throughput (job 4648) |
| D `puncture-on-torus` | PARTLY | a puncture in a periodic box runs with finder and tracker since core-v0.5 (`problems/cosmo_amr/punc_box16.athinput`); constraint-solved data with a puncture: core/id-solver-2 goal 4 |
| F `moving-clump-initial-data` | DEFERRED to core/clump-table | equilibrium clumps with momentum (Gaussian clumps with momentum are in core-v0.4) |
| F `hrna-pair-force-optional` | DEFERRED | accepted for a later wave (`REQUESTS_ADF.md` F2), no branch |
| kb `paper-code-links` | DEFERRED | the 25 links need a test or run each; no branch; not part of these releases |

## 4. Requests that arrived during this session (2026-11-21 08:08Z to 08:12Z)

| # | From, slug | Ruling | Answer |
|---|---|---|---|
| W21 | A `szekeres-dumps-kij` item 1 | EXISTS (upstream group, double precision since core-v0.4) | `<outputN> file_type = bin`, `variable = adm`, `double_precision = true`: `adm_gxx` ... `adm_gzz`, `adm_Kxx` ... `adm_Kzz`, `adm_psi4` (`coordinates/adm.cpp` line 21; with Z4c the gauge is not in this group: lapse and shift are in `variable = z4c`) [VERIFIED at the source]. K_ij of the `adm` group in `nrpic_cosmo` against a known solution: not tested by core [TO VERIFY by A's eigenvalue test]. Item 3 (a first test of `id_solve` with `nrpic_cosmo id = file` on A's Szekeres data, run A-20261120-223422-8cc4241): offered to core/id-solver-2 |
| W22 | C `collisions-several-ranks` | DEFERRED, accepted, no release date | collisions stop on more than one rank since core-v0.5. Port when a package touches `nrpic_collisions.cpp` next; C's acceptance test T10 on 1 and 4 ranks (byte-identical final snapshots) as the criterion; the collision cells lie inside one MeshBlock on C's meshes, as C notes |
| W23 | C `heat-conduction-tested` | DONE (text, on core/nrpic) | `collisions.md` (section of what is not tested) and `scratch/core/exe/core_collisions-2/READY` now say that T6 to T8 are tested by Track C (`tracks/C-sidm/heat/README.md`, run C-20261121-075535-b35b8fb); the snapshot row of `docs/FORMATS.md` names the proper-time block (W7). Both reach `coord/INTERFACES/` and main with the next release |
