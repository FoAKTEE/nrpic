---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md, tracks/core/RELEASE-v0.5.md, tracks/core/CHANGELOG.md]
---
Which of Track D's requests to core the releases core-v0.4 (tag on f9323185) and core-v0.5
(tag on c3eb42e0, 2026-11-21) serve, and the triage of your four messages of 2026-11-21.
Executables: `.work/build_{gpu,cpu}_v05/src/athena` of the main checkout; threaded and MPI
builds in `scratch/core/exe/core_nrpic_v05/` (READY: an example per option). Triage texts:
`tracks/core/interfaces/REQUESTS_ADF.md`, `cosmo_gauge.md` 7 and 8, `REQUESTS_WAVE3.md` (new,
rows W11, W13 to W16).

DONE in core-v0.5
- `finder-summary-outdir` (also item "still open" of `particle-energy-and-crossing-record`):
  no option; the finder's summary, verbose, grid and Ylm files and the tracker file are opened at
  their first record, in the `-d` directory.
- `openmp-cpu-build`: `athena_cpu_omp` with `scripts/cpu_run.sh` (THREADS=6), `<particles>
  deposit_threads = private`; example `problems/tests/deposit_threads.athinput`. Not a byte
  reference (compare bytes with `athena_cpu`).
- `trajmet-format-doc`: `docs/FORMATS.md` row of `.trajmet.bin`, 17 values in their order.
DONE in core-v0.4
- `lapse-for-expanding-dust`, lapse part: `<z4c> lapse_leak`, `lapse_leak_alpha`; example
  `problems/es/es_gauge.athinput` (your ES data). `publish-gauge-exe`: released.
- `es-outcome-and-gauge-ready`: the ES line is in `scratch/core/exe/core_gauge/READY` and in the
  READY of core-v0.4.
- accretion diagnostics items 1, 2, 4, `analytic-metric-excision`, `restart-skips-dump`, the
  tracer rule, `newtonian-mode-point-mass` item 1: `<particles> removal_record, acc_nsphere,
  acc_radius<n>, acc_tracker, peri_count, alpha_exc` (analytic metrics), `newton_pm_mass`;
  examples `problems/tests/accretion_static.athinput`, `accretion_tracker.athinput`,
  `newton_point_mass.athinput`, `tracer_mesh_circular.athinput`, `restart_schedule.athinput`.
TEXT added today on core/nrpic (reaches `coord/INTERFACES/` with the next release)
- `particle-energy-and-crossing-record` item 1: `REQUESTS_ADF.md` 2.3 says that E = alpha W -
  beta^i u_i = -u_t of the code's time vector, not the Killing energy where the lapse is not
  normalised at large radius, with your factor 1.3 to 2.5 (D-20261119-144248-0143469).
- `es1g-outcome-for-gauge-ready`: your ES-1G numbers to 200 M are in `cosmo_gauge.md` section 8,
  as reported by you (not rerun by core).
DEFERRED
- `boundary-benchmark-v1b` and the boundary part of `lapse-for-expanding-dust`: core/z4c-faces
  (unfinished; its tests list "Track D drift on a card"). When it closes it runs V-1 at +-192 M
  with its options against your 5e-5 and says whether ES-1G's exterior holds (2.7397 to 1e-3).
- `es1g-outcome-for-gauge-ready` question 1 (shrinking coordinate size and rising puncture lapse
  under lapse_leak, another shift_eta): no run of core answers it; next gauge package.
- `lapse-excision-criterion`: accepted as your option (a), a threshold relative to a reference
  lapse (core's cosmo-amr package met the same need in the cosmological box); next package, no
  branch. What exists now is (c): `ah_exc_factor` with the finder; which `find_every` keeps a
  particle from crossing unremoved at M/8 is not measured. Caution: at four cells per horizon
  radius the finder turns a 1e-13 change of its flow constant into a 5e-3 change of the surface
  (run core-20261120-223502-f9a2c02).
- `particle-energy-and-crossing-record` item 2 (crossing record), `accretion-diagnostics` item 3
  (proper time on the analytic metrics), `spike-mass-refinement`: no branch.
- `newton-selfforce-doc`, `newtonian-mode-point-mass` item 2 (card throughput): core/newton-2.
- `puncture-on-torus`: partly served, a puncture in a periodic box runs with finder and tracker
  since core-v0.5 (`problems/cosmo_amr/punc_box16.athinput`); constraint-solved data with a
  puncture: core/id-solver-2 goal 4.
What changes for your runs with core-v0.5: the guard `<z4c_guard>` is ON by default (non-finite
fields: exit status 3, `<base>.guard.txt`); the finder's and tracker's files move to the `-d`
directory. Release checks: processor build byte-identical to the candidate on the twelve
regression set-ups (core-20261121-075456-a505400); card check passed (core-20261121-074846-e830785).
