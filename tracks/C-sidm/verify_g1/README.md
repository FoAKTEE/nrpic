# verify_g1: fresh-context verifier of the G1 material of C-sidm (criterion C17)

Wave 3, round 1. Independent verifier: own reference code, own analysis of the raw
AthenaK outputs of the track's runs; the track's readings were not read before the blind
verdicts were committed (`VERDICTS_BLIND.md`). After that: `../stage/G1/VERIFIER.md`.

## What is in this directory

| File | What |
|---|---|
| `JOURNAL.md` | predictions before each computation, outcomes after |
| `VERDICTS_BLIND.md` | blind verdicts V1 to V4 (V5 if done), committed before any claim was read |
| `lib.py` | own readers of the AthenaK history and snapshot files (beside `nrpic.collide.read_snapshot`, `read_dump`) and Maxwell-Juttner functions |
| `ce_kappa.py` | V1: Chapman-Enskog thermal conductivity of hard spheres by Monte Carlo collision brackets (non-relativistic Sonine orders 1-4; relativistic first approximation, Eckart frame) |
| `heat_ref.py` | V1: nonlinear isobaric heat-equation reference (Lagrangian mass coordinate) for the mode and the step |
| `v1_mode.py`, `v1_step.py` | V1: decay rate of the isobaric mode (T7) and fit of the temperature step (T6(b)) from the run outputs |
| `v2_box.py` | V2: collision rate against the Moller integral (T2) and conservation per step (T1) |
| `v3_static.py` | V3: collision rate in the static homogeneous metric (T12) |
| `v4_ev.py` | V4: own spherically symmetric Einstein-Vlasov equilibria (King b = 1, F21 b = 0.1), thresholds |
| `figs/` | figures of every item (style `python/nrpic/figstyle.py`) |
| `results/` | JSON outputs of the registered analysis runs are in `scratch/C-sidm/<run_id>/`; small copies here |

## How to rerun

Every computation is a registered run (`harness/bin/nrpic-run submit --kind scouting --gate G1
--package tracks/C-sidm/verify_g1 --cores 2 ...`); the commands are in the manifests under
`tracks/C-sidm/runs/<run_id>/manifest.json` (run ids in `VERDICTS_BLIND.md`). Python: the
worktree `.venv`.

## Requests

(filled at the end)
