# JOURNAL of es_runs (helper package of D-bh-dress, wave 2)

Predictions are written before each test and are not edited afterwards; outcomes are
appended below them, also when a prediction failed. Paths relative to
`tracks/D-bh-dress/`; run ids are `nrpic-run` ids (manifests in `runs/<run_id>/`).

## Entry 1 (2026-11-15): data sets ES (outer dust edge at 60 M) and V-1, offline check

Task: regenerate the Einstein-Straus data set with the outer dust edge at 60 M as the
lead decided (`HANDOFF.md`, `stage/G1/STATUS.md`: `make_es.py --Rb 56 --w_out 4`, hp = 1 M)
and build the matched vacuum table V-1 ("the same table without dust, the f-slice of a
single Schwarzschild hole, Painleve-Gullstrand beyond 36 M"). Tool: `es_runs/make_data.py`
(calls `einstein_straus/make_es.py` with its figures redirected into the run directory;
V-1 is `es_model.EinsteinStrausBH` with `matched = False, rho0 = 0`).

Predictions (before the registered run):
- D1. Dust between R = 36 and 60 M; total mass M_tot = 2.74 +- 0.01 M [JUDGEMENT: the
  plateau is matched, m = (R/40)^3 M on it, and the symmetric smooth edge about Rb = 56 M
  acts nearly as a sharp edge at 56 M: (56/40)^3 = 2.744]. Plateau H = 5.5812e-3/M, the
  same as the wave-1 data set (the matched rho_0 depends only on Rw, w_in; es.json of
  D-bh-dress-20261115-043445-b782009). Particle number 7.09e5 +- 1 per cent (lead's
  estimate 709346, `analysis/lead_checks/first_run_plan.json`). Lattice dust mass equal
  to the continuum mass to better than 1e-6 (wave-1 data: 2.8e-8).
- D2. Bare puncture mass m_p = 1.0239688282062387 and u(0) unchanged (they depend only on
  f and M inside 36 M), for ES and V-1 alike; the 140 tracers of V-1 at the same
  positions as in ES (difference below 1e-12 M).
- D3. Exact crossing times of R = 2M for the tracer groups at R0 = 6 and 10 M equal to
  those of the wave-1 data set (same f and m = M inside 36 M); the lead quoted 15.0 and
  34.6 M, read off the 0.2 M grid of `es_reference.csv` (first grid point at or below
  2M), so the interpolated values lie at most 0.2 M below them.
- D4. Offline check (`einstein_straus/offline_check.py` through `es_runs/tools/
  offline_check_es.py`, figures redirected): the 1D and 3D residuals of ES fall at fourth
  order (measured orders between 3.5 and 4.5 in every region and sub-box with resolved
  residuals, as 3.85-4.07 in run D-bh-dress-20261115-042704-f3da881); the table
  interpolation error below 1e-6 of the field scale. V-1, same checks with rho = 0:
  the same orders. Refuted by an order below 3 in any region with residuals above the
  round-off floor (then the new edge at 52-60 M is under-resolved by drbar = 0.02 or the
  generator is wrong for rho = 0).
