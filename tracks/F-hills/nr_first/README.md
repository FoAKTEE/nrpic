# nr_first: first full-relativity runs of the Hills track (F-hills, wave 2)

Work package of a helper of F-hills (wave 2): the t = 0 constraints of the three-black-hole
data at mass ratio four against resolution, two single-puncture runs (junk energy; gauge
settling of the light member), readers of trackers, horizons and member energies, and the
passage P1 at q = 4 prepared but not submitted. Predictions and outcomes, including the
failed ones: `JOURNAL.md` (entries E1-E9). Labels [VERIFIED], [JUDGEMENT] as in the journal.

## State (2026-11-15)

| Item | State | Evidence |
|---|---|---|
| E1 trees of the q = 4 data | 1128 / 1716 / 2514 MeshBlocks at m/4, m/8, m/16 (t = 0) | run F-20261115-173543-29e87e8 |
| E2 t = 0 residual against resolution (C0) | done; at m/8 truncation dominates (4.7e-5), the corrected data's own residual is 4.9e-7 (1/33 of uncorrected), visible from m/16 on; order 7.6-8 | runs F-20261115-173547-a02af7d, F-20261115-181434-b9c8916; `figures/fig_c0_constraints.png`, `results/c0_constraints.json` |
| E3 single-puncture runs S3, S2 | submitted, queued on the cards (see "Pending"); the optional S1 (m/16) was withdrawn before it started (card-hour cap) | F-20261115-173601-2fae2dc (S3, S2); F-20261115-173606-efcbf69 (S1, stopped) |
| E3a single-puncture analysis checked on core's run A | reproduces core's tracker ratios 0.480/0.557/0.616, horizon 1.010719, H 2.35e-6 | F-20261115-182100-613c9c6 |
| E4 readers | `scripts/nrread.py`; synthetic test 10/10; on the three-hole data at t = 0: trackers at the input positions (4e-9), m2's horizon not found, m1 and M 0.7-0.8 percent below m Lambda | F-20261115-173821-b2c969a, F-20261115-181805-f9c3473; `figures/fig_test_nrread_synthetic.png` |
| E5 trackers across restarts | AthenaK truncates the tracker files on every restart; `scripts/athena_keep_trackers.sh` keeps them; checks 7/7 | F-20261115-173930-deef41a, F-20261115-181049-ab04d03 |
| E6 baselines of P1 | Newton ejects m1 (+1.312 units), HRNA ejects m2 (+0.970) | F-20261115-174102-ffa764f; `figures/fig_baselines_p1.png`, `results/baselines_p1.json` |
| E7 P1 smoke test on a card (400 cycles) | submitted, queued | F-20261115-174602-c6879fe |
| E8 why m2's horizon is missed at m/8 | the flow reaches the horizon and then oscillates (mass 0.126-0.137) until 400 iterations | F-20261115-182223-17ca48a |
| E9 passage analysis `scripts/p1_analysis.py` | on synthetic tracker files: +1.31187 / -1.62654 units, separation at t = 115.2 | F-20261115-183737-49f0a7f |
| P1 | prepared, NOT submitted (the lead decides) | section "P1" below |

## Contents

| Path | What |
|---|---|
| `inputs/single_P025.athinput` | one Bowen-York puncture, m = 1, P/m = 0.25 (the members of the q = 4 passage have 0.234 and 0.268), at the origin, spheres 30, 40, 50 m |
| `inputs/batch_S3_S2.list`, `batch_S1.list`, `batch_P1smoke.list` | card batches: S3 (m/8, eta m = 2), S2 (m/8, eta m = 0.25), S1 (m/16, eta m = 2), P1 for 400 cycles |
| `inputs/p1_q4.athinput` | the passage P1; its `<problem>` block is that of `three_punctures/inputs/hills_q4_m8.athinput` (wave 1), only the header differs |
| `scripts/nrread.py` | readers: trackers (segments merged), horizon summaries, history, r psi4 modes; radiated energy; member energies (two-body with M; against the barycentre of M and the other member) |
| `scripts/test_nrread.py` | tests of the readers: `synthetic`, `single <rundirs>`, `three <rundir>` |
| `scripts/athena_keep_trackers.sh` | executable wrapper for chains: copies `*.co_*.txt` to `trk_keep/<time>/` before every start |
| `scripts/test_keep_trackers.sh`, `check_keep_trackers.py` | E5 |
| `scripts/probe_mesh.sh`, `c0_t0.sh`, `c0_constraints.py` | E1, E2 |
| `scripts/single_analysis.py` | E3: junk energy, tracker speed ratio, horizon drift, constraint norms |
| `scripts/baselines_p1.py` | E6: Newton and HRNA from the P1 state (python of `scratch/F-hills/venv-gb`, numba) |
| `scripts/p1_analysis.py` | E9: the readers applied to a passage run (distances, member energies, horizons, history, radiated energy; baselines overlaid) |
| `inputs/p1_q4_finderdiag.athinput`, `scripts/finderdiag.sh` | E8 |
| `inputs/single_P025_profile.athinput`, `inputs/batch_S2g.list` | S2 repeated with core's mass-scaled shift damping (needs `scratch/core/exe/core_gauge/`; not run) |
| `figures/`, `results/` | copies of the figures and JSON of the runs named above |

## How to rerun

From `/data/haiyangw/nrpic/wt/F-hills`, each through `harness/bin/nrpic-run submit --kind
scouting --gate G1 --package tracks/F-hills/nr_first --purpose "..."`; scripts take their
output directory from `$NRPIC_RUN_DIR` (do not pass the string `'$NRPIC_RUN_DIR'`: the
command is not run by a shell).

    ... --cores 1 -- bash tracks/F-hills/nr_first/scripts/c0_t0.sh                (35 min)
    ... --cores 1 -- python tracks/F-hills/nr_first/scripts/c0_constraints.py <C0 rundir>
    ... --cores 1 -- python tracks/F-hills/nr_first/scripts/test_nrread.py synthetic
    ... --cores 1 -- bash tracks/F-hills/nr_first/scripts/test_keep_trackers.sh     (25 min)
    ... --cores 1 -- /data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python \
            tracks/F-hills/nr_first/scripts/baselines_p1.py tracks/F-hills/nr_first/inputs/p1_q4.athinput
    ... --launcher batch --list tracks/F-hills/nr_first/inputs/batch_S3_S2.list --gpu-hours 1.0 \
            --wall 00:59:00 --exe /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena

Analysis of the card runs when they have finished (not yet run):

    ... --cores 1 -- python tracks/F-hills/nr_first/scripts/single_analysis.py results_dir \
            scratch/F-hills/<S3S2 run>/S3 scratch/F-hills/<S3S2 run>/S2 scratch/F-hills/<S1 run>/S1
    ... --cores 1 -- python tracks/F-hills/nr_first/scripts/test_nrread.py single <the same run dirs>
    ... --cores 1 -- python tracks/F-hills/nr_first/scripts/test_nrread.py three scratch/F-hills/<smoke run>/P1smoke
    ... --cores 1 -- python tracks/F-hills/nr_first/scripts/p1_analysis.py scratch/F-hills/<P1 run> \
            --baselines=tracks/F-hills/nr_first/results/baselines_p1.json

Processor runs use one core: the release's processor build is serial (2.6 MeshBlock-cycles
per second measured, E5), so anything beyond t = 0 belongs on a card.

## P1: the first passage at q = 4 (prepared, not submitted)

Input `inputs/p1_q4.athinput`: M = 1, m1 = m2 = 0.125 (bare), a_b = 5.11 (e = 0.033),
centre-of-mass orbit e = 1.0002, r_p = 9.81 M, start at 31.75 M (4 r_t), coplanar prograde;
members at m/8 (0.015625), heavy hole at M/8; `corr = approx` with the background factor;
`shift_eta = 2` (eta M = 2, eta m = 0.25); tlim 280; restart every 5 M; spheres 40, 48, 70, 90.

Command (from the worktree root; dry run accepted on 2026-11-15, it then printed the note
of decision 0014 for runs above eight card-hours):

    harness/bin/nrpic-run submit --launcher chain --kind scouting --gate G1 \
        --package tracks/F-hills/nr_first --gpu-hours 20 \
        --exe tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh \
        --input /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena \
        --purpose "P1: first Hills passage in full GR at q = 4 (M = 1, m1 = m2 = 0.125, a_b = 5, r_p = 9.8 M, coplanar prograde), members at m/8, 280 M" \
        -- tracks/F-hills/nr_first/inputs/p1_q4.athinput

The wrapper is required: without it the chain keeps the trajectories of its last segment
only (E5). Before submitting: announce it in `tracks/F-hills/STATUS.md` (decision 0014), and
read the outcome of E7 and of S2 (whether eta m = 0.25 is acceptable for the members; if
core publishes `scratch/core/exe/core_gauge/READY` with `shift_eta_profile`, consider
`--exe` with `NRPIC_REAL_ATHENA` pointing to it and the profile switched on in the input).

Cost [arithmetic from measured inputs]: dt = 0.25 x 0.015625 = 0.00390625, so 71680 cycles
for 280 M. MeshBlocks 1716 at t = 0 (E1, the release executable), 1744 on average along the
Newtonian track (wave-1 trees, run F-hills-20261115-131933-907e5fe), 11 percent more with
AMR (core's three-hole run). At 2140-2201 MeshBlock-cycles per second (core's three-hole run;
novelty run F-hills-20261115-045438-f62d553): 15.8-18.0 card-hours, about 20 chain segments
of 50 minutes. E7 replaces the rate and the start count with values of this input. Card
memory: 2700 slots, about 70 GB of the 80 (26 MB per slot, core's measurement; E7 checks).

Predictions of the two baselines from the P1 state (E6, run F-20261115-174102-ffa764f;
unit (m1 m2/a)(M/m_b)^(1/3) = 4.96e-3 M) [VERIFIED as model outputs]:

| | Newton (full three-body) | HRNA (geodesic + Newtonian pair, hole fixed) |
|---|---|---|
| leaves | m1 (comp0), +1.312 units against the barycentre of M + m2 | m2 (comp1), +0.970 units |
| bound | m2 (comp1), -1.627 units, between 5.78 and 9.69 M, pericentres t = 122, 251 | m1 (comp0), -0.500 units, pericentre 7.26 M at t = 121, apocentre 42 M at t = 566 |
| binary wider than 2 a_b | t = 115.7 | t = 134.6 |
| at t = 280 | r_1M = 76.0, r_2M = 7.96, r_12 = 79.9 M | r_1M = 27.9, r_2M = 51.7, r_12 = 63.1 M |
| heavy hole | moves 13.3 M (it carries momentum 0.056) | fixed |

The baselines disagree about which member leaves: P1 decides that by t = 200. Newton with
the hole fixed agrees with full Newton on the sense (m1 leaves, +1.83 units), so the
difference is the relativistic potential, not the recoil. Read the NR trackers relative to
the heavy hole's tracker (it moves), use the barycentric energy for the member that leaves
and the two-body energy with M for the bound one (E4), and expect tracker lags of a few M
(E3 gives the size for eta m = 0.25). My expectation [JUDGEMENT]: the NR passage follows
HRNA's sense (m2 leaves, m1 bound); refuted if at t = 280 m1 is beyond 50 M and receding
while m2 stays within 15 M of the heavy hole.

Run-health predictions [JUDGEMENT; to be checked against E7]: 1716 MeshBlocks at the start,
below 2700 throughout; three trackers; horizons: heavy 0.99-1.01 M, members 0.125-0.132 M;
at m/8 the finder of m2 did not find its horizon at t = 0 on processors (C0, case approx at
m/8: `hills.horizon_summary_1.txt` NaN; m1 0.12778, heavy 0.99607), so member horizons may
be missing in early searches; no non-finite values; history Volume constant.

## Pending (not done by this package)

- Card runs queued since 17:36 UTC behind six jobs of other owners: S3 + S2 (job 4474), P1
  smoke (4476); S1 (4475) withdrawn. Their analysis commands are above.
- The repeat of the light single-puncture run with core's mass-scaled shift damping: core
  has not published `scratch/core/exe/core_gauge/READY` (branch `core/gauge` has
  `shift_eta_profile` in progress).
- `test_nrread.py three` on a three-hole run with more than one horizon search (E7 output).

## Requests

- core: (1) `compact_object_tracker.cpp` line 78 opens `<base>.co_<n>.txt` with truncation
  also on a restart, so chained runs lose their trajectories; append when restarting (or
  name the file per segment). Until then use `scripts/athena_keep_trackers.sh` (E5).
  (2) At m/8 the finder did not find the horizon of the member with P/m = 0.268 at t = 0
  (C0); advice on `flow_alpha_beta_const`, the first-guess radius or `mass_tol` for holes
  resolved by about 4 cells per horizon radius. (3) The mass-scaled shift damping
  (`core/gauge`): publish the executable with READY so that S2 can be repeated with it.
- orch (harness): (1) `nrpic-run submit --launcher local` runs in the worktree root, and
  AthenaK writes trackers and horizon summaries into its working directory, not into `-d`:
  they dirty the tree (E1/E2 incidents). Run the command in the run directory, or say so in
  `harness/RULES.md`. (2) The command is not run by a shell: `'$NRPIC_RUN_DIR'` arrives
  literally; RULES.md could say "read NRPIC_RUN_DIR from the environment". (3) The processor
  build of the release is serial; `--cores` above one reserves cores athena does not use.
- F-hills lead: the decision on P1 (command above); whether to keep one `shift_eta = 2` after
  S2, or wait for the profile.
