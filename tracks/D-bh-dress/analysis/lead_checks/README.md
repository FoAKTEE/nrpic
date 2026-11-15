# lead_checks: the D-bh-dress lead's re-checks of the wave-1 helper packages

| File | What | Run |
|---|---|---|
| `lrun.py` | registers a run (UTC run id, manifest under `../../runs/`, output in `scratch/D-bh-dress/<run_id>/`) | |
| `drift_recheck.py` | D-pre-4 drift, excursions, spin from the raw finder output, own code; `figs/lead_drift_recheck.png` | D-bh-dress-20261115-145546-5259f48 |
| `infall_recheck.py` | D-pre-3 closed-form turnaround and collapse masses, own code; `figs/lead_infall_recheck.png` | D-bh-dress-20261115-145610-5259f48 |
| `first_run_plan.py` | exact references, 1+log lapse estimate and cost of the first full-relativity run; `figs/first_run_plan.png`, `first_run_plan.json` | D-bh-dress-20261115-145950-23fa1c7 |

Also registered: the rerun of the D-pre-1 symbolic identities (D-bh-dress-20261115-065141-5fdc744,
local-time id), of `scope/scoping_estimates.py` (D-bh-dress-20261115-145611-5259f48) and of
`spike/spike_reference.py` (D-bh-dress-20261115-145636-5259f48). Predictions and outcomes:
`../../JOURNAL.md`, lead entry of 2026-11-15T14:55Z. Rerun: `python3 lrun.py --purpose ... -- python3 $PWD/<script> --out {out}`.
