# runs_ball: full-relativity runs of the expanding ball (Track A)

Helper package of A-emd-pbh. Wave 2 (2026-11-15): SR-1 (geodesic slicing) and SR-2
(conformal-time lapse) on data set 2t. Wave 2b (2026-11-19): SR-1L, data set 2t with the relaxed
1+log lapse of core's gauge package, and BH-1, data set 3, whose first horizon (areal radius
1.37 M) these meshes resolve; BH-1R, the same with one static level of cells M/16. Wave 3
(2026-11-20/21): the analysis of those card runs, a turnaround estimator without a fit window,
SR-1L on a fixed box, and the excision criterion. Everything is compared with the exact
solution (`expball/exact.py`) in invariants only. Predictions and outcomes with every run id:
`JOURNAL.md` (entries 1-6 wave 2, 7-10 wave 2b, 11-19 wave 3). Figures: `figs/` (each looked at).

## Wave 3 results (numbers with run ids; details in JOURNAL entries 11, 12, 18, 19)

Card runs (executable `scratch/core/exe/core_gauge/athena_gpu`, source b4430da):
A-20261119-144419-13d5601 (Slurm 4642: SR-1L at dx = M, M/2 over [-64,64]^3 to t = 44 and M/4
over [-32,32]^3 to t = 24; BH-1 at uniform M/4, M/6, M/8 over [-16,16]^3 to t = 16),
A-20261119-164634-f1fe887 (Slurm 4665: BH-1R), A-20261120-223310-a9ce31a (Slurm 4748: SR-1L on
[-32,32]^3 at dx = M, M/2). All closed (`nrpic-run finish`, completed).
Analyses: A-20261121-074923-d396d73 (SR-1L, BH-1), A-20261121-080558-02c3188 (BH-1R),
A-20261121-081153-b92c08c (excision, BH-1 breakdown, BH-1R line diagnostics and G2 summary),
A-20261121-081138-ebe70b4 (turnaround estimators, SR-1 breakdown criteria),
A-20261121-081605-f95b10c (fixed box, SR-1L reruns for the gauge figure and the light speed).

| quantity | value | run id |
|---|---|---|
| SR-1L reaches its end, finite | t = 44 (M, M/2), 24 (M/4); mean abs(H) grows 3.9x from t = 10 to 40 (M/2) | -074923- |
| SR-1L central lapse against the homogeneous relaxed-lapse reference | within 5.7e-3 to t = 15; above it afterwards (alpha_c = 0.876 at t = 44, reference < 0.1 from t = 40.3) | -074923- |
| SR-1L central proper time at t = 44 | 43.44 (M/2), 43.70 (M); first trapping 44.349: no horizon by t = 44 | -074923- |
| SR-1L core max abs(R/R_ex - 1) at tau = 16.894 | 1.38e-2 (M), 6.4e-4 (M/2), 1.52e-4 (M/4, L = 32) | -074923- |
| same at fixed box L = 32 and lattice h = M/4 | 1.21e-2 (M), 9.13e-4 (M/2), 1.52e-4 (M/4): orders 3.73, 2.59 | -081605- |
| box L = 32 vs 64 at M/2 (h = M/2) | core error 6.399e-4 vs 6.400e-4; turnaround V3 -0.0063 in both | -081605- |
| lattice h = M/4 vs M/2 at dx = M/2 | core error 9.13e-4 vs 6.40e-4; turnaround +0.014 vs -0.005 M (C) | -081605- |
| SR-1L mean core turnaround error (V3; C = cycloid fit) | M: -0.59 (-0.76); M/2: -0.0063 (-0.0099); M/4: -0.0049 (-0.0056) M | -074923-, -081138- |
| SR-1L coordinate light speed on the line, t <= 20 | 1.11 (1.13 with the shift) | -081605- |
| BH-1 uniform M/4, M/6, M/8: finder | no horizon in 64-65 searches (start radius 3 M) | -074923- |
| BH-1: first slice with a trapped sphere (particles' clocks) | code time 10.33, 10.41, 10.47 | -074923- |
| BH-1: trapped sphere on the line (M/8) | from t = 11.0 at coordinate radius 0.44-0.47 M, Misner-Sharp mass 0.694-0.716 vs exact 0.688-0.692 | -074923- |
| BH-1: first non-positive metric determinant (non-finite end) | t = 14.31, 14.50, 15.03 | -081153- |
| BH-1 core max abs(eps) at the turnaround tau = 3.37 | 1.39e-2, 6.75e-3, 5.29e-3 | -074923- |
| BH-1R: reaches t = 16 finite; first finder detection | code time 10.875 (first trapped slice 10.54); found in all 41 searches to 15.875 | -080558-, -081153- |
| BH-1R: clock of the shell at the horizon minus its exact tau_AH | -0.046 M at first detection, within +-0.012 M from t = 11.25 | -081153- |
| BH-1R: finder m_irr vs exact horizon mass of the same slice | +1.97e-2 at first detection; median -4.5e-4 over the first 4 M; abs <= 6.3e-4 from t = 11.75 | -081153- |
| BH-1R: line Misner-Sharp mass of the trapped sphere | +1.0e-2 at t = 11.0, +6e-4 at t = 16 (same dip as the finder at t = 11.5) | -081153- |
| BH-1R: central lapse; constraints | < 0.1 from t = 12.98, 0.073 at 16; max abs(H) 5 inside the horizon, mean 3.5e-3 at t = 16 | -080558- |
| BH-1R core turnaround (V3); core-edge trapping per particle | -0.0012 M; -0.0085, -0.0029, -0.0020 M (bands R_i = 2.60, 2.70, 2.80) | -080558- |
| particle excision | lapse criterion through the interpolated lapse at the particle: BH-1 M/2 removed 515 particles while every cell lapse was >= 0.48; BH-1R 325784 particles (rest mass 0.827) inside the horizon from t = 12.70; BH-1 M/4-M/8 lose all particles at the blow-up (non-finite states) | -081153- |
| SR-2 turnaround at M/4 (R2 re-judged) | local maximum (V3 +0.031, GCV spline +0.035): fails 0.02; secular cycloid fit +0.0178 +- 0.0023 (plateau 0.018-0.020 for windows >= 4 M): holds | -081138- |
| SR-1 breakdown (dx = M/2 / M), by criterion | non-positive determinant 32.875 / 30.25; abs(H) > 1e10 33.0 / 30.75; first non-finite cstat 33.125 / 31.0 | -081138- |

Source paper level [VERIFIED, `refs/arxiv_2611.12831/src/main.tex`]: final mass after excision
against M_ADM "<~ 1e-3" (line 945); RMS eps_M = 2.061e-3, 9.362e-4, 7.347e-4 for A1-A3 (line
1484). BH-1R's horizon-mass error after the formation transient (3e-4 to 6e-4) is of the same order
[JUDGEMENT: different quantity, one resolution; entry 12].

Turnaround estimators (`turnaround.py`, entry 13): V3 (vertex through three records), P_k (least
squares over 2k+1 records), S (smoothing spline, smoothing by generalized cross-validation), C
(three-parameter cycloid over 0 <= tau <= 2 tau_ta), C(W) (the same within W of the exact
turnaround), Cexp (expansion only), O (exact cycloid of the shell with free offset and scale).
S and C have no tunable window; S measures the local maximum of R(tau), C the turnaround of the
secular motion. C is window independent where the shell error has no secular drift (SR-1L M/4,
SR-2 M/4), not where the record runs into an instability or is one-sided (SR-1). Figures:
`fig_turnaround_windows.png` (estimator against window), `fig_turnaround_synthetic.png`,
`fig_turnaround_particles.png`, `fig_turnaround_eps.png`, and `_box` versions.

## Wave 2 results (details in JOURNAL entries 3 and 6)

| | SR-1, lapse 1, shift 0 (geodesic slicing) | SR-2, conformal-time lapse + Gamma-driver |
|---|---|---|
| runs (dx = M/2; dx = M) | A-emd-pbh-20261115-153843-7172b66; -155056-ec1b816 | A-emd-pbh-20261115-153845-7172b66; -155056-ec1b816 |
| breakdown | first non-positive metric determinant at t = 32.875 (M/2), 30.25 (M); fields non-finite from 33.125 and 30.75-31.0 (entry 18) | t = 53 (end) |
| core turnaround, mean proper-time error (dx = M/2, V3) | -0.022 M | +0.043 M (local maximum; cycloid fit +0.115, entry 18) |
| core shells, largest abs(R/R_exact - 1) at tau = 16.9 (dx = M; M/2) | 5.6e-2; 6.2e-3 | 2.1e-2; 7.5e-3 |
| first horizon | not reached | none: the collapsed core lies inside one cell |
| dx = M/4 to t = 20 | A-emd-pbh-20261115-164539-0b18e84; turnaround -0.0125 M | -164541-0b18e84; +0.031 (V3), +0.018 (C) |

## What is here

| file | content |
|---|---|
| `common.py` | model of data set 2t, readers of trajectories, histories, table lines, horizon summaries, snapshots; areal radius and Misner-Sharp mass in spherical symmetry |
| `prep.py`, `prep_bh.py` | data set 2t lattices and exact references; data set 3 (expball compensated top-hat) with lattices, exact events, m_AH(tau), lapse reference |
| `compare.py` | the comparison with the exact solution (gauges sr1, sr2, leak; any data set of prep_bh.py): shells, turnaround, trapping, crunch, Misner-Sharp mass on the line, finder mass against the exact mass of the same slice (`finder_g2`), central lapse, constraints, coordinate light speed (`line_light_speed`); options `--dx-fine/--fine-half` (static refined level), `--line-hmax` (default 1), `--g2-window` (default 4 M) |
| `turnaround.py` | turnaround estimators of entry 13; synthetic test; breakdown times of a run by criterion (`--breakdown`) |
| `excision.py` | which criterion removed particles: mesh minimum of the lapse, last recorded lapse and momentum of tracked particles, particles missing between snapshots |
| `fields.py`, `summary.py`, `summary3.py` | z = 0 slices; resolution summaries (wave 2; SR-1L and BH-1) |
| `lapse_ref.py`, `verify_ds3.py`, `constraints_ds3.py` | relaxed-lapse reference; second check of the exact events and constraints of data set 3 |
| `sr1.athinput`, `sr2.athinput`, `sr1l.athinput`, `bh.athinput`, `bh_smr.athinput` | decks (SR-1L, BH-1, BH-1R need `scratch/core/exe/core_gauge/`) |
| `box_list.txt` | batch list of the fixed-box card job (entry 14) |
| `after_m4.sh`, `after_runs3.sh`, `after_wave3.sh` | registered analyses (each registers its own run) |
| `run_cpu.sh`, `runreg.py` | wave-2 processor driver and registration by hand (superseded by `nrpic-run`) |
| `figs/` | PNG copies of the figures |

## How to rerun

    cd /data/haiyangw/nrpic/wt/A-emd-pbh
    C=tracks/A-emd-pbh/runs_ball
    # card job of a batch list (one line per run: <name> <deck> [overrides]); e.g. the fixed box:
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package $C --launcher batch \
        --exe /data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_gpu --list $C/box_list.txt \
        --wall 00:15:00 --purpose "..."
    # analyses (each closes its card run where needed and registers itself; commit figs/ between
    # them, because nrpic-run refuses a dirty package):
    bash $C/after_runs3.sh runs3        # SR-1L and BH-1 of job 4642
    bash $C/after_runs3.sh bh_smr       # BH-1R
    bash $C/after_wave3.sh turnaround A-20261121-074923-d396d73
    bash $C/after_wave3.sh bh -         # excision, BH-1 breakdown, BH-1R with --line-hmax 1e3
    bash $C/after_wave3.sh box A-20261121-074923-d396d73
    # single comparison by hand, e.g. BH-1R:
    .venv/bin/python $C/compare.py --prep <prep>/lat136 --seg <run dir>/bh_smr --gauge leak --leak 8 \
        --dx 0.125 --dx-fine 0.0625 --fine-half 4.0 --line-hmax 1e3 --label bh_smr --out <dir> --figdir $C/figs

The batch lists of the card jobs are `batch.list` in their output directories.

## Requests

- **core** (excision through the interpolant): in BH-1 at dx = M/2 the lapse criterion
  (`alpha_exc = 0.1`) removed 515 particles (rest mass 0.768 of 1.146) while no cell value of the
  lapse on the mesh was below 0.48 (nrpic.hst [16]); the lapse interpolated at those particles
  (trajmet, b-spline) was 0.096 (median, 291 tracked particles within 0.11 M of the origin, where
  eight MeshBlocks meet). In BH-1R 74208 particles went before any cell value fell below 0.1.
  Please check the interpolated lapse near MeshBlock corners against the cell values, and consider
  excising on the cell values of the stencil (or the smaller of the two); and write the removal
  code (-2 lapse, -3 horizon, -4 non-finite) into the removal record, which the executable of
  core_gauge counts together.
- **core** (finder start radius): with the finder started at 3.0 M coordinate radius it found
  nothing in BH-1 at M/8 although the line shows a trapped sphere at 0.44-0.47 M for 0.75 M of
  coordinate time; started at 1.0 M (BH-1R) it found the horizon at every search. A start radius
  tied to a trapped-surface probe on the axis, or several start radii, would make the finder robust
  when the horizon is small in coordinates.
- **core** (non-finite runs): BH-1 at M/4-M/8 wrote non-finite fields from t = 14.3-15.0 and
  exited 0 (the `<z4c_guard>` of core-v0.5 stops such runs with exit 3; the core_gauge executable
  predates it). For the next ball runs please publish the gauge options (`lapse_leak`) in an
  executable that has the guard (they are in core-v0.4 and later per CLAUDE.md; confirm that
  `bh.athinput` and `bh_smr.athinput` run unchanged on core-v0.5).
- **lead of A-emd-pbh**: (1) G2 horizon-mass criterion: BH-1R meets the source paper's order
  after the formation transient at one resolution; the convergence of horizon time and mass needs
  BH-1R at a second refined resolution and a larger outer box (the vacuum exterior is spoiled by
  the boundary at 16 M: line Misner-Sharp mass down to -2.5 beyond 7 M by t = 16), which is
  conv_ball's package. (2) G2 turnaround criterion: use the cycloid estimator C on records that end
  at least one turnaround time after the turnaround and before any instability, and report V3/S
  beside it; at fixed box and lattice the SR-1L turnaround error falls 0.40 -> 0.014 -> 0.006 M but
  changes sign, so an order needs dx = M/8. (3) Name the criterion with every breakdown time
  (entry 18 gives the wording); the SR-2 R2 verdict depends on the estimator (entry 18).
  (4) The lattice, not the box, separates the wave-2 dx = M/4 runs from the M/2 ones (entry 19):
  choose one particle per cell or vary the lattice as its own convergence leg.
- **orch**: none from this round (registration through `nrpic-run --package` worked for every
  run of wave 3).
