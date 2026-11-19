# nr_first: first full-relativity runs of the Hills track (F-hills, waves 2 and 2b)

Work package of a helper of F-hills: the t = 0 constraints of the three-black-hole data at
mass ratio four against resolution, single-puncture runs (junk energy; gauge settling of the
light member), readers of trackers, horizons and member energies, the smoke test and the cost
of the passage P1 at q = 4. Predictions and outcomes, including the failed ones: `JOURNAL.md`
(entries E1-E11; wave 2b from "2026-11-19 Wave 2b resumed" on). Labels [VERIFIED],
[JUDGEMENT] as in the journal.

## State (2026-11-19, 14:50 UTC)

| Item | State | Evidence |
|---|---|---|
| E1 trees of the q = 4 data | 1128 / 1716 / 2514 MeshBlocks at m/4, m/8, m/16 (t = 0) | run F-20261115-173543-29e87e8 |
| E2 t = 0 residual against resolution (C0) | at m/8 truncation dominates (4.7e-5); the corrected data's own residual 4.9e-7 (1/33 of uncorrected), visible from m/16 on | F-20261115-173547-a02af7d, F-20261115-181434-b9c8916; `figures/fig_c0_constraints.png` |
| E3 single punctures S3 (eta m = 2), S2 (eta m = 0.25), cells m/8 | both STOPPED by the slot limit (1632 > 1600 MeshBlocks) at t = 22 m (S3) and 14 m (S2): junk energy not measured; tracker: S2 settles at f = 0.76 by 4 m, S3 still accelerating at 22 m (f = 0.52); horizon at t = 0 0.87 percent low (0.99909), good searches from t = 2.5-3.5 m at 1.0062-1.0079, drift t = 4-6 to 12-14: S3 +5.1e-4, S2 +8.5e-4; S2's coordinate horizon smaller (0.89 m against 1.18 m at t = 14) | F-20261115-173601-2fae2dc; analysis F-20261119-143214-5f5dc3a; `figures/fig_e3_single_gauge.png`, `results/e3_single_analysis.json` (made before the reader fix: its found/missed counts are wrong, see E4) |
| E3a analysis checked on core's run A | reproduces core's tracker ratios and horizon mass | F-20261115-182100-613c9c6 |
| E4 readers | `scripts/nrread.py`; FIXED 2026-11-19: a failed horizon search writes the previous row again (`z4c/fastflow.cpp` 379-392, 808-822), now counted as missed; tests 10/10 (synthetic, failures planted), 6/8 (S3, S2: searches fail at t = 1-3 m), 3/4 (P1 smoke) | F-20261119-143627-1a84aa5, -143632-0f6e57d, -143633-dfd3607 |
| E5 trackers across restarts | AthenaK truncates the tracker files on every restart; `scripts/athena_keep_trackers.sh` keeps them | F-20261115-173930-deef41a, F-20261115-181049-ab04d03 |
| E6 baselines of P1 | Newton ejects m1 (+1.312 units), HRNA ejects m2 (+0.970) | F-20261115-174102-ffa764f; `figures/fig_baselines_p1.png` |
| E7 P1 smoke on a card (400 cycles) | 1716 -> 1744 MeshBlocks; 2057 MeshBlock-cycles per second; 70847 MiB at 2700 slots; trackers at the input positions; member horizons good from t = 0.5 M (0.1295), heavy hole fails 17 of 25 early searches; H(t = 0) equal to the processor value | F-20261115-174602-c6879fe; analysis F-20261119-144544-d9c8542; `figures/fig_e7_p1smoke.png` |
| E8 why m2's horizon is missed at t = 0 at m/8 | the flow oscillates (mass 0.126-0.137) until 400 iterations; on the card m2 is found from t = 0.0625 M | F-20261115-182223-17ca48a |
| E9 passage analysis `scripts/p1_analysis.py` | checked on synthetic tracker files | F-20261115-183737-49f0a7f |
| E10 S2g (mass-scaled shift damping, core_gauge) | prediction written; submitted, QUEUED (Slurm job 4640, expected start by 19:58 UTC); comparison script tested on S3, S2 (E10a) | F-20261119-143443-f11ebb9; E10a F-20261119-144351-b448f38 |
| E11 why 1632 MeshBlocks | the wave-zone radius (56 m, level 3) with the 2:1 rule takes every root block to level 1: 1576 blocks; 1632 once the tracker passes x = 2.20 m; a model of the rules equals the restart trees exactly; maximum 1632 along x = 0-20 m | F-20261119-144425-10a94b7, F-20261119-144024-988d5c9; `figures/fig_e11_tree_check.png` |
| P1 | input ready (section "P1"); NOT submitted (the lead decides; decision 0014: above eight card-hours) | E7 |

Card time of this package: 0.30 card-hours (S3 7.4 min, S2 4.8 min, P1 smoke 5.8 min); S2g
reserved (at most 0.98 h, expected 0.55 h).

## Contents

| Path | What |
|---|---|
| `inputs/single_P025.athinput` | one Bowen-York puncture, m = 1, P/m = 0.25, at the origin, spheres 30, 40, 50 m; `max_nmb_per_rank = 1600` is too small (E11): give `mesh_refinement/max_nmb_per_rank=2400` on the command line |
| `inputs/single_P025_profile.athinput` | S2g: as above with `shift_eta = 0.25`, `shift_eta_profile = true`, `shift_eta_mref = 8` (eta m = 2 at the hole, 0.25 far); needs `scratch/core/exe/core_gauge/athena_gpu` |
| `inputs/batch_S3_S2.list`, `batch_S1.list`, `batch_P1smoke.list`, `batch_S2g.list` | card batches (S1 not run; it needs the slot override too, and more: check with `tree_check.py` first) |
| `inputs/p1_q4.athinput` | the passage P1; `<problem>` block identical to `three_punctures/inputs/hills_q4_m8.athinput` (wave 1) |
| `inputs/p1_q4_finderdiag.athinput` | E8 |
| `scripts/nrread.py` | readers: trackers (segments merged), horizon summaries (failed searches counted as missed), history, r psi4 modes, radiated energy, member energies |
| `scripts/test_nrread.py` | tests of the readers: `synthetic`, `single <rundirs>`, `three <rundir>` |
| `scripts/athena_keep_trackers.sh` | executable wrapper for chains: copies `*.co_*.txt` to `trk_keep/<time>/` before every start; the real executable is `$NRPIC_REAL_ATHENA` or the release card build |
| `scripts/single_analysis.py` | E3: tracker speed ratio, horizon, constraints, junk energy of single-puncture runs |
| `scripts/s2g_compare.py` | E10: S2g against S3 and S2 on common windows, the E10 criteria as PASS/FAIL checks |
| `scripts/tree_check.py` | E11: trees from restart files; a model of AthenaK's refinement rules (`model`, `path` modes) |
| `scripts/p1_analysis.py`, `baselines_p1.py` | E9, E6 |
| `scripts/probe_mesh.sh`, `c0_t0.sh`, `c0_constraints.py`, `finderdiag.sh`, `test_keep_trackers.sh`, `check_keep_trackers.py` | E1, E2, E8, E5 |
| `figures/`, `results/` | copies of the figures and JSON of the runs named above (`e3_`, `e4_`, `e7_`, `e10a_`, `e11_` from wave 2b) |

## How to rerun

From `/data/haiyangw/nrpic/wt/F-hills`, each through `harness/bin/nrpic-run submit --kind
scouting --gate G1 --package tracks/F-hills/nr_first --purpose "..."` (local runs: `--cores 1
-- .venv/bin/python tracks/F-hills/nr_first/scripts/<script> - <args>`; `-` means "write to
`$NRPIC_RUN_DIR`"). With S=/data/haiyangw/nrpic/scratch/F-hills/F-20261115-173601-2fae2dc and
P=/data/haiyangw/nrpic/scratch/F-hills/F-20261115-174602-c6879fe (expanded by your shell):

    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/single_analysis.py - $S/S3 $S/S2
    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/test_nrread.py synthetic
    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/test_nrread.py single $S/S3 $S/S2
    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/test_nrread.py three $P/P1smoke
    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/p1_analysis.py $P/P1smoke \
            --baselines=tracks/F-hills/nr_first/results/baselines_p1.json
    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/tree_check.py - \
            tracks/F-hills/nr_first/inputs/single_P025.athinput $S/S3 $S/S2
    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/tree_check.py path \
            tracks/F-hills/nr_first/inputs/single_P025.athinput 0 20 0.125
    ... -- .venv/bin/python tracks/F-hills/nr_first/scripts/s2g_compare.py - $S/S3 $S/S2

Card batches: `--launcher batch --list tracks/F-hills/nr_first/inputs/<list> --gpu-hours 1.0
--wall 00:59:00 --exe <card executable>` (S2g: `--exe
/data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_gpu`). The processor build of the
release is serial: anything beyond t = 0 belongs on a card.

## P1: the first passage at q = 4

Input `inputs/p1_q4.athinput`: M = 1, m1 = m2 = 0.125 (bare), a_b = 5.11 (e = 0.033),
centre-of-mass orbit e = 1.0002, r_p = 9.81 M, start at 31.75 M (4 r_t), coplanar prograde;
members at m/8 (0.015625), heavy hole at M/8; `corr = approx` with the background factor;
`shift_eta = 2` (eta M = 2, eta m = 0.25); tlim 280; restart every 5 M; spheres 40, 48, 70, 90.

Cost, from the smoke test E7 on this input [arithmetic from measured numbers]: 71680 cycles
(dt = 3.90625e-3 M) at 2057 MeshBlock-cycles per second (measured with three finders every 16
cycles, four spheres, regrids and restart output inside the timing). Mean tree 1744 MeshBlocks
(the smoke at cycle 400 and the mean of the wave-1 trees along the Newtonian track) gives 16.9
card-hours; 1905 (11 percent growth, core's three-hole run) 18.4; 2080 (largest wave-1 tree)
20.1. So 17-20 card-hours, 21-25 chain segments of 50 min. Card memory 70847 MiB at 2700 slots
(26.2 MiB per slot; 11 GiB left on the 80 GB card), so the slot limit cannot be raised much.
Disk: restart files of 4.2 GB every 5 M, 235 GB over the run unless older ones are removed.

Ready to submit: YES, as tested in the smoke, with the release core-v0.3 card executable
(`/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena`) behind the tracker wrapper, gauge
1+log lapse with advection and the Gamma-driver with constant `shift_eta = 2` (eta M = 2,
eta m = 0.25), and `--gpu-hours 26` (the chain is capped at floor(gpu-hours / 59 min)
segments; the 20 of the wave-2 command gave 16.7 h of athena time, too few). Decision 0014:
above eight card-hours, announce in `tracks/F-hills/STATUS.md` and wait for an otherwise empty
queue (lead).

    harness/bin/nrpic-run submit --launcher chain --kind scouting --gate G1 \
        --package tracks/F-hills/nr_first --gpu-hours 26 \
        --exe tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh \
        --input /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena \
        --purpose "P1: first Hills passage in full GR at q = 4 (M = 1, m1 = m2 = 0.125, a_b = 5, r_p = 9.8 M, coplanar prograde), members at m/8, 280 M" \
        -- tracks/F-hills/nr_first/inputs/p1_q4.athinput

Gauge [JUDGEMENT]: with eta m = 0.25 the light member's tracker settles within 4 m at
f = 0.76 of its boost speed (S2), against f = 0.52 and still rising at 22 m with eta m = 2
(S3); its horizon mass drifts 1.7 times faster on t = 4-14 m (8.5e-4 against 5.1e-4) and its
coordinate horizon is 25 percent smaller (0.89 m = 7 cells against 1.18 m at t = 14 m). Over the
passage (280 M = 2240 member masses) neither drift is measured. Core's mass-scaled profile
(`core_gauge`, `shift_eta = 2`, `shift_eta_profile = true`, `shift_eta_mref = 1`: eta m = 2 at
each member, 2/M elsewhere; core's recommendation for Track F) would keep the members' horizons
as in S3, but it is tested on single and paired holes only (core/gauge READY: "Not tested:
more than two holes, a Hills passage"), and S2g, its test at the member's damping, is queued.
If S2g passes E10, the profile variant needs its own 400-cycle smoke on a card (0.1
card-hours) before a passage; until then the release with constant eta is the tested choice.

Run-health expectations for P1 (E7): three trackers; member horizons from t = 0.5 M, heavy
hole's from about t = 4 M (its early searches fail as the single puncture's do at the same
cells per mass, E3); read masses only from searches with hrms below 1e-3; no non-finite
values; history Volume constant. Baseline predictions (E6): Newton ejects m1 (+1.312 units),
HRNA ejects m2 (+0.970); P1 decides by t = 200 M.

## Pending (not done by this package)

- S2g: run F-20261119-143443-f11ebb9, Slurm job 4640 (queued at 14:34 UTC behind ten jobs;
  Slurm's estimate of the start 19:58 UTC). When it has ended:

      harness/bin/nrpic-run finish F-20261119-143443-f11ebb9
      G=/data/haiyangw/nrpic/scratch/F-hills/F-20261119-143443-f11ebb9
      S=/data/haiyangw/nrpic/scratch/F-hills/F-20261115-173601-2fae2dc
      harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/nr_first \
          --cores 1 --parent F-20261119-143443-f11ebb9 --purpose "nr_first E10: S2g against S3, S2" \
          -- .venv/bin/python tracks/F-hills/nr_first/scripts/s2g_compare.py - $S/S3 $S/S2 $G/S2g
      ... --purpose "nr_first E10: S2g junk energy" \
          -- .venv/bin/python tracks/F-hills/nr_first/scripts/single_analysis.py - $S/S3 $S/S2 $G/S2g

  then record the outcome of E10 against its predictions in `JOURNAL.md` (criteria unchanged),
  read the figures, and decide on the gauge of P1 (section "P1").
- Junk energy of a single member (E3 prediction 3) and the m/16 partner S1: not measured; S2g
  measures the junk at m/8 if it reaches t = 90 m.
- The decision on P1 (lead).

## Requests

- core: (1) `compact_object_tracker.cpp` line 78 opens `<base>.co_<n>.txt` with truncation
  also on a restart, so chained runs lose their trajectories; append when restarting (or name
  the file per segment). Until then use `scripts/athena_keep_trackers.sh` (E5). (2) At m/8 the
  finder misses m2 at t = 0 (E8) and the heavy hole's early searches fail or converge in mass to
  poor surfaces (hrms 0.02-0.15) for the first few M (E7, E3): a convergence test on hrms, or
  advice on `flow_alpha_beta_const`, for horizons resolved by about 4 cells per radius. (3) A
  failed search writes the previous search's values again (`fastflow.cpp` lines 379-392,
  808-822); a flag column (found or not) in the summary would make this explicit. (4) For
  the profile variant of P1: the outcome of core's card versions of E1/E2 (job 4478) in READY,
  and whether `shift_eta_profile` has been run with three holes.
- F-hills lead: the decision on P1 (command above, `--gpu-hours 26`); announce it in STATUS.md
  (decision 0014). Analyse S2g with the commands above when job 4640 has ended.
