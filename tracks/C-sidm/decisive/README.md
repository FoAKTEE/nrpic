# decisive: runs D1 and D3 of stage/REVIEW-wave2.md section 7 (wave 3, round 1)

Helper package of C-sidm. Question: does the energy defect of the release collision operator
(`coll_energy` absent = `cell`) change the collapse of the wave-2 collisional King clusters
(D1), what is the seed scatter of a collapse time (D1), and does a King model clearly on the
stable side of the fluid onset contract relative to its control as the gravothermal
hypothesis says (D3)? `JOURNAL.md` holds the go/no-go reading of the card executable (entry
1: GO), the predictions (entries 2 and 4, written before the runs) and the outcomes.

State: see "Results" and "Pending" below (this file is rewritten as runs finish).

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | go/no-go, predictions D1 and D3, outcomes |
| `scripts/decks.py` | `d1`: the D1 decks from `threshold_scan/inputs/cc{1,2}_kn10.athinput` (only `rng_seed`, `coll_energy` changed); `d3 --ic-dir DIR --tag TAG`: the D3 decks from the CC2 decks with the D3 model's files and sigma~; writes the card batch lists |
| `scripts/make_d3_ic.py` | D3 initial data (King b = 1, y0 = 0.26, N = 1e5) with the track's generator, its offline checks, K and sigma~; `--from DIR`: figure and geometry only |
| `scripts/analyze_decisive.py` | analysis of the histories: central lapse relative to the control, t_c(alpha_min < 0.3), D50/D100, collisions per particle, budget columns 31-36, seed scatter and mode comparison; reads the wave-2 runs under D1 names |
| `inputs/*.athinput` | decks: `cc{1,2}_kn10_part_s{1,2}`, `cc2_kn10_cell_s2`, `d3_kninf`, `d3_kn{10,1}_part_s1` |
| `inputs/d1_job{1,2}.list`, `inputs/d3_job{3,4}.list` | card batch lists, each starting with a smoke run to t = 0.5 M |

Executable of every card run: `/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu`
(core/collisions-2 at f46f159, sha256 82a05ada...). Mesh, particle numbers, options and
300 M as the wave-2 runs (`threshold_scan/JOURNAL.md` entry 1).

## How to rerun

From the worktree root `/data/haiyangw/nrpic/wt/C-sidm` (venv: `harness/bin/nrpic-env create --no-kokkos`):

```bash
python3 tracks/C-sidm/decisive/scripts/decks.py d1
harness/bin/nrpic-run submit --launcher local --cores 2 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "D3 initial data" -- \
  python3 tracks/C-sidm/decisive/scripts/make_d3_ic.py --out '$NRPIC_RUN_DIR'
python3 tracks/C-sidm/decisive/scripts/decks.py d3 --ic-dir /data/haiyangw/nrpic/scratch/C-sidm/<IC run> --tag king_y0p26000
# card jobs: one per list, at most one of this package in the queue (see Pending)
harness/bin/nrpic-run submit --launcher local --cores 1 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "D1/D3 analysis" -- \
  python3 tracks/C-sidm/decisive/scripts/analyze_decisive.py --out '$NRPIC_RUN_DIR' --batch <card run ids>
```

## Runs so far

| Run | What | Outcome |
|---|---|---|
| C-20261120-221846-797bdbe | card, D1 job 1: cc2_kn10_part_s1, cc2_kn10_part_s2 (Slurm 4737) | submitted 22:18 UTC |
| C-20261120-222427-6b27eea | D3 initial data, checks, K | completed: alpha_c 0.71884, +0.0482 from the Juttner onset (1.44 x the largest control drift); 18/18 checks pass; K = 251.509 |
| C-20261120-222941-595c263 | analysis test on the wave-2 runs | PASS: reproduces t_c, onsets, collision counts, defect sums |
| C-20261120-222949-2712568 | D3 figure and geometry | 97.4 percent of D3 particles in the M/4 region (CC2 98.9) |

## Results

(filled in as the card runs finish)

## Pending

(filled in at the end)

## Requests

(filled in at the end)
