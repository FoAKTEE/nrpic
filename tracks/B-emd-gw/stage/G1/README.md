# stage/G1 of B-emd-gw: files of verifier2 (wave 2b, 2026-11-19)

This directory is the owner's G1 stage package (`STAGE_REPORT.md`, `EVIDENCE.md`,
`OPEN.md`, `CHECKLIST.md`, `STATUS.md`, `VERIFY_RESULTS.*`, written by the lead and the
harness). The helper verifier2 added only the files below; it changed none of the others.

| Path | What |
|---|---|
| `VERIFIER.md` | verifier's report (item C18): verdict per claim of the wave-2 runs (first-source scan, Newtonian mode), comparison with `../REVIEW-wave2.md` |
| `JOURNAL.md` | verifier2's predictions (written before the checks) and outcomes |
| `verifier2/scripts/athio.py` | own readers: AthenaK bin and restart dumps, NRPIC snapshots and trajectories |
| `verifier2/scripts/derive_s.py` | second-order Einstein equations (sympy), coefficient s of the (k,k,0) mode |
| `verifier2/scripts/scan.py` | per-dump flat-TT diagnostics of the crossed-wave runs |
| `verifier2/scripts/compare.py` | comparison with s g(eta), null, meshes, gauges, bin against rst; figures |
| `verifier2/scripts/linearity.py` | linearity in eps pair by pair, fourth-order ratio test |
| `verifier2/scripts/newton_checks.py` | pancakes against exact 1D sheets, ellipsoid against the homogeneous-ellipsoid ODE |
| `verifier2/scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `verifier2/results/` | small copies of the run outputs (`compare.json` of B-20261119-142332-dd28d1d, `linearity.json`, `newton_checks.json`, the derivation's output) |
| `verifier2/figs/` | PNG copies of the figures (looked at): `kk0_amplitude`, `null`, `res32_64`, `gauge`, `linearity`, `pancakes`, `ellipsoid` |

## How to rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create
--no-kokkos`); each line is one registered run, as in the manifests under
`tracks/B-emd-gw/runs/B-20261119-14*`. Scripts write into the run directory when the output
argument is `-`. `S=/data/haiyangw/nrpic/scratch/B-emd-gw`, `P=tracks/B-emd-gw/stage/G1`.

```
R="harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --launcher local"
$R --cores 1 --purpose ... -- python3 $P/verifier2/scripts/derive_s.py                  # 1 min
$R --cores 8 --purpose ... -- env NWORK=8 OMP_NUM_THREADS=1 python3 $P/verifier2/scripts/scan.py - \
    n64_eps0:$S/B-20261115-164059-d802e82/cw_eps0 ... n32_eps1_gd:$S/B-20261115-165525-f7c2004/cw_eps1_gd   # 6 min
$R --cores 1 --purpose ... -- python3 $P/verifier2/scripts/compare.py <scan run dir> -
$R --cores 1 --purpose ... -- python3 $P/verifier2/scripts/linearity.py <scan run dir> -
$R --cores 1 --purpose ... -- python3 $P/verifier2/scripts/newton_checks.py - \
    east:16:<dir> east:32:<dir> east:64:<dir> sin:16:<dir> ... ell:128:<dir>
```

The exact argument lists are in the manifests (`command`).

## Requests

To the lead of B-emd-gw:
1. `first_source/README.md` item 1, "linear in eps to 0.05 percent": that holds for
   eps = 0.1 against 0.3 (and is the single-precision floor); eps = 1 departs by 0.2 % at
   a = 10, the fourth-order term (VERIFIER.md F3). Reword where the claim is cited.
2. `first_source/README.md`, "agrees between 32^3 and 64^3 to 0.5 percent up to a = 80":
   true at a = 80 itself, not as a bound for eps = 1 (1.02 % at a = 75.8) or the Gamma
   driver (1.6-1.9 % at a = 79-80) (F7; the review already corrects the eps = 1 case).
3. `newton_tests/README.md`, "plane symmetry is kept to 1.3e-15 L": say which measure; the
   largest spread of x within a sheet is up to 1.2e-14 at n = 64 before crossing (N3).
4. Item C18 of `CHECKLIST.md` can cite `VERIFIER.md` for the wave-2 runs named there; the
   G_tot correction, the energies and the late-rise analysis are not covered by it.

To core: none beyond the track's earlier request for a double-precision Z4c dump without
particles; single precision limits the eps = 0.1 box mode to 1e-4 relative (F8), which is
what made the eps-linearity in bin a noise measurement.
