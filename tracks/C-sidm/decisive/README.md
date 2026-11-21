# decisive: runs D1 and D3 of stage/REVIEW-wave2.md section 7 (wave 3, round 1)

Helper package of C-sidm. Question: does the energy defect of the release collision operator
(`coll_energy` absent = `cell`) change the collapse of the wave-2 collisional King clusters
(D1), what is the seed scatter of a collapse time (D1), and does a King model clearly on the
stable side of the fluid onset contract relative to its control as the gravothermal
hypothesis says (D3)? `JOURNAL.md` holds the go/no-go reading of the card executable (entry
1: GO), the predictions (entries 2, 4, 8, 9 and 10, each written before its runs) and the
outcomes (entries 7, 10, 11 and later).

State (2026-11-21 05:30 UTC): D1 jobs 1 and 2 and D3 job 3 ran and are analysed (entries 7, 10,
11); D3 job 4 (d3_kn10_part_s1, cc2_kn10_cell_s2) is queued; job 5 (CC1 cell seeds 2 and 3,
added in entry 10) is not submitted (one job of this package in the queue at a time).

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | go/no-go, predictions D1 and D3, outcomes |
| `scripts/decks.py` | `d1`: the D1 decks from `threshold_scan/inputs/cc{1,2}_kn10.athinput` (only `rng_seed`, `coll_energy` changed), including the job-5 cell seeds; `d3 --ic-dir DIR --tag TAG`: the D3 decks from the CC2 decks with the D3 model's files and sigma~; writes the card batch lists |
| `scripts/make_d3_ic.py` | D3 initial data (King b = 1, y0 = 0.26, N = 1e5) with the track's generator, its offline checks, K and sigma~; `--from DIR`: figure and geometry only |
| `scripts/analyze_decisive.py` | analysis of the histories: central lapse relative to the control, t_c(alpha_min < 0.3) at the record and by linear crossing, D25-D150, collisions per particle, budget columns 31-36 to t_c and to the first excision, seed scatter (window means and the instantaneous difference of the lapse curves), mode comparison, cosine fit of the controls (form of `drift/scripts/controls.py`); reads the wave-2 runs under D1 names |
| `inputs/*.athinput` | decks: `cc{1,2}_kn10_part_s{1,2}`, `cc2_kn10_cell_s2`, `cc1_kn10_cell_s{2,3}`, `d3_kninf`, `d3_kn{10,1}_part_s1` |
| `inputs/d1_job{1,2,5}.list`, `inputs/d3_job{3,4}.list` | card batch lists, each starting with a smoke run to t = 0.5 M |

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
# card jobs: one per list (commands under Pending)
harness/bin/nrpic-run submit --launcher local --cores 1 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "D1/D3 analysis" -- \
  python3 tracks/C-sidm/decisive/scripts/analyze_decisive.py --out '$NRPIC_RUN_DIR' --batch <card run ids>
```

## Runs

| Run | What | Outcome |
|---|---|---|
| C-20261120-221846-797bdbe | card, D1 job 1: cc2_kn10_part_s1, cc2_kn10_part_s2 (Slurm 4737) | completed; 35.0 min |
| C-20261121-025633-bb8dac4 | card, D1 job 2: cc1_kn10_part_s1, cc1_kn10_part_s2 (Slurm 4756) | completed; 34.7 min |
| C-20261121-035737-295e5c3 | card, D3 job 3: d3_kninf, d3_kn1_part_s1 (Slurm 4764) | completed; 35.6 min |
| C-20261121-052716-6b64f97 | card, D3 job 4: d3_kn10_part_s1, cc2_kn10_cell_s2 (Slurm 4767) | submitted 05:27 UTC |
| C-20261120-222427-6b27eea | D3 initial data, checks, K | completed: alpha_c 0.71884, +0.0482 from the Juttner onset (1.44 x the largest control drift); 18/18 checks pass; K = 251.509 |
| C-20261120-222941-595c263 | analysis test on the wave-2 runs | PASS: reproduces t_c, onsets, collision counts, defect sums |
| C-20261120-222949-2712568 | D3 figure and geometry | 97.4 percent of D3 particles in the M/4 region (CC2 98.9) |
| C-20261121-025642-fb29332 | analysis of job 1 (script of entry 3) | t_c 206.75 M for all three CC2 runs |
| C-20261121-025928-94def70 | analysis of job 1 (extended script) | JOURNAL entry 7 |
| C-20261121-035741-b3595d4 | analysis of jobs 1, 2 | JOURNAL entry 10 |
| C-20261121-052720-75f3fff | analysis of jobs 1-3 | JOURNAL entry 11 |

Card time used so far: 1.76 card-hours of allocation (35.0 + 34.7 + 35.6 min); cap 3.0.

## Results

All at N = 1e5, static M/4 mesh, 300 M, collisions-2 card executable; t_c = first alpha_min
< 0.3 by linear crossing between the 0.25 M records.

D1 (energy defect, seed scatter), JOURNAL entries 7 and 10:

| model, Kn = 10 | cell s1 (wave 2) | part s1 | part s2 | part mean - cell | part seed difference |
|---|---|---|---|---|---|
| CC2 t_c (M) | 206.66 | 206.56 | 206.73 | -0.02 | 0.17 |
| CC1 t_c (M) | 184.02 | 184.93 | 185.85 | +1.37 | 0.92 |
| CC2 D100 | 0.04264 | 0.04231 | 0.04235 | -3.1e-4 | 4.9e-5 |
| CC1 D100 | 0.05069 | 0.04917 | 0.04878 | -1.7e-3 | 3.9e-4 |

- [VERIFIED] The energy defect of the release operator does not cause the collapse and moves
  its time by at most about 1 M: CC2 -0.02 M, CC1 +1.37 M (0.7 percent; one cell seed, so a
  mode effect of that size is neither shown nor excluded; job 5 tests it).
- [VERIFIED] Seed scatter of t_c: 0.17 M (CC2), 0.92 M (CC1, at the collisionless threshold);
  the relative lapse dalpha(t) differs between seeds by rms 6e-4 over 0-100 M and 2-3e-3 later,
  oscillating on about 10 M without accumulating.
- [VERIFIED] Particle mode keeps the summed change of sum M H in the collision steps at
  3e-16 of it to t_c (+1.9 to 2.0e-21 M per collision); no pair without a root before t_c;
  detailed-balance rejections 3-6e-4 of the collisions to 150 M, 3e-3 to t_c.

D3 (King b = 1, y0 = 0.26, alpha_c = 0.719, 8.7 times CC2's distance from the Juttner fluid
onset), JOURNAL entry 11:

| run | t_c (M) | D25 | D50 | collisions per particle to t_c |
|---|---|---|---|---|
| d3_kninf (control) | none; largest excursion of alpha_c 0.0053, cosine period 282 M | | | |
| d3_kn1_part_s1 | 100.46 | 0.0094 | 0.0613 | 23.9 |
| cc2_kn1 (wave 2, cell) | 77.75 | 0.0170 | 0.0991 | 15.3 |
| cc1_kn1 (wave 2, cell) | 72.43 | 0.0185 | 0.1134 | 13.4 |

- [VERIFIED] D3 contracts relative to its control at Kn = 1 (0.56 of CC2's early rate; per
  collision almost as CC2 and CC1) and collapses at 100.5 M, 1.29 times CC2's time for 8.7 times
  its distance from the onset: the gravothermal clause "comparable contraction" holds, the
  clause "later in proportion to the distance" is refuted.
- [JUDGEMENT] The collapse of these collisional runs is set by the collisional contraction,
  not by the closeness of the model to the relativistic onset.

Failed predictions (each in the journal): seed scatter of t_c (predicted about 4 M), the sign
"particle contracts more", one-signed dH steps (CC2, CC1), n_noroot/n_balance/max_dlam bounds
beyond 150 M, the magnitude of the change of sum M H by 200 M, the entry-8 bound of 1 M on the
CC1 shift (s2 +1.83 M), the proportional collapse time of D3 at Kn = 1, the count z of D3 at
Kn = 1 (-9.9; -2.3 after adding back the balance rejections).

## Pending

| Job | List | Runs | State |
|---|---|---|---|
| D3 job 4 | `inputs/d3_job4.list` | d3_kn10_part_s1, cc2_kn10_cell_s2 | run C-20261121-052716-6b64f97, Slurm 4767, queued |
| D1 job 5 | `inputs/d1_job5.list` | cc1_kn10_cell_s2, cc1_kn10_cell_s3 | not submitted |

Each job: smoke run (t = 0.5 M) plus two runs of 300 M at 3.45-3.6 s per M, about 35 min,
0.58-0.60 card-hours; package total with job 5 about 2.95 of the 3.0 allowed. Submit one at a
time, only when `squeue -u haiyangw -o '%i %j %T'` shows fewer than two C-* jobs and the pause
flag is absent, from `/data/haiyangw/nrpic/wt/C-sidm` with a clean `tracks/C-sidm/decisive`:

```bash
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/d1_job5.list \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 \
  --purpose "decisive D1 job 5: CC1 Kn=10 cell mode seeds 2 and 3 (cell-mode seed scatter of CC1), 300 M; prediction decisive/JOURNAL.md entry 10"
# after each job: harness/bin/nrpic-run finish <run id>; then the analysis over all finished jobs:
harness/bin/nrpic-run submit --launcher local --cores 1 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "decisive: D1/D3 analysis against predictions" -- \
  python3 tracks/C-sidm/decisive/scripts/analyze_decisive.py --out '$NRPIC_RUN_DIR' \
  --batch C-20261120-221846-797bdbe C-20261121-025633-bb8dac4 C-20261121-035737-295e5c3 \
  C-20261121-052716-6b64f97 <job 5 run id>
```

D2 (cc2_kninf and cc2_kn10 in particle mode, one more refinement level, `coll_cell_factor =
2`; 2-5 card-hours by the review's estimate) does not fit the cap of this package after D1
and D3; no decks are written for it.

## Requests

To the lead of C-sidm:
1. Read the wave-2 collapse times at Kn = 10 as independent of the energy defect of the
   release operator to about 1 M (CC2 -0.02 M, CC1 +1.4 M) and reproducible to 0.2 M (CC2)
   and 0.9 M (CC1) per seed; one seed suffices for a collapse time far from the threshold, two
   near it.
2. Do not read the wave-2 collapses as evidence of the relativistic onset: D3, 8.7 times
   farther from the onset than CC2, collapses at Kn = 1 after 1.29 times CC2's time
   (entry 11). The collisional contraction sets the collapse; D2 (cell size of the collisions)
   is now the decisive test of whether that contraction rate is physical, and it needs its own
   card allotment (2-5 card-hours).
3. Particle mode is the operator to use from here on: its budget holds to rounding up to the
   collapse; its detailed-balance rejections (up to 0.7 percent at Kn = 1 before t_c) lower the
   collision count against sum_P, which a count test must add back.
