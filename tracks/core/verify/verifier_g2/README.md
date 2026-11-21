# verify/verifier_g2: fresh verifier of core's gate G2

Helper package of owner core, batch 6 (2026-11-21), no card time. A verifier that did not
produce core's results recomputes a sample of the numbers core's G2 package marks as met
(`tracks/core/stage/G2/EVIDENCE.md`, `CHECKLIST.md`, `verify/LADDER.md`, the interface
documents) from the registered raw outputs with its own short code, and reruns the one
claim that needs a fresh run (exact restart) on the release executable of core-v0.6.
The report is `tracks/core/stage/G2/VERIFIER.md`; predictions and outcomes are in
`JOURNAL.md` here (entry 0 was committed before any check).

## What is here

| Path | What |
|---|---|
| `JOURNAL.md` | claims chosen, predictions (entry 0), outcomes per check, failed attempts |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` (figure style) |
| `scripts/v1_kerr.py` | V1: Kerr geodesic invariants (own Kerr-Schild metrics, Carter constant), dt order against own DOP853 reference, pericentre from own radial potential |
| `scripts/v2_os.py` | V2, V5a: Oppenheimer-Snyder horizon mass, deposition identity |
| `scripts/v3_clusters.py` | V3: fates of the five relativistic clusters, wave-2 member |
| `scripts/v4_flrw.py` | V4: homogeneous dust universe against own Einstein-de Sitter solution |
| `scripts/v5_mpi.py` | V5b: particle module on 1, 2, 4 MPI ranks |
| `scripts/v6_restart.py` | V6: straight against restarted runs on release core-v0.6 (fresh simulations) |
| `scripts/v7a_point.py` | V7a: Newtonian point-mass forces (own snapshot reader `read_snap`) |
| `scripts/v7b_pancake.py` | V7b: Fourier Poisson solver against the exact Zel'dovich slab moment |
| `scripts/v8_coll.py` | V8: collisional relaxation (conservation, own Maxwell-Juttner KS and pressure) |
| `scripts/v9_scalar.py` | V9: Klein-Gordon wave, own dump reader, two-wave frequency fit, own stencil symbols |
| `scripts/v10a_idsolve.py` | V10a: initial-data solver T1 against own continuum psi of a Gaussian |
| `scripts/v10b_idsolve2.py` | V10b: solver on static refinement (own NRIDBLK1 reader) |
| `scripts/v11_faces.py` | V11: boundary-cell constraint of a puncture against own ghost-stencil estimate; fresh stock vs `ghost_falloff` runs |
| `figs/` | the figure of each registered run (PNG copies; looked at, see JOURNAL) |

Readers are my own (formats from `docs/FORMATS.md` and the writers in `athenak/src`);
none of `python/nrpic` or core's analysis code is imported. Each reader is checked on an
analytic case before use (metric inverse, cos(k.x) at t = 0, chi = psi^-4, file-size
layouts, Ixx at t = 0).

## How to rerun

Every check is one registered run (`harness/bin/nrpic-run submit --kind scouting --gate
G2 --package tracks/core/verify/verifier_g2 --cores 1 -- python3
tracks/core/verify/verifier_g2/scripts/<script> <inputs> '$NRPIC_RUN_DIR'`); the exact
commands, inputs with checksums and run ids are in `tracks/core/runs/<run_id>/manifest.json`
(run ids in JOURNAL.md and VERIFIER.md). Python: the worktree's `.venv` (numpy, scipy,
matplotlib). The simulations of V6 and V11 use
`/data/haiyangw/nrpic/.work/build_cpu_v06/src/athena` on one core.

## Requests

- To core (lead): correct three texts found wrong or ambiguous (VERIFIER.md, table):
  CHECKLIST C3 "|Theta| 1.1e-11" is the history column Theta-norm2 (a volume integral of
  Theta^2), the pointwise max |Theta| is 2.3e-7; `interfaces/scalar_field.md` test 1 says
  omega_meas/omega_h - 1 = -1.2e-8 ... -1.34e-8, the data give -1.21e-9 ... -1.31e-9 (the
  RK4 phase error at dt = 1/512); `interfaces/newtonian_mode.md` 5.2 counts 846 tracers at
  r >= 0.5, there are 706; `interfaces/id_solver.md` T1 "error of psi - 1" is the relative
  error of psi - 1. Also note in OPEN.md the restart result of V6 (VERIFIER.md).
- To core (lead): register the pre-program runs that carry ladder rows 2 and 4
  (`runs/os/nocap_sc`, `runs/st/*`, untracked) or rerun them on a release, so the rows do
  not rest on unregistered directories.
