# decisive: runs D1 and D3 of stage/REVIEW-wave2.md section 7 (wave 3, round 1)

Helper package of C-sidm. Question: does the energy defect of the release collision operator
(`coll_energy` absent = `cell`) change the collapse of the wave-2 collisional King clusters
(D1), what is the seed scatter of a collapse time (D1), and does a King model clearly on the
stable side of the fluid onset contract relative to its control as the gravothermal
hypothesis says (D3)? `JOURNAL.md` holds the go/no-go reading of the card executable (entry
1: GO), the predictions (entries 2, 4 and 8, written before the runs) and the outcomes
(entries 7 and later).

State (2026-11-21 03:10 UTC): D1 for CC2 done and analysed (entry 7); D1 job 2 (CC1) queued;
D3 jobs 3 and 4 not yet submitted (one job of this package in the queue at a time).

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | go/no-go, predictions D1 and D3, outcomes |
| `scripts/decks.py` | `d1`: the D1 decks from `threshold_scan/inputs/cc{1,2}_kn10.athinput` (only `rng_seed`, `coll_energy` changed); `d3 --ic-dir DIR --tag TAG`: the D3 decks from the CC2 decks with the D3 model's files and sigma~; writes the card batch lists |
| `scripts/make_d3_ic.py` | D3 initial data (King b = 1, y0 = 0.26, N = 1e5) with the track's generator, its offline checks, K and sigma~; `--from DIR`: figure and geometry only |
| `scripts/analyze_decisive.py` | analysis of the histories: central lapse relative to the control, t_c(alpha_min < 0.3) at the record and by linear crossing, D25-D150, collisions per particle, budget columns 31-36 to t_c and to the first excision, seed scatter (window means and the instantaneous difference of the lapse curves), mode comparison; reads the wave-2 runs under D1 names |
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

## Runs

| Run | What | Outcome |
|---|---|---|
| C-20261120-221846-797bdbe | card, D1 job 1: cc2_kn10_part_s1, cc2_kn10_part_s2 (Slurm 4737) | completed; 35.0 min, 0.58 card-hours |
| C-20261121-025633-bb8dac4 | card, D1 job 2: cc1_kn10_part_s1, cc1_kn10_part_s2 (Slurm 4756) | submitted 02:56 UTC |
| C-20261120-222427-6b27eea | D3 initial data, checks, K | completed: alpha_c 0.71884, +0.0482 from the Juttner onset (1.44 x the largest control drift); 18/18 checks pass; K = 251.509 |
| C-20261120-222941-595c263 | analysis test on the wave-2 runs | PASS: reproduces t_c, onsets, collision counts, defect sums |
| C-20261120-222949-2712568 | D3 figure and geometry | 97.4 percent of D3 particles in the M/4 region (CC2 98.9) |
| C-20261121-025642-fb29332 | analysis of job 1 (script of entry 3) | t_c 206.75 M for all three CC2 runs |
| C-20261121-025928-94def70 | analysis of job 1 (extended script) | numbers of JOURNAL entry 7 |

## Results

D1, CC2 (King b = 1, y0 = 0.314) at Kn = 10, N = 1e5, M/4 mesh (JOURNAL entry 7; analysis
C-20261121-025928-94def70):

| run | t_c linear (M) | D100 | coll. per particle to t_c | summed dH / sum MH to t_c |
|---|---|---|---|---|
| cell s1 (wave 2, C-20261115-171059-35441e3) | 206.663 | 0.04264 | 2.8816 | (cell: dE_particles 2.16e-4 of sum MW) |
| part s1 (C-20261120-221846-797bdbe) | 206.556 | 0.04231 | 2.8917 | 3.1e-16 |
| part s2 (C-20261120-221846-797bdbe) | 206.728 | 0.04235 | 2.8931 | 3.2e-16 |

- [VERIFIED] The energy defect of the release operator does not move the collapse of CC2:
  t_c(particle mean) - t_c(cell) = -0.02 M; the lapse curves agree to the seed scatter.
- [VERIFIED] Seed scatter at N = 1e5, Kn = 10: collapse time 0.17 M (0.1 percent); the
  instantaneous difference of the relative lapse dalpha(t) has rms 6e-4 (0-100 M) and
  1.7e-3 (100-196 M) and oscillates on about 10 M without accumulating.
- [VERIFIED] Particle mode keeps the summed change of sum M H in the collision steps at
  3e-16 to t_c (+1.9e-21 M per collision); no pair without a root before t_c; detailed-balance
  rejections 3e-4 to 5e-4 of the collisions to 150 M, 3e-3 to t_c.
- Failed predictions: seed scatter of t_c (predicted about 4 M), the window seed scatter of
  D100 (predicted about 1e-3, one draw gave 5e-5), one-signed dH steps, n_noroot/n_balance/
  max_dlam bounds "to the first excision", the magnitude of the change of sum M H by 200 M
  (entry 7 lists each).

## Pending

| Job | List | Runs | State |
|---|---|---|---|
| D1 job 2 | `inputs/d1_job2.list` | cc1_kn10_part_s1, cc1_kn10_part_s2 | run C-20261121-025633-bb8dac4, Slurm 4756, queued |
| D3 job 3 | `inputs/d3_job3.list` | d3_kninf, d3_kn1_part_s1 | not submitted |
| D3 job 4 | `inputs/d3_job4.list` | d3_kn10_part_s1, cc2_kn10_cell_s2 | not submitted |

Each job: smoke run (t = 0.5 M) plus two runs of 300 M at 3.45-3.49 s per M, 35 min, 0.58
card-hours; package total about 2.3 of the 3.0 allowed. Submit one at a time, only when
`squeue -u haiyangw -o '%i %j %T'` shows fewer than two C-* jobs and the pause flag is
absent, from `/data/haiyangw/nrpic/wt/C-sidm` with a clean `tracks/C-sidm/decisive`:

```bash
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/d3_job3.list \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 \
  --purpose "decisive D3 job 3: King b=1 y0=0.26 control (Kn=inf) and Kn=1 with coll_energy=particle, 300 M; predictions decisive/JOURNAL.md entries 4 and 8"
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/d3_job4.list \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 \
  --purpose "decisive D3/D1 job 4: King y0=0.26 at Kn=10 (particle) and CC2 Kn=10 cell mode seed 2; predictions decisive/JOURNAL.md entries 2, 4 and 8"
# after each job: harness/bin/nrpic-run finish <run id>; then the analysis over all finished jobs:
harness/bin/nrpic-run submit --launcher local --cores 1 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "decisive: D1/D3 analysis against predictions" -- \
  python3 tracks/C-sidm/decisive/scripts/analyze_decisive.py --out '$NRPIC_RUN_DIR' \
  --batch C-20261120-221846-797bdbe C-20261121-025633-bb8dac4 <later run ids>
```

D2 (cc2_kninf and cc2_kn10 in particle mode, one more refinement level, `coll_cell_factor =
2`; 2-5 card-hours by the review's estimate) does not fit the cap of this package after D1
and D3; no decks are written for it.

## Requests

To the lead of C-sidm (to be completed when D1 and D3 are in):
1. Read the wave-2 collapse times of CC2 at Kn = 10 as independent of the energy defect of
   the release operator and as reproducible to about 0.2 M per seed (entry 7); a second seed
   is not needed for t_c at N = 1e5 and Kn = 10.
2. D2 needs its own card allotment (2-5 card-hours); it is not in this package's cap.
