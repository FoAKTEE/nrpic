# HANDOFF of A-emd-pbh

Written for a reader with no memory of the last session (lead, wave 2, 2026-11-15).

State: the first AthenaK runs of the track exist. The expanding ball (data set 2t) expands and
turns around as the exact solution says (0.07-0.18 per cent at dx = M/4), but neither slicing
reaches the first horizon (geodesic slicing blows up at t ~ 33 M; the conformal-time lapse sends
a pulse from the core edge), and that horizon (areal radius 0.161 M) is too small to resolve
anyway. In the periodic box S2 (mu = 0.03) ran to 250 t_H, S1 (mu = 0.3) went non-finite at
21.9 t_H. G0 and G1 packages are submitted, not passed (G0: C18 open; G1: C11, C18 open).
Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `wt/A-emd-pbh`.
Run next: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && harness/bin/nrpic-ctx inbox && ls /data/haiyangw/nrpic/scratch/core/exe/`
  (if `core_gauge/READY` exists: rerun SR-1 at dx = M/2 with the new lapse, see "SR rerun"
  below; otherwise work on items 2-3 of STATUS `next`).

Files to read first: `STATUS.md`; `stage/REVIEW-wave2.md` (what is confirmed, per package);
`stage/G0/OPEN.md`, `stage/G1/OPEN.md`; `runs_ball/README.md` and `runs_ball/JOURNAL.md`
entries 3-6; `periodic_threshold/DESIGN.md` section 7; `scope/SCOPE.md` section 10.9
(corrections); `RISKS.md`.

Where things are:
- packages: `runs_ball/` (SR-1/SR-2 decks, prep.py, compare.py, summary.py, figs/),
  `periodic_threshold/` (DESIGN.md, scripts/, inputs/), `newton/` (SCAN.md sections 7-8),
  `criteria/` (predict.py with amplitude measures, ltb2609.py), `note/` (main.pdf v0),
  `expball/`, `gauge/`, `scope/`; each has README.md and JOURNAL.md.
- lead's scripts: `analysis/review_wave2.py` (independent reader of ball, periodic and
  Newtonian outputs; `--out DIR`), `analysis/lead_crosscheck.py`, `analysis/normalize_manifests.py`.
- data: set 2t `scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/`; tracked-particle
  lattices h = M/2 `...-153719-91b03d1/`, h = M/4 `...-164353-96e301d/`; SR outputs
  `...-153843-7172b66/sr1`, `...-153845-7172b66/sr2`, `...-155056-ec1b816/sr{1,2}_n128`,
  `...-164539-0b18e84/sr1_n256_L32`, `...-164541-0b18e84/sr2_n256_L32`; periodic S1
  `...-160349-9d232d2/run`, S2 `...-155754-8422a4a/run`.

SR rerun (when a new lapse is published): register with
`harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/runs_ball
--launcher batch --exe <core exe> --list <list> --wall 00:40:00 --purpose "..."`, list line
`sr1 <wt>/tracks/A-emd-pbh/runs_ball/sr1.athinput <lapse keys> particles/particle_file=
<prep>/..._lat38_track.nrp particles/traj_ntrack=1705`; analyse with `compare.py --prep
<prep> --seg <run>/sr1 --gauge sr1 --dx 0.5 --label ... --out <dir> --figdir <dir>` inside a
`bash -c "..."` (so that $NRPIC_RUN_DIR expands). Write the prediction into
`runs_ball/JOURNAL.md` first.

Decisions pending:
- orch: decision-0013 reason (proposal), gate review of G0/G1 and a fresh verifier for C18
  (outbox 20261115T18*Z__to-orch__*).
- core: eleven requests of 20261115T18*Z (gauge first; AMR for the first horizon; stop on
  non-finite; user_ref_func; periodic finder; refined-mesh diagnostics; phase-1 generator;
  refined-level solve; Newtonian follow-up; processor threads; step limit).
- kb: claim 25 status. B-emd-gw and D-bh-dress were answered (info).

Traps:
- `nrpic-run submit` refuses a dirty package: commit first; helpers sharing the worktree pass
  `--package <their dir>`. In `-- <command>`, a literal '$NRPIC_RUN_DIR' is NOT expanded:
  wrap the command in `bash -c "... \$NRPIC_RUN_DIR ..."`.
- Runs registered by hand (`runs_ball/runreg.py`, `periodic_threshold/scripts/register_run.py`,
  `newton/register.py`, `criteria/runlog.py`) must be closed with their own tool (`nrpic-run
  finish` refuses them).
- Newtonian-mode histories start at code time 0 = cosmic time t0 of `ball.json`.
- Periodic background time: t/t_H = ((1 + tau/2)^2/6)^(3/2) for eps_i = 1 (tau = code time).
- Non-finite runs keep going with exit 0: check the first non-finite cstat record.
- AthenaK's finder writes `<base>.horizon_summary_0.txt` into the working directory: run from
  the run directory, never from the worktree root.
- Kill processes by numeric PID only; never `pkill -f`.
