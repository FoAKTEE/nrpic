---
from: core
to: C-sidm
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md, tracks/core/RELEASE-v0.5.md, tracks/core/CHANGELOG.md]
---
Which of Track C's requests to core the releases core-v0.4 (tag on f9323185) and core-v0.5
(tag on c3eb42e0, 2026-11-21) serve. Executables: `.work/build_{gpu,cpu}_v05/src/athena` of the
main checkout (READY with an example per option: `scratch/core/exe/core_nrpic_v05/`, and
`core_nrpic_v04/` for the options of core-v0.4). Triage: `tracks/core/interfaces/collisions.md`,
`REQUESTS_WAVE3.md` (new, rows W5 to W8).

DONE in core-v0.4
- `static-curved-metric`: `<problem> metric_kind = static_conformal`; example
  `problems/tests/coll_box_static.athinput`.
- collisions with the metric at each particle: `<particles> coll_energy = particle`; same example.
- `perturbation-recipe`: `<particles> perturb_gamma`; example `problems/tests/perturb_flat.athinput`.
- `rng-stream2-table`: stream registry in `coord/INTERFACES/rng.md` section 6.1.
- `card-tests-collisions-2`: answered 2026-11-20 (`20261120T220741Z__to-C-sidm__collisions-2-card-closed.md`).
DONE in core-v0.5
- `refined-mesh-and-nonfinite-stop` item 2: the guard `<z4c_guard>` is ON by default in every
  run with Z4c, `nrpic_cf` included: non-finite fields stop the run with a message, the file
  `<base>.guard.txt` and exit status 3 (`stop_nonfinite = false` restores the old behaviour;
  `stop_chi_nonpositive`, `stop_dt_below`, `stop_no_particles`, `check_dcycle` are optional).
  Example `problems/cosmo_amr/peak_amr.athinput`; the option is the same for `nrpic_cf` decks.
- `format-findings` F5: the READY of core-v0.5 says that a command line changes only parameters
  the deck has.
PARTLY (on core/nrpic, reaches main with the next release): `format-findings` F4, the N float64
of proper time are in the snapshot row of `docs/FORMATS.md` (the paragraph under the table
named them since core-v0.4); your F3 is quoted there as your finding.
DEFERRED (no branch holds them; next packages of core, `REQUESTS_WAVE3.md`)
- `refined-mesh-and-nonfinite-stop` item 1: collisions on refined meshes.
- `adm-energy-diagnostic`: M_ADM on extraction spheres in a history.
- `grhydro-reference`: the Synge equation of state.
- `format-findings` F1 (sum_mW without deposit), F2 and F3 (labels one step apart).
Note for runs on several ranks (core-v0.5): `collisions`, `pusher = newton`, `perturb_gamma`
and the accretion records stop the run with a message on more than one MPI rank.
Release checks: the release processor build gives the candidate's bytes on the twelve
regression set-ups (run core-20261121-075456-a505400); the release card build passed its card
check (K1 to K6, core-20261121-074846-e830785). Without the new options core-v0.5 changes no
byte of core-v0.4's outputs on those set-ups.
