# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State: wave 1 done by five helpers and re-checked by the lead. Established: D-pre-1 (Einstein-Straus data, exact,
constraint-checked), D-pre-2 Schwarzschild spike, D-pre-3 semi-analytic, D-pre-4 noise floor (2.18 card-hours).
Open: Kerr spike, AthenaK Newtonian-mode run, the first full-relativity run ES-1 (blocked by core: format-2 merge,
tracer push of the release card executable, lapse). G0 package written, not yet reviewed; G1 not yet met.
Owner: D-bh-dress, branch `track/D-bh-dress`, worktree `wt/D-bh-dress`.
Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox`
  then, if core has answered: regenerate the ES data with the outer dust edge at 60 M
  (in `tracks/D-bh-dress/einstein_straus/`: `python3 nrun.py --purpose "ES data, outer edge 60 M" --tag dataset
  --cores 8 -- python3 $PWD/make_es.py --out {out} --hp 1.0 --tau_max 400 --Rb 56 --w_out 4`), rerun `offline_check.py` on it, write the vacuum table V-1, write the
  prediction of `stage/G1/STATUS.md` into JOURNAL.md, then submit ES-1 and V-1 at M/8 (about 2.6 card-hours).
  If core has not answered: the Kerr spike baseline (`spike/README.md`, "Not done").
Files to read first: `tracks/D-bh-dress/STATUS.md`, `stage/G1/STATUS.md` (ES-1 specification and prediction),
  `stage/G0/REPORT.md`, `stage/G0/OPEN.md`, `einstein_straus/README.md`, `puncture_drift/README.md`,
  the lead entry of `JOURNAL.md` (re-checks L1-L6).
Decisions pending: core on the 8 requests of `outbox/20261115T1510Z__to-core__*`; orch on
  `outbox/20261115T1510Z__to-orch__brief-and-notes-corrections.md` (and a second-agent review); kb sources; A's LTB
  conventions.
Traps: (1) every input must set `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8` (defaults
  are wrong). (2) The puncture of the ES data has bare mass m_p = 1.0239688282062387, not 1. (3) psi = 1 outside the
  ES ball: read masses as Misner-Sharp or horizon masses, never from the 1/r tail. (4) A run that went to NaN ends
  "successfully" with zero particles: check column 3 of `<base>.nrpic.hst`. (5) Massless tracers on the release card
  executable are wrong until core answers (R1). (6) `harness/bin/nrpic-run` refuses a worktree shared by helpers;
  the packages' own register scripts (`einstein_straus/nrun.py`, `analysis/lead_checks/lrun.py`, ...) write the
  manifests, which must be added with `git add -f` (the `runs/` ignore line). (7) Run ids are UTC since 5259f48;
  the einstein_straus ids 0426xx-0434xx are local time. (8) Never kill by pattern; never run long jobs in the
  foreground on more than 16 cores.
