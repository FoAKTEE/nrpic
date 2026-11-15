# The longer threshold scan: prepared inputs and cost (not run in wave 2)

State 2026-11-15 (helper of C-sidm, package threshold_scan). Inputs are written by
`make_scan.py` (particle files: registered run named in the README; decks:
`inputs/scan/`). Costs scale with the measured cost per M of the wave-2 card runs
(`JOURNAL.md`, outcome of Test 3); until then the first paper's 3.27 s per M on the same
mesh (400 MeshBlocks, one A100; `runs/st/dir_yc0500_comp/athena.20261113-062219.log` of the
main checkout) is used, with 3.7 s per M as the upper value. [JUDGEMENT on the block design
below; the G2 criterion of decision 0013: "the collisionless threshold is located with
three-way convergence and compared with the turning-point criterion".]

## Blocks

| Block | Purpose | Runs | Length | Card-hours (3.27-3.7 s/M) |
|---|---|---|---|---|
| A | collisionless threshold of the King b = 1 sequence: the fate (collapse, migration outward, oscillation) of the five models y0 = 0.314, 0.324, 0.334032, 0.344, 0.354 under a one-percent coherent radial kick inward and outward; the unperturbed y0 = 0.314 and 0.334032 are the wave-2 controls | 10 (`scanA_*`) | 1000 M | 9.1-10.3 |
| A' | continuation of the wave-2 controls cc1_kninf, cc2_kninf to 1000 M from their restart files at 300 M | 2 | 700 M | 1.3-1.4 |
| B | three-way convergence at the pair of models that brackets the threshold in A: particle number 10^4 against 10^5; mesh with a level-7 region (M/8) inside \|x\| < 3.9 M (about 464 MeshBlocks and half the step, about 2.3 times the cost); domain 1024 M against 512 M (one more level, about 1.14 times) | 6 (2 models x 3 variants) | 1000 M | about 8.9 |
| C | collisional pilot on the threshold model: Kn = 3 and 0.3 (unperturbed), with the wave-2 Kn = 10 and 1 continued from 300 M; the first points of the collapsed mass fraction against Kn | 2 new (`scanC_cc1_kn3`, `scanC_cc1_kn0p3`) + 2 continued | 1000 M, 700 M | 1.8-2.1 + 1.3-1.4 |
| | total | 22 | | about 22-24 |

The decks of B are written once A has located the bracket (`make_decks.deck` with another
particle file, or `refined_region2` with `level = 7`, or `x1min = -1024` and `nx1 = 128`).
Decision 0014 gives C 45 card-hours toward the next gate; no single run exceeds eight.

## How to run

Each run of A and C is longer than an hour: one chain each (`scripts/submit_chain.sh`
through the harness; two segments of 50 min, restart files every 200 M):

    cd /data/haiyangw/nrpic/wt/C-sidm && harness/bin/nrpic-run submit --launcher chain \
      --kind scouting --gate G2 --package tracks/C-sidm/threshold_scan --gpu-hours 2 \
      --particles 100000 --purpose "scan A: <model> <kick>" \
      -- tracks/C-sidm/threshold_scan/inputs/scan/scanA_y0p33403_kin.athinput

A continuation (A', C) copies the restart pair `rst/cc.00001.rst` and `rst/cc.00001.rst.prt`
of the wave-2 run into `<new chain dir>/rst/` and starts the chain with the same deck and
`time/tlim=1000` (the chain resumes from the newest restart; restarts are exact, CLAUDE.md).

## What each block decides

- A: the sign of the fate on each side of y_max = 0.334032 (2009.08163 finds the binding-
  energy maximum to be the onset, lines 1083-1092); the threshold is bracketed by the last
  model that oscillates under both kicks and the first that collapses under the inward
  kick. With the coarse y0 grid of 0.01 the bracket is +-0.01 in y0; a second pass halves
  it around the bracket (4 more runs, about 4 card-hours, not in the table).
- B: whether the bracket moves with N, mesh and domain (G2 three-way convergence).
- C: whether collisions turn the marginal model into a collapse, and the mass that ends
  inside the apparent horizon (needs the horizon finder settings of the first paper's
  collapse runs: adaptive mesh to M/16, `problems/st/st_cluster_amr.athinput`; a collapse
  seen on the static M/4 mesh is to be rerun there).
