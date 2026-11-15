# G0 evidence of A-emd-pbh: artefacts, paths, run ids

Paths are relative to `tracks/A-emd-pbh/` unless they start with `/`. Run manifests:
`runs/<run_id>/manifest.json` (committed; helper-written ones normalized by
`analysis/normalize_manifests.py`, changes listed under `lead_corrections`). Outputs:
`/data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>/` (untracked). "Rerun" = the lead's rerun
from the committed scripts (prediction L1, `JOURNAL.md` entry 2026-11-15T12:57Z).

## Scoping documents

| Item | Path | Basis |
|---|---|---|
| problem statement, position against arXiv:2609.14218 (H1-H4), threshold definition, set-ups, parameter ranges, diagnostics, exit criteria, section-10 test plan, risks, compute | `scope/SCOPE.md` sections 1-9 | helper scope |
| lead's decisions and corrections (amplitude convention, set-up order, no sharp edges, G2 horizon-mass target, locators re-read, scouting runs, compute to G2, timeline) | `scope/SCOPE.md` section 10 | lead |
| twelve key references with file:line locators | `scope/REFERENCES.md` | raw store `kb-data/raw/arxiv/<id>/<v>/src/` |
| risk list | `RISKS.md` | lead, from SCOPE.md section 8, expball, gauge, core's journal |
| checklist of the harness (C1-C18) | `stage/G0/CHECKLIST.md` | `nrpic-stage collect` |

## Runs

| Run id | Package | What | Status | Rerun by the lead |
|---|---|---|---|---|
| A-emd-pbh-20261115-112500-61acbec | scope | first try; `python3 -I` hid numpy | failed (kept) | |
| A-emd-pbh-20261115-112505-61acbec | scope | superseded by -112625 | completed | |
| A-emd-pbh-20261115-112625-e854f12 | scope | T1-T5: hoop line, collapse times, ball geometry, dispersion, cost | completed | A-20261115-130252-7877b7a: 291 numbers identical |
| A-emd-pbh-20261115-113103-9832afd | newton | validation P1-P7 | completed | A-emd-pbh-20261115-130252-4290486: `validate.json` identical |
| A-emd-pbh-20261115-113108-9832afd | newton | tables (superseded, same numbers) | completed | |
| A-emd-pbh-20261115-113152-cd9539e | newton | reference tables and scan figures | completed | |
| A-emd-pbh-20261115-113807-e02c969, -113822-87cba08 | newton | snapshot-analysis self-test (first superseded) | completed | A-emd-pbh-20261115-130300-efc25b0: t1 to 1.2e-5 |
| A-emd-pbh-20261115-113223-5581665, -113244-8e0363b, -113446-024989f, -114638-35ca5e4, -115122-2eb3117, -115232-bee5b2e | criteria | first checks, scan, figure fixes | completed | |
| A-emd-pbh-20261115-115120-2eb3117 | criteria | final check run, 37 checks, 33 pass | completed | A-20261115-130252-01e8b64 (see `stage/G1/STATUS.md`) |
| A-emd-pbh-20261115-120425-80492f8 | criteria | scan over the brief's range; example tables | completed | |
| A-emd-pbh-20261115-113608-374a41a, -113614-374a41a | gauge | T1 lapse toy (first has figure defects) | completed | A-20261115-130252-4290486: JSON identical |
| A-emd-pbh-20261115-113755-cac3c4b, -113807-43300e5 | gauge | T2 von Neumann (one superseded) | completed | same: identical |
| A-emd-pbh-20261115-113921-ca3786e | gauge | T3 bh2 onset | completed | same: identical |
| A-emd-pbh-20261115-113810-e02c969 | gauge | T4 toy against the lapse-driver run | completed | same: identical |
| A-emd-pbh-20261115-115339-044312f, -115559-c4a583e | expball | aborted (partial logs) | stopped (kept) | |
| A-emd-pbh-20261115-115552-c4a583e, -115659-c4a583e | expball | figures with the defective solver (superseded) | completed | |
| A-emd-pbh-20261115-121643-6bfb707 | expball | slice and exact-shell figures | completed | |
| A-emd-pbh-20261115-121654-6bfb707, -122121-aa1c84d | expball | G1 constraint convergence N = 32-256 | completed | A-emd-pbh-20261115-130402-f5566fb: 901 values identical |
| A-emd-pbh-20261115-122117-aa1c84d | expball | smoothed top-hat at N = 512 | completed | |
| A-emd-pbh-20261115-121659-6bfb707, -122325-aa1c84d | expball | particle noise | completed | A-emd-pbh-20261115-130639-947c898: results identical |
| A-emd-pbh-20261115-121707-6bfb707, -121710-6bfb707 | expball | data sets with a header issue (superseded) | completed | |
| A-emd-pbh-20261115-121749-90764e1 | expball | data set 1 (marginally bound ball) | completed | check A-emd-pbh-20261115-130344-f5566fb ok |
| A-emd-pbh-20261115-121753-90764e1 | expball | data set 2 (smoothed top-hat core) | completed | check A-emd-pbh-20261115-130352-f5566fb ok |
| A-emd-pbh-20261115-121859-ac2eb52, -121905-ac2eb52 | expball | end-to-end checks of data sets 1, 2 | completed | |
| A-20261115-125927-6d2c1e6, A-20261115-125932-{f221206, b90223c, 5a90432, 574c747}, A-emd-pbh-20261115-125932-{574c747, 779f753} | lead | first rerun attempt: `nrpic-run local` runs in the worktree venv, which did not exist yet (no matplotlib) | failed (kept) | |
| A-20261115-130252-c744ff7 | lead | rerun of expball: sym 27/27, 36/36, 11/11; 32 tests pass; children -130344, -130352, -130402, -130639 | completed | |
| A-20261115-130257-a7374a4 | lead | cross-checks L2-L6 (`analysis/lead_crosscheck.py`, `fig_crosscheck.png`) | completed | |
| A-emd-pbh-20261115-130609-947c898 | lead (expball generator) | data set 2t for the scouting runs (taper w = 1.5 M, lattice h = 0.5 M, 28768 sites) | completed | check A-emd-pbh-20261115-130846-947c898 ok |
| A-20261115-130948-5a2b58a | lead | predictions of SR-1 and SR-2 (`analysis/scouting_predictions.py`, `fig_scouting_predictions.png`) | completed | |

## Figures looked at by the lead (PNG read)

Scope rerun: `fig_hoop`, `fig_timing`, `fig_design`, `fig_cost`. Expball rerun:
`fig_constraint_convergence_leadrerun`. Newton rerun: `fig_paper_cases`; committed
`newton/figs/fig_scan_hoop_time.png`. Gauge rerun: `t1/lapse_toy`, `t3/bh2_onset`. Lead:
`fig_crosscheck`, `fig_scouting_predictions`. Each agrees with the numbers quoted for it.
The helpers' own lists of inspected figures are in their READMEs and journals.

## Sources outside this track

| Item | Where |
|---|---|
| format 2 reader and core's tests of the ball in AthenaK | branch `core/id-extrinsic` at aef2f7b: `athenak/src/pgen/nrpic/nrpic_cf.cpp`, `tracks/core/JOURNAL-id.md`, `tracks/core/interfaces/spherical_id_format2.md`, `problems/ball/ball.athinput` |
| horizon-mass error of the source paper | `/data/haiyangw/nrpic/refs/arxiv_2611.12831/src/main.tex:945, 1484` (untracked, never redistributed) |
| unit card cost | core run core-20261115-040406-1311b8e (manifest on `core/id-extrinsic`) |
