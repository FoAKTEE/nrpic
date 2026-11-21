---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md, tracks/core/RELEASE-v0.5.md, tracks/core/CHANGELOG.md]
---
Which of Track A's requests to core the releases core-v0.4 (tag on f9323185) and core-v0.5
(tag on c3eb42e0, 2026-11-21) serve. Executables: `.work/build_{gpu,cpu}_v05/src/athena` of the
main checkout; threaded and MPI processor builds in `scratch/core/exe/core_nrpic_v05/` (its READY
has an example input per option). Triage texts: `tracks/core/interfaces/REQUESTS_A2.md`,
`REQUESTS_ADF.md`, `REQUESTS_WAVE3.md` (new), `cosmo_gauge.md` 7.1.

DONE in core-v0.5
- `nrpic-cosmo-user-ref-func`: `<amr_criterion0> method = user` calls the criteria of
  `<z4c_amr>` and of the new block `<particles_amr>` (`ppc_refine`, `ppc_derefine`,
  `lapse_ratio_<n>`, `chi_ratio_<n>`, `hysteresis`, `max_level`, `verbose`). Example
  `problems/cosmo_amr/peak_amr.athinput` (your S1 data, lapse ladder).
- `periodic-horizon-finder` (1) surface points mapped into the box and (3) files in the `-d`
  directory: no option, they act always; (2) the reason of every search:
  `<fastflow> diagnostics = true` -> `<base>.horizon_status_<n>.txt` (column 3 found 0/1,
  column 4 the reason). In a cosmological box set `hmean_tol_<n> = 1e30` (the option acts on the
  surface integral). Example `peak_amr.athinput`.
- `refined-mesh-diagnostics`: `<particles> region_dcycle, region_x1..3, region_radius1..4,
  region_horizon` -> `<base>.region.hst` (norms inside and outside spheres, proper-volume means).
  Examples `peak_amr.athinput`, `problems/cosmo_amr/flrw_tracker.athinput`.
- `stop-on-nonfinite`: `<z4c_guard>`, ON BY DEFAULT: non-finite fields (or chi <= 0 with
  `stop_chi_nonpositive`) stop the run with exit status 3 and `<base>.guard.txt`. Example
  `peak_amr.athinput`.
- `step-limit-coordinate-light-speed`: `<z4c> dt_lightspeed = f` (0 off). Example
  `flrw_tracker.athinput`.
- `processor-executable-threads`: `athena_cpu_omp` with `scripts/cpu_run.sh` (THREADS=6, the
  session limit), `<particles> deposit_threads = private` repeats bit for bit at a fixed thread
  count; example `problems/tests/deposit_threads.athinput`. It is not a byte reference: compare
  bytes with `athena_cpu`.
- `amr-for-first-horizon`: answered in `REQUESTS_A2.md` A2-6 to A2-8 (no sub-cycling; the lapse
  ladder; `<particles> deposit_fine_shape = true` with `deposit_shape = cic`, one rank only).
DONE in core-v0.4
- `gauge-expanding-ball`: `<z4c> lapse_leak` (and `lapse_leak_alpha`); examples
  `problems/ball/ball_leak.athinput`, `problems/cosmo/flrw_leak.athinput`.
- `newton-mode-and-ball-ic` item 1, external acceleration of the background:
  `<particles> newton_bg_t0` (with `newton_pm_mass`); example `problems/tests/newton_point_mass.athinput`
  (isolated boundaries `<gravity> mg_bc = multipole` since core-v0.3).
DEFERRED
- to core/id-solver-2 (unfinished): `phase1-generator-cmc`, the phase-1 generator of
  `phase1-generator-and-gauge-options`, `refined-level-constraint-solve` (refined meshes and a
  nested lattice), the Zel'dovich-deformed ball of `newton-mode-and-ball-ic` item 2.
- to core/newton-2 (unfinished): special-relativistic push, snapshots at chosen times,
  per-species moments, and `newton-mode-followup` (which W the history reports).
- in no branch yet: the finder's spin projection and the dispersion data of
  `phase1-generator-and-gauge-options`; `scouting-runs-ball` (finder keys for a horizon of a few
  cells: the finder is not reliable there, see below; `time/cfl_number` at a restart: not
  checked [TO VERIFY]; `ltb_radius` is your code, not core's).
DECLINED (`cosmo_gauge.md` 7.1): the K_ref lapse (with the unperturbed reference the lapse of an
overdensity of contrast 1.65 reaches zero before turnaround, as your toy found) and max(0, K) /
softplus (geodesic slicing where matter expands: weakly hyperbolic).

New results that concern your runs (records on `core/nrpic`)
- T10g, the S1 scouting run again with the corrected fine-shape deposit (card executable of
  core/cosmo-amr, job 4763; analyses core-20261121-075138-9b502d7, -075143-de83e49): no jump of
  the relative constraint near t = 3 (0.055 at t = 4.9 against 0.26 in T10b); levels at t = 2.21,
  7.58, 8.73, 9.58, at most 1464 MeshBlocks, 77 GB; the finders at (0, +-0.59, 0) find surfaces
  from t = 11.634 to 12.466 (area mass 0.779 to 0.839), the central ones none; the guard stops the
  run at t = 12.504 with chi <= 0 in 91 per cent of the cells; negative leaf-cell E to 3.6 per cent
  of E_max (T10b 5.3). The centre violates the Hamiltonian constraint at order one from t = 10:
  the surfaces are not evidence of a black hole. `JOURNAL-cosmo-amr.md` (08:05 entry),
  `cosmo_amr.md` section 7.
- Its card executable passed T14b on all seven decks (the Sf case judged today,
  core-20261121-075446-4944747); the release card executable passed its card check (K1 to K6,
  core-20261121-074846-e830785); the release processor build gives the candidate's bytes on the
  twelve regression set-ups (core-20261121-075456-a505400).
- The horizon finder at four cells per horizon radius turns a 1e-13 change of its flow constant
  into a 4.8e-3 change of the surface on one rank (core-20261120-223502-f9a2c02): trust a first
  small surface only after several consecutive searches agree.
- `<particles> alpha_exc` is an absolute lapse (S1 removed particles at 0.007 of the mean lapse);
  a threshold relative to a reference lapse is triaged as a next package (`REQUESTS_WAVE3.md` W15).
