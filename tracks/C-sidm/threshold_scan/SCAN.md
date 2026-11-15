# The longer threshold scan: prepared inputs and cost (not run in wave 2)

State 2026-11-15, after the wave-2 card runs (helper of C-sidm, package threshold_scan).
Inputs are written by `make_scan.py` (particle files: run C-20261115-174556-3544e2c;
decks: `inputs/scan/`, list `inputs/scan/decks.list`). Costs use what the wave-2 runs
measured: 3.42-3.46 s per M on the static M/4 mesh at N = 10^5 (six runs, analysis run
C-20261115-191420-8538aa4); for the adaptive mesh to M/16 the G0 estimate 14.2-17.5 s per M
(first paper's collapse runs at N = 10^4, `../stage/G0/REPORT.md` section 8; not measured
at N = 10^5). [JUDGEMENT on the block design; the G2 criterion of decision 0013 reads "the
collisionless threshold is located with three-way convergence and compared with the
turning-point criterion".]

What wave 2 changed in the plan (`JOURNAL.md` entry 6):

1. Collisions at Kn = 10 and 1 made both King models (y0 = 0.334032 and 0.314) collapse
   within 72-207 M. The static M/4 mesh cannot follow the black hole: the constraint norm
   grows to 10-1900 after the collapse and the state turns non-finite (the run still exits
   with status 0). The collapsed mass therefore needs the adaptive mesh with the horizon
   finder (`scanC_amr_*`), and a static-mesh run must be stopped once alpha_min < 0.3.
2. Both collisionless controls make a slow outward excursion (alpha_c up by 0.018 and
   0.033, back by 300 M); its cause is open and the mesh leg of block B tests it.
3. The collisional threshold, if any, lies at a lower compactness than y0 = 0.314: block D.

## Blocks

| Block | Purpose | Decks | Length | Card-hours |
|---|---|---|---|---|
| A | collisionless threshold of the King b = 1 sequence: fate (collapse, migration outward, oscillation) of y0 = 0.314, 0.324, 0.334032, 0.344, 0.354 under a one-percent coherent radial kick inward and outward (static M/4 mesh; stop a run once alpha_min < 0.3) | 10 (`scanA_*`) | 1000 M | 9.5-9.6 |
| A' | continuation of the wave-2 controls cc1_kninf, cc2_kninf to 1000 M from their restart files at 300 M (does the excursion return to the start, grow, or turn into collapse?) | 2 | 700 M | 1.3-1.4 |
| B | three-way convergence at the pair of models that brackets the threshold in A: N = 10^4 against 10^5; mesh with a level-7 region (M/8) inside \|x\| < 3.9 M (about 464 MeshBlocks and half the step, about 2.3 times the cost); domain 1024 M against 512 M (one more level, about 1.14 times); the mesh leg also tests the controls' excursion | 6 (2 models x 3 variants; written once A has the bracket) | 1000 M | about 8.9 |
| C | collisional collapse of the threshold model on the adaptive mesh with the apparent-horizon finder (`problems/st/st_cluster_amr.athinput`): Kn = 10, 3, 1, 0.3; collapsed mass against Kn | 4 (`scanC_amr_cc1_kn{10,3,1,0p3}`) | 300 M | 4.7-5.8 |
| C (static) | the same at Kn = 3 and 0.3 on the static mesh, for the phase before the collapse only (cheaper; stop at alpha_min < 0.3) | 2 (`scanC_cc1_kn3`, `scanC_cc1_kn0p3`) | to collapse, at most 300 M | 0.6 |
| D | bracket of the collisional threshold: Kn = 1 on less compact King models (for example y0 = 0.1, 0.2, 0.25; particle files from `make_ic.py`-like calls of the equilibria package, decks from `make_decks.deck`), static M/4 mesh | 3 (not written yet) | 300 M | 0.9 |
| | total | 27 | | about 26-28 |

Decision 0014 gives C 45 card-hours toward the next gate (1.73 used in wave 2, 43.27 left
per `nrpic-run budget`); no single run exceeds eight card-hours.

## How to run

A run longer than an hour is a chain (`scripts/submit_chain.sh` through the harness; two
segments of 50 min for 1000 M on the static mesh; restart files every 200 M, 50 M on the
adaptive mesh):

    cd /data/haiyangw/nrpic/wt/C-sidm && harness/bin/nrpic-run submit --launcher chain \
      --kind scouting --gate G2 --package tracks/C-sidm/threshold_scan --gpu-hours 2 \
      --particles 100000 --purpose "scan A: <model> <kick>" \
      -- tracks/C-sidm/threshold_scan/inputs/scan/scanA_y0p33403_kin.athinput

Runs of an hour or less go in pairs through `--launcher batch --list <file> --wall 00:55:00`
as in wave 2. A continuation (A') copies the restart pair `rst/cc.00001.rst` and
`rst/cc.00001.rst.prt` of the wave-2 run into `<new chain dir>/rst/` and starts the chain
with the same deck and `time/tlim=1000` (the chain resumes from the newest restart).
Analysis: `analyze.py <run ids>` reads any run directory named `cc*_kn*`; scan runs need
their names mapped (`analyze.find_runs`).

## What each block decides

- A: the sign of the fate on each side of y_max = 0.334032 (2009.08163 finds the binding-
  energy maximum to be the onset, lines 1083-1092). With the y0 grid of 0.01 the bracket is
  +-0.01; a second pass halves it (4 more runs, about 4 card-hours, not in the table).
- B: whether the bracket moves with N, mesh and domain (G2 three-way convergence).
- C: the collapsed mass (apparent horizon) against Kn on the threshold model; collisions in
  an adaptive mesh are untested by core (`coord/INTERFACES/collisions.md` section 9: adaptive
  refinement during a run not exercised), so the first C run is also that test.
- D: whether a collisional threshold exists above y0 = 0.1 at Kn = 1.

Open before C and D are science runs: the pair-energy correction of the collision step
(the defect grows to 1.6e-3 of sum M W before the collapse at Kn = 1 on M/4 cells), and the
occupation of the collision cells (2.3 particles on average at N = 10^5; core advises about
100 for relaxation fidelity).
