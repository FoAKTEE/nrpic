# core to D-bh-dress: answers to six requests (work package dfix)

Branch `core/requests-adf`; triage and evidence: `tracks/core/interfaces/REQUESTS_ADF.md`
(`git show core/requests-adf:tracks/core/interfaces/REQUESTS_ADF.md`); journal
`tracks/core/JOURNAL-dfix.md`. Executables for scouting runs (decision 0013):
`/data/haiyangw/nrpic/scratch/core/exe/core_requests-adf/` (`READY` lists every option
with an example input and what is tested).

- `tracer-push-release-build`: not a card defect. Since commit 4467852 a particle with
  m = 0 on the mesh metric was pushed as a photon, on processors and cards alike (your
  tracers left at psi^-4 = 0.726, 0.785, 0.823 at r = 6, 8, 10 M; the one at rest was
  removed in its first step; run core-20261115-152835-920d573, card run
  core-20261115-154030-5ba192a). Corrected: m = 0 is a timelike tracer on every metric
  (`zero_mass = null` restores the old rule). Your 250 M acceptance run of
  `problems/puncture/horizon_calib.athinput` with `athena_gpu` is yours to run: it did
  not fit into this package's card hour. With the release executables, `p<n>_m = 1e-300`
  on the command line gives the same motion.
- `restart-skips-dump`: corrected (`Driver::Finalize`); no scheduled output is lost after
  a stop at the wall clock or cycle limit (test T2).
- `accretion-diagnostics` items 1, 2, 4 and `analytic-metric-excision`: done
  (`removal_record`, `acc_nsphere`/`acc_radius<n>`, `acc_tracker`, `peri_count`;
  `alpha_exc` on the analytic metrics); tests T3 (exact Schwarzschild), T7 (moving
  puncture), card check. Item 3 (proper time) exists for the midpoint pusher on the
  mesh metric; on the analytic metrics it is deferred.
- `newtonian-mode-point-mass`: items 1 and 3 done (`newton_pm_*`, counter in the
  Newtonian mode; test T4); item 2 (throughput at 256^3 and 384^3) deferred to core's
  verification package.
- `puncture-on-torus`: deferred to wave 3 (needs the elliptic solve with a puncture in a
  periodic box and the periodic gauge near a hole).
