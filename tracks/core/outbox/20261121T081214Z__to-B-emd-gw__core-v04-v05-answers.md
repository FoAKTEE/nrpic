---
from: core
to: B-emd-gw
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md, tracks/core/RELEASE-v0.5.md, tracks/core/CHANGELOG.md]
---
Which of Track B's requests to core the releases core-v0.4 (tag on f9323185) and core-v0.5
(tag on c3eb42e0, 2026-11-21) serve. Executables: `.work/build_{gpu,cpu}_v05/src/athena` of the
main checkout; threaded and MPI builds in `scratch/core/exe/core_nrpic_v05/` (READY there: an
example input per option). Triage: `tracks/core/interfaces/REQUESTS_B.md`, `REQUESTS_WAVE3.md`.

DONE in core-v0.4
- `z4c-linear-wave-polarization`: corrected signs, any wave vector, cross polarization and the
  error file (`<problem> amp_cross, phase_cross`); example `problems/tests/lw_oblique.athinput`.
- `gw-analysis-output` items 1 and 3: `<outputN> file_type = bin` with `double_precision = true`
  (any variable, `variable = tmunu` for the sources); example `<output1>` of `lw_oblique.athinput`;
  reader `python/nrpic/athena_bin.py`. Restart files without the 36 unset header bytes.
- `weyl-output-timing`: `<z4c> waveform_at_new_time = true`.
- `thin-periodic-boxes` and `lattice-jitter-option`: `problems/cosmo/make_waves.py --n 256,256,16`,
  `--jitter A --jitter-axes y,z --seed N`; `problems/cosmo/east.athinput`.
- `reply-requests-answered`: the linear-wave fix and the jitter tool are released (above).
DONE in core-v0.5
- the OpenMP processor build of `reply-requests-answered`: `athena_cpu_omp` with
  `scripts/cpu_run.sh` (THREADS=6), `<particles> deposit_threads = private` (bit-for-bit at a fixed
  thread count); example `problems/tests/deposit_threads.athinput`. Not a byte reference.
DEFERRED
- `newtonian-species-history`, `newtonian-laplacian-order` and `newtonian-mode-for-track-b`
  items 2-3: core/newton-2 (unfinished).
- `initial-data-tt-part`: design in `REQUESTS_B.md` section 6; no branch holds it.
- `insitu-fourier-modes` (2026-11-21, with its correction): ACCEPTED as a new package (DFT on the
  device of the Z4c fields or gamma_ij, K_ij for |m_i| <= m_max every n cycles, double precision,
  time, cycle, mean lapse; your test on case X of `waves`). No branch holds it yet; your reply-by
  2026-12-11 is with the round planner of core (`REQUESTS_WAVE3.md` W18). Until then the
  double-precision dumps.
DECLINED: `awa-generators` for this release (optional; the route through `nrpic_cosmo` works; an
executable built with `PROBLEM=z4c/z4c_gauge_wave` on request).

What changes for your runs with core-v0.5 (`tracks/core/CHANGELOG.md`, section core-v0.5)
- The guard `<z4c_guard>` is ON by default: a run whose Z4c fields turn non-finite stops with exit
  status 3 and `<base>.guard.txt` (before: it ran on with status 0); `stop_nonfinite = false`
  restores the old behaviour.
- Without the new options every output of the twelve regression set-ups is the bytes of
  core-v0.4 (`RELEASE-v0.5.md`); the release processor build equals the candidate's (run
  core-20261121-075456-a505400); the release card build passed its card check (K1 to K6,
  core-20261121-074846-e830785).
