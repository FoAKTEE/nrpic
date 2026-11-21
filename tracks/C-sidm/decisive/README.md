# decisive: runs D1 and D3 of stage/REVIEW-wave2.md section 7 (wave 3, round 1)

Helper package of C-sidm. Question: does the energy defect of the release collision operator
(`coll_energy` absent = `cell`) change the collapse of the wave-2 collisional King clusters
(D1), what is the seed scatter of a collapse time (D1), and does a King model clearly on the
stable side of the fluid onset contract relative to its control as the gravothermal
hypothesis says (D3)? `JOURNAL.md` holds the go/no-go reading of the card executable (entry
1: GO), the predictions (entries 2, 4, 8, 9, 10 and 12, each written before its runs) and the
outcomes (entries 7, 10, 11 and 13).

State (2026-11-21 06:30 UTC): D1 and D3 as designed have run and are analysed (jobs 1-4).
Job 5 (CC1 cell seeds 2 and 3, added in entry 10 to test whether CC1's particle-cell shift of
1.4 M is a mode effect) is submitted and waits for a card; its analysis is pending (below).

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | go/no-go, predictions D1 and D3, outcomes |
| `scripts/decks.py` | `d1`: the D1 decks from `threshold_scan/inputs/cc{1,2}_kn10.athinput` (only `rng_seed`, `coll_energy` changed), including the job-5 cell seeds; `d3 --ic-dir DIR --tag TAG`: the D3 decks from the CC2 decks with the D3 model's files and sigma~; writes the card batch lists |
| `scripts/make_d3_ic.py` | D3 initial data (King b = 1, y0 = 0.26, N = 1e5) with the track's generator, its offline checks, K and sigma~; `--from DIR`: figure and geometry only |
| `scripts/analyze_decisive.py` | analysis of the histories: central lapse relative to the control, t_c(alpha_min < 0.3) at the record and by linear crossing, D25-D150, collisions per particle, budget columns 31-36 to t_c and to the first excision, seed scatter (window means and the instantaneous difference of the lapse curves), mode comparison, cosine fit of the controls (form of `drift/scripts/controls.py`); reads the wave-2 runs under D1 names; figures `fig_d1_lapse`, `fig_d1_diff`, `fig_d1_budget`, `fig_d3_contraction`, `fig_controls` |
| `inputs/*.athinput` | decks: `cc{1,2}_kn10_part_s{1,2}`, `cc2_kn10_cell_s2`, `cc1_kn10_cell_s{2,3}`, `d3_kninf`, `d3_kn{10,1}_part_s1` |
| `inputs/d1_job{1,2,5}.list`, `inputs/d3_job{3,4}.list` | card batch lists, each starting with a smoke run to t = 0.5 M |

Executable of every card run: `/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu`
(core/collisions-2 at f46f159, sha256 82a05ada...). Mesh, particle numbers, options and
300 M as the wave-2 runs (`threshold_scan/JOURNAL.md` entry 1). Figures and `summary.json` of
the latest analysis: `/data/haiyangw/nrpic/scratch/C-sidm/C-20261121-062412-7473ef1/`.

## How to rerun

From the worktree root `/data/haiyangw/nrpic/wt/C-sidm` (venv: `harness/bin/nrpic-env create --no-kokkos`):

```bash
python3 tracks/C-sidm/decisive/scripts/decks.py d1
harness/bin/nrpic-run submit --launcher local --cores 2 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "D3 initial data" -- \
  python3 tracks/C-sidm/decisive/scripts/make_d3_ic.py --out '$NRPIC_RUN_DIR'
python3 tracks/C-sidm/decisive/scripts/decks.py d3 --ic-dir /data/haiyangw/nrpic/scratch/C-sidm/<IC run> --tag king_y0p26000
# card jobs: one per list, e.g.
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/<list> \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 --purpose "..."
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
| C-20261121-052716-6b64f97 | card, D3 job 4: d3_kn10_part_s1, cc2_kn10_cell_s2 (Slurm 4767) | completed; 35.2 min |
| C-20261121-062408-49fa14a | card, D1 job 5: cc1_kn10_cell_s2, cc1_kn10_cell_s3 (Slurm 4770) | submitted 06:24 UTC, pending |
| C-20261120-222427-6b27eea | D3 initial data, checks, K | completed: alpha_c 0.71884, +0.0482 from the Juttner onset (1.44 x the largest control drift); 18/18 checks pass; K = 251.509 |
| C-20261120-222941-595c263 | analysis test on the wave-2 runs | PASS: reproduces t_c, onsets, collision counts, defect sums |
| C-20261120-222949-2712568 | D3 figure and geometry | 97.4 percent of D3 particles in the M/4 region (CC2 98.9) |
| C-20261121-025642-fb29332 | analysis of job 1 (script of entry 3) | t_c 206.75 M for all three CC2 runs |
| C-20261121-025928-94def70 | analysis of job 1 (extended script) | JOURNAL entry 7 |
| C-20261121-035741-b3595d4 | analysis of jobs 1, 2 | JOURNAL entry 10 |
| C-20261121-052720-75f3fff | analysis of jobs 1-3 | JOURNAL entry 11 |
| C-20261121-062412-7473ef1 | analysis of jobs 1-4 | JOURNAL entry 13; the numbers below |

Card time: 2.34 card-hours of allocation used by jobs 1-4 (35.0 + 34.7 + 35.6 + 35.2 min);
job 5 adds about 0.58, 2.93 in all; cap 3.0.

## Results

All at N = 1e5, static M/4 mesh, 300 M, collisions-2 card executable; t_c = first alpha_min
< 0.3 by linear crossing between the 0.25 M records; dalpha = alpha_c(control) - alpha_c;
D100 its mean over 95-105 M. Analysis C-20261121-062412-7473ef1.

D1 (energy defect, seed scatter), JOURNAL entries 7, 10, 13:

| Kn = 10 | cell s1 (wave 2) | cell s2 | part s1 | part s2 | part mean - cell mean |
|---|---|---|---|---|---|
| CC2 t_c (M) | 206.66 | 206.26 | 206.56 | 206.73 | +0.18 (z = 0.8) |
| CC1 t_c (M) | 184.02 | job 5 | 184.93 | 185.85 | +1.37 (one cell seed) |
| CC2 D100 | 0.04264 | 0.04397 | 0.04231 | 0.04235 | -9.7e-4 (z = -1.5) |
| CC1 D100 | 0.05069 | job 5 | 0.04917 | 0.04878 | -1.7e-3 (one cell seed) |

- [VERIFIED] The energy defect of the release operator does not cause the collapse of CC2 or
  CC1 and does not move CC2's collapse time (+0.18 M against a seed scatter of 0.2-0.4 M).
  CC1's particle runs collapse 1.37 M (0.7 percent) after the one cell run; job 5 decides
  whether that is a mode effect.
- [VERIFIED] Seed scatter of t_c: CC2 0.17 M (particle) and 0.40 M (cell); CC1 0.92 M
  (particle, at the collisionless threshold). The relative lapse dalpha(t) differs between
  seeds by rms 6-9e-4 over 0-100 M and 2-3e-3 later, oscillating on about 10 M without
  accumulating.
- [VERIFIED] Particle mode keeps the summed change of sum M H in the collision steps at
  2-3e-16 of it to t_c (+1.2 to 2.0e-21 M per collision); the release operator, measured in
  the same column, changes it by 1.6e-4 (+9e-10 M per collision). No pair without a root
  before t_c at Kn = 10; detailed-balance rejections 2-6e-4 of the collisions to 150 M, 3e-3
  to t_c.

D3 (King b = 1, y0 = 0.26, alpha_c = 0.719, 8.7 times CC2's distance from the Juttner fluid
onset), JOURNAL entries 11 and 13:

| run | t_c (M) | D25 | D50 | D100 | collisions per particle to t_c (or 300 M) |
|---|---|---|---|---|---|
| d3_kninf (control) | none; largest excursion of alpha_c 0.0053, cosine period 282 M | | | | |
| d3_kn1_part_s1 | 100.46 | 0.0094 | 0.0613 | | 23.9 |
| cc2_kn1 (wave 2, cell) | 77.75 | 0.0170 | 0.0991 | | 15.3 |
| d3_kn10_part_s1 | none in 300 M (alpha_min 0.656) | 0.0014 | 0.0078 | 0.0258 | (2.88) |
| cc2_kn10 (part mean) | 206.64 | 0.0022 | 0.0117 | 0.0423 | 2.89 |

- [VERIFIED] D3 contracts relative to its control at both Knudsen numbers, at 0.56 (Kn = 1)
  and 0.61 (Kn = 10, D100) of CC2's rate: the gravothermal clause "comparable contraction"
  holds. At Kn = 1 it collapses at 100.5 M, 1.29 times CC2's time for 8.7 times its distance
  from the onset: the clause "later in proportion to the distance" is refuted there. At Kn = 10
  it does not collapse in 300 M although it collected as many collisions per particle (2.88)
  as CC2 did before its collapse.
- [JUDGEMENT] The collapse of these collisional runs is set by the collisional (gravothermal)
  contraction, in collisions per particle 1.5 times more for D3 than for CC2, not by the
  closeness of the model to the relativistic onset, which decides at most the last part of it.

Failed predictions (each in the journal): seed scatter of t_c (predicted about 4 M; measured
0.17-0.92 M), the sign "particle contracts more", one-signed dH steps, n_noroot/n_balance/
max_dlam bounds beyond 150 M and up to the first excision, the magnitude of the change of
sum M H by 200 M, the entry-8 bound of 1 M on the CC1 shift (part s2 +1.83 M), the entry-8 cell
seed scatter of collisions per particle (1.25 percent, not below 0.2), the cell-mode dH per
collision in the first 25 M (2.9e-10 M, above 2.4e-10), the proportional collapse time of D3 at
Kn = 1, the count z of D3 at Kn = 1 (-9.9; -2.3 after adding back the balance rejections).

## Pending

| Job | List | Runs | State |
|---|---|---|---|
| D1 job 5 | `inputs/d1_job5.list` | cc1_kn10_cell_s2, cc1_kn10_cell_s3 | run C-20261121-062408-49fa14a, Slurm 4770, submitted 06:24 UTC, pending |

When Slurm 4770 has ended (`squeue -j 4770` empty), from `/data/haiyangw/nrpic/wt/C-sidm`:

```bash
harness/bin/nrpic-run finish C-20261121-062408-49fa14a
harness/bin/nrpic-run submit --launcher local --cores 1 --kind scouting --gate G2 \
  --package tracks/C-sidm/decisive --purpose "decisive: D1 job 5 (CC1 cell seeds) against JOURNAL entry 10; all D1/D3 runs" -- \
  python3 tracks/C-sidm/decisive/scripts/analyze_decisive.py --out '$NRPIC_RUN_DIR' \
  --batch C-20261120-221846-797bdbe C-20261121-025633-bb8dac4 C-20261121-035737-295e5c3 \
  C-20261121-052716-6b64f97 C-20261121-062408-49fa14a
```

Then judge entry 10's job-5 prediction from `mode_comparison.cc1_kn10.t_c_interp` and
`groups.cc1_kn10_cell` of the new `summary.json`: a mode effect is shown if |mean(part) -
mean(cell)| exceeds 3 sigma with sigma^2 = s_cell^2/3 + s_part^2/2 (sample standard
deviations of the three cell and two particle t_c), excluded at the 1 M level if the
difference is below 0.5 M. If the job fails or is cancelled, its resubmission is:

```bash
harness/bin/nrpic-run submit --launcher batch --list tracks/C-sidm/decisive/inputs/d1_job5.list \
  --wall 00:55:00 --gpu-hours 0.65 --exe /data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu \
  --kind scouting --gate G2 --package tracks/C-sidm/decisive --particles 100000 \
  --purpose "decisive D1 job 5: CC1 Kn=10 cell mode seeds 2 and 3, 300 M; prediction decisive/JOURNAL.md entry 10"
```

D2 (cc2_kninf and cc2_kn10 in particle mode, one more refinement level, `coll_cell_factor =
2`; 2-5 card-hours by the review's estimate) does not fit the cap of this package; no decks are
written for it.

## Requests

To the lead of C-sidm:
1. Read the wave-2 collapse times at Kn = 10 as independent of the energy defect of the
   release operator (CC2: +0.18 M against a seed scatter of 0.2-0.4 M; CC1: +1.4 M with one
   cell seed, job 5 pending) and reproducible to 0.2-0.4 M (CC2) and 0.9 M (CC1) per seed: one
   seed suffices for a collapse time away from the threshold, two near it.
2. Do not read the wave-2 collapses as evidence of the relativistic onset. D3, 8.7 times farther
   from the onset than CC2, collapses at Kn = 1 after 1.29 times CC2's time and contracts at
   Kn = 10 at 0.6 of CC2's rate. The collisional contraction sets the collapse; whether its
   rate is physical or set by the collision cells (M/4, about 2.3 particles per cell by `../stage/REVIEW-wave2.md` line 162) is D2's
   question, which now decides the reading of every collisional run. D2 needs its own card
   allotment (2-5 card-hours).
3. Use `coll_energy = particle` from here on: its budget holds to rounding up to the collapse;
   its detailed-balance rejections (up to 0.7 percent at Kn = 1 before t_c) lower the
   collision count against sum_P, which a count test must add back (`n_balance`).
4. A continuation of d3_kn10_part_s1 (its restart file `rst/cc.00001.rst` in the run directory, at 300 M if the deck's restart cadence is that of the wave-2 decks [TO VERIFY]) would say
   whether D3 collapses at Kn = 10 after about 4.5 collisions per particle, as the collision
   scaling of entry 13 implies (prediction to be written first); not in this package's cap.
5. For drift (its JOURNAL entry 6): the control d3_kninf gives the third period point,
   P(y0 = 0.26) = 282 M, A = 0.0022 in drift's cosine form (journal entry 11); judging drift's
   prediction is drift's.
