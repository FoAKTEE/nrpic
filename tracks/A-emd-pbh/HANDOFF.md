# HANDOFF of A-emd-pbh

Written for a reader with no memory of the last session (lead, wave 1, 2026-11-15).

State: offline references of S1 are done and re-verified (expanding-ball data and exact
solution, analytic criteria, Newtonian references, gauge toys); G0 lacks the note v0, two
schematics, a verifier and REPORT.md; G1 has two of three criteria met. No AthenaK run of
this track yet: the first two (SR-1, SR-2) are specified and wait for core's format-2 reader.
Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `wt/A-emd-pbh`.
Run next: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git log --oneline -3 main -- athenak/src/pgen/nrpic/nrpic_cf.cpp`
  (if the format-2 reader is on main: write the prediction-checking script, then submit SR-1 and
  SR-2 with `harness/bin/nrpic-run submit --launcher batch ...` from `stage/G1/STATUS.md`
  section 3; if not: close G0, item list in `stage/G0/OPEN.md`).

Files to read first: `STATUS.md`; `stage/G1/STATUS.md` (scouting runs, predictions,
refutation criteria); `stage/G0/OPEN.md`; `scope/SCOPE.md` sections 3 and 10; the end of
`JOURNAL.md` (entry 2026-11-15T12:57Z); on branch `core/id-extrinsic`:
`tracks/core/JOURNAL-id.md` entries 5-7 and `problems/ball/ball.athinput` (gauge findings
and recommended settings for the ball).

Where things are:
- helper packages: `scope/` (SCOPE.md, REFERENCES.md), `expball/` (README.md first),
  `criteria/` (README.md), `newton/` (README.md, SCAN.md), `gauge/` (GAUGE.md, DIAGNOSTICS.md);
  each has its own JOURNAL.md with predictions and outcomes.
- lead's scripts: `analysis/normalize_manifests.py`, `analysis/lead_rerun.sh <package>`,
  `analysis/lead_crosscheck.py`, `analysis/scouting_predictions.py`.
- data set 2t (input of SR-1/SR-2): `/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/`.
- core's Python of core/id-extrinsic for cross-checks: export again with
  `git archive core/id-extrinsic python/nrpic | tar -x -C /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/core_id_python`.

Decisions pending:
- orch: threshold line in the periodic box instead of the ball; G1 T3 accepted on the
  reference-based scan design; `.gitignore` `runs/` anchoring; nrpic-run robustness
  (`outbox/20261115T1320Z__to-orch__*.md`).
- core: answers in `outbox/20261115T1320Z__to-core__*.md` (finder keys for a 0.16 M horizon,
  cfl change at restart, T2e outcome, Newtonian mode, phase-1 generator).
- kb, B-emd-gw: `outbox/20261115T1320Z__to-kb__*.md`, `__to-B-emd-gw__*.md`.

Traps:
- `nrpic-run local` runs in the worktree venv `.venv` (made with
  `harness/bin/nrpic-env create --no-kokkos`); without it Python packages are missing.
- `nrpic-run` refuses a dirty worktree and crashes (KeyError 'outputs') on manifests that
  lack `outputs.dir`: helper scripts that register themselves (expball, criteria, newton
  runners) write such manifests; run `python3 tracks/A-emd-pbh/analysis/normalize_manifests.py`
  after them and commit `runs/*/manifest.json` with `git add -f` (`.gitignore` hides runs/).
- expball's `run_noise.py` and `run_convergence.py` write figures into `expball/figures/`
  (rerun copies: restore with `git checkout -- <file>` or delete them by explicit path).
- Sharp ball edges: do not evolve them (non-converging constraints; expball sharp tables
  carry no `breaks` line); use the taper (`--edge-width`).
- Geodesic slicing: shrink the step before the core's coordinate light speed R_i/R exceeds
  0.618/cfl (stage plan in `stage/G1/STATUS.md`).
- Two amplitude measures: central contrast 12 mu/5 (criteria) and mean in r_m 0.883 mu
  (scope); name the measure in every table.
- This session ran as a workflow subagent whose harness refuses to write files named as
  reports; a normal lead session can write `stage/G0/REPORT.md`.
- Kill processes by numeric PID only; never `pkill -f`.
