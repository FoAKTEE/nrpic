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
| `v4_ev.py` | V4: own static spherically symmetric Einstein-Vlasov equilibria (King b = 1, F21 b = 0.1, k = 0.5 polytrope), E_b maximum, turning points, radial-pulsation onsets (F21 trial function and finite elements; 1 + p/u, Juttner Gamma_1) |
| `v4_models.py` | V4: the track's model files against my equilibria; energy-matched-temperature onset; particle radial distributions |
| `v5_box.py`, `v5_t9ks.py` | V5: T10 reproducibility, T1 over 1e4 steps, T3, T4 (own exact rate), T9; T9 KS against three reference temperatures |
| `figs/` | figures of every item (style `python/nrpic/figstyle.py`) |
| `results/` | JSON outputs of the registered analysis runs are in `scratch/C-sidm/<run_id>/`; small copies here |

## Registered runs of this package

| Item | Run id | Note |
|---|---|---|
| V1a | C-20261120-222423-519f12b | Chapman-Enskog brackets |
| V1b | C-20261120-223130-6742500 | isotropic mode (of record); C-20261120-222754-14bd23d first evaluation, same numbers |
| V1c | C-20261120-223133-2f98a0e | temperature step |
| V2 | C-20261121-074926-5d9ae56 | flat box T1, T2 |
| V3 | C-20261121-075256-2084cb5 | T12 |
| V4 | C-20261121-080313-84094f1 | thresholds (C-20261121-080152-b8d0acd failed at its figure, same numbers) |
| V4b | C-20261121-080720-dbcd7ff | model files (C-20261121-080633-8ee41f7: sample check invalid, sign error of mine) |
| V5 | C-20261121-081036-0d6117b | T10, T1 long, T3, T4, T9 |
| V5b | C-20261121-081415-b8c9d29 | T9 KS reference temperatures |

## How to rerun

Every computation is a registered run (`harness/bin/nrpic-run submit --kind scouting --gate G1
--package tracks/C-sidm/verify_g1 --cores 2 ...`); the commands are in the manifests under
`tracks/C-sidm/runs/<run_id>/manifest.json` (run ids in `VERDICTS_BLIND.md`). Python: the
worktree `.venv`.

## Requests

(filled at the end)
